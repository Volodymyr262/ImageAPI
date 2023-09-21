from rest_framework.serializers import ModelSerializer
from base.models import ImageModel
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import os
import uuid


class ImageSerializer(ModelSerializer):
    class Meta:
        model = ImageModel
        fields = ['file', 'title']

    def create(self, validated_data):
        # Set the 'user' field to the current user (request.user)
        validated_data['user'] = self.context['request'].user

        # Get the uploaded image file
        uploaded_image = validated_data['file']

        # Create a 200px thumbnail
        thumbnail_200px = self.create_thumbnail(uploaded_image, (200, 200))
        validated_data['file200px'] = thumbnail_200px

        # Create a 400px thumbnail
        thumbnail_400px = self.create_thumbnail(uploaded_image, (400, 400))
        validated_data['file400px'] = thumbnail_400px

        image = ImageModel.objects.create(**validated_data)
        return image

    def create_thumbnail(self, image, size):
        # Open the uploaded image
        img = Image.open(image)

        # Create a thumbnail
        img.thumbnail(size)

        # Generate a unique filename for the thumbnail
        thumbnail_filename = f"thumbnail_{str(uuid.uuid4())}.jpg"

        # Define the full path for the thumbnail
        thumbnail_path = os.path.join('images', thumbnail_filename)

        # Save the thumbnail
        img.save(thumbnail_path, format='JPEG')

        # Create a SimpleUploadedFile from the saved thumbnail
        thumbnail = SimpleUploadedFile(thumbnail_filename, open(thumbnail_path, 'rb').read())

        # Clean up by deleting the temporary thumbnail file
        os.remove(thumbnail_path)

        return thumbnail