"""Standard coding tools registry for Codex Agentic Harness."""
import os
import glob
import re
import fnmatch
import time
from typing import Dict, Any, List, Optional
from harness.types import ToolResult, ToolCall, ApprovalPolicy
from harness.sandbox import ExecutionSandbox

class ToolRegistry:
    def __init__(self, sandbox: ExecutionSandbox):
        self.sandbox = sandbox
        self.workspace_root = sandbox.workspace_root

    def _resolve_path(self, rel_path: str) -> str:
        """Resolve a path safely relative to workspace root."""
        if not rel_path:
            return self.workspace_root
        if os.path.isabs(rel_path):
            return os.path.abspath(rel_path)
        return os.path.abspath(os.path.join(self.workspace_root, rel_path))

    def bash(self, command: str, cwd: Optional[str] = None, timeout: Optional[float] = None) -> ToolResult:
        """Execute a shell command inside the sandbox."""
        resolved_cwd = self._resolve_path(cwd) if cwd else self.workspace_root
        return self.sandbox.run_command(command, cwd=resolved_cwd, timeout=timeout)

    def read_file(self, path: str, start_line: int = 1, end_line: Optional[int] = None) -> ToolResult:
        """Read lines from a file with line numbering."""
        start_time = time.time()
        abs_path = self._resolve_path(path)
        if not os.path.exists(abs_path):
            return ToolResult(
                call_id="", name="read_file", success=False,
                output="", error=f"File not found: {path}", exit_code=1,
                execution_time=round(time.time() - start_time, 3)
            )
        if os.path.isdir(abs_path):
            return ToolResult(
                call_id="", name="read_file", success=False,
                output="", error=f"Target path is a directory, not a file: {path}", exit_code=1,
                execution_time=round(time.time() - start_time, 3)
            )

        try:
            with open(abs_path, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()

            total_lines = len(lines)
            s = max(1, start_line)
            e = min(total_lines, end_line) if end_line else total_lines

            numbered_lines = []
            for i in range(s - 1, e):
                numbered_lines.append(f"{i + 1:4d} | {lines[i].rstrip()}")

            header = f"[FILE: {path} (Showing lines {s}-{e} of {total_lines})]\n"
            content = header + "\n".join(numbered_lines)

            return ToolResult(
                call_id="", name="read_file", success=True,
                output=content, exit_code=0,
                execution_time=round(time.time() - start_time, 3)
            )
        except Exception as e:
            return ToolResult(
                call_id="", name="read_file", success=False,
                output="", error=str(e), exit_code=1,
                execution_time=round(time.time() - start_time, 3)
            )

    def write_file(self, path: str, content: str, overwrite: bool = True) -> ToolResult:
        """Create or overwrite a file with specified content."""
        start_time = time.time()
        abs_path = self._resolve_path(path)

        if os.path.exists(abs_path) and not overwrite:
            return ToolResult(
                call_id="", name="write_file", success=False,
                output="", error=f"File exists and overwrite is False: {path}", exit_code=1,
                execution_time=round(time.time() - start_time, 3)
            )

        try:
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)
            with open(abs_path, "w", encoding="utf-8") as f:
                f.write(content)

            lines_count = len(content.splitlines())
            bytes_count = len(content.encode("utf-8"))
            msg = f"Successfully wrote {bytes_count} bytes ({lines_count} lines) to {path}"

            return ToolResult(
                call_id="", name="write_file", success=True,
                output=msg, exit_code=0,
                execution_time=round(time.time() - start_time, 3)
            )
        except Exception as e:
            return ToolResult(
                call_id="", name="write_file", success=False,
                output="", error=str(e), exit_code=1,
                execution_time=round(time.time() - start_time, 3)
            )

    def edit_file(self, path: str, target_content: str, replacement_content: str, allow_multiple: bool = False) -> ToolResult:
        """Edit an existing file by replacing target_content with replacement_content."""
        start_time = time.time()
        abs_path = self._resolve_path(path)

        if not os.path.exists(abs_path):
            return ToolResult(
                call_id="", name="edit_file", success=False,
                output="", error=f"File not found: {path}", exit_code=1,
                execution_time=round(time.time() - start_time, 3)
            )

        try:
            with open(abs_path, "r", encoding="utf-8") as f:
                old_text = f.read()

            if target_content not in old_text:
                return ToolResult(
                    call_id="", name="edit_file", success=False,
                    output="", error=f"Target content not found in file: {path}", exit_code=1,
                    execution_time=round(time.time() - start_time, 3)
                )

            count = old_text.count(target_content)
            if count > 1 and not allow_multiple:
                return ToolResult(
                    call_id="", name="edit_file", success=False,
                    output="", error=f"Target content occurs {count} times. Specify unique lines or set allow_multiple=True.", exit_code=1,
                    execution_time=round(time.time() - start_time, 3)
                )

            new_text = old_text.replace(target_content, replacement_content) if allow_multiple else old_text.replace(target_content, replacement_content, 1)

            with open(abs_path, "w", encoding="utf-8") as f:
                f.write(new_text)

            return ToolResult(
                call_id="", name="edit_file", success=True,
                output=f"Successfully replaced {count if allow_multiple else 1} occurrence(s) in {path}", exit_code=0,
                execution_time=round(time.time() - start_time, 3)
            )
        except Exception as e:
            return ToolResult(
                call_id="", name="edit_file", success=False,
                output="", error=str(e), exit_code=1,
                execution_time=round(time.time() - start_time, 3)
            )

    def list_dir(self, path: str = ".", max_entries: int = 50) -> ToolResult:
        """List contents of a directory with file types and sizes."""
        start_time = time.time()
        abs_path = self._resolve_path(path)

        if not os.path.exists(abs_path):
            return ToolResult(
                call_id="", name="list_dir", success=False,
                output="", error=f"Directory not found: {path}", exit_code=1,
                execution_time=round(time.time() - start_time, 3)
            )

        try:
            entries = []
            for item in sorted(os.listdir(abs_path)):
                if item.startswith(".git") or item == "__pycache__":
                    continue
                item_path = os.path.join(abs_path, item)
                is_dir = os.path.isdir(item_path)
                badge = "[DIR] " if is_dir else "[FILE]"
                size_str = ""
                if not is_dir:
                    try:
                        sz = os.path.getsize(item_path)
                        size_str = f" ({sz:,} bytes)"
                    except Exception:
                        pass
                entries.append(f"{badge} {item}{size_str}")

            clipped = entries[:max_entries]
            output = f"Contents of {path} ({len(entries)} items):\n" + "\n".join(clipped)
            if len(entries) > max_entries:
                output += f"\n[... {len(entries) - max_entries} more entries omitted ...]"

            return ToolResult(
                call_id="", name="list_dir", success=True,
                output=output, exit_code=0,
                execution_time=round(time.time() - start_time, 3)
            )
        except Exception as e:
            return ToolResult(
                call_id="", name="list_dir", success=False,
                output="", error=str(e), exit_code=1,
                execution_time=round(time.time() - start_time, 3)
            )

    def grep_search(self, query: str, path: str = ".", case_sensitive: bool = False, max_matches: int = 30) -> ToolResult:
        """Search for literal query in files across workspace."""
        start_time = time.time()
        abs_path = self._resolve_path(path)

        matches = []
        flags = 0 if case_sensitive else re.IGNORECASE
        pattern = re.compile(re.escape(query), flags)

        for root, dirs, files in os.walk(abs_path):
            # Skip noise directories
            dirs[:] = [d for d in dirs if d not in {".git", "__pycache__", "node_modules", ".venv", "libs"}]
            for fname in files:
                fpath = os.path.join(root, fname)
                try:
                    with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                        for idx, line in enumerate(f, 1):
                            if pattern.search(line):
                                rel = os.path.relpath(fpath, self.workspace_root)
                                matches.append(f"{rel}:{idx}: {line.strip()}")
                                if len(matches) >= max_matches:
                                    break
                except Exception:
                    pass
                if len(matches) >= max_matches:
                    break
            if len(matches) >= max_matches:
                break

        if matches:
            res_str = f"Found {len(matches)} match(es) for '{query}':\n" + "\n".join(matches)
        else:
            res_str = f"No matches found for '{query}' in {path}"

        return ToolResult(
            call_id="", name="grep_search", success=True,
            output=res_str, exit_code=0,
            execution_time=round(time.time() - start_time, 3)
        )

    def run_tests(self, command: Optional[str] = None, test_file: Optional[str] = None) -> ToolResult:
        """Run automated test suite (pytest, unittest, or custom runner) and parse output."""
        if not command:
            if test_file:
                command = f"python3 -m unittest {test_file}"
            elif os.path.exists(os.path.join(self.workspace_root, "tests")):
                command = "python3 -m unittest discover -s tests"
            else:
                command = "python3 -m unittest"

        res = self.bash(command)

        # Parse test metrics (e.g., Ran X tests, OK or FAILED)
        out = res.output or ""
        test_summary = "Tests execution finished."
        if "Ran " in out:
            match = re.search(r'Ran (\d+) tests? in ([\d\.]+)s', out)
            if match:
                test_summary = f"Ran {match.group(1)} test(s) in {match.group(2)}s."

        status_flag = "PASSED" if res.success else "FAILED"
        parsed_output = f"[TEST RUNNER: {status_flag}]\nSummary: {test_summary}\n\n{out}"

        return ToolResult(
            call_id=res.call_id,
            name="run_tests",
            success=res.success,
            output=parsed_output,
            error=res.error,
            exit_code=res.exit_code,
            execution_time=res.execution_time
        )

    def dispatch(self, name: str, arguments: Dict[str, Any]) -> ToolResult:
        """Dispatch tool invocation dynamically by name."""
        name = name.lower().strip()
        handler = getattr(self, name, None)
        if not handler or not callable(handler):
            return ToolResult(
                call_id="", name=name, success=False,
                output="", error=f"Unknown tool: '{name}'. Available: [bash, read_file, write_file, edit_file, list_dir, grep_search, run_tests]",
                exit_code=1, execution_time=0.0
            )

        try:
            return handler(**arguments)
        except TypeError as te:
            return ToolResult(
                call_id="", name=name, success=False,
                output="", error=f"Invalid arguments for {name}: {str(te)}",
                exit_code=1, execution_time=0.0
            )
        except Exception as e:
            return ToolResult(
                call_id="", name=name, success=False,
                output="", error=f"Error executing {name}: {str(e)}",
                exit_code=1, execution_time=0.0
            )

    def get_schemas(self) -> List[Dict[str, Any]]:
        """Return standardized OpenAI/Codex JSON schemas for all registered tools."""
        return [
            {
                "name": "bash",
                "description": "Execute a shell command in the workspace sandbox.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": "The exact shell command line string to run."},
                        "cwd": {"type": "string", "description": "Optional working directory relative to workspace root."},
                        "timeout": {"type": "number", "description": "Optional timeout in seconds."}
                    },
                    "required": ["command"]
                }
            },
            {
                "name": "read_file",
                "description": "Read file contents with 1-indexed line numbers and line range slicing.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Path to file relative to workspace root."},
                        "start_line": {"type": "integer", "description": "Starting line number (1-indexed)."},
                        "end_line": {"type": "integer", "description": "Ending line number (inclusive)."}
                    },
                    "required": ["path"]
                }
            },
            {
                "name": "write_file",
                "description": "Create a new file or completely overwrite an existing file.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Target file path."},
                        "content": {"type": "string", "description": "Exact text content to write."},
                        "overwrite": {"type": "boolean", "description": "Whether to overwrite existing file."}
                    },
                    "required": ["path", "content"]
                }
            },
            {
                "name": "edit_file",
                "description": "Replace a unique contiguous block of text in an existing file.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Path to file to edit."},
                        "target_content": {"type": "string", "description": "Exact text string to replace."},
                        "replacement_content": {"type": "string", "description": "Replacement text content."},
                        "allow_multiple": {"type": "boolean", "description": "Allow multiple replacements if target appears multiple times."}
                    },
                    "required": ["path", "target_content", "replacement_content"]
                }
            },
            {
                "name": "list_dir",
                "description": "List files and directories within a specified path.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Directory path relative to workspace."},
                        "max_entries": {"type": "integer", "description": "Max entries to return."}
                    }
                }
            },
            {
                "name": "grep_search",
                "description": "Search for a pattern or literal string across files in the workspace.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search term or regex pattern."},
                        "path": {"type": "string", "description": "Root path to search within."},
                        "case_sensitive": {"type": "boolean", "description": "Case-sensitive match."}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "run_tests",
                "description": "Execute automated test suites (unittest/pytest) and parse pass/fail results.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": "Custom test command line."},
                        "test_file": {"type": "string", "description": "Optional specific test file path."}
                    }
                }
            }
        ]
