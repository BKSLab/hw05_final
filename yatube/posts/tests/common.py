from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image


def image(name: str = 'giffy.gif') -> SimpleUploadedFile:
    file = BytesIO()
    Image.new('RGBA', size=(30, 30), color=(155, 0, 0)).save(file, 'gif')
    file.seek(0)
    return SimpleUploadedFile(
        name=name,
        content=file.read(),
        content_type='image/gif',
    )
