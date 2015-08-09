import redis

from social_relay import config


r = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB)


def get_pod_preferences():
    return r.hgetall("pod_preferences")
