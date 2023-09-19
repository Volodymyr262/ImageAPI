from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import ImageSerializer
from base.models import Image
from rest_framework import generics


@api_view(['GET'])
def getRoutes(request):
    routes = [
        'GET /api',
        'POST /api/image/:id',
        'GET /api/images',
    ]
    return Response(routes)


@api_view(['GET'])
def getImage(request, pk):
    image = Image.objects.get(id=pk)
    serializer = ImageSerializer(image, many=False)
    return Response(serializer.data)


@api_view(['GET'])
def getImages(request):
    image = Image.objects.all()
    serializer = ImageSerializer(image, many=True)
    return Response(serializer.data)



