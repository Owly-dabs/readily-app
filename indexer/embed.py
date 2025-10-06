# embed.py
import os
import google.generativeai as genai

# Configure API key (expects GEMINI_API_KEY to be set as an environment variable)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Choose embedding model (EmbeddingGemma)
EMBEDDING_MODEL = "models/gemini-embedding-001"
DEFAULT_DIM = 768  # Can be 768, 512, 256, or 128


def embed_text(text: str, dim: int = DEFAULT_DIM) -> list[float]:
    """
    Generate an embedding vector for a single text using Google Embedding Gemma.
    Args:
        text (str): The text to embed
        dim (int): Desired embedding dimensionality (default 768)
    Returns:
        list[float]: The embedding vector
    """
    if not text.strip():
        raise ValueError("Text to embed cannot be empty.")

    response = genai.embed_content(
        model=EMBEDDING_MODEL,
        content=text,
        task_type="RETRIEVAL_DOCUMENT",  # can also use RETRIEVAL_QUERY
        output_dimensionality=dim,
    )
    return response["embedding"]


def embed_texts(texts: list[str], dim: int = DEFAULT_DIM) -> list[list[float]]:
    """
    Embed multiple texts in batch.
    Note: The Gemini API supports batching natively when you pass a list of content strings.
    Args:
        texts (list[str]): List of text strings to embed
        dim (int): Output dimension
    Returns:
        list[list[float]]: List of embedding vectors
    """
    if not texts:
        return []

    response = genai.embed_content(
        model=EMBEDDING_MODEL,
        content=texts,
        task_type="RETRIEVAL_DOCUMENT",
        output_dimensionality=dim,
    )
    return response["embedding"]


def test():
    sample_text = "This is a sample text to embed."
    embedding = embed_text(sample_text)
    print(f"Embedding for single text (length {len(embedding)}): {embedding[:5]}...")

    sample_texts = [
        "First sample text.",
        "Second sample text, a bit longer than the first.",
        "Third sample text is here!",
    ]
    embeddings = embed_texts(sample_texts)
    print(f"Embeddings for multiple texts (count {len(embeddings)}):")
    for i, emb in enumerate(embeddings):
        print(f" Text {i+1} embedding (length {len(emb)}): {emb[:5]}...")


if __name__ == "__main__":
    test()
