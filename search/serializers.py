from django_elasticsearch_dsl_drf.serializers import DocumentSerializer
from rest_framework import serializers

from .documents import UserDocument


class UserDocumentSerializer(DocumentSerializer):
    """
    Сериализатор для поиска пользователей в Elasticsearch.
    """
    id = serializers.SerializerMethodField()

    class Meta:
        document = UserDocument
        fields = ["id", "username", "avatar"]

    def get_id(self, obj):
        return obj.meta.id
