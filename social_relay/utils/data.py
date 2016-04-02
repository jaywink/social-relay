# -*- coding: utf-8 -*-
import redis
from rq import Queue, Worker

from social_relay import config


r = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB)

public_queue = Queue("receive", connection=r)


def get_pod_preferences():
    return r.hgetall("pod_preferences")


def get_worker_count():
    return len(Worker.all(public_queue.connection))
