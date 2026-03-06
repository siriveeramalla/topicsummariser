import logging

import fitz
import yake
from nltk.tokenize import sent_tokenize
from textblob import TextBlob
from transformers import pipeline

logger = logging.getLogger(__name__)

summarizer = None

def get_summarizer():
    global summarizer
    if summarizer is None:
        summarizer = pipeline(
            "summarization", 
            model="facebook/bart-large-cnn", 
            device=-1
        )
    return summarizer

def extract_text_from_pdf(pdf_file):
    text = ""
    try:
        stream = pdf_file.read() if hasattr(pdf_file, "read") else pdf_file
        doc = fitz.open(stream=stream, filetype="pdf")
        for page in doc:
            text += page.get_text() + " "
        doc.close()
    except Exception as e:
        logger.exception("pdf_extraction_failed: %s", e)
    return text

def extract_keywords(text):
    if not text.strip(): return []
    kw_extractor = yake.KeywordExtractor(lan="en", n=1, top=8)
    keywords = kw_extractor.extract_keywords(text)
    return [kw[0] for kw in keywords]

def get_sentiment(text):
    if not text.strip():
        return "Neutral"
    sample = " ".join(text.split()[:1000])
    polarity = TextBlob(sample).sentiment.polarity
    if polarity > 0.1:
        return "Positive"
    elif polarity < -0.1:
        return "Negative"
    else:
        return "Neutral"

def generate_summary(text):
    model = get_summarizer()
    tokenizer = getattr(model, "tokenizer", None)
    if tokenizer is None:
        # Fallback: should not happen for HF pipelines, but keep safe.
        tokenizer = None
    
    if len(text.split()) < 30:
        return text

    def _summarize_piece(piece: str) -> str:
        wc = len(piece.split())
        t_max = min(180, max(40, int(wc * 0.35)))
        t_min = max(20, min(t_max - 5, int(t_max * 0.5)))
        res = model(piece, max_length=t_max, min_length=t_min, do_sample=False)
        return res[0]["summary_text"]

    # Token-aware chunking when tokenizer is available.
    try:
        if tokenizer is not None:
            max_in = getattr(tokenizer, "model_max_length", 1024) or 1024
            # Keep some headroom for special tokens.
            max_chunk = max(256, min(900, max_in - 24))
            ids = tokenizer.encode(text, add_special_tokens=False)
            if len(ids) <= max_chunk:
                return _summarize_piece(text)
            summaries = []
            for i in range(0, len(ids), max_chunk):
                chunk_ids = ids[i : i + max_chunk]
                chunk = tokenizer.decode(chunk_ids, skip_special_tokens=True)
                if chunk.strip():
                    summaries.append(_summarize_piece(chunk))
        else:
            # Simple fallback: word chunking
            words = text.split()
            chunk_size = 600
            summaries = []
            for i in range(0, len(words), chunk_size):
                chunk = " ".join(words[i : i + chunk_size])
                if chunk.strip():
                    summaries.append(_summarize_piece(chunk))
    except Exception:
        logger.exception("summarization_failed")
        return text

    combined_summary = " ".join(summaries)
    if len(combined_summary.split()) < 150:
        return combined_summary

    try:
        final = model(combined_summary[:3000], max_length=170, min_length=40, do_sample=False)
        return final[0]["summary_text"]
    except Exception:
        logger.exception("final_summarization_failed")
        return combined_summary

def summary_as_bullets(text):
    summary = generate_summary(text)
    bullets = sent_tokenize(summary)
    return [b.strip() for b in bullets]

def generate_simple_explanation(text):
    model = get_summarizer()
    base_summary = generate_summary(text)
    try:
        result = model(
            "Explain like I'm 10: " + base_summary,
            max_length=60,
            min_length=20,
            do_sample=False
        )
        return result[0]["summary_text"]
    except Exception:
        logger.exception("simple_explanation_failed")
        return base_summary