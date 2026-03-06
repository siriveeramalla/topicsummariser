from langdetect import detect, LangDetectException
import os
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
import re
from .summariser_engine import generate_summary
from .summariser_engine import summary_as_bullets,generate_simple_explanation,extract_keywords,get_sentiment
    

def _ensure_nltk_resource(path: str, download_name: str) -> None:
    try:
        nltk.data.find(path)
    except LookupError:
        auto = os.getenv("NLTK_AUTO_DOWNLOAD", "1").strip().lower() in {"1", "true", "yes", "on"}
        if not auto:
            raise
        nltk.download(download_name)


def ensure_nltk_resources() -> None:
    # Tokenizers
    _ensure_nltk_resource("tokenizers/punkt", "punkt")
    # Corpora
    _ensure_nltk_resource("corpora/stopwords", "stopwords")


def preprocess_and_summarize(text):
    try:
        ensure_nltk_resources()
    except LookupError:
        return {"error": "NLTK resources missing. Run once: python -c \"import nltk; nltk.download('punkt'); nltk.download('stopwords')\""}

    if not text or len(text.strip()) < 30:
        return {"error": "Please enter more text (at least 50 characters)."}

    try:
        language = detect(text)
    except LangDetectException:
        language = "unknown"

    clean_text = text.lower()
    clean_text = re.sub(r'[^a-zA-Z0-9\s]', '', clean_text)

    sentences = sent_tokenize(clean_text)
    words = word_tokenize(clean_text)
    summary = generate_summary(text)
    bullets = summary_as_bullets(text)
    simple = generate_simple_explanation(text)
    stop_words = set(stopwords.words('english'))
    keywords = extract_keywords(text)
    sentiment = get_sentiment(text)
    filtered_words = [w for w in words if w not in stop_words]

   

    return {
        "language": language,
        "sentences": sentences,
        "tokens": filtered_words,
        "summary": summary,
        "bullets": bullets,
        "simple_explanation": simple,
        "keywords": keywords,
        "sentiment": sentiment
    }
