"""Модуль фикстур для бизнес-логики"""

import uuid
from datetime import datetime

import pytest

from smartyard.logic.auth import Auth
from smartyard.logic.user import User


@pytest.fixture
def logic_user() -> User:
    """Фикстура тестового клиента"""
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


@pytest.fixture
def logic_auth() -> Auth:
    """Фикстура объекта аутентификации(телефон и код для смс)"""
    return Auth(userphone=79001234567, smscode=1234)
