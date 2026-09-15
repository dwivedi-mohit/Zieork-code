"""Workspace, AGENTS.md, Git Worktrees & Review Manager for Zieork."""
import os
import sys
import json
import subprocess
import time
import shutil
from typing import Dict, Any, List, Optional

class WorkspaceManager:
    def __init__(self, workspace_root: str = "."):
        self.workspace_root = os.path.abspath(workspace_root)
        self.agents_md_path = os.path.join(self.workspace_root, "AGENTS.md")

    def get_file_tree(self, path: str = "", max_depth: int = 4) -> Dict[str, Any]:
        """Generate a hierarchical file tree of the workspace."""
        target_dir = os.path.abspath(os.path.join(self.workspace_root, path))
        if not os.path.exists(target_dir):
            return {"error": f"Directory not found: {path}"}

        ignore_dirs = {".git", "__pycache__", "node_modules", ".venv", "libs", ".cache"}

        def build_tree(current_path: str, depth: int):
            if depth > max_depth:
                return []
            items = []
            try:
                entries = sorted(os.listdir(current_path))
            except Exception:
                return []

            for entry in entries:
                if entry in ignore_dirs or entry.startswith(".git"):
                    continue
                full_path = os.path.join(current_path, entry)
                rel_path = os.path.relpath(full_path, self.workspace_root)
                is_dir = os.path.isdir(full_path)

                item_info = {
                    "name": entry,
                    "path": rel_path,
                    "is_dir": is_dir
                }

                if is_dir:
                    item_info["children"] = build_tree(full_path, depth + 1)
                else:
                    try:
                        item_info["size"] = os.path.getsize(full_path)
                    except Exception:
                        item_info["size"] = 0
                items.append(item_info)
            return items

        return {
            "root": self.workspace_root,
            "tree": build_tree(target_dir, 1)
        }

    def read_file(self, rel_path: str) -> Dict[str, Any]:
        """Read the exact contents of a file within the workspace."""
        abs_path = os.path.abspath(os.path.join(self.workspace_root, rel_path))
        if not abs_path.startswith(self.workspace_root):
            return {"error": "Path traversal not permitted."}
        if not os.path.exists(abs_path):
            return {"error": f"File not found: {rel_path}"}
        if os.path.isdir(abs_path):
            return {"error": f"Target is a directory: {rel_path}"}

        try:
            with open(abs_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            return {
                "path": rel_path,
                "content": content,
                "size": len(content),
                "lines": len(content.splitlines())
            }
        except Exception as e:
            return {"error": str(e)}

    def get_agents_md(self) -> Dict[str, Any]:
        """Read AGENTS.md instructions for Zieork."""
        if not os.path.exists(self.agents_md_path):
            # Create default AGENTS.md if it doesn't exist
            default_content = (
                "# 🤖 Zieork Project Instructions & Operational Rules (AGENTS.md)\n\n"
                "## 1. Code Standards\n"
                "- Write self-contained, elegant Python code with standard library support.\n"
                "- Never use deprecated methods or unverified third-party libraries.\n"
                "- Include docstrings and type hints for all public methods.\n\n"
                "## 2. Test Verification\n"
                "- Always write unit tests for new modules in `tests/`.\n"
                "- Verify all tests pass with zero warnings before declaring a task complete.\n\n"
                "## 3. Git & Worktrees\n"
                "- Use Conventional Commits (`feat:`, `fix:`, `refactor:`, `test:`).\n"
                "- Keep diffs minimal, clean, and well-documented.\n\n"
                "## 4. Safety & Sandbox\n"
                "- Never delete workspace files without user confirmation.\n"
                "- Execute terminal commands inside the sandboxed environment.\n"
            )
            with open(self.agents_md_path, "w", encoding="utf-8") as f:
                f.write(default_content)

        with open(self.agents_md_path, "r", encoding="utf-8") as f:
            content = f.read()

        return {"path": "AGENTS.md", "content": content}

    def save_agents_md(self, content: str) -> Dict[str, Any]:
        """Save updated AGENTS.md rules."""
        with open(self.agents_md_path, "w", encoding="utf-8") as f:
            f.write(content)
        return {"success": True, "message": "AGENTS.md updated successfully."}

    def get_environment_info(self) -> Dict[str, Any]:
        """Retrieve system & environment diagnostics."""
        import platform
        import psutil

        mem = psutil.virtual_memory()
        disk = psutil.disk_usage(self.workspace_root)

        return {
            "os": platform.platform(),
            "python_version": sys.version.split()[0],
            "workspace": self.workspace_root,
            "cpu_count": psutil.cpu_count(logical=True),
            "ram_used_gb": round((mem.total - mem.available) / (1024**3), 2),
            "ram_total_gb": round(mem.total / (1024**3), 2),
            "disk_free_gb": round(disk.free / (1024**3), 2),
            "active_env": sys.prefix
        }

    def get_worktrees(self) -> Dict[str, Any]:
        """List active Git worktrees."""
        worktrees = [
            {"path": self.workspace_root, "branch": "main", "is_bare": False, "is_current": True}
        ]
        try:
            res = subprocess.run(
                "git worktree list",
                shell=True,
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                timeout=2
            )
            if res.returncode == 0 and res.stdout.strip():
                worktrees = []
                for line in res.stdout.strip().splitlines():
                    parts = line.split()
                    if parts:
                        wt_path = parts[0]
                        branch = parts[2].strip("[]") if len(parts) >= 3 else "detached"
                        is_curr = (os.path.abspath(wt_path) == self.workspace_root)
                        worktrees.append({
                            "path": wt_path,
                            "branch": branch,
                            "is_current": is_curr
                        })
        except Exception:
            pass

        return {"worktrees": worktrees}

    def create_worktree(self, branch_name: str, path: Optional[str] = None) -> Dict[str, Any]:
        """Create a new isolated Git worktree for parallel agent workflows."""
        clean_branch = branch_name.strip().replace(" ", "-")
        target_path = path or os.path.join(self.workspace_root, f".worktrees/{clean_branch}")
        os.makedirs(os.path.dirname(target_path), exist_ok=True)

        try:
            cmd = f"git worktree add -b {clean_branch} {target_path}"
            res = subprocess.run(cmd, shell=True, cwd=self.workspace_root, capture_output=True, text=True, timeout=5)
            if res.returncode == 0:
                return {"success": True, "branch": clean_branch, "path": target_path}
            else:
                return {"success": False, "error": res.stderr or res.stdout}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def handle_review_action(self, action: str, file_path: Optional[str] = None, revision_prompt: Optional[str] = None) -> Dict[str, Any]:
        """Process user review decision: accept, reject, or revise."""
        action = action.lower().strip()
        if action == "accept":
            # Keep changes and stage if git repository exists
            try:
                subprocess.run("git add .", shell=True, cwd=self.workspace_root, capture_output=True, text=True, timeout=2)
            except Exception:
                pass
            return {"success": True, "action": "accept", "message": "Changes accepted and staged for commit."}

        elif action == "reject":
            # Revert modified files
            if file_path:
                abs_f = os.path.join(self.workspace_root, file_path)
                try:
                    subprocess.run(f"git checkout -- {file_path}", shell=True, cwd=self.workspace_root, capture_output=True, text=True, timeout=2)
                except Exception:
                    pass
            else:
                try:
                    subprocess.run("git checkout .", shell=True, cwd=self.workspace_root, capture_output=True, text=True, timeout=2)
                except Exception:
                    pass
            return {"success": True, "action": "reject", "message": "All proposed changes have been rejected and reverted."}

        elif action == "revise":
            return {
                "success": True,
                "action": "revise",
                "message": f"Revision request registered: '{revision_prompt or 'Make adjustments'}'. Zieork is planning the revisions now."
            }

        return {"error": f"Unknown review action: {action}"}

workspace_mgr = WorkspaceManager(".")
