"""Automated verification for Zieork Sovereign 1M+ Infinite Context Engine."""
import os
import sys

sys.path.insert(0, os.path.abspath("."))
from tools.infinite_context import InfiniteContextEngine

def run_tests():
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

    print("\n--- Testing Zieork 1M+ Infinite Context Engine ---")

    test_db = "data/test_context.db"
    if os.path.exists(test_db):
        os.remove(test_db)

    engine = InfiniteContextEngine(db_path=test_db, chunk_size=100, overlap=20)

    # 1. Test Ingestion of Long Text
    sample_text = (
        "Zieork Sovereign AI is created and developed by Mohit Dwivedi. "
        "It features deep causal attention, 1M+ infinite context indexing, "
        "and runs 100% privately on local CPU without cloud dependency. "
    ) * 50  # ~800 words
    tokens = engine.index_text("test_sovereignty.txt", sample_text)
    assert_eq("Indexed document returned token count", tokens > 500)

    # 2. Check Stats
    stats = engine.get_stats()
    assert_eq("Stats report indexed document", stats["indexed_documents"] == 1)
    assert_eq("Stats report multiple chunks", stats["indexed_chunks"] > 5)
    assert_eq("Capacity reports 1M+ support", "1,000,000+" in stats["capacity"])

    # 3. Retrieve Semantically Relevant Chunks
    results = engine.retrieve("Mohit Dwivedi sovereign CPU", max_tokens=300)
    assert_eq("Retrieval returns non-empty list", len(results) > 0)
    assert_eq("Retrieved chunk contains creator name", "Mohit Dwivedi" in results[0]["content"])
    assert_eq("Score is positive float", results[0]["score"] > 0)

    # 4. Format Prompt with Context
    query = "Who developed Zieork?"
    augmented_prompt = engine.format_prompt_with_context(query, max_tokens=500)
    assert_eq("Augmented prompt contains reference context header", "verified reference context" in augmented_prompt)
    assert_eq("Augmented prompt includes user query", "Who developed Zieork?" in augmented_prompt)

    # 5. Clear Database
    engine.clear()
    cleared_stats = engine.get_stats()
    assert_eq("Cleared stats report 0 documents", cleared_stats["indexed_documents"] == 0)
    assert_eq("Cleared stats report 0 chunks", cleared_stats["indexed_chunks"] == 0)

    # Clean up test database
    if os.path.exists(test_db):
        os.remove(test_db)

    print(f"\n✨ ALL {passed}/{total} INFINITE CONTEXT VERIFICATION CHECKS PASSED!\n")

if __name__ == "__main__":
    run_tests()
