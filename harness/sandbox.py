"""Execution sandbox for Codex Agentic Harness."""
import os
import sys
import subprocess
import time
from typing import Dict, Any, Optional, Tuple
from harness.types import ToolResult, ApprovalPolicy

DANGEROUS_PATTERNS = [
    "rm -rf /",
    "rm -rf /*",
    "mkfs",
    "dd if=",
    ":(){ :|:& };:",
    "> /dev/sda",
    "chmod -R 777 /",
    "chown -R"
]

class ExecutionSandbox:
    def __init__(self, workspace_root: str, default_timeout: float = 30.0):
        self.workspace_root = os.path.abspath(workspace_root)
        self.default_timeout = default_timeout

    def is_dangerous(self, command: str) -> Tuple[bool, str]:
        """Check if a bash command contains destructive or system-critical operations."""
        cmd_clean = command.strip().lower()
        for pattern in DANGEROUS_PATTERNS:
            if pattern in cmd_clean:
                return True, f"Command contains high-risk pattern: '{pattern}'"
        return False, ""

    def run_command(
        self,
        command: str,
        cwd: Optional[str] = None,
        timeout: Optional[float] = None,
        env: Optional[Dict[str, str]] = None,
        policy: ApprovalPolicy = ApprovalPolicy.AUTO
    ) -> ToolResult:
        """Execute a shell command within the workspace sandbox."""
        start_time = time.time()
        timeout = timeout or self.default_timeout
        target_cwd = os.path.abspath(cwd) if cwd else self.workspace_root

        # Ensure cwd is within or valid for workspace
        if not os.path.exists(target_cwd):
            os.makedirs(target_cwd, exist_ok=True)

        # Guardrail check
        is_risky, reason = self.is_dangerous(command)
        if is_risky and policy != ApprovalPolicy.AUTO:
            return ToolResult(
                call_id="blocked",
                name="bash",
                success=False,
                output="",
                error=f"[GUARDED POLICY BLOCKED] {reason}",
                exit_code=126,
                execution_time=0.0
            )

        # Setup environment
        exec_env = os.environ.copy()
        exec_env["no_proxy"] = "127.0.0.1,localhost"
        exec_env["NO_PROXY"] = "127.0.0.1,localhost"
        exec_env["WORKSPACE_ROOT"] = self.workspace_root
        existing_pythonpath = exec_env.get("PYTHONPATH", "")
        exec_env["PYTHONPATH"] = f"{self.workspace_root}:{existing_pythonpath}".strip(":")
        if env:
            exec_env.update(env)

        try:
            proc = subprocess.run(
                command,
                shell=True,
                cwd=target_cwd,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=exec_env
            )
            duration = time.time() - start_time
            out = proc.stdout or ""
            err = proc.stderr or ""
            combined = out
            if err:
                combined = f"{out}\n[STDERR]\n{err}".strip() if out else f"[STDERR]\n{err}".strip()

            return ToolResult(
                call_id="",
                name="bash",
                success=(proc.returncode == 0),
                output=combined,
                error=err if proc.returncode != 0 else None,
                exit_code=proc.returncode,
                execution_time=round(duration, 3)
            )
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            return ToolResult(
                call_id="",
                name="bash",
                success=False,
                output=f"[TIMEOUT] Command timed out after {timeout} seconds.",
                error=f"Execution timed out ({timeout}s)",
                exit_code=124,
                execution_time=round(duration, 3)
            )
        except Exception as e:
            duration = time.time() - start_time
            return ToolResult(
                call_id="",
                name="bash",
                success=False,
                output=f"[EXECUTION ERROR] {str(e)}",
                error=str(e),
                exit_code=1,
                execution_time=round(duration, 3)
            )
