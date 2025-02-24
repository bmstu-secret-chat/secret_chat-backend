from prometheus_client import Gauge

from .models import UniqueUserStats

unique_users_daily = Gauge("unique_users_daily", "Уникальные пользователи за день")

unique_users_monthly = Gauge("unique_users_monthly", "Уникальные пользователи за месяц")


def update_metrics():
    """
    Обновляет метрики перед каждым экспортом в Prometheus.
    """
    latest_stat = UniqueUserStats.objects.order_by("-date").first()
    if latest_stat:
        unique_users_daily.set(latest_stat.daily_users)
        unique_users_monthly.set(latest_stat.monthly_users)
