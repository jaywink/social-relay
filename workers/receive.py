from _socket import timeout
import json
import logging
import requests
from requests.exceptions import ConnectionError, Timeout

from federation.controllers import handle_receive
from federation.entities.base import Post
from federation.exceptions import NoSuitableProtocolFoundError

from social_relay import config
from social_relay.utils.data import get_pod_preferences


def pods_who_want_tags(tags):
    pods = []
    for pod, data in get_pod_preferences().items():
        data = json.loads(data.decode("utf-8"))
        if not set(data["tags"]).isdisjoint(tags):
            # One or more tags match
            pods.append(pod.decode("utf-8"))
    return pods


def pods_who_want_all():
    pods = []
    for pod, data in get_pod_preferences().items():
        data = json.loads(data.decode("utf-8"))
        if data["subscribe"] and data["scope"] == "all":
            pods.append(pod.decode("utf-8"))
    return pods


def send_payload(host, payload):
    """Post payload to host, try https first, fall back to http.

    Return True or False, depending on success of operation.
    Timeouts or connection errors will not be raised.
    """
    logging.info("Sending payload to %s" % host)
    try:
        try:
            response = requests.post("https://%s/receive/public" % host, data={"xml": payload}, timeout=10)
        except timeout:
            response = False
        if not response or response.status_code != 200:
            response = requests.get("http://%s/receive/public" % host, data={"xml": payload}, timeout=10)
            if response.status_code != 200:
                return False
    except (ConnectionError, Timeout):
        return False
    return True


def process(payload):
    """Open payload and route it to any pods that might be interested in it."""
    try:
        sender, protocol_name, entities = handle_receive(payload, skip_author_verification=True)
        logging.debug("sender=%s, protocol_name=%s, entities=%s" % (sender, protocol_name, entities))
    except NoSuitableProtocolFoundError:
        logging.warning("No suitable protocol found for payload")
        return
    if protocol_name != "diaspora":
        logging.warning("Unsupported protocol: %s, sender: %s" % (protocol_name, sender))
        return
    if not entities:
        logging.warning("No entities in payload")
        return
    send_to_pods = pods_who_want_all()
    send_to_pods += config.ALWAYS_FORWARD_TO_HOSTS
    if sender.split("@")[1] in send_to_pods:
        # Don't send back to sender
        send_to_pods.remove(sender.split("@")[1])
    for entity in entities:
        logging.info("Entity: %s" % entity)
        # We only care about posts atm
        if isinstance(entity, Post):
            # Add pods who want this posts tags
            final_send_to_pods = send_to_pods[:] + pods_who_want_tags(entity.tags)
            # Send out
            for pod in final_send_to_pods:
                send_payload(pod, payload)
