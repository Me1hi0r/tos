from celery import shared_task
from celery.utils.log import get_task_logger
from datetime import datetime, timedelta

from django.conf import settings
from .models import UserLog, TrackedHost
from clickhouse_driver import Client


logger = get_task_logger(__name__)


@shared_task
def get_log_task():
    def time_sub_delta(minutes=0):
        return (datetime.utcnow() - timedelta(minutes=minutes)).strftime(settings.DT_FORMAT)

    start_dt = time_sub_delta(settings.TOS_WORKER_START_MIN)
    finish_dt = time_sub_delta(settings.TOS_WORKER_END_MIN)

    query = f"select host, sum(time) from metric.tos where session in (select distinct session from metric.tos where timestamp>='{start_dt}' and timestamp < '{finish_dt}') group by session, host "
    ch_client = Client(host='tos-click', port=9000)
    result = ch_client.execute(query)
    if result:
        for [host, tos] in result:
            active = TrackedHost.objects.filter(host=host, active=True).first()
            if active:
                tos_log = UserLog.objects.create(host=active, tos=tos)
                tos_log.save()
