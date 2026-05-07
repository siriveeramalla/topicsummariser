import logging

from rest_framework.decorators import api_view
from rest_framework.response import Response

from .nlp import preprocess_and_summarize
from .summariser_engine import extract_text_from_pdf, generate_topic_content

logger = logging.getLogger(__name__)


@api_view(["POST"])
def summarize_api(request):
    uploaded_file = request.FILES.get("file")

    text = (request.data.get("text") or "").strip()
    topic = (request.data.get("topic") or "").strip()
    summary_length = (request.data.get("summary_length") or "medium").strip().lower()

    # New: quiz count (3 to 10 allowed)
    raw_quiz_count = request.data.get("quiz_count", 5)
    try:
        quiz_count = int(raw_quiz_count)
    except Exception:
        quiz_count = 5
    quiz_count = max(3, min(10, quiz_count))

    if summary_length not in {"short", "medium", "long"}:
        summary_length = "medium"

    # Accept only one primary input type
    provided_inputs = sum([bool(uploaded_file), bool(text), bool(topic)])
    if provided_inputs > 1:
        return Response(
            {
                "ok": False,
                "error": {
                    "code": "AMBIGUOUS_INPUT",
                    "message": "Send either text, PDF, or topic only.",
                },
            },
            status=400,
        )

    # Topic flow
    if topic:
        generated_text = generate_topic_content(topic).strip()

        if not generated_text:
            return Response(
                {
                    "ok": False,
                    "error": {
                        "code": "TOPIC_EMPTY",
                        "message": "Topic generation returned empty text.",
                    },
                },
                status=500,
            )

        # Process generated content through NLP pipeline
        result = preprocess_and_summarize(
            generated_text,
            summary_length=summary_length,
            quiz_count=quiz_count,
        )

        # Keep full generated topic explanation as main summary (optional but useful)
        if isinstance(result, dict) and "error" not in result:
            result["summary"] = generated_text

        if isinstance(result, dict) and set(result.keys()) == {"error"}:
            return Response(
                {
                    "ok": False,
                    "error": {
                        "code": "NLP_ERROR",
                        "message": str(result.get("error")),
                    },
                },
                status=400,
            )

        return Response({"ok": True, "data": result})

    # PDF flow
    if uploaded_file:
        extracted = extract_text_from_pdf(uploaded_file).strip()
        logger.info(
            "pdf_received name=%s size=%s extracted_chars=%s",
            getattr(uploaded_file, "name", "?"),
            getattr(uploaded_file, "size", "?"),
            len(extracted),
        )
        text = extracted

    # Text required if not topic
    if not text:
        return Response(
            {
                "ok": False,
                "error": {
                    "code": "NO_TEXT",
                    "message": "No text provided (or PDF had no extractable text).",
                },
            },
            status=400,
        )

    # NLP processing
    try:
        result = preprocess_and_summarize(
            text,
            summary_length=summary_length,
            quiz_count=quiz_count,
        )
    except Exception as e:
        logger.exception("nlp_processing_failed: %s", e)
        return Response(
            {
                "ok": False,
                "error": {
                    "code": "NLP_PROCESSING_ERROR",
                    "message": str(e),
                },
            },
            status=500,
        )

    # NLP validation response
    if isinstance(result, dict) and set(result.keys()) == {"error"}:
        return Response(
            {
                "ok": False,
                "error": {
                    "code": "NLP_ERROR",
                    "message": str(result.get("error")),
                },
            },
            status=400,
        )

    return Response({"ok": True, "data": result})