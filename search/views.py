from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .documents import UserDocument
from .serializers import UserDocumentSerializer


@api_view(['GET'])
def search_view(request):
    """
    Поиск по пользователям.
    """
    search_query = UserDocument.search()

    username = request.GET.get("username")
    search = search_query.query("match_phrase_prefix", username=username)

    response = search.execute()

    serializer = UserDocumentSerializer(response.hits, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
