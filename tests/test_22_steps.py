"""Verification test suite for Zieork's 22-Step Master Engineering Workflow."""
import json
import sys
import os

sys.path.insert(0, os.path.abspath("."))
from app import app

def run_tests():
    client = app.test_client()
    passed = 0
    total = 0

    def assert_eq(test_name, condition, details=""):
        nonlocal passed, total
        total += 1
        if condition:
            passed += 1
            print(f"  [PASS] {test_name}")
        else:
            print(f"  [FAIL] {test_name}: {details}")
            sys.exit(1)

    print("\n--- Testing Zieork 22-Step Workflow Endpoints ---")

    # 1. Step 4: Workspace Files
    res = client.get("/api/workspace/files")
    assert_eq("GET /api/workspace/files", res.status_code == 200 and "tree" in res.json)

    # 2. Step 4: Specific File Read
    res = client.get("/api/workspace/file?path=app.py")
    assert_eq("GET /api/workspace/file", res.status_code == 200 and "content" in res.json and res.json["lines"] > 0)

    # 3. Step 4: AGENTS.md Read & Update
    res = client.get("/api/workspace/agents_md")
    assert_eq("GET /api/workspace/agents_md", res.status_code == 200 and "content" in res.json)

    orig_content = res.json["content"]
    res = client.post("/api/workspace/agents_md", json={"content": orig_content})
    assert_eq("POST /api/workspace/agents_md", res.status_code == 200 and res.json.get("success") is True)

    # 4. Step 4: Environment Diagnostics
    res = client.get("/api/workspace/env")
    assert_eq("GET /api/workspace/env", res.status_code == 200 and "os" in res.json and "python_version" in res.json)

    # 5. Step 8: Implementation Plan Generator
    res = client.post("/api/task/plan", json={"task": "Implement system font picker with XAML"})
    assert_eq("POST /api/task/plan", res.status_code == 200 and len(res.json.get("steps", [])) == 5)

    # 6. Step 14: Review Actions (accept, reject, revise)
    res = client.post("/api/task/review", json={"action": "accept"})
    assert_eq("POST /api/task/review (accept)", res.status_code == 200 and res.json.get("success") is True)

    res = client.post("/api/task/review", json={"action": "reject"})
    assert_eq("POST /api/task/review (reject)", res.status_code == 200 and res.json.get("success") is True)

    res = client.post("/api/task/review", json={"action": "revise", "prompt": "Use async loader"})
    assert_eq("POST /api/task/review (revise)", res.status_code == 200 and res.json.get("success") is True)

    # 7. Step 16: Git Worktrees
    res = client.get("/api/git/worktrees")
    assert_eq("GET /api/git/worktrees", res.status_code == 200 and "worktrees" in res.json)

    # 8. Step 17: Multi-Agent Team Orchestra (Architect, Backend, Frontend, QA, Reviewer)
    res = client.post("/api/multiagent/run", json={"task": "Build scalable token caching middleware"})
    assert_eq("POST /api/multiagent/run", res.status_code == 200 and len(res.json.get("agents", [])) == 5)

    # 9. Step 18 & 21: Skills and Automations
    res = client.get("/api/skills")
    assert_eq("GET /api/skills", res.status_code == 200 and len(res.json.get("skills", [])) > 0)

    res = client.get("/api/automations")
    assert_eq("GET /api/automations", res.status_code == 200 and len(res.json.get("automations", [])) > 0)

    # 10. Step 19: MCP Servers Registry & Toggle
    res = client.get("/api/mcp/servers")
    assert_eq("GET /api/mcp/servers", res.status_code == 200 and len(res.json.get("servers", [])) >= 5)

    res = client.post("/api/mcp/servers", json={"name": "filesystem", "enabled": True})
    assert_eq("POST /api/mcp/servers", res.status_code == 200 and res.json.get("enabled") is True)

    # 11. Step 22: Ship & Deploy Pipeline
    res = client.post("/api/ship/deploy", json={"target": "production"})
    assert_eq("POST /api/ship/deploy", res.status_code == 200 and res.json.get("status") == "HEALTHY" and "metrics" in res.json)

    # 12. Frontend index.html served
    res = client.get("/")
    assert_eq("GET / (index.html)", res.status_code == 200 and b"Zieork" in res.data and b"plan-card" in res.data)

    print(f"\n✨ ALL {passed}/{total} VERIFICATION CHECKS PASSED!\n")

if __name__ == "__main__":
    run_tests()
