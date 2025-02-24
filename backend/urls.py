from django.urls import include, path

from users.views import metrics_view

urlpatterns = [
    path("api/backend/", include("backend.router")),
    path("metrics", metrics_view, name="metrics"),
]
