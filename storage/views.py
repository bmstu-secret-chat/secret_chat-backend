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
    file = request.FILES["file"]

    try:
        image = Image.open(file)
        image.verify()
    except (IOError, SyntaxError):
        return Response({"error": "Файл не является изображением"}, status=status.HTTP_400_BAD_REQUEST)

    filename = f"{uuid.uuid4()}_{file.name}"

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

    s3.upload_fileobj(file, bucket_name, filename)

    url = f"{NGINX_URL}/{bucket_name}/{filename}"
    return Response({"url": url}, status=status.HTTP_200_OK)
