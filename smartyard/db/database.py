import functools

from flask_sqlalchemy import SQLAlchemy


@functools.lru_cache
def create_db_connection():
    return SQLAlchemy()
