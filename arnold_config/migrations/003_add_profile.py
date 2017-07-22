# -*- coding: utf-8 -*-
from social_relay.config import database
from social_relay.models import Profile

tables = [Profile]


def up():
    database.create_tables(tables)


def down():
    database.drop_tables(tables)
