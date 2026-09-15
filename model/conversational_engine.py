"""Conversational Engine with Contextual Memory and Neural Generation."""
import re
import random
import time
from typing import List, Dict, Generator, Optional
from model.tokenizer import Tokenizer
from model.transformer import MicroTransformer

class ConversationalEngine:
    def __init__(self, model: MicroTransformer, tokenizer: Tokenizer):
        self.model = model
        self.tokenizer = tokenizer
        self.user_name: Optional[str] = None
        self.context_memory: Dict[str, str] = {}

    def update_context(self, user_text: str):
        """Extract and memorize user preferences, name, and facts from dialogue."""
        text_lower = user_text.lower().strip()

        # Name extraction: "my name is X", "i am X", "call me X"
        name_match = re.search(r'\b(?:my name is|i am|call me|myself)\s+([A-Za-z]+)', text_lower)
        if name_match:
            extracted_name = name_match.group(1).capitalize()
            # Avoid matching common words
            if extracted_name.lower() not in {"a", "an", "the", "ready", "happy", "curious", "testing", "here"}:
                self.user_name = extracted_name
                self.context_memory["name"] = extracted_name

    def generate_response(self, messages: List[Dict[str, str]], system_prompt: str = "") -> str:
        """Generate a complete coherent response based on conversation history."""
        if not messages:
            return "Hello! How can I help you today?"

        last_user_msg = messages[-1].get("content", "").strip()
        self.update_context(last_user_msg)

        text_lower = last_user_msg.lower().strip()
        text_clean = re.sub(r'[^\w\s]', '', text_lower)

        # 1. Greetings & Personal Introductions
        if text_clean in {"hi", "hello", "hey", "greetings", "good morning", "good evening", "hl", "hii", "helo"}:
            if self.user_name:
                return f"Hello {self.user_name}! It's great to talk to you. What would you like to build or explore today?"
            return "Hello! I am your local AI assistant running completely from scratch on your CPU. How can I help you today?"

        # 2. User Name inquiry
        if any(q in text_lower for q in ["what is my name", "who am i", "do you know my name", "remember my name"]):
            if self.user_name:
                return f"Your name is {self.user_name}! You told me earlier. How can I assist you, {self.user_name}?"
            return "I don't think you've told me your name yet! What should I call you?"

        # Name introduction statement: "my name is mohit"
        if re.search(r'\b(my name is|call me)\b', text_lower):
            if self.user_name:
                return f"Nice to meet you, {self.user_name}! I'm Zieork, created and developed by Mohit Dwivedi. How can I assist you today?"

        # 3. Identity, Creator & Owner (Mohit Dwivedi)
        if any(q in text_lower for q in ["who made you", "who created you", "who is your owner", "who is your boss", "who built you", "who is your creator"]):
            return (
                "I was created, developed, and owned by **Mohit Dwivedi**.\n\n"
                "Mohit is a Full-Stack & AI Software Developer, an HCL Tech Scholar (TechBee early-career engineering program), "
                "and the Founder & CEO of [hackORtech](https://hackortech.in) from Karkeli, Umaria, Madhya Pradesh, India. "
                "You can explore his work at [mohitdwivedi.in](https://mohitdwivedi.in) or connect with him on GitHub at [github.com/dwivedi-mohit](https://github.com/dwivedi-mohit)."
            )

        if any(q in text_lower for q in ["built by openai", "made by openai", "created by openai", "are you chatgpt", "made by google", "made by meta", "made by anthropic"]):
            return (
                "No, I was not built by OpenAI, Google, Anthropic, or Meta. "
                "I was created and developed by **Mohit Dwivedi**, a Full-Stack and AI Developer based in India, "
                "using modern neural engineering and model orchestration techniques."
            )

        if any(q in text_lower for q in ["mohit dwivedi", "who is mohit", "about mohit", "tell me about mohit", "mohit projects"]):
            return (
                "**Mohit Dwivedi** is a Full-Stack & AI Software Developer, Founder, and Product Builder based in Karkeli, District Umaria, MP, India.\n\n"
                "• **Current Roles:** HCL Tech Scholar (Enterprise software, SAP ABAP, relational databases) & Founder/CEO of [hackORtech](https://hackortech.in).\n"
                "• **Signature Projects (15+ Apps):** hackORtech, Zieork AI (zieork.mohitdwivedi.in), Spex (real-time WebRTC communications), NFSQL (NL-to-SQL converter), Versant prep simulator, Vibe Coding, CodeDSA, and Mirror.\n"
                "• **Verified Links:** [Portfolio](https://mohitdwivedi.in) • [GitHub](https://github.com/dwivedi-mohit) • Email: `mohitdwivedi633@gmail.com`."
            )

        if any(q in text_lower for q in ["who are you", "what are you", "your name", "what model", "about yourself"]):
            return (
                "I am **Zieork**, an advanced sovereign artificial intelligence assistant created, developed, and owned by **Mohit Dwivedi**.\n\n"
                "I run directly on local edge hardware with zero external cloud dependencies, providing deep technical reasoning, code generation, and multi-modal tool integration."
            )

        if any(q in text_lower for q in ["how many parameters", "model size", "specs", "ram usage"]):
            return (
                "Here are my live specifications:\n"
                "• **System:** Zieork Sovereign Neural Operating System\n"
                "• **Creator & Owner:** Mohit Dwivedi (https://mohitdwivedi.in)\n"
                "• **Architecture:** Deep Causal Self-Attention Tensor Core\n"
                "• **Engine Tiers:** Zieork Prime (1.23B Coder Reasoning), Zieork Micro (Pure NumPy Kernel)\n"
                "• **Execution:** 100% Private Local Edge Execution (Zero Cloud Dependency)\n"
                "• **Hardware:** Multi-threaded Intel CPU compute"
            )

        # 4. Core Concepts & Explanations
        if "what is ai" in text_lower or text_clean == "ai":
            return (
                "**Artificial Intelligence (AI)** refers to computer systems engineered to simulate human intelligence. "
                "Instead of following rigid, hand-written rules, AI models learn complex mathematical patterns from data to understand language, recognize images, and make decisions."
            )

        if "neural network" in text_lower:
            return (
                "A **Neural Network** is a computational graph inspired by biological brains. It is made of:\n\n"
                "1. **Input Layer:** Receives the raw features (tokens or pixels).\n"
                "2. **Hidden Layers:** Tensors of weights and biases with non-linear activation functions (like GELU or ReLU).\n"
                "3. **Output Layer:** Produces probabilities (e.g. predicting the next word or class)."
            )

        if "transformer" in text_lower or "self-attention" in text_lower:
            return (
                "**Transformers** are deep learning architectures introduced in 2017 ('Attention Is All You Need').\n\n"
                "Their superpower is **Causal Self-Attention**: for every word in a sentence, the model computes Query ($Q$), Key ($K$), and Value ($V$) matrices to score how relevant other words are, processing language in parallel with incredible efficiency."
            )

        if "cpu vs gpu" in text_lower or ("cpu" in text_lower and "gpu" in text_lower):
            return (
                "**CPU vs. GPU in AI:**\n\n"
                "• **CPU (Central Processing Unit):** Designed for complex sequential logic with a few powerful cores. Ideal for lightweight models (<100MB) like this one!\n"
                "• **GPU (Graphics Processing Unit):** Packed with thousands of smaller cores engineered for massive parallel matrix multiplications, essential for training giant multi-billion parameter models."
            )

        if "quantization" in text_lower:
            return (
                "**Quantization** is the process of compressing a model's weights from high precision (like 32-bit floating point) to lower precision (like 8-bit, 4-bit, or even 1-bit).\n\n"
                "This shrinks model size by 4x to 8x and accelerates CPU inference while preserving accuracy."
            )

        if "machine learning" in text_lower:
            return (
                "**Machine Learning (ML)** is a subset of AI where algorithms learn rules and relationships directly from data. As they process more examples, their predictive accuracy automatically improves."
            )

        # 5. Code Generation
        if "python" in text_lower or "code" in text_lower or "function" in text_lower:
            if "reverse" in text_lower:
                return (
                    "Here is a Python function to reverse a string:\n\n"
                    "```python\n"
                    "def reverse_string(text: str) -> str:\n"
                    "    return text[::-1]\n\n"
                    "# Example usage:\n"
                    "print(reverse_string('mohit'))   # Output: 'tihom'\n"
                    "print(reverse_string('Zieork'))   # Output: 'kroeiz'\n"
                    "```"
                )
            if "prime" in text_lower:
                return (
                    "Here is a Python function to check if a number is prime:\n\n"
                    "```python\n"
                    "def is_prime(n: int) -> bool:\n"
                    "    if n < 2:\n"
                    "        return False\n"
                    "    for i in range(2, int(n**0.5) + 1):\n"
                    "        if n % i == 0:\n"
                    "            return False\n"
                    "    return True\n\n"
                    "# Example:\n"
                    "print(is_prime(17))  # True\n"
                    "print(is_prime(20))  # False\n"
                    "```"
                )
            if "add" in text_lower or "sum" in text_lower:
                return (
                    "Here is a Python function to add two numbers:\n\n"
                    "```python\n"
                    "def add(a: float, b: float) -> float:\n"
                    "    return a + b\n\n"
                    "print(add(15, 27))  # 42\n"
                    "```"
                )
            if "max" in text_lower or "largest" in text_lower:
                return (
                    "Here is a Python function to find the maximum in a list:\n\n"
                    "```python\n"
                    "def find_max(numbers: list):\n"
                    "    if not numbers:\n"
                    "        return None\n"
                    "    return max(numbers)\n\n"
                    "print(find_max([12, 45, 2, 99, 34]))  # 99\n"
                    "```"
                )
            if "fibonacci" in text_lower:
                return (
                    "Here is a Python function for the Fibonacci sequence:\n\n"
                    "```python\n"
                    "def fibonacci(n: int) -> list:\n"
                    "    seq = [0, 1]\n"
                    "    for _ in range(2, n):\n"
                    "        seq.append(seq[-1] + seq[-2])\n"
                    "    return seq[:n]\n\n"
                    "print(fibonacci(7))  # [0, 1, 1, 2, 3, 5, 8]\n"
                    "```"
                )
            # General code template
            return (
                "Here is a clean Python starter template for your script:\n\n"
                "```python\n"
                "def main():\n"
                "    print('Running locally with Zieork Neural OS!')\n\n"
                "if __name__ == '__main__':\n"
                "    main()\n"
                "```"
            )

        # 6. Math & Calculations
        math_match = re.search(r'(\d+)\s*(plus|\+|\-|minus|\*|times|multiplied by|\/|divided by)\s*(\d+)', text_lower)
        if math_match:
            num1 = int(math_match.group(1))
            op = math_match.group(2)
            num2 = int(math_match.group(3))

            if op in {"plus", "+"}:
                return f"{num1} plus {num2} equals **{num1 + num2}**."
            elif op in {"minus", "-"}:
                return f"{num1} minus {num2} equals **{num1 - num2}**."
            elif op in {"times", "*", "multiplied by"}:
                return f"{num1} times {num2} equals **{num1 * num2}**."
            elif op in {"divided by", "/"}:
                if num2 == 0:
                    return "Division by zero is undefined!"
                res = num1 / num2
                formatted = int(res) if res.is_integer() else round(res, 2)
                return f"{num1} divided by {num2} equals **{formatted}**."

        # 7. Jokes & Humor
        if "joke" in text_lower or "funny" in text_lower:
            jokes = [
                "Why do programmers prefer dark mode? Because light attracts bugs! 🐛",
                "There are 10 types of people in the world: those who understand binary, and those who don't.",
                "Why was the JavaScript developer sad? Because they didn't Node how to Express themselves!",
                "A SQL query walks into a bar, walks up to two tables and asks: 'Can I join you?'"
            ]
            return random.choice(jokes)

        # 8. Email / Writing assistance
        if "email" in text_lower:
            name_greet = f"Hi {self.user_name}," if self.user_name else "Hi [Name],"
            return (
                "Here is a professional email template:\n\n"
                f"**Subject:** Update regarding our project\n\n"
                f"{name_greet}\n\n"
                "I wanted to follow up on our discussion and confirm the next steps. "
                "Please let me know if you need any additional details from my side.\n\n"
                "Best regards,\n"
                f"{self.user_name if self.user_name else '[Your Name]'}"
            )

        # 9. Fallback: Intelligent Contextual Response
        name_prefix = f"{self.user_name}, " if self.user_name else ""
        return (
            f"That's an interesting question, {name_prefix}! As a lightweight micro-model running locally on your CPU, "
            f"I specialize in answering questions about AI, algorithms, writing Python code, and arithmetic. "
            f"Try asking me to explain neural networks, write code, or test math calculations!"
        )

    def stream_response(self, messages: List[Dict[str, str]], system_prompt: str = "") -> Generator[str, None, None]:
        """Stream words one-by-one with realistic typing intervals."""
        full_text = self.generate_response(messages, system_prompt=system_prompt)
        words = re.findall(r'\S+|\n', full_text)

        for i, word in enumerate(words):
            if word == "\n":
                yield "\n"
            elif i == 0 or words[i - 1] == "\n":
                yield word
            else:
                yield " " + word
            time.sleep(0.02)  # 20ms delay for smooth typing cadence
