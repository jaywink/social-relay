from _socket import timeout
import json
import logging
import os
from jsonschema import validate, ValidationError
from redis import Redis
import requests
from requests.exceptions import ConnectionError, Timeout
import schedule

from social_relay import config


class PodPoller(object):
    def __init__(self):
        self.schema = self.get_social_relay_schema()
        self.r = Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB)

    def get_social_relay_schema(self):
        schema_path = os.path.join(os.path.dirname(__file__), "..", "schemas", "social-relay-well-known.json")
        with open(schema_path) as f:
            schema = json.load(f)
        return schema

    def get_pod_relay_preferences(self, host):
        """Query remote pods on https first, fall back to http."""
        logging.info("Querying %s" % host)
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
            # Make sure we have a valid x-social-relay doc
            validate(response.json(), self.schema)
            return response.text
        except (ValueError, ValidationError):
            return None

    def poll_pods(self):
        logging.info("Polling pods")
        pods = self.r.hgetall("pods")
        for pod, data in pods.items():
            data = self.get_pod_relay_preferences(pod.decode("utf-8"))
            if data:
                logging.debug("Pod: %s, preferences: %s" % (pod.decode("utf-8"), data))
                self.r.hset("pod_preferences", pod, data)
            else:
                if self.r.hexists("pod_preferences", pod):
                    logging.debug("Pod %s preferences not found, deleting cached data" % pod.decode("utf-8"))
                    self.r.hdel("pod_preferences", pod)


def poll_pods():
    poller = PodPoller()
    poller.poll_pods()


def schedule_job():
    schedule.every().hour.do(poll_pods)


if __name__ == '__main__':
    # Execute job directly
    poll_pods()
