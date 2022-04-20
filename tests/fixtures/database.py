import pytest
import sqlalchemy
import sqlalchemy.orm

from smartyard.db import Temps, Users


@pytest.fixture(scope="module")
def database_engine() -> sqlalchemy.engine.Engine:
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
def database_session(database_engine) -> sqlalchemy.orm.Session:
    Session = sqlalchemy.orm.sessionmaker(bind=database_engine)
    session = Session()
    yield session
    session.query(Temps).delete()
    session.query(Users).delete()
    session.commit()
