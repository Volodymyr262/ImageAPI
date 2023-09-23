from rest_framework.serializers import ModelSerializer, ValidationError
from django.core.signing import TimestampSigner
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from base.models import ImageModel
from PIL import Image
import os
import uuid
import base64


class ImageSerializer(ModelSerializer):
    class Meta:
        model = ImageModel
        fields = ['file']

    def __init__(self, *args, **kwargs):
        # Get the user's account tier from the context
        user_account_tier = kwargs['context']['request'].user.account_tier.name

        # Define serializer fields based on the user's account tier
        if user_account_tier == 'Basic' or user_account_tier=='Premium':
            self.Meta.fields = ['file']
        elif user_account_tier == 'Enterprise':
            self.Meta.fields = ['file', 'expiring_link_seconds']

        super().__init__(*args, **kwargs)

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

        if user_account_tier == 'Basic':
            data.pop('file', None)
            if instance.file200px:
                data['thumbnail200px'] = request.build_absolute_uri(instance.file200px.url)
            else:
                data['thumbnail200px'] = None

        elif user_account_tier == 'Premium':
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

        elif user_account_tier == 'Enterprise':
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

            expiration_time_seconds = instance.expiring_link_seconds

            # Calculate the expiration time as a timestamp (adding seconds to the current time)
            expiration_time = timezone.now() + timezone.timedelta(seconds=expiration_time_seconds)

            # Create a signer and sign the URL with the expiration time as a string
            signer = TimestampSigner()
            signed_url = signer.sign(instance.file.url + str(int(expiration_time.timestamp())))

            # Encode the signed URL using base64
            encoded_signed_url = base64.urlsafe_b64encode(signed_url.encode()).decode()

            # Include the encoded signed URL in the response data
            data['expiring_image_link'] = request.build_absolute_uri(encoded_signed_url)

        return data

    def validate_expiring_link_seconds(self, value):
        if value:
            if not (300 <= value <= 3000):
                raise ValidationError("Expiration seconds must be between 300 and 3000.")
            return value

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