import base64
import io
import uuid

from django.conf import settings

import boto3
import environ
from botocore.exceptions import ClientError
from PIL import Image
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

env = environ.Env()

NGINX_URL = env("NGINX_URL")


@api_view(['POST'])
def upload_image_view(request):
    """
    Загрузка изображения в MinIO.
    """
    base64_file = request.data.get("file")
    if not base64_file:
        return Response({"error": "Файл отсутсвует"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        decoded_file = base64.b64decode(base64_file)
        file_bytes = io.BytesIO(decoded_file)
        image = Image.open(file_bytes)
        image.verify()
        file_bytes.seek(0)
    except (IOError, SyntaxError, base64.binascii.Error):
        return Response({"error": "Файл не является корректным изображением"}, status=status.HTTP_400_BAD_REQUEST)

    file_format = image.format.lower()
    filename = f"{uuid.uuid4()}.{file_format}"

    s3 = boto3.client(
        "s3",
        endpoint_url=NGINX_URL,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        verify=False,
    )

    bucket_name = settings.AWS_STORAGE_BUCKET_NAME

    try:
        s3.head_bucket(Bucket=bucket_name)
    except ClientError:
        s3.create_bucket(Bucket=bucket_name)

    s3.upload_fileobj(file_bytes, bucket_name, filename)

    url = f"{NGINX_URL}/{bucket_name}/{filename}"
    return Response({"url": url}, status=status.HTTP_200_OK)
