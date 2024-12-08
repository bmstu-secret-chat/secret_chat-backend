from django.urls import path

from .views import check_view, create_view

app_name = "users"

urlpatterns = [
    path("create/", create_view, name="create"),
    path("check/", check_view, name="check"),
]
