from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import ImageSerializer, TemporaryLinkSerializer
from base.models import ImageModel, TemporaryLink
from rest_framework import status
from rest_framework import generics
from django.http import HttpResponse
import os
from django.conf import settings


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


class create_temporary_link_view(generics.CreateAPIView):
    serializer_class = TemporaryLinkSerializer


@api_view(['GET'])
def check_temporary_link(request, pk):
    try:
        link = TemporaryLink.objects.get(pk=pk)
    except TemporaryLink.DoesNotExist:
        return Response({'message': 'image not found'}, status=status.HTTP_404_NOT_FOUND)

    if link.is_expired():
        return Response({'message': 'link expired'}, status=status.HTTP_400_BAD_REQUEST)

    # Формируем правильный путь к изображению относительно MEDIA_ROOT
    image_path = link.image_url()

    # Проверяем, существует ли файл
    # if not os.path.exists(os.path.join(settings.BASE_DIR, image_path)):
    #     return Response({'message': 'image not found'}, status=status.HTTP_404_NOT_FOUND)

    # Определяем тип контента на основе расширения файла
    file_extension = image_path.split('.')[-1].lower()
    if file_extension in ('jpg', 'jpeg'):
        content_type = 'image/jpeg'
    elif file_extension == 'png':
        content_type = 'image/png'
    else:
        # Если тип неизвестен, можно установить общий тип контента
        content_type = 'application/octet-stream'

    # Открываем и отправляем изображение как HTTP-ответ
    with open(image_path, 'rb') as image_file:
        image_data = image_file.read()

    return HttpResponse(image_data, content_type=content_type)


