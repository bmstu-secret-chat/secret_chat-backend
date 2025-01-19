from django.urls import path

from .views import upload_image_view

app_name = "storage"

urlpatterns = [
    path("upload-image/", upload_image_view, name="upload-image"),
]
