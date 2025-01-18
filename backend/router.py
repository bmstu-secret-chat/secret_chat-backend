from django.urls import include, path

urlpatterns = [
    path("storage/", include("storage.urls", namespace="storage")),
    path("users/", include("users.urls", namespace="users")),
]
