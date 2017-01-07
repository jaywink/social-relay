# -*- coding: utf-8 -*-
import pytest
from peewee import ProgrammingError, OperationalError

from social_relay.models import create_all_tables, drop_all_tables


@pytest.fixture
def app(request):
    from social_relay import app, database
    try:
        drop_all_tables(database)
    except (ProgrammingError, OperationalError):
        pass
    create_all_tables(database)

    def drop_db():
        drop_all_tables(database)

    request.addfinalizer(drop_db)

    return app
