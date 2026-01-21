import os
import sys
from langchain_groq import ChatGroq

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.config import GROQ_API_KEY, GROQ_MODEL


def get_chatgroq_model():
    """Initialize and return the Groq chat model using configured API key and model."""
    if not GROQ_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY is not set. Configure it via environment variable or Streamlit secrets."
        )
    try:
        groq_model = ChatGroq(
            api_key=GROQ_API_KEY,
            model=GROQ_MODEL,
        )
        return groq_model
    except Exception as e:
        raise RuntimeError(f"Failed to initialize Groq model: {str(e)}")