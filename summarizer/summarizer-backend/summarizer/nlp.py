from langdetect import detect, LangDetectException
import os
import re
import nltk

from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize

from .summariser_engine import (
    generate_summary,
    summary_as_bullets,
    extract_keywords,
    get_sentiment,
    generate_quiz_from_text,
)


def _ensure_nltk_resource(path, download_name):
    try:
        nltk.data.find(path)
    except LookupError:
        auto = os.getenv("NLTK_AUTO_DOWNLOAD", "1").strip().lower() in {
            "1", "true", "yes", "on"
        }
        if not auto:
            raise
        nltk.download(download_name)


def ensure_nltk_resources():
    _ensure_nltk_resource("tokenizers/punkt", "punkt")
    _ensure_nltk_resource("corpora/stopwords", "stopwords")


def _split_sentences_fallback(text):
    parts = re.split(r"(?<=[\.\!\?।])\s+|\n+", text)
    return [s.strip() for s in parts if s.strip()]


def preprocess_and_summarize(text, summary_length="medium", quiz_count=5):
    try:
        ensure_nltk_resources()
    except LookupError:
        return {
            "error": (
                "NLTK resources missing. Run:\n"
                "python -c \"import nltk; nltk.download('punkt'); nltk.download('stopwords')\""
            )
        }

    if not text or len(text.strip()) < 30:
        return {
            "error": "Please enter more text (minimum 30 characters)."
        }

    if summary_length not in {"short", "medium", "long"}:
        summary_length = "medium"

    try:
        quiz_count = int(quiz_count)
    except Exception:
        quiz_count = 5
    quiz_count = max(3, min(10, quiz_count))

    try:
        language = detect(text)
    except LangDetectException:
        language = "unknown"

    # English-specific normalization only for English.
    # Preserve native scripts for non-English.
    if language.startswith("en"):
        clean_text = re.sub(r"[^a-zA-Z0-9\s]", "", text.lower())
        try:
            stop_words = set(stopwords.words("english"))
        except Exception:
            stop_words = set()
    else:
        clean_text = text
        stop_words = set()

    try:
        sentences = sent_tokenize(clean_text)
    except Exception:
        sentences = _split_sentences_fallback(clean_text)

    try:
        words = word_tokenize(clean_text)
    except Exception:
        words = clean_text.split()

    filtered_words = [w for w in words if w not in stop_words]

    try:
        summary = generate_summary(
            text,
            summary_length=summary_length,
            language=language
        )
    except Exception:
        summary = "Unable to generate summary."

    try:
        bullets = summary_as_bullets(
            text,
            summary_length=summary_length,
            language=language
        )
    except Exception:
        bullets = []

    try:
        keywords = extract_keywords(text, language=language)
    except Exception:
        keywords = []

    try:
        sentiment = get_sentiment(text)
    except Exception:
        sentiment = "Neutral"

    try:
        quiz = generate_quiz_from_text(
            text,
            language=language,
            quiz_count=quiz_count
        )
    except Exception:
        quiz = []

    return {
        "language": language,
        "sentences": sentences,
        "tokens": filtered_words,
        "summary": summary,
        "bullets": bullets,
        "keywords": keywords,
        "sentiment": sentiment,
        "quiz": quiz,
    }