from rest_framework.decorators import api_view
from rest_framework.response import Response
from .nlp import preprocess_and_summarize

@api_view(['POST'])
def summarize_api(request):
    text = request.data.get("text")
    result = preprocess_and_summarize(text)
    return Response(result)
