from typing import Iterable, List
from kion_vectorstore.document import Document

class RecursiveCharacterTextSplitter:
    """
    A simple, native text splitter that:
    - Produces chunks up to `chunk_size` characters
    - Uses a character-based overlap of `chunk_overlap`
    - Tries to split at natural boundaries (\\n\\n, then \\n, then space) before falling back to a hard cut
    - Returns a list of Document objects when splitting documents
    """

    def __init__(self, chunk_size: int, chunk_overlap: int, length_function=len, is_separator_regex: bool = False):
        if chunk_size <= 0:
            raise ValueError("chunk_size must be > 0")
        if chunk_overlap < 0:
            raise ValueError("chunk_overlap must be >= 0")
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")
        self.chunk_size = int(chunk_size)
        self.chunk_overlap = int(chunk_overlap)
        self.length_function = length_function
        self.is_separator_regex = is_separator_regex  # accepted for API parity; not used here

    def split_text(self, text: str) -> List[str]:
        text = text or ""
        n = self.length_function(text)
        if n <= self.chunk_size:
            return [text] if text.strip() else []

        chunks: List[str] = []
        start = 0
        # Greedy, natural-boundary-aware slicing:
        # Prefer split at '\n\n' within the window
        # Else at '\n'
        # Else at ' '
        # Else hard cut at chunk_size
        while start < n:
            end = min(start + self.chunk_size, n)

            split_at = -1
            for sep in ("\n\n", "\n", " "):
                idx = text.rfind(sep, start, end)
                if idx != -1 and idx > start:
                    split_at = idx + len(sep)
                    break

            if split_at == -1:
                split_at = end  # hard cut

            chunk = text[start:split_at]
            if chunk:
                chunks.append(chunk)

            # Ensure forward progress even when overlap is large
            next_start = max(split_at - self.chunk_overlap, start + 1)
            start = next_start

        # Trim empty/whitespace-only pieces
        return [c.strip() for c in chunks if c and c.strip()]

    def split_documents(self, docs: Iterable[Document]) -> List[Document]:
        out: List[Document] = []
        for doc in docs:
            content = getattr(doc, "page_content", "") or ""
            base_meta = dict(getattr(doc, "metadata", {}) or {})
            for piece in self.split_text(content):
                out.append(Document(page_content=piece, metadata=dict(base_meta)))
        return out