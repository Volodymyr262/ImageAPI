from datetime import timedelta
from rest_framework.serializers import ModelSerializer, ValidationError
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from base.models import ImageModel, TemporaryLink
from PIL import Image
from rest_framework.response import Response
import os
import uuid


class TemporaryLinkSerializer(ModelSerializer):
    class Meta:
        model = TemporaryLink
        fields = ['file', 'time']

    def create(self, validated_data):
        validated_data['expiration_time'] = timezone.now() + timedelta(seconds=int(validated_data['time']))
        validated_data['user'] = self.context['request'].user
        temp_link = TemporaryLink.objects.create(**validated_data)
        return temp_link

    def validate_time(self, value):
        if value:
            if not (300 <= value <= 3000):
                raise ValidationError("Expiration seconds must be between 300 and 3000.")
            return value

    def to_representation(self, instance):
        # Get the default serialized data
        data = super().to_representation(instance)
        data.pop('file', None)
        data.pop('time', None)
        # Get the request object from the context
        request = self.context.get('request')
        if request.user.account_tier.name == 'Enterprise':
            data['temporary_link'] = 'http://127.0.0.1:8000/api/link/' + str(instance.id)
        elif request.user.account_tier.exp_link:
            data['temporary_link'] = 'http://127.0.0.1:8000/api/link/' + str(instance.id)
        else:
            data['temporary_link'] = 'Access denied'

        return data


class ImageSerializer(ModelSerializer):
    class Meta:
        model = ImageModel
        fields = ['file']

    def __init__(self, *args, **kwargs):
        # Get the user's account tier from the context
        user_account_tier = kwargs['context']['request'].user.account_tier.name

        # Define serializer fields based on the user's account tier
        if user_account_tier == 'Basic' or user_account_tier == 'Premium':
            self.Meta.fields = ['file']
        elif user_account_tier == 'Enterprise':
            self.Meta.fields = ['file', 'expiring_link_seconds']

        super().__init__(*args, **kwargs)

    def create(self, validated_data):
        # Set the 'user' field to the current user (request.user)
        validated_data['user'] = self.context['request'].user

        # Get the uploaded image file
        uploaded_image = validated_data['file']
        if self.context['request'].user.account_tier.name == 'Basic':
            # Create a 200px thumbnail
            thumbnail_200px = self.create_thumbnail(uploaded_image, (200, 200))
            validated_data['file200px'] = thumbnail_200px

        if self.context['request'].user.account_tier.name == 'Premium' or self.context['request'].user.account_tier.name == 'Enterprise':
            thumbnail_200px = self.create_thumbnail(uploaded_image, (200, 200))
            validated_data['file200px'] = thumbnail_200px
            thumbnail_400px = self.create_thumbnail(uploaded_image, (400, 400))
            validated_data['file400px'] = thumbnail_400px

        else:
            if self.context['request'].user.account_tier.width and self.context['request'].user.account_tier.height:
                thumbnail = self.create_thumbnail(uploaded_image, (self.context['request'].user.account_tier.width, self.context['request'].user.account_tier.height))
                validated_data['thumbnail'] = thumbnail
            else:
                return Response("invalid Image model")
        image = ImageModel.objects.create(**validated_data)
        return image

    def validate_file(self, value):
        """
        Validate that the uploaded file is in PNG or JPG format.
        """
        allowed_formats = ['image/jpeg', 'image/png']

        # Check if the uploaded file's content type is allowed
        if value.content_type not in allowed_formats:
            raise ValidationError("Only PNG or JPG images are allowed.")

        return value

    def to_representation(self, instance):
        # Get the default serialized data
        data = super().to_representation(instance)

        # Get the request object from the context
        request = self.context.get('request')

        # Check the user's account tier and include links accordingly
        user_account_tier = instance.user.account_tier.name if instance.user.account_tier else None
        data.pop('file', None)
        if user_account_tier == 'Basic':
            if instance.file200px:
                data['thumbnail200px'] = request.build_absolute_uri(instance.file200px.url)
            else:
                data['thumbnail200px'] = None

        elif user_account_tier == 'Premium' or user_account_tier == 'Enterprise':
            if instance.file200px:
                data['thumbnail200px'] = request.build_absolute_uri(instance.file200px.url)
            else:
                data['thumbnail200px'] = None

            if instance.file400px:
                data['thumbnail400px'] = request.build_absolute_uri(instance.file400px.url)
            else:
                data['thumbnail400px'] = None

            if instance.file:
                data['original_image'] = request.build_absolute_uri(instance.file.url)
            else:
                data['original_image'] = None
        else:
            if instance.user.account_tier.original_image:
                data['thumbnail'] = request.build_absolute_uri(instance.thumbnail.url)
                data['original_image'] = request.build_absolute_uri(instance.file.url)

        return data

    def create_thumbnail(self, image, size):
        img = Image.open(image)
        img.thumbnail(size)

        # Generate a unique filename for the thumbnail
        thumbnail_filename = f"thumbnail_{str(uuid.uuid4())}.jpg"

        # Define the full path for the thumbnail
        thumbnail_path = os.path.join('images', thumbnail_filename)

        img.save(thumbnail_path, format='JPEG')

        # Create a SimpleUploadedFile from the saved thumbnail
        thumbnail = SimpleUploadedFile(thumbnail_filename, open(thumbnail_path, 'rb').read())

        # Clean up by deleting the temporary thumbnail file
        os.remove(thumbnail_path)

        return thumbnail


class ImagesSerializer(ModelSerializer):
    class Meta:
        model = ImageModel
        fields = '__all__'