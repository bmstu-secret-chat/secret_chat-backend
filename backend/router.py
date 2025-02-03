from django.urls import include, path

urlpatterns = [
    path("search/", include("search.urls", namespace="search")),
    path("storage/", include("storage.urls", namespace="storage")),
    path("users/", include("users.urls", namespace="users")),
]
