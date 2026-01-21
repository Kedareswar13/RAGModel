from langchain_community.embeddings import HuggingFaceEmbeddings


def get_embeddings_model():
    """Return a sentence-transformers embedding model for RAG."""
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
    )

