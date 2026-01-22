import os
import sys
from langchain_google_genai import ChatGoogleGenerativeAI

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.config import GEMINI_API_KEY, GEMINI_MODEL


def get_gemini_model():
    """Initialize and return the Gemini chat model using configured API key and model."""
    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Configure it via environment variable or Streamlit secrets."
        )
    try:
        gemini_model = ChatGoogleGenerativeAI(
            api_key=GEMINI_API_KEY,
            model=GEMINI_MODEL,
        )
        return gemini_model
    except Exception as e:
        raise RuntimeError(f"Failed to initialize Gemini model: {str(e)}")