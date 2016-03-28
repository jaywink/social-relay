import datetime

from peewee import DateTimeField, CharField, IntegerField

from social_relay import database


class StatisticBase(database.Model):
    """Base model for statistics."""
    created_at = DateTimeField(default=datetime.datetime.now)


class ReceiveStatistic(StatisticBase):
    """Received objects statistics."""
    sender_host = CharField()


class WorkerReceiveStatistic(StatisticBase):
    """Received processing statistics."""
    protocol = CharField()
    # How many entities contained
    entities = IntegerField(default=0)
    # How many remotes sent to
    sent_amount = IntegerField(default=0)
    # How many remote sends succeeded
    sent_success = IntegerField(default=0)
