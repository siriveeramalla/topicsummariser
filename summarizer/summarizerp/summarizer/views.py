import logging

from rest_framework.decorators import api_view
from rest_framework.response import Response

from .nlp import preprocess_and_summarize
from .summariser_engine import extract_text_from_pdf

logger = logging.getLogger(__name__)

@api_view(['POST'])
def summarize_api(request):
    uploaded_file = request.FILES.get("file")
    text = (request.data.get("text") or "").strip()

    if uploaded_file and text:
        return Response(
            {"ok": False, "error": {"code": "AMBIGUOUS_INPUT", "message": "Send either a PDF file or text, not both."}},
            status=400,
        )

    if uploaded_file:
        extracted = extract_text_from_pdf(uploaded_file).strip()
        logger.info("pdf_received name=%s size=%s extracted_chars=%s", getattr(uploaded_file, "name", "?"), getattr(uploaded_file, "size", "?"), len(extracted))
        text = extracted

    if not text:
        return Response(
            {"ok": False, "error": {"code": "NO_TEXT", "message": "No text provided (or PDF had no extractable text)."}},
            status=400,
        )

    result = preprocess_and_summarize(text)
    if isinstance(result, dict) and "error" in result and set(result.keys()) == {"error"}:
        return Response(
            {"ok": False, "error": {"code": "NLP_ERROR", "message": str(result.get("error"))}},
            status=400,
        )

    return Response({"ok": True, "data": result})
