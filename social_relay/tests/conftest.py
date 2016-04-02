# -*- coding: utf-8 -*-
import os

import pytest

from social_relay.models import create_all_tables


@pytest.fixture
def app():
    try:
        os.remove("test.db")
    except:
        pass
    from social_relay import app, database
    create_all_tables(database)
    return app
