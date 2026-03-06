import fitz
import yake
from textblob import TextBlob
from transformers import pipeline
import nltk
from nltk.tokenize import sent_tokenize

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

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
        stream = pdf_file.read() if hasattr(pdf_file, 'read') else pdf_file
        doc = fitz.open(stream=stream, filetype="pdf")
        for page in doc:
            text += page.get_text() + " "
        doc.close()
    except Exception as e:
        print(f"Extraction Error: {e}")
    return text

def extract_keywords(text):
    if not text.strip(): return []
    kw_extractor = yake.KeywordExtractor(lan="en", n=1, top=8)
    keywords = kw_extractor.extract_keywords(text)
    return [kw[0] for kw in keywords]

def get_sentiment(text):
    if not text.strip(): return "Neutral 😐"
    sample = " ".join(text.split()[:1000])
    polarity = TextBlob(sample).sentiment.polarity
    if polarity > 0.1:
        return "Positive 😊"
    elif polarity < -0.1:
        return "Negative 😔"
    else:
        return "Neutral 😐"

def generate_summary(text):
    model = get_summarizer()
    words = text.split()
    word_count = len(words)
    
    if word_count < 30:
        return text

    if word_count <= 600:
        try:
            t_max = min(150, max(30, int(word_count * 0.5)))
            t_min = min(t_max - 5, max(10, int(t_max * 0.3)))
            res = model(text, max_length=t_max, min_length=t_min, do_sample=False)
            return res[0]["summary_text"]
        except:
            return text

    chunk_size = 600 
    summaries = []
    for i in range(0, word_count, chunk_size):
        chunk = " ".join(words[i : i + chunk_size])
        input_len = len(chunk.split())
        t_max = max(40, int(input_len * 0.4))
        t_min = max(20, int(t_max * 0.5))
        try:
            res = model(chunk, max_length=t_max, min_length=t_min, do_sample=False)
            summaries.append(res[0]["summary_text"])
        except:
            continue

    combined_summary = " ".join(summaries)
    if len(combined_summary.split()) < 150:
        return combined_summary

    try:
        final = model(combined_summary[:3000], max_length=150, min_length=40, do_sample=False)
        return final[0]["summary_text"]
    except:
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
            "Summary: " + base_summary,
            max_length=60,
            min_length=20,
            do_sample=False
        )
        return result[0]["summary_text"]
    except:
        return base_summary