# -*- coding: utf-8 -*-
from rq import Queue, Worker

from social_relay.utils.data import r


public_queue = Queue("receive", connection=r)


def get_worker_count():
    return len(Worker.all(public_queue.connection))
