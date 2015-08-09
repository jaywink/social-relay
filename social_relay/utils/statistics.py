import json

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
                if stats["scope"] == "all":
                    stats["subscribers"]["all"] += 1
                elif stats["scope"] == "tags":
                    stats["subscribers"]["tags"] += 1
                tags += data["tags"]
                stats["tags"] = set(tags)
        except KeyError:
            pass
    return stats
