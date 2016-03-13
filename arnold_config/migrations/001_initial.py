from arnold_config import database

from social_relay.models import ReceiveStatistic, WorkerReceiveStatistic


tables = [ReceiveStatistic, WorkerReceiveStatistic]


def up():
    database.create_tables(tables)


def down():
    database.drop_tables(tables)
