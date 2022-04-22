"""Модуль фикстур для базы данных"""

import pytest
import sqlalchemy
import sqlalchemy.orm

from smartyard.db import Temps, Users


@pytest.fixture(scope="module")
def database_engine() -> sqlalchemy.engine.Engine:
    """Фикстура подключения к базе данных"""
    # return sqlalchemy.create_engine("sqlite:///:memory:")
    engine = sqlalchemy.create_engine(
        "postgresql://smartyard:smartyardpass@127.0.0.1:5432/smartyard"
    )
    Temps.metadata.create_all(engine)
    Users.metadata.create_all(engine)
    yield engine
    Temps.metadata.drop_all(engine)
    Users.metadata.drop_all(engine)


@pytest.fixture
# pylint: disable=redefined-outer-name
def database_session(database_engine) -> sqlalchemy.orm.Session:
    """Фикстура сессии подключения к базе данных"""
    session = sqlalchemy.orm.sessionmaker(bind=database_engine)()
    yield session
    session.query(Temps).delete()
    session.query(Users).delete()
    session.commit()
