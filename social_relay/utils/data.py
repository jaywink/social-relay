# -*- coding: utf-8 -*-
import json

import redis

from social_relay import config


r = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB)


def get_pod_preferences():
    return r.hgetall("pod_preferences")


def nodes_who_want_tags(tags):
    nodes = set()
    for node, data in get_pod_preferences().items():
        data = json.loads(data.decode("utf-8"))
        if not set(data["tags"]).isdisjoint(tags):
            # One or more tags match
            nodes.add(node.decode("utf-8"))
    return nodes


def nodes_who_want_all():
    nodes = set()
    for node, data in get_pod_preferences().items():
        data = json.loads(data.decode("utf-8"))
        if data["subscribe"] and data["scope"] == "all":
            nodes.add(node.decode("utf-8"))
    return nodes
