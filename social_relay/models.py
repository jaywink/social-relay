# -*- coding: utf-8 -*-
import datetime
import logging

from federation.fetchers import retrieve_remote_profile
from peewee import DateTimeField, CharField, IntegerField, BooleanField, TextField, DoesNotExist
from playhouse.fields import ManyToManyField

from social_relay import database
from social_relay.utils.text import safe_text


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


# TODO remove in next release after migration drops it
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


# TODO remove in next release after migration drops it
NodePost = Post.nodes.get_through_model()


class Profile(database.Model):
    """Store profile public keys."""
    identifier = CharField(unique=True)
    public_key = TextField()
    created_at = DateTimeField(default=datetime.datetime.now)

    @staticmethod
    def get_public_key(identifier):
        profile = Profile.get_profile(identifier)
        if profile:
            return profile.public_key

    @staticmethod
    def get_profile(identifier):
        """Get or create remote profile.

        Fetch it from federation layer if necessary or if the public key is empty for some reason.
        """
        try:
            sender_profile = Profile.get(Profile.identifier == identifier)
            if not sender_profile.public_key:
                raise DoesNotExist
        except DoesNotExist:
            remote_profile = retrieve_remote_profile(identifier)
            if not remote_profile:
                logging.warning("Remote profile %s not found locally or remotely.", identifier)
                return
            sender_profile = Profile.from_remote_profile(remote_profile)
        return sender_profile

    @staticmethod
    def from_remote_profile(remote_profile):
        """Create a Profile from a remote Profile entity."""
        public_key = safe_text(remote_profile.public_key)
        profile, created = Profile.get_or_create(
            identifier=safe_text(remote_profile.handle),
            defaults={
                "public_key": public_key,
            },
        )
        if not created and profile.public_key != public_key:
            profile.public_key = public_key
            profile.save()
        return profile


TABLES = (
    ReceiveStatistic, WorkerReceiveStatistic, Node, Post, NodePost, Profile,
)


def create_all_tables(db):
    """Create all tables to the designated db."""
    db.database.create_tables(TABLES)


def drop_all_tables(db):
    """Drop all tables from the designated db."""
    db.database.drop_tables(TABLES)
