import os

import pytest

from social_relay.models import ReceiveStatistic, WorkerReceiveStatistic


@pytest.fixture
def app():
    try:
        os.remove("test.db")
    except:
        pass
    from social_relay import app, database
    database.database.create_tables([ReceiveStatistic, WorkerReceiveStatistic])
    return app
