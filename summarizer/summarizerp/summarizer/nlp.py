from langdetect import detect, LangDetectException
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
import re
from .summariser_engine import generate_summary
from .summarizer_engine import generate_summary, summary_as_bullets

summary = generate_summary(text)
bullets = summary_as_bullets(text)

stop_words = set(stopwords.words('english'))

def preprocess_and_summarize(text):
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
    filtered_words = [w for w in words if w not in stop_words]

    summary = generate_summary(text)

    return {
        "language": language,
        "sentences": sentences,
        "tokens": filtered_words,
        "summary": summary
    }
