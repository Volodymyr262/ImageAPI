from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import ImageSerializer
from base.models import ImageModel
from rest_framework import status
from rest_framework import generics


@api_view(['GET'])
def getRoutes(request):
    routes = [
        'GET /api',
        'GET /api/images',
        'POST /api/upload'
    ]
    return Response(routes)


@api_view(['GET'])
def getImages(request):
    images = ImageModel.objects.filter(user=request.user)
    serializer = ImageSerializer(images, many=True)
    return Response(serializer.data)


class ImageUploadView(generics.CreateAPIView):
    serializer_class = ImageSerializer

