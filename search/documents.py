from django.contrib.auth import get_user_model

from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

User = get_user_model()


@registry.register_document
class UserDocument(Document):
    username = fields.TextField(
        attr="username",
        fields={
            "raw": fields.KeywordField(),
        }
    )
    avatar = fields.KeywordField(attr="avatar")

    class Index:
        name = "users"
        settings = {"number_of_shards": 1, "number_of_replicas": 0}

    class Django:
        model = User
        fields = ["id"]

    def get_queryset(self):
        return User.objects.filter(is_deleted=False)
