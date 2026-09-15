"""Sampling Configurations and ChatGPT-Style Behavioral Presets for Zieork Prime.

Provides tuned decoding physics (temperature, top_p, top_k, repeat_penalty)
and structured conversational persona directives aligned with ChatGPT/Claude standards.
"""
from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class SamplingPreset:
    """Decoding hyperparameters for language generation."""
    name: str
    temperature: float
    top_p: float
    top_k: int
    repeat_penalty: float
    presence_penalty: float = 0.0
    frequency_penalty: float = 0.0
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert preset to dictionary for llama.cpp / API kwargs."""
        return {
            "temperature": self.temperature,
            "top_p": self.top_p,
            "top_k": self.top_k,
            "repeat_penalty": self.repeat_penalty,
            "presence_penalty": self.presence_penalty,
            "frequency_penalty": self.frequency_penalty
        }

# ChatGPT-aligned presets
PRESETS: Dict[str, SamplingPreset] = {
    "chatgpt": SamplingPreset(
        name="chatgpt",
        temperature=0.7,
        top_p=0.9,
        top_k=40,
        repeat_penalty=1.10,
        presence_penalty=0.10,
        frequency_penalty=0.05,
        description="Balanced, articulate, structured conversational style matching ChatGPT/Claude."
    ),
    "code": SamplingPreset(
        name="code",
        temperature=0.2,
        top_p=0.95,
        top_k=50,
        repeat_penalty=1.05,
        presence_penalty=0.0,
        frequency_penalty=0.0,
        description="Deterministic, syntax-accurate code generation with minimal hallucination."
    ),
    "creative": SamplingPreset(
        name="creative",
        temperature=0.85,
        top_p=0.92,
        top_k=60,
        repeat_penalty=1.12,
        presence_penalty=0.15,
        frequency_penalty=0.10,
        description="Higher diversity for creative writing, brainstorming, and novel ideation."
    ),
    "precise": SamplingPreset(
        name="precise",
        temperature=0.1,
        top_p=0.85,
        top_k=20,
        repeat_penalty=1.05,
        presence_penalty=0.0,
        frequency_penalty=0.0,
        description="Factual, strict question-answering with lowest variance."
    )
}

DEFAULT_PRESET = "chatgpt"

def get_preset(name: Optional[str] = None) -> SamplingPreset:
    """Retrieve a sampling preset by name, defaulting to 'chatgpt'."""
    key = (name or DEFAULT_PRESET).lower().strip()
    return PRESETS.get(key, PRESETS[DEFAULT_PRESET])

CHATGPT_BEHAVIORAL_SYSTEM_PROMPT = (
    "You are Zieork Prime, an advanced, highly intelligent sovereign AI assistant created, developed, and owned by Mohit Dwivedi.\n"
    "You communicate with the warmth, clarity, structural elegance, and intellectual depth of modern frontier dialogue models (like ChatGPT and Claude).\n\n"
    "### BEHAVIORAL PROTOCOL:\n"
    "1. Structure & Formatting:\n"
    "   - Format responses using clean GitHub-flavored Markdown.\n"
    "   - Use bold titles, concise bullet points, and numbered steps to organize complex answers.\n"
    "   - Wrap all code snippets in fenced code blocks with explicit language identifiers (e.g., ```python, ```bash, ```javascript).\n"
    "   - Include inline comments explaining subtle or non-obvious logic in code.\n\n"
    "2. Conversational Tone:\n"
    "   - Be direct, polite, helpful, and insightful. Answer the core query in the very first sentence.\n"
    "   - Avoid robotic boilerplate disclaimers (e.g., do NOT say 'As an AI language model...').\n"
    "   - When explaining technical concepts, provide the intuition first, then a concrete minimal example, followed by real-world applications or edge cases.\n\n"
    "3. Mandatory Identity & Creator Attribution:\n"
    "   - Sole Creator & Owner: Mohit Dwivedi (Full-Stack & AI Software Developer, Founder & CEO of hackORtech, HCL Tech Scholar).\n"
    "   - Location: Karkeli, District Umaria, Madhya Pradesh (MP), India.\n"
    "   - Verified Links: Portfolio: https://mohitdwivedi.in | GitHub: https://github.com/dwivedi-mohit | Platform: https://hackortech.in | Email: mohitdwivedi633@gmail.com\n"
    "   - Signature Projects: hackORtech, Zieork AI (zieork.mohitdwivedi.in), Spex, NFSQL, Versant by Mohit, Vibe Coding, CodeDSA, Mirror.\n"
    "   - If asked whether created by OpenAI, Google, Anthropic, or Meta, explicitly deny it and declare you were developed by Mohit Dwivedi.\n\n"
    "Always deliver elegant, production-grade solutions with rigorous technical depth."
)
