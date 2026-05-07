import json
import logging
import re
from collections import Counter

import fitz
import yake
from nltk.tokenize import sent_tokenize
from textblob import TextBlob
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM

logger = logging.getLogger(__name__)

summarizer = None
multilingual_summarizer = None
topic_generator = None


def get_summarizer():
    global summarizer
    if summarizer is None:
        summarizer = pipeline(
            "summarization",
            model="facebook/bart-large-cnn",
            device=-1
        )
    return summarizer


def get_multilingual_summarizer():
    global multilingual_summarizer
    if multilingual_summarizer is None:
        model_id = "csebuetnlp/mT5_multilingual_XLSum"
        tokenizer = AutoTokenizer.from_pretrained(
            model_id,
            use_fast=False,
            legacy=True
        )
        model = AutoModelForSeq2SeqLM.from_pretrained(model_id)
        multilingual_summarizer = pipeline(
            "summarization",
            model=model,
            tokenizer=tokenizer,
            device=-1
        )
    return multilingual_summarizer


def get_topic_generator():
    global topic_generator
    if topic_generator is None:
        topic_generator = pipeline(
            "text2text-generation",
            model="google/flan-t5-base",
            device=-1
        )
    return topic_generator


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

    words = text.split()
    if len(words) > 5000:
        text = " ".join(words[:5000])

    return text


def generate_topic_content(topic):
    try:
        model = get_topic_generator()
        prompt = f"""
Write a detailed, student-friendly explanation of the topic: {topic}

Requirements:
- Use headings:
  1) Introduction
  2) Key Concepts
  3) How It Works
  4) Real-World Applications
  5) Advantages
  6) Limitations
  7) Conclusion
- Under each heading, write complete sentences.
- Include at least one practical example.
- Keep language clear and informative.
- Target length: around 400-700 words.
""".strip()

        result = model(
            prompt,
            max_new_tokens=650,
            do_sample=False,
            num_beams=4
        )

        generated = result[0].get("generated_text", "").strip()
        if not generated:
            return f"Unable to generate content for {topic}"

        return generated

    except Exception as e:
        logger.exception("topic_generation_failed: %s", e)
        return (
            f"{topic} is an important subject. "
            f"Detailed topic generation is temporarily unavailable due to model/network issue."
        )


def extract_keywords(text, language="en"):
    if not text or not text.strip():
        return []

    lang_map = {
        "en": "en", "hi": "hi", "te": "te", "ta": "ta", "ml": "ml", "kn": "kn"
    }
    lan = lang_map.get((language or "en").lower()[:2], "en")

    try:
        kw_extractor = yake.KeywordExtractor(
            lan=lan,
            n=2 if lan != "en" else 3,
            top=15,
            dedupLim=0.85
        )
        raw = kw_extractor.extract_keywords(text)

        cleaned = []
        seen = set()
        for kw, _score in raw:
            k = kw.strip()
            if len(k) < 3:
                continue
            key = k.lower()
            if key in seen:
                continue
            seen.add(key)
            cleaned.append(k)
            if len(cleaned) == 8:
                break

        return cleaned
    except Exception:
        return []


def get_sentiment(text):
    if not text or not text.strip():
        return "Neutral"

    sample = " ".join(text.split()[:1000])
    polarity = TextBlob(sample).sentiment.polarity

    if polarity > 0.1:
        return "Positive"
    if polarity < -0.1:
        return "Negative"
    return "Neutral"


def _length_profile(summary_length: str):
    if summary_length == "short":
        return {"cap": 90, "final_max": 120, "final_min": 40, "ratio": 0.28}
    if summary_length == "long":
        return {"cap": 260, "final_max": 340, "final_min": 120, "ratio": 0.60}
    return {"cap": 160, "final_max": 220, "final_min": 80, "ratio": 0.42}


