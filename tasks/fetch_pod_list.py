import logging
from redis import Redis
import requests
import schedule

from social_relay import config


r = Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB)


def fetch_pod_lists():
    logging.info("Fetching pod list")
    response = requests.get(config.POD_LIST_JSON)
    data = response.json()
    # TODO: also remove inactives from list
    for pod in data["pods"]:
        r.hset("pods", pod["host"], pod)


def schedule_job():
    schedule.every().hour.do(fetch_pod_lists)


if __name__ == '__main__':
    # Execute job directly
    fetch_pod_lists()
