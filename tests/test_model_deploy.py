"""Automated verification for Zieork Sovereign Model Deployment & OpenAI Endpoints."""
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

    print("\n--- Testing Zieork Model Deployment & OpenAI-Compatible Endpoints ---")

    # 1. GET /v1/models
    res = client.get("/v1/models")
    assert_eq("GET /v1/models returns 200", res.status_code == 200)
    data = res.json
    model_ids = [m["id"] for m in data.get("data", [])]
    assert_eq("Models list contains zieork-micro", "zieork-micro" in model_ids)
    assert_eq("Models list contains zieork-fast-135m", "zieork-fast-135m" in model_ids)
    assert_eq("Models list contains zieork-prime-1b", "zieork-prime-1b" in model_ids)

    # 2. GET /api/model/status
    res = client.get("/api/model/status")
    assert_eq("GET /api/model/status returns 200", res.status_code == 200)
    status_data = res.json
    assert_eq("Status shows HEALTHY", status_data.get("status") == "HEALTHY")
    assert_eq("zieork-micro is available", status_data.get("tiers", {}).get("zieork-micro", {}).get("available") is True)

    # 3. POST /api/model/deploy
    deploy_req = {
        "model": "zieork-micro",
        "device": "cpu",
        "quantization": "fp32",
        "threads": 6
    }
    res = client.post("/api/model/deploy", json=deploy_req)
    assert_eq("POST /api/model/deploy returns 200", res.status_code == 200)
    assert_eq("Deployment status is ONLINE", res.json.get("deployment", {}).get("status") == "ONLINE")

    # 4. POST /v1/chat/completions (Non-Streaming)
    prompt = "What is AI?"
    chat_req = {
        "model": "zieork-micro",
        "messages": [
            {"role": "system", "content": "You are Zieork AI."},
            {"role": "user", "content": prompt}
        ],
        "stream": False
    }
    res = client.post("/v1/chat/completions", json=chat_req)
    assert_eq("POST /v1/chat/completions returns 200", res.status_code == 200)
    chat_data = res.json
    assert_eq("Response object is chat.completion", chat_data.get("object") == "chat.completion")
    choices = chat_data.get("choices", [])
    assert_eq("Choices array has at least 1 choice", len(choices) > 0)
    content = choices[0].get("message", {}).get("content", "")
    assert_eq("Assistant message has content", len(content) > 0, f"Got: {content}")
    assert_eq("Usage tokens reported", chat_data.get("usage", {}).get("total_tokens", 0) > 0)

    # 5. POST /v1/chat/completions (Streaming SSE)
    chat_stream_req = {
        "model": "zieork-micro",
        "messages": [{"role": "user", "content": "Hello!"}],
        "stream": True
    }
    res = client.post("/v1/chat/completions", json=chat_stream_req)
    assert_eq("Streaming chat completions returns 200", res.status_code == 200)
    assert_eq("MIME type is text/event-stream", "text/event-stream" in res.content_type)
    assert_eq("Stream ends with [DONE]", b"data: [DONE]" in res.data)

    print(f"\n✨ ALL {passed}/{total} MODEL DEPLOYMENT VERIFICATION CHECKS PASSED!\n")

if __name__ == "__main__":
    run_tests()
