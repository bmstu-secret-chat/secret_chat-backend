from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/backend/", include("backend.router")),
    path('api/chats/', include('chats.urls')),
]
