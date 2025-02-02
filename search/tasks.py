from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils.timezone import now

from celery import shared_task

from .documents import UserDocument

User = get_user_model()


@shared_task
def sync_users_to_elasticsearch():
    """
    Задача для синхронизации пользователей с Elasticsearch.
    """
    last_sync_time = now() - timedelta(minutes=6)
    users = User.objects.filter(updated_at__gte=last_sync_time, is_deleted=False)

    for user in users:
        user_document = UserDocument(meta={"id": user.id}, username=user.username)
        user_document.save()
