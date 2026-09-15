"""Context management, output clamping, and compaction policies for Codex Harness."""
import re
from typing import List, Dict, Any, Tuple
from harness.types import HarnessStep, Milestone, SessionContext

class ContextManager:
    def __init__(
        self,
        max_lines_per_output: int = 150,
        max_chars_per_output: int = 10000,
        compaction_step_threshold: int = 6,
        keep_recent_steps: int = 3
    ):
        self.max_lines = max_lines_per_output
        self.max_chars = max_chars_per_output
        self.compaction_threshold = compaction_step_threshold
        self.keep_recent_steps = keep_recent_steps

    def clamp_output(self, text: str) -> str:
        """Clamp oversized tool outputs using head/tail preservation invariants."""
        if not text:
            return ""

        lines = text.splitlines()
        if len(lines) > self.max_lines:
            head_count = self.max_lines // 2
            tail_count = self.max_lines - head_count
            omitted = len(lines) - (head_count + tail_count)
            clamped_lines = (
                lines[:head_count]
                + [f"\n[... {omitted} lines truncated to preserve context window ...]\n"]
                + lines[-tail_count:]
            )
            text = "\n".join(clamped_lines)

        if len(text) > self.max_chars:
            head_len = self.max_chars // 2
            tail_len = self.max_chars - head_len
            omitted_chars = len(text) - (head_len + tail_len)
            text = (
                text[:head_len]
                + f"\n[... {omitted_chars} characters truncated ...]\n"
                + text[-tail_len:]
            )

        return text

    def estimate_tokens(self, text: str) -> int:
        """Estimate token count based on whitespace and subword heuristics (~4 chars/token)."""
        if not text:
            return 0
        return max(1, len(text) // 4)

    def compact_history(self, context: SessionContext) -> bool:
        """Compact older steps into milestones when step count exceeds compaction threshold."""
        total_steps = len(context.steps)
        if total_steps <= self.compaction_threshold:
            return False

        # Steps to summarize: all steps except recent N
        steps_to_compact = context.steps[:-self.keep_recent_steps]
        if not steps_to_compact:
            return False

        # Generate structured milestone digest
        actions_summary = []
        for s in steps_to_compact:
            tname = s.tool_call.name if s.tool_call else "reasoning"
            targs = ""
            if s.tool_call and s.tool_call.arguments:
                # brief args
                args_keys = list(s.tool_call.arguments.keys())
                primary_arg = s.tool_call.arguments.get(args_keys[0], "") if args_keys else ""
                targs = f"({str(primary_arg)[:40]})"
            status_symbol = "✓" if (s.tool_result and s.tool_result.success) else "✗"
            actions_summary.append(f"Step {s.step_index}: [{tname}{targs}] {status_symbol}")

        milestone_title = f"Milestone: Completed initial setup & exploration (Steps 1-{len(steps_to_compact)})"
        milestone_summary = (
            f"Executed {len(steps_to_compact)} operational steps: "
            + "; ".join(actions_summary)
            + ". Work environment state updated."
        )

        milestone = Milestone(
            title=milestone_title,
            summary=milestone_summary,
            steps_covered=[s.step_index for s in steps_to_compact]
        )
        context.milestones.append(milestone)

        # Retain only the recent steps in the active prompt sequence
        context.steps = context.steps[-self.keep_recent_steps:]
        return True

    def build_prompt_context(self, context: SessionContext) -> List[Dict[str, str]]:
        """Construct conversation message payload formatted with milestone summaries and recent turns."""
        messages: List[Dict[str, str]] = []

        # 1. Past milestones
        if context.milestones:
            milestone_texts = [f"• {m.title}: {m.summary}" for m in context.milestones]
            milestone_payload = "PREVIOUS MILESTONES (COMPACTED):\n" + "\n".join(milestone_texts)
            messages.append({"role": "system", "content": milestone_payload})

        # 2. Active steps
        for step in context.steps:
            if step.thought:
                messages.append({"role": "assistant", "content": f"THOUGHT: {step.thought}"})

            if step.tool_call:
                tool_msg = f"ACTION: {step.tool_call.name}\nARGUMENTS: {step.tool_call.arguments}"
                messages.append({"role": "assistant", "content": tool_msg})

            if step.tool_result:
                clamped_obs = self.clamp_output(step.tool_result.output)
                obs_status = "SUCCESS" if step.tool_result.success else "FAILURE"
                obs_msg = f"OBSERVATION ({obs_status}, exit code {step.tool_result.exit_code}):\n{clamped_obs}"
                messages.append({"role": "user", "content": obs_msg})

        return messages
