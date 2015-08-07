from _socket import timeout
from redis import Redis
import requests
from requests.exceptions import ConnectionError, Timeout
import schedule

from social_relay import config


r = Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB)


def get_pod_relay_preferences(host):
    """Query remote pods on https first, fall back to http."""
    print("Querying %s" % host)
    try:
        try:
            response = requests.get("https://%s/.well-known/x-social-relay" % host, timeout=5)
        except timeout:
            response = None
        if not response or response.status_code != 200:
            response = requests.get("http://%s/.well-known/x-social-relay" % host, timeout=5)
            if response.status_code != 200:
                return None
    except (ConnectionError, Timeout):
        return None
    try:
        return response.text
    except ValueError:
        return None


def poll_pods():
    print("Polling pods")
    pods = r.hgetall("pods")
    for pod, data in pods.items():
        data = get_pod_relay_preferences(pod.decode("utf-8"))
        if data:
            r.hset("pod_preferences", pod, data)
        else:
            if r.hexists("pod_preferences", pod):
                r.hdel("pod_preferences", pod)


def schedule_job():
    schedule.every().hour.do(poll_pods)


if __name__ == '__main__':
    # Execute job directly
    poll_pods()
