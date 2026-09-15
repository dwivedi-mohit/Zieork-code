"""Comprehensive Automated Verification for ChatGPT-Style Behavior & Presets."""
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("libs"))

from tools.sampling_config import (
    PRESETS,
    get_preset,
    SamplingPreset,
    CHATGPT_BEHAVIORAL_SYSTEM_PROMPT
)
from tools.conversational_align import (
    validate_dataset,
    calculate_repetition_rate,
    score_markdown_structure
)
from cli import compact_conversation_messages
from app import app

class TestChatGPTBehavior(unittest.TestCase):
    """Test suite verifying ChatGPT behavioral alignment, presets, and memory compaction."""

    def test_sampling_presets_defined(self):
        """Verify all expected decoding presets exist and have valid values."""
        self.assertIn("chatgpt", PRESETS)
        self.assertIn("code", PRESETS)
        self.assertIn("creative", PRESETS)
        self.assertIn("precise", PRESETS)

        chatgpt_p = PRESETS["chatgpt"]
        self.assertEqual(chatgpt_p.temperature, 0.7)
        self.assertEqual(chatgpt_p.top_p, 0.9)
        self.assertEqual(chatgpt_p.repeat_penalty, 1.10)
        self.assertEqual(chatgpt_p.top_k, 40)

        # Verify to_dict output
        d = chatgpt_p.to_dict()
        self.assertIn("temperature", d)
        self.assertIn("repeat_penalty", d)
        self.assertIn("top_p", d)

    def test_get_preset_fallback(self):
        """Verify fallback behavior for unknown preset names."""
        p_valid = get_preset("code")
        self.assertEqual(p_valid.name, "code")

        p_unknown = get_preset("nonexistent_preset_xyz")
        self.assertEqual(p_unknown.name, "chatgpt")

        p_none = get_preset(None)
        self.assertEqual(p_none.name, "chatgpt")

    def test_chatgpt_system_prompt_identity_and_behavior(self):
        """Verify the behavioral prompt includes both Mohit Dwivedi identity and ChatGPT guidelines."""
        prompt = CHATGPT_BEHAVIORAL_SYSTEM_PROMPT

        # 1. Identity & Attribution
        self.assertIn("Mohit Dwivedi", prompt)
        self.assertIn("hackORtech", prompt)
        self.assertIn("mohitdwivedi.in", prompt)
        self.assertIn("Karkeli", prompt)
        self.assertIn("sole creator", prompt.lower())

        # 2. Behavioral guidelines
        self.assertIn("Markdown", prompt)
        self.assertIn("code snippets", prompt)
        self.assertIn("robotic boilerplate", prompt)

    def test_conversational_dataset_validation(self):
        """Verify alignment dataset is valid and parseable."""
        result = validate_dataset("data/conversational_alignment_dataset.jsonl")
        self.assertTrue(result.get("valid"), f"Dataset failed validation: {result.get('error')}")
        self.assertGreaterEqual(result.get("samples", 0), 5)
        self.assertGreater(result.get("estimated_tokens", 0), 500)

    def test_repetition_rate_calculation(self):
        """Verify repetition rate metric detects repeated loops."""
        # Non-repetitive text
        clean_text = "The quick brown fox jumps over the lazy dog in the sunny park."
        rate_clean = calculate_repetition_rate(clean_text)
        self.assertEqual(rate_clean, 0.0)

        # Highly repetitive looped text
        loop_text = "hello world repeat this hello world repeat this hello world repeat this hello world repeat this"
        rate_loop = calculate_repetition_rate(loop_text)
        self.assertGreater(rate_loop, 0.5)

    def test_markdown_structure_scoring(self):
        """Verify markdown structure scoring evaluates headers, code blocks, lists, and bolding."""
        markdown_text = (
            "### Solution Overview\n\n"
            "**Key idea**: Use a hash map.\n\n"
            "* Item one\n"
            "* Item two\n\n"
            "```python\ndef foo():\n    return 42\n```"
        )
        scores = score_markdown_structure(markdown_text)
        self.assertEqual(scores["score_out_of_4"], 4)
        self.assertTrue(scores["has_headings"])
        self.assertTrue(scores["has_code_block"])
        self.assertTrue(scores["has_bullet_points"])
        self.assertTrue(scores["has_bold"])

    def test_conversation_compaction(self):
        """Verify sliding window memory compaction prevents context blowup."""
        # Under budget
        short_msgs = [{"role": "user", "content": "Hi"}, {"role": "assistant", "content": "Hello"}]
        compacted = compact_conversation_messages(short_msgs, max_token_budget=1000)
        self.assertEqual(len(compacted), 2)

        # Over budget
        many_msgs = [{"role": "user", "content": "Word " * 200}, {"role": "assistant", "content": "Word " * 200}] * 5
        compacted_large = compact_conversation_messages(many_msgs, max_token_budget=500)
        self.assertLessEqual(len(compacted_large), 6)

    def test_openai_endpoint_with_chatgpt_parameters(self):
        """Verify /v1/chat/completions accepts preset and custom decoding parameters."""
        client = app.test_client()
        req_payload = {
            "model": "zieork-micro",
            "messages": [{"role": "user", "content": "Hello!"}],
            "preset": "chatgpt",
            "temperature": 0.7,
            "top_p": 0.9,
            "repeat_penalty": 1.10
        }
        res = client.post("/v1/chat/completions", json=req_payload)
        self.assertEqual(res.status_code, 200)
        data = res.json
        self.assertEqual(data.get("object"), "chat.completion")
        self.assertGreater(len(data.get("choices", [])), 0)

if __name__ == "__main__":
    unittest.main()