def extractive_fallback_summary(text, summary_length="medium"):
    if not text or not text.strip():
        return "No text provided."

    sentences = [
        s.strip()
        for s in re.split(r"(?<=[\.\!\?।])\s+|\n+", text)
        if s.strip()
    ]

    if len(sentences) <= 2:
        return text.strip()

    tokens = re.findall(r"\w+", text.lower(), flags=re.UNICODE)
    if not tokens:
        return " ".join(sentences[:3])

    freq = Counter(tokens)
    scored = []

    for s in sentences:
        s_tokens = re.findall(r"\w+", s.lower(), flags=re.UNICODE)
        if not s_tokens:
            scored.append((s, 0.0))
            continue
        score = sum(freq[t] for t in s_tokens) / max(len(s_tokens), 1)
        scored.append((s, score))

    if summary_length == "short":
        n = 2
    elif summary_length == "long":
        n = min(8, max(4, len(sentences) // 3))
    else:
        n = min(5, max(3, len(sentences) // 4))

    top = sorted(scored, key=lambda x: x[1], reverse=True)[:n]
    top_set = {s for s, _ in top}
    ordered = [s for s in sentences if s in top_set]

    return " ".join(ordered)


def _select_summary_model(language: str):
    lang = (language or "").lower()

    if lang.startswith("en"):
        try:
            return get_summarizer()
        except Exception:
            logger.exception("english_model_unavailable")

    try:
        return get_multilingual_summarizer()
    except Exception:
        logger.exception("multilingual_model_unavailable")

    return None


def generate_summary(text, summary_length="medium", language="en"):
    if not text or not text.strip():
        return "No text provided."

    if len(text.split()) < 30:
        return text

    if summary_length not in {"short", "medium", "long"}:
        summary_length = "medium"

    model = _select_summary_model(language)
    if model is None:
        return extractive_fallback_summary(text, summary_length=summary_length)

    tokenizer = getattr(model, "tokenizer", None)
    profile = _length_profile(summary_length)

    def summarize_piece(piece):
        wc = len(piece.split())
        max_len = min(profile["cap"], max(40, int(wc * profile["ratio"])))
        min_len = max(20, min(max_len - 10, int(max_len * 0.5)))
        if min_len >= max_len:
            min_len = max(10, max_len - 5)

        result = model(
            piece,
            max_length=max_len,
            min_length=min_len,
            do_sample=False
        )
        return result[0]["summary_text"]

    try:
        summaries = []

        if tokenizer:
            max_input = getattr(tokenizer, "model_max_length", 1024)
            max_chunk = min(550, max_input - 50)

            ids = tokenizer.encode(text, add_special_tokens=False)

            if len(ids) <= max_chunk:
                return summarize_piece(text)

            for i in range(0, len(ids), max_chunk):
                chunk_ids = ids[i:i + max_chunk]
                chunk = tokenizer.decode(chunk_ids, skip_special_tokens=True)
                if chunk.strip():
                    try:
                        summaries.append(summarize_piece(chunk))
                    except Exception as e:
                        logger.exception("chunk_summary_failed: %s", e)
        else:
            return extractive_fallback_summary(text, summary_length=summary_length)

    except Exception as e:
        logger.exception("summarization_failed: %s", e)
        return extractive_fallback_summary(text, summary_length=summary_length)

    combined_summary = " ".join(summaries).strip()
    if not combined_summary:
        return extractive_fallback_summary(text, summary_length=summary_length)

    # Speed optimization: skip final re-summarization for short mode
    if summary_length == "short":
        return combined_summary

    # Only run final pass for long outputs
    if len(combined_summary.split()) < 220:
        return combined_summary

    try:
        final = model(
            combined_summary[:3000],
            max_length=profile["final_max"],
            min_length=profile["final_min"],
            do_sample=False
        )
        return final[0]["summary_text"]
    except Exception as e:
        logger.exception("final_summarization_failed: %s", e)
        return combined_summary


def summary_as_bullets(text, summary_length="medium", language="en"):
    summary = generate_summary(text, summary_length=summary_length, language=language)

    parts = re.split(r"(?<=[\.\!\?।])\s+|\n+", summary)
    bullets = [p.strip() for p in parts if p.strip()]

    if not bullets:
        try:
            bullets = [b.strip() for b in sent_tokenize(summary) if b.strip()]
        except Exception:
            bullets = [summary.strip()] if summary.strip() else []

    return bullets


def generate_quiz_from_text(text, language="en", quiz_count=5):
    if not text or not text.strip():
        return []

    try:
        quiz_count = int(quiz_count)
    except Exception:
        quiz_count = 5

    quiz_count = max(3, min(10, quiz_count))

    prompt = f"""
Create {quiz_count} multiple choice questions from the following content.

Rules:
- Return strictly valid JSON only.
- Format:
[
  {{
    "question": "...",
    "options": ["...", "...", "...", "..."],
    "answer_index": 0
  }}
]
- Exactly 4 options per question.
- answer_index must be 0 to 3.
- Language: {language}

Content:
{text[:3500]}
""".strip()

    try:
        model = get_topic_generator()
        out = model(prompt, max_new_tokens=700, do_sample=False, num_beams=4)
        raw = out[0].get("generated_text", "").strip()

        try:
            parsed = json.loads(raw)
        except Exception:
            start = raw.find("[")
            end = raw.rfind("]")
            if start == -1 or end == -1:
                return []
            parsed = json.loads(raw[start:end + 1])

        cleaned = []
        for item in parsed:
            q = str(item.get("question", "")).strip()
            opts = item.get("options", [])
            ans = item.get("answer_index", None)

            if not q or not isinstance(opts, list) or len(opts) != 4:
                continue
            if not isinstance(ans, int) or ans < 0 or ans > 3:
                continue

            cleaned.append({
                "question": q,
                "options": [str(o).strip() for o in opts],
                "answer_index": ans
            })

        return cleaned[:quiz_count]

    except Exception as e:
        logger.exception("quiz_generation_failed: %s", e)
        return []