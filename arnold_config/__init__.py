from peewee import SqliteDatabase

from social_relay import config


database = SqliteDatabase(config.DATABASE_NAME)
