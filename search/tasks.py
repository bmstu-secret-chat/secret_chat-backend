from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import F, Q
from django.utils.timezone import now

from celery import shared_task

from .documents import UserDocument

User = get_user_model()


@shared_task
def sync_users_to_elasticsearch():
    """
    Задача для синхронизации пользователей с Elasticsearch.
    """
    with transaction.atomic():
        users = list(User.objects.filter(
            Q(updated_at__gt=F("sync_at")) | Q(sync_at__isnull=True),
            is_deleted=False,
        ))

        User.objects.filter(id__in=(user.id for user in users)).update(sync_at=now())

        for user in users:
            user_document = UserDocument(meta={"id": user.id}, username=user.username, avatar=user.avatar)
            user_document.save()
