import sys

from redis import Redis
from rq import Queue, Connection, Worker

from social_relay.config import REDIS_HOST, REDIS_PORT, REDIS_DB


if __name__ == '__main__':
    # Provide queue names to listen to as arguments to this script,
    # similar to rqworker
    conn = Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
    with Connection(conn):
        qs = map(Queue, sys.argv[1:]) or [Queue()]
        w = Worker(qs)
        w.work()
