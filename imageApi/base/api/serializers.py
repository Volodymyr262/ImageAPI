from rest_framework.serializers import ModelSerializer
from base.models import Image


class ImageSerializer(ModelSerializer):
    class Meta:
        model = Image
        fields = '__all__'