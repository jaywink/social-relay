import datetime
import json

from social_relay.models import ReceiveStatistic, WorkerReceiveStatistic
from social_relay.utils.data import get_pod_preferences


def get_subscriber_stats():
    stats = {
        "total": 0,
        "subscribers": {
            "total": 0,
            "all": 0,
            "tags": 0,
        },
        "tags": [],
    }
    tags = []
    for pod, data in get_pod_preferences().items():
        data = json.loads(data.decode("utf-8"))
        try:
            stats["total"] += 1
            if data["subscribe"]:
                stats["subscribers"]["total"] += 1
                if data["scope"] == "all":
                    stats["subscribers"]["all"] += 1
                elif data["scope"] == "tags":
                    stats["subscribers"]["tags"] += 1
                tags += data["tags"]
        except KeyError:
            pass
    stats["tags"] = set(tags)
    return stats


def get_count_stats():
    day_ago = datetime.datetime.now() - datetime.timedelta(hours=24)
    week_ago = datetime.datetime.now() - datetime.timedelta(days=7)
    month_ago = datetime.datetime.now() - datetime.timedelta(days=30)
    incoming = {
        "today": ReceiveStatistic.select().where(ReceiveStatistic.created_at >= day_ago).count(),
        "week": ReceiveStatistic.select().where(ReceiveStatistic.created_at >= week_ago).count(),
        "month": ReceiveStatistic.select().where(ReceiveStatistic.created_at >= month_ago).count(),
        "all_time": ReceiveStatistic.select().count(),
    }
    outgoing = {
        "today": WorkerReceiveStatistic.select().where(WorkerReceiveStatistic.created_at >= day_ago).count(),
        "week": WorkerReceiveStatistic.select().where(WorkerReceiveStatistic.created_at >= week_ago).count(),
        "month": WorkerReceiveStatistic.select().where(WorkerReceiveStatistic.created_at >= month_ago).count(),
        "all_time": WorkerReceiveStatistic.select().count(),
    }
    return incoming, outgoing
