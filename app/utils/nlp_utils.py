import spacy
from collections import Counter

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    import spacy.cli
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

def extract_keywords(text: str, num_keywords: int = 5) -> list:
    """Extracts keywords from text using spaCy."""
    try:
        doc = nlp(text)
        keywords = [token.text.lower() for token in doc if not token.is_stop and token.is_alpha]
        keyword_counts = Counter(keywords)
        return [keyword for keyword, _ in keyword_counts.most_common(num_keywords)]
    except Exception as e:
        print(f"Error extracting keywords: {str(e)}")
        return []
