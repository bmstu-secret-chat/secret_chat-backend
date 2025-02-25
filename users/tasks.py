from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.utils.timezone import now

from celery import shared_task

from .models import UniqueUserStats

User = get_user_model()


@shared_task
def update_unique_users():
    """
    Задача обновления статистики уникальных пользователей за вчера и за последние 30 дней.
    """
    yesterday = now().date() - timedelta(days=1)
    last_30_days = yesterday - timedelta(days=30)

    yesterday_start_ts = int(datetime.combine(yesterday, datetime.min.time()).timestamp())
    yesterday_end_ts = int(datetime.combine(yesterday, datetime.max.time()).timestamp())
    last_30_days_ts = int(datetime.combine(last_30_days, datetime.min.time()).timestamp())

    daily_count = User.objects.filter(last_online__gte=yesterday_start_ts, last_online__lte=yesterday_end_ts).count()
    monthly_count = User.objects.filter(last_online__gte=last_30_days_ts, last_online__lte=yesterday_end_ts).count()

    UniqueUserStats.objects.create(date=yesterday, daily_users=daily_count, monthly_users=monthly_count)
