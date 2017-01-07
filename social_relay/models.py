# -*- coding: utf-8 -*-
import datetime

from peewee import DateTimeField, CharField, IntegerField, BooleanField
from playhouse.fields import ManyToManyField

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


class Node(database.Model):
    """Stores Nodes, ie pods, servers, etc."""
    host = CharField(unique=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    last_success = DateTimeField(null=True)
    total_delivered = IntegerField(default=0)
    failure_count = IntegerField(default=0)
    https = BooleanField(default=False)


class Post(database.Model):
    """Stores list of domains where posts have been delivered to."""
    nodes = ManyToManyField(Node, related_name="posts")
    guid = CharField()
    protocol = CharField()
    created_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        indexes = (
            (("guid", "protocol"), True),
        )


NodePost = Post.nodes.get_through_model()


TABLES = (
    ReceiveStatistic, WorkerReceiveStatistic, Node, Post, NodePost,
)


def create_all_tables(db):
    """Create all tables to the designated db."""
    db.database.create_tables(TABLES)


def drop_all_tables(db):
    """Drop all tables from the designated db."""
    db.database.drop_tables(TABLES)
