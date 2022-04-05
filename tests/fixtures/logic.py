import uuid
from datetime import datetime

import pytest

from smartyard.logic.user import User


@pytest.fixture
def logic_user() -> User:
    return User(
        userphone=79001234567,
        name="Name",
        patronymic="Patronymic",
        email="email@localhost",
        uuid=uuid.uuid4(),
        videotoken="Token",
        vttime=datetime.now(),
        strims=[
            "stream_1",
        ],
    )
