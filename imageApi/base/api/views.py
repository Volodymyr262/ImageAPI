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
        'GET /api/image/:id',
        'GET /api/images',
        'POST /api/upload'
    ]
    return Response(routes)


@api_view(['GET'])
def getImage(request, pk):
    image = ImageModel.objects.get(id=pk)
    serializer = ImageSerializer(image, many=False)
    size = (400, 400)
    thumb200(image.file.name, size=size)
    return Response(serializer.data)


@api_view(['GET'])
def getImages(request):
    images = ImageModel.objects.filter(user=request.user)
    serializer = ImageSerializer(images, many=True)
    return Response(serializer.data)


class ImageUploadView(generics.CreateAPIView):
    serializer_class = ImageSerializer

