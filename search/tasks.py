from django.contrib.auth import get_user_model

from celery import shared_task

from .documents import UserDocument

User = get_user_model()


@shared_task
def sync_users_to_elasticsearch():
    """
    Задача для синхронизации пользователей с Elasticsearch.
    """
    users = User.objects.filter(is_deleted=False)

    for user in users:
        user_document = UserDocument(meta={"id": user.id}, username=user.username)
        user_document.save()
