from rest_framework.serializers import ModelSerializer
from base.models import ImageModel


class ImageSerializer(ModelSerializer):
    class Meta:
        model = ImageModel
        fields = ['file', 'title']

    def create(self, validated_data):
        # Set the 'user' field to the current user (request.user)
        validated_data['user'] = self.context['request'].user
        image = ImageModel.objects.create(**validated_data)
        return image