from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image


def create_test_image():
    file = BytesIO()
    image = Image.new('RGBA', size=(30, 30), color=(155, 0, 0))
    image.save(file, 'gif')
    file.name = 'giffy.gif'
    file.seek(0)
    return file


def image(name: str = 'giffy.gif') -> SimpleUploadedFile:
    return SimpleUploadedFile(
        name=name,
        content=create_test_image().read(),
        content_type='image/gif',
    )
