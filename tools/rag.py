"""Zieork Semantic Document RAG Engine (Zero-Dependency BM25 / TF-IDF)."""
import re
import math
from typing import List, Dict, Any

class DocumentRAG:
    def __init__(self, chunk_size: int = 250, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_text(self, text: str) -> List[Dict[str, Any]]:
        """Split a long text into overlapping chunks with metadata."""
        # Split into words or paragraphs
        words = text.split()
        if not words:
            return []

        chunks = []
        stride = max(1, self.chunk_size - self.overlap)
        total_words = len(words)

        chunk_idx = 0
        for i in range(0, total_words, stride):
            chunk_words = words[i:i + self.chunk_size]
            chunk_str = " ".join(chunk_words)

            # Estimate page number (approx 350 words per page)
            approx_page = (i // 350) + 1

            chunks.append({
                "chunk_id": chunk_idx + 1,
                "approx_page": approx_page,
                "text": chunk_str,
                "word_count": len(chunk_words)
            })
            chunk_idx += 1

            if i + self.chunk_size >= total_words:
                break

        return chunks

    def _tokenize(self, text: str) -> List[str]:
        """Simple clean tokenization."""
        return re.findall(r'\b[a-zA-Z0-9_]{2,}\b', text.lower())

    def retrieve(self, query: str, chunks: List[Dict[str, Any]], top_k: int = 3) -> List[Dict[str, Any]]:
        """Score and retrieve top_k most relevant chunks using TF-IDF / BM25 weighting."""
        if not chunks:
            return []

        query_tokens = set(self._tokenize(query))
        if not query_tokens:
            return chunks[:top_k]

        # Calculate document frequencies
        doc_freq = {}
        for c in chunks:
            c_tokens = set(self._tokenize(c["text"]))
            for t in query_tokens:
                if t in c_tokens:
                    doc_freq[t] = doc_freq.get(t, 0) + 1

        total_docs = len(chunks)
        scored_chunks = []

        for c in chunks:
            c_tokens = self._tokenize(c["text"])
            c_len = len(c_tokens) or 1
            score = 0.0

            for t in query_tokens:
                tf = c_tokens.count(t)
                if tf > 0:
                    df = doc_freq.get(t, 1)
                    idf = math.log(1.0 + (total_docs - df + 0.5) / (df + 0.5))
                    # BM25 term saturation
                    score += idf * ((tf * 2.2) / (tf + 1.2 * (0.25 + 0.75 * (c_len / 250.0))))

            scored_chunks.append((score, c))

        # Sort descending by relevance score
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored_chunks[:top_k]]

    def prepare_rag_context(self, query: str, full_document_text: str, top_k: int = 3) -> Dict[str, Any]:
        """
        Analyze document size. If small, pass through. If large, chunk and retrieve.
        """
        # If text is short enough to fit directly
        if len(full_document_text.split()) < 400:
            return {
                "rag_used": False,
                "context": full_document_text,
                "chunks_used": 1
            }

        chunks = self.chunk_text(full_document_text)
        top_chunks = self.retrieve(query, chunks, top_k=top_k)

        rag_lines = [f"### 📑 Retrieved Relevant Passages (Document Total: {len(chunks)} sections):"]
        for c in top_chunks:
            rag_lines.append(f"\n--- [Passage #{c['chunk_id']} • Approx Page {c['approx_page']}] ---\n{c['text']}")

        return {
            "rag_used": True,
            "context": "\n".join(rag_lines),
            "chunks_used": len(top_chunks),
            "total_chunks": len(chunks)
        }

    def synthesize_web_rag(self, query: str, search_results: List[Dict[str, str]], top_k: int = 4) -> Dict[str, Any]:
        """Convert live search results into chunked, BM25-ranked high-density RAG context."""
        if not search_results:
            return {"rag_used": False, "context": "", "citations": []}

        passages = []
        citations = []
        for i, r in enumerate(search_results):
            text = f"Title: {r.get('title', '')}\nSnippet: {r.get('snippet', '')}"
            passages.append({
                "chunk_id": i + 1,
                "approx_page": 1,
                "text": text,
                "source": r.get("url", ""),
                "title": r.get("title", "")
            })
            if r.get("url"):
                citations.append({"title": r.get("title", "Source"), "url": r.get("url")})

        top_passages = self.retrieve(query, passages, top_k=top_k)
        
        context_lines = ["### 🌐 Live Web RAG Ground Truth Context:"]
        for p in top_passages:
            context_lines.append(f"\n[Source: {p['title']}]({p.get('source', '')}):\n{p['text']}")

        return {
            "rag_used": True,
            "context": "\n".join(context_lines),
            "citations": citations,
            "chunks_used": len(top_passages)
        }

document_rag = DocumentRAG()
