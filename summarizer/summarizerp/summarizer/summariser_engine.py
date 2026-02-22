from transformers import pipeline
from nltk.tokenize import sent_tokenize

def summary_as_bullets(text):
    summary = generate_summary(text)
    bullets = sent_tokenize(summary)
    return bullets

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def generate_summary(text):
    word_count = len(text.split())

    max_len = min(120, word_count)
    min_len = max(20, word_count // 4)

    summary = summarizer(
        text,
        max_length=max_len,
        min_length=min_len,
        do_sample=False
    )

    return summary[0]['summary_text']
