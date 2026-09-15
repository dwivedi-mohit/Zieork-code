"""Agent Tool Adapter for Codex Agentic Harness."""
import os
from typing import Dict, Any, Optional, List
from harness import CodexHarness, CodexBench, ApprovalPolicy

# Global harness instance
_harness_instance = None
_bench_instance = None

def get_harness() -> CodexHarness:
    global _harness_instance
    if _harness_instance is None:
        _harness_instance = CodexHarness(workspace_root=".")
    return _harness_instance

def get_bench() -> CodexBench:
    global _bench_instance
    if _bench_instance is None:
        _bench_instance = CodexBench(workspace_root=".")
    return _bench_instance

def execute_harness_task(goal: str, max_steps: int = 10, policy: str = "auto") -> Dict[str, Any]:
    """Run an autonomous coding mission inside the Codex Agentic Harness."""
    h = get_harness()
    app_policy = ApprovalPolicy.GUARDED if policy == "guarded" else ApprovalPolicy.AUTO
    ctx = h.run_mission(goal=goal, max_steps=max_steps, policy=app_policy)

    # Format human-readable trace
    trace_lines = [
        f"### ⚡ Codex Agentic Harness — Execution Trace (`{ctx.session_id}`)\n",
        f"**Goal**: {ctx.goal}",
        f"**Status**: `{ctx.status.value.upper()}` • **Steps**: {len(ctx.steps)} • **Policy**: `{app_policy.value}`\n",
        "| Step | Action | Tool | Status | Output Preview |",
        "| :--- | :--- | :--- | :--- | :--- |"
    ]

    for s in ctx.steps:
        tool_name = s.tool_call.name if s.tool_call else "finish"
        status_badge = "✅ PASSED" if (s.tool_result and s.tool_result.success) else "⚠️ FAILED"
        preview = ""
        if s.tool_result and s.tool_result.output:
            first_line = s.tool_result.output.strip().splitlines()[0] if s.tool_result.output.strip() else ""
            preview = first_line[:65].replace("|", "\\|")
        trace_lines.append(f"| Step {s.step_index} | {s.thought[:40]}... | `{tool_name}` | {status_badge} | `{preview}` |")

    trace_lines.append(f"\n**Final Result**: {ctx.final_response or 'Mission accomplished.'}")

    return {
        "session_id": ctx.session_id,
        "status": ctx.status.value,
        "steps_count": len(ctx.steps),
        "formatted_trace": "\n".join(trace_lines),
        "steps": [
            {
                "step_index": s.step_index,
                "thought": s.thought,
                "tool": s.tool_call.name if s.tool_call else "finish",
                "arguments": s.tool_call.arguments if s.tool_call else {},
                "output": s.tool_result.output if s.tool_result else "",
                "success": s.tool_result.success if s.tool_result else True,
                "exit_code": s.tool_result.exit_code if s.tool_result else 0
            }
            for s in ctx.steps
        ]
    }

def run_codex_benchmarks(task_ids: Optional[List[str]] = None) -> Dict[str, Any]:
    """Run CodexBench evaluation suite and format results."""
    bench = get_bench()
    return bench.run_benchmark(task_ids=task_ids)
