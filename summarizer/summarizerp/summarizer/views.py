from rest_framework.decorators import api_view
from rest_framework.response import Response
from .nlp import preprocess_and_summarize
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .nlp import preprocess_and_summarize
from .summariser_engine import extract_text_from_pdf

@api_view(['POST'])
def summarize_api(request):
    text = ""
    if 'file' in request.FILES:
        pdf_file = request.FILES['file']
        text = extract_text_from_pdf(pdf_file)
        print(f"DEBUG: Extracted text length: {len(text)}") # Check this!
    else:
        text = request.data.get("text")

    if not text or len(text.strip()) == 0:
        print("DEBUG: No text found after extraction")
        return Response({"error": "No text provided"}, status=400)

    result = preprocess_and_summarize(text)
    print(f"DEBUG: Result being sent to frontend: {result}") # Check this!
    return Response(result)
