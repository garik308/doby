import io

from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile


def create_test_image(filename="photo.jpg", size=(100, 100)):
    file = io.BytesIO()
    image = Image.new('RGB', size, color='red')
    image.save(file, format='JPEG')
    file.seek(0)
    return SimpleUploadedFile(filename, file.getvalue(), content_type='image/jpeg')