# -*- coding: utf-8 -*-
import datetime
from _socket import timeout
import json
import logging
import requests

from federation.controllers import handle_receive
from federation.entities.diaspora.entities import DiasporaPost
from federation.exceptions import NoSuitableProtocolFoundError
from requests.exceptions import ConnectionError, Timeout

from social_relay import config
from social_relay.models import Node, Post
from social_relay.utils.data import get_pod_preferences
from social_relay.utils.statistics import log_worker_receive_statistics


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

    Return a dictionary containing:
        "result": True or False, depending on success of operation.
        "https": True or False

    Timeouts or connection errors will not be raised.
    """
    logging.info("Sending payload to %s" % host)
    https = True
    try:
        try:
            response = requests.post(
                "https://%s/receive/public" % host, data={"xml": payload}, timeout=10, allow_redirects=False
            )
        except timeout:
            response = False
        if not response or response.status_code not in [200, 202]:
            https = False
            response = requests.post(
                "http://%s/receive/public" % host, data={"xml": payload}, timeout=10, allow_redirects=False
            )
            if response.status_code not in [200, 202]:
                return {"result": False, "https": https}
    except (ConnectionError, Timeout) as ex:
        logging.debug("Connection failed with {host}: {ex}".format(host=host, ex=ex))
        return {"result": False, "https": https}
    return {"result": True, "https": https}


def save_post_metadata(entity, protocol, hosts):
    """Save Post metadata to db.

    :param entity: DiasporaPost entity
    :param protocol: Protocol identifier
    :param hosts: List of hostnames that send was done successfully
    """
    try:
        post, created = Post.get_or_create(guid=entity.guid, protocol=protocol)
        for host in hosts:
            post.nodes.add(Node.get(host=host))
    except Exception as ex:
        logging.warning("Exception when trying to save post '{entity}' into database: {exc}".format(
            entity=entity, exc=ex))


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
    sent_amount = 0
    sent_success = 0
    try:
        for entity in entities:
            logging.info("Entity: %s" % entity)
            # We only care about posts atm
            if isinstance(entity, DiasporaPost):
                sent_to_nodes = []
                # Add pods who want this posts tags
                final_send_to_pods = send_to_pods[:] + pods_who_want_tags(entity.tags)
                # Send out
                for pod in final_send_to_pods:
                    response = send_payload(pod, payload)
                    if response["result"]:
                        sent_success += 1
                        sent_to_nodes.append(pod)
                    sent_amount += 1
                    update_node(pod, response)
                if sent_to_nodes:
                    save_post_metadata(entity=entity, protocol=protocol_name, hosts=sent_to_nodes)
    finally:
        log_worker_receive_statistics(
            protocol_name, len(entities), sent_amount, sent_success
        )


def update_node(pod, response):
    """Update Node in database

    :param pod: Hostname
    :param response: Dictionary with booleans "result" and "https"
    """
    try:
        Node.get_or_create(host=pod)
        if response["result"]:
            # Update delivered_count and last_success, nullify failure_count
            Node.update(
                last_success=datetime.datetime.now(), total_delivered=Node.total_delivered + 1,
                failure_count=0, https=response["https"]).where(Node.host==pod).execute()
        else:
            # Update failure_count
            Node.update(
                failure_count=Node.failure_count + 1).where(Node.host==pod).execute()
    except Exception as ex:
        logging.warning("Exception when trying to save or update Node {node} into database: {exc}".format(
            node=pod, exc=ex)
        )
