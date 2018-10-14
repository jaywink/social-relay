import datetime
import logging

from federation.entities.base import Image
from federation.entities.diaspora.entities import DiasporaPost
from federation.exceptions import NoSuitableProtocolFoundError
from federation.inbound import handle_receive
from federation.utils.network import send_document

from social_relay import config
from social_relay.models import Node, Profile
from social_relay.utils.data import nodes_who_want_tags, nodes_who_want_all
from social_relay.utils.statistics import log_worker_receive_statistics

HEADERS = {
    "User-Agent": config.USER_AGENT, "Content-Type": "application/magic-envelope+xml",
}

SUPPORTED_ENTITIES = (
    DiasporaPost,
)


def get_send_to_nodes(sender, entity):
    """Get the target nodes to send this entity to.

    :param sender: Sender handle
    :type sender: unicode
    :param entity: Entity instance
    :return: list
    """
    if isinstance(entity, (DiasporaPost, Image)):
        nodes = nodes_who_want_all()
        if config.ALWAYS_FORWARD_TO_HOSTS:
            nodes.update(set(config.ALWAYS_FORWARD_TO_HOSTS))
        if isinstance(entity, DiasporaPost):
            nodes.update(nodes_who_want_tags(entity.tags))
        if sender.split("@")[1] in nodes:
            # Don't send back to sender
            nodes.remove(sender.split("@")[1])
        return nodes
    return set()


def process(payload):
    """Open payload and route it to any pods that might be interested in it."""
    try:
        sender, protocol_name, entities = handle_receive(payload, sender_key_fetcher=Profile.get_public_key)
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
    sent_amount = 0
    sent_success = 0
    nodes = set()
    sent_to_nodes = []
    entity = None
    try:
        for entity in entities:
            # Diaspora payloads should only have one top level entity. Once we find a suitable one, just start sending
            if isinstance(entity, SUPPORTED_ENTITIES):
                nodes = get_send_to_nodes(sender, entity)
                break
        # Send out
        if nodes:
            logging.info("Sending %s to %s nodes", entity, len(nodes))
        for node in nodes:
            status, error = send_document(
                url="https://%s/receive/public" % node,
                data=payload,
                headers=HEADERS,
            )
            is_success = status in [200, 202]
            if is_success:
                sent_success += 1
                sent_to_nodes.append(node)
            sent_amount += 1
            update_node(node, is_success)
        logging.info("Successfully sent to %s nodes", len(sent_to_nodes))
    finally:
        log_worker_receive_statistics(
            protocol_name, len(entities), sent_amount, sent_success
        )


def update_node(node, success):
    """Update Node in database

    :param node: Hostname
    :param success: Was the last call a success (bool)
    """
    try:
        Node.get_or_create(host=node)
        if success:
            # Update delivered_count and last_success, nullify failure_count
            # TODO: remove the whole https tracking - we're only delivering to https now
            Node.update(
                last_success=datetime.datetime.now(), total_delivered=Node.total_delivered + 1,
                failure_count=0, https=True).where(Node.host == node).execute()
        else:
            # Update failure_count
            Node.update(
                failure_count=Node.failure_count + 1).where(Node.host == node).execute()
    except Exception as ex:
        logging.warning("Exception when trying to save or update Node {node} into database: {exc}".format(
            node=node, exc=ex)
        )
