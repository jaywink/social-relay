# -*- coding: utf-8 -*-
from social_relay.config import database
from social_relay.models import Post, NodePost


tables = [Post, NodePost]


def up():
    database.drop_tables(tables)


def down():
    database.create_tables(tables)
