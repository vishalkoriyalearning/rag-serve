"""
Module for chunking text into smaller overlapping segments.
Example output:
[
    "This is the first chunk of text that is designed to be",
    "text that is designed to be overlapping with the next",
    "overlapping with the next chunk to ensure continuity."
]
"""

def chunk_text(text: str, chunk_size: int = 300, overlap: int = 50):
    """
    Split text into overlapping chunks.
    """
    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)

        # overlap for next chunk
        start = end - overlap
        if start < 0:
            start = 0

    return chunks
