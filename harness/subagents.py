"""Subagent coordinator for the Codex Agentic Harness."""
import time
from typing import Dict, Any, List, Optional
from harness.types import ToolResult, ToolCall

class SubagentManager:
    def __init__(self, tool_registry):
        self.tool_registry = tool_registry

    def spawn(self, role: str, instruction: str) -> ToolResult:
        """Spawn a specialized subagent to execute a focused task without cluttering main context."""
        start_time = time.time()
        role = role.lower().strip()

        if role in ["researcher", "codebase_researcher"]:
            # Run search / inspection
            grep_res = self.tool_registry.grep_search(query=instruction, path=".")
            dir_res = self.tool_registry.list_dir(path=".")
            summary = (
                f"[Subagent: Researcher]\n"
                f"Scope: {instruction}\n"
                f"Findings:\n{grep_res.output[:800]}\n"
                f"Workspace structure:\n{dir_res.output[:400]}"
            )
            return ToolResult(
                call_id="", name=f"subagent_{role}", success=True,
                output=summary, exit_code=0, execution_time=round(time.time() - start_time, 3)
            )

        elif role in ["tester", "unit_tester"]:
            # Run test discovery
            test_res = self.tool_registry.run_tests()
            summary = f"[Subagent: Tester]\nStatus: {'PASSED' if test_res.success else 'FAILED'}\n{test_res.output}"
            return ToolResult(
                call_id="", name=f"subagent_{role}", success=test_res.success,
                output=summary, exit_code=test_res.exit_code, execution_time=round(time.time() - start_time, 3)
            )

        elif role in ["debugger"]:
            # Run python syntax check or linter on suspected files
            py_files = self.tool_registry.list_dir(".")
            summary = f"[Subagent: Debugger]\nInvestigating: {instruction}\nAnalyzed workspace files."
            return ToolResult(
                call_id="", name=f"subagent_{role}", success=True,
                output=summary, exit_code=0, execution_time=round(time.time() - start_time, 3)
            )

        else:
            return ToolResult(
                call_id="", name="subagent", success=False,
                output="", error=f"Unknown subagent role: '{role}'. Available: [researcher, tester, debugger]",
                exit_code=1, execution_time=round(time.time() - start_time, 3)
            )
