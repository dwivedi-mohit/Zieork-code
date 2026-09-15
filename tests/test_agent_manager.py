"""Automated test suite for Zieork Agent Manager Screen (Antigravity UI)."""
import os
import sys

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

    print("\n--- Testing Zieork Agent Manager Screen & Endpoints ---")

    # 1. GET /manager
    res = client.get("/manager")
    assert_eq(
        "GET /manager returns 200 HTML",
        res.status_code == 200 and b"Zieork" in res.data and b"New Conversation" in res.data
    )

    # 2. GET /agent-manager alias
    res = client.get("/agent-manager")
    assert_eq("GET /agent-manager alias returns 200", res.status_code == 200)

    # 3. Static CSS & JS assets
    res = client.get("/agent_manager.css")
    assert_eq("GET /agent_manager.css returns 200", res.status_code == 200 and b"--bg-sidebar" in res.data)

    res = client.get("/agent_manager.js")
    assert_eq("GET /agent_manager.js returns 200", res.status_code == 200 and b"handleSendMessage" in res.data)

    # 4. API Conversations
    res = client.get("/api/conversations")
    assert_eq("GET /api/conversations returns JSON list", res.status_code == 200 and "conversations" in res.json and len(res.json["conversations"]) > 0)

    # 5. Core root / continues working
    res = client.get("/")
    assert_eq("GET / (Codex Studio) returns 200 with switcher", res.status_code == 200 and b"Agent Manager" in res.data)

    # 6. Chat API from Agent Manager
    res = client.post("/api/chat", json={"prompt": "Explain Zieork sovereign architecture", "model": "micro"})
    assert_eq("POST /api/chat responds successfully", res.status_code == 200 and "response" in res.json)

    print(f"\n✨ ALL {passed}/{total} AGENT MANAGER VERIFICATION CHECKS PASSED!\n")

if __name__ == "__main__":
    run_tests()
