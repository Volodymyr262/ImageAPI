from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import ImageSerializer, TemporaryLinkSerializer, ImagesSerializer
from base.models import ImageModel, TemporaryLink
from rest_framework import status
from rest_framework import generics
from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated


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
    if request.user.is_authenticated:
        images = ImageModel.objects.filter(user=request.user)
        serializer = ImagesSerializer(images, many=True)
        return Response(serializer.data)
    else:
        return Response("Access denied, you have to be logged in")


class ImageUploadView(generics.CreateAPIView):
    serializer_class = ImageSerializer
    permission_classes = [IsAuthenticated]


class create_temporary_link_view(generics.CreateAPIView):
    serializer_class = TemporaryLinkSerializer
    permission_classes = [IsAuthenticated]


@api_view(['GET'])
def get_temporary_link(request, pk):
    try:
        link = TemporaryLink.objects.get(pk=pk)
    except TemporaryLink.DoesNotExist:
        return Response({'message': 'image not found'}, status=status.HTTP_404_NOT_FOUND)

    if link.is_expired():
        return Response({'message': 'link expired'}, status=status.HTTP_400_BAD_REQUEST)

    image_path = link.image_url()

    file_extension = image_path.split('.')[-1].lower()
    if file_extension in ('jpg', 'jpeg'):
        content_type = 'image/jpeg'
    elif file_extension == 'png':
        content_type = 'image/png'
    else:
        content_type = 'application/octet-stream'

    with open(image_path, 'rb') as image_file:
        image_data = image_file.read()

    return HttpResponse(image_data, content_type=content_type)


