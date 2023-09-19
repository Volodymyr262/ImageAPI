from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import ImageSerializer
from base.models import Image

@api_view(['GET'])
def getRoutes(request):
    routes = [
        'GET /api',
        'POST /api/post_image',
        'GET /api/list_images',
    ]
    return Response(routes)


@api_view(['GET'])
def getImage(request, pk):
    room = Image.objects.get(id=pk)
    serializer = ImageSerializer(room, many=False)
    return Response(serializer.data)

