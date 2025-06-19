
import re

def preprocess_text(text: str) -> str:
    """Clean and normalize text."""
    text = re.sub(r"\s+", " ", text.strip().lower())
    return text
