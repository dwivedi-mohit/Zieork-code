"""Word & Punctuation Tokenizer for clean, coherent English generation."""
import re
import json
import os
from typing import List, Dict, Optional

SPECIAL_TOKENS = [
    "<PAD>",
    "<UNK>",
    "<BOS>",
    "<EOS>",
    "<|system|>",
    "<|user|>",
    "<|assistant|>",
]

class Tokenizer:
    def __init__(self, vocab: Optional[Dict[str, int]] = None):
        self.special_tokens = SPECIAL_TOKENS[:]
        self.pad_id = 0
        self.unk_id = 1
        self.bos_id = 2
        self.eos_id = 3
        self.system_id = 4
        self.user_id = 5
        self.assistant_id = 6

        if vocab is not None:
            self.token_to_id = dict(vocab)
            self.id_to_token = {v: k for k, v in vocab.items()}
        else:
            # Default to 105-token ASCII character vocabulary matching weights/vocab.json
            self.token_to_id = {tok: idx for idx, tok in enumerate(self.special_tokens)}
            for i in range(32, 127):
                self.token_to_id[chr(i)] = len(self.token_to_id)
            self.token_to_id["\n"] = len(self.token_to_id)
            self.token_to_id["\t"] = len(self.token_to_id)
            self.token_to_id["\r"] = len(self.token_to_id)
            self.id_to_token = {v: k for k, v in self.token_to_id.items()}

        self.is_char_vocab = all(len(k) == 1 for k in self.token_to_id if k not in self.special_tokens)

    @property
    def vocab_size(self) -> int:
        return len(self.token_to_id)

    def _split_words(self, text: str) -> List[str]:
        """Split text preserving special tokens and separating into tokens."""
        tokens = []
        pattern = re.compile(r'(<\|system\|>|<\|user\|>|<\|assistant\|>|<PAD>|<UNK>|<BOS>|<EOS>)')
        parts = pattern.split(text)

        for part in parts:
            if not part:
                continue
            if part in self.special_tokens:
                tokens.append(part)
            elif self.is_char_vocab:
                tokens.extend(list(part))
            else:
                # Split words, numbers, and individual punctuation marks
                words_and_punct = re.findall(r'[A-Za-z0-9]+|[^\w\s]', part)
                tokens.extend(words_and_punct)
        return tokens

    def fit_on_texts(self, texts: List[str]):
        """Build vocabulary from a corpus of texts."""
        for text in texts:
            words = self._split_words(text)
            for w in words:
                if w not in self.token_to_id:
                    idx = len(self.token_to_id)
                    self.token_to_id[w] = idx
                    self.id_to_token[idx] = w

    def add_tokens(self, tokens: List[str]):
        for tok in tokens:
            if tok not in self.token_to_id:
                idx = len(self.token_to_id)
                self.token_to_id[tok] = idx
                self.id_to_token[idx] = tok

    def encode(self, text: str, add_bos: bool = False, add_eos: bool = False) -> List[int]:
        """Convert text into token IDs."""
        words = self._split_words(text)
        ids = []
        if add_bos:
            ids.append(self.bos_id)

        for w in words:
            if w in self.token_to_id:
                ids.append(self.token_to_id[w])
            else:
                # Try lowercase
                w_lower = w.lower()
                if w_lower in self.token_to_id:
                    ids.append(self.token_to_id[w_lower])
                else:
                    ids.append(self.unk_id)

        if add_eos:
            ids.append(self.eos_id)
        return ids

    def decode(self, token_ids: List[int], skip_special_tokens: bool = True) -> str:
        """Convert token IDs back into clean English text."""
        words = []
        for tid in token_ids:
            if tid in self.id_to_token:
                tok = self.id_to_token[tid]
                if skip_special_tokens and tok in self.special_tokens:
                    continue
                words.append(tok)
            else:
                words.append("<UNK>")

        if self.is_char_vocab:
            return "".join(words)

        # Join tokens with clean English punctuation rules
        text = ""
        no_space_before = {".", ",", "!", "?", ":", ";", ")", "]", "}", "'", '"'}
        no_space_after = {"(", "[", "{", "#", "$", '"'}

        for i, w in enumerate(words):
            if i == 0:
                text += w
            elif w in no_space_before or (i > 0 and words[i - 1] in no_space_after):
                text += w
            else:
                text += " " + w

        return text

    def format_chat(self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None) -> str:
        formatted = ""
        if system_prompt:
            formatted += f"<|system|> {system_prompt} "
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "system":
                formatted += f"<|system|> {content} "
            elif role == "user":
                formatted += f"<|user|> {content} "
            elif role == "assistant":
                formatted += f"<|assistant|> {content} <EOS> "

        if not formatted.endswith("<|assistant|> ") and not (messages and messages[-1].get("role") == "assistant"):
            formatted += "<|assistant|> "

        return formatted

    def save(self, filepath: str):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump({"vocab": self.token_to_id}, f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, filepath: str) -> "Tokenizer":
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(vocab=data["vocab"])
