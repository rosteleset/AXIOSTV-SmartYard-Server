"""Модуль тестирования работы с базой данных"""

import uuid
from datetime import datetime
from typing import Iterable, Union

import pytest
import sqlalchemy.orm

from smartyard.db import Storage, Temps, Users

expected_user_uuid = uuid.uuid4()


@pytest.mark.parametrize(
    "exists_phones,delete_phone,phones_after_clear",
    (
        ((Temps(79001234567, 1234),), 79001234567, 0),
        (
            (
                Temps(79001234567, 1234),
                Temps(79001234568, 1235),
                Temps(79001234569, 1236),
            ),
            79001234567,
            2,
        ),
        (
            (
                Temps(79001234568, 1235),
                Temps(79001234569, 1236),
            ),
            79001234567,
            2,
        ),
    ),
)
def test_clear_codes_for_phone(
    database_session: sqlalchemy.orm.Session,
    exists_phones: Iterable,
    delete_phone: int,
    phones_after_clear: int,
):
    """Тест очистки существующих смс-кодов по номеру телефона"""
    storage = Storage(database_session)

    for phone in exists_phones:
        database_session.add(phone)
    database_session.commit()

    storage.clear_codes_for_phone(delete_phone)

    codes = database_session.query(Temps).all()
    assert len(codes) == phones_after_clear


@pytest.mark.parametrize(
    "exists_phones,auth_phone,expected_result",
    (
        ((Temps(79001234567, 1234),), 79001234567, Temps(79001234567, 1234)),
        (
            (
                Temps(79001234567, 1234),
                Temps(79001234568, 1235),
                Temps(79001234569, 1236),
            ),
            79001234567,
            Temps(79001234567, 1234),
        ),
        (
            (
                Temps(79001234568, 1235),
                Temps(79001234569, 1236),
            ),
            79001234567,
            None,
        ),
    ),
)
def test_auth_by_phone(
    database_session: sqlalchemy.orm.Session,
    exists_phones: Iterable,
    auth_phone: int,
    expected_result: Temps,
):
    """Тест атунтификации по номеру телефона"""
    storage = Storage(database_session)

    for phone in exists_phones:
        database_session.add(phone)
    database_session.commit()

    result = storage.auth_by_phone(auth_phone)

    assert result == expected_result


@pytest.mark.parametrize(
    "exists_phones,auth_phone,auth_code,expected_result",
    (
        ((Temps(79001234567, 1234),), 79001234567, 1234, Temps(79001234567, 1234)),
        (
            (
                Temps(79001234567, 1234),
                Temps(79001234568, 1235),
                Temps(79001234569, 1236),
            ),
            79001234567,
            1234,
            Temps(79001234567, 1234),
        ),
        (
            (
                Temps(79001234567, 1234),
                Temps(79001234568, 1235),
                Temps(79001234569, 1236),
            ),
            79001234567,
            1235,
            None,
        ),
        (
            (
                Temps(79001234567, 1234),
                Temps(79001234568, 1235),
                Temps(79001234569, 1236),
            ),
            79001234567,
            9999,
            None,
        ),
        (
            (
                Temps(79001234568, 1235),
                Temps(79001234569, 1236),
            ),
            79001234567,
            1234,
            None,
        ),
    ),
)
def test_auth_by_phone_and_code(
    database_session: sqlalchemy.orm.Session,
    exists_phones: Iterable,
    auth_phone: int,
    auth_code: int,
    expected_result: Temps,
):
    """Тест атунтификации по номеру телефона и смс-коду"""
    storage = Storage(database_session)

    for phone in exists_phones:
        database_session.add(phone)
    database_session.commit()

    result = storage.auth_by_phone_and_code(auth_phone, auth_code)

    assert result == expected_result


@pytest.mark.parametrize(
    "exists_users,token,expected_result",
    (
        (
            (
                Users(
                    uuid=expected_user_uuid,
                    userphone=79001234567,
                    name="User",
                    patronymic="-",
                    email="email@localhost",
                    videotoken="TOKEN",
                    vttime=datetime(2022, 12, 31, 23, 59, 59),
                    strims=[],
                ),
            ),
            "TOKEN",
            Users(
                uuid=expected_user_uuid,
                userphone=79001234567,
                name="User",
                patronymic="-",
                email="email@localhost",
                videotoken="TOKEN",
                vttime=datetime(2022, 12, 31, 23, 59, 59),
                strims=[],
            ),
        ),
        (
            (
                Users(
                    uuid=expected_user_uuid,
                    userphone=79001234567,
                    name="User",
                    patronymic="-",
                    email="email@localhost",
                    videotoken="TOKEN",
                    vttime=datetime(2022, 12, 31, 23, 59, 59),
                    strims=[],
                ),
                Users(
                    uuid=uuid.uuid4(),
                    userphone=79001234568,
                    name="User",
                    patronymic="-",
                    email="email@localhost",
                    videotoken="TOKEN_1",
                    vttime=datetime(2022, 12, 31, 23, 59, 59),
                    strims=[],
                ),
            ),
            "TOKEN",
            Users(
                uuid=expected_user_uuid,
                userphone=79001234567,
                name="User",
                patronymic="-",
                email="email@localhost",
                videotoken="TOKEN",
                vttime=datetime(2022, 12, 31, 23, 59, 59),
                strims=[],
            ),
        ),
        (
            (
                Users(
                    uuid=uuid.uuid4(),
                    userphone=79001234568,
                    name="User",
                    patronymic="-",
                    email="email@localhost",
                    videotoken="TOKEN_1",
                    vttime=datetime(2022, 12, 31, 23, 59, 59),
                    strims=[],
                ),
            ),
            "TOKEN",
            None,
        ),
    ),
)
def test_user_by_video_token(
    database_session: sqlalchemy.orm.Session,
    exists_users: Iterable,
    token: str,
    expected_result: Users,
):
    """Тест поиска пользователя по токену для видеопотоков"""
    storage = Storage(database_session)

    for user in exists_users:
        database_session.add(user)
    database_session.commit()

    result = storage.user_by_video_token(token)

    assert result == expected_result


@pytest.mark.parametrize(
    "exists_users,phone,expected_user",
    (
        (
            (
                Users(
                    uuid=expected_user_uuid,
                    userphone=79001234567,
                    name="User",
                    patronymic="-",
                    email="email@localhost",
                    videotoken="TOKEN",
                    vttime=datetime(2022, 12, 31, 23, 59, 59),
                    strims=[],
                ),
            ),
            79001234567,
            Users(
                uuid=expected_user_uuid,
                userphone=79001234567,
                name="User",
                patronymic="-",
                email="email@localhost",
                videotoken="TOKEN",
                vttime=datetime(2022, 12, 31, 23, 59, 59),
                strims=[],
            ),
        ),
        (
            (
                Users(
                    uuid=expected_user_uuid,
                    userphone=79001234567,
                    name="User",
                    patronymic="-",
                    email="email@localhost",
                    videotoken="TOKEN",
                    vttime=datetime(2022, 12, 31, 23, 59, 59),
                    strims=[],
                ),
                Users(
                    uuid=uuid.uuid4(),
                    userphone=79001234568,
                    name="User",
                    patronymic="-",
                    email="email@localhost",
                    videotoken="TOKEN_1",
                    vttime=datetime(2022, 12, 31, 23, 59, 59),
                    strims=[],
                ),
            ),
            79001234567,
            Users(
                uuid=expected_user_uuid,
                userphone=79001234567,
                name="User",
                patronymic="-",
                email="email@localhost",
                videotoken="TOKEN",
                vttime=datetime(2022, 12, 31, 23, 59, 59),
                strims=[],
            ),
        ),
        (
            (
                Users(
                    uuid=uuid.uuid4(),
                    userphone=79001234568,
                    name="User",
                    patronymic="-",
                    email="email@localhost",
                    videotoken="TOKEN_1",
                    vttime=datetime(2022, 12, 31, 23, 59, 59),
                    strims=[],
                ),
            ),
            79001234567,
            None,
        ),
    ),
)
def test_user_by_phone(
    database_session: sqlalchemy.orm.Session,
    exists_users: Iterable,
    phone: int,
    expected_user: Users,
):
    """Тест поиска пользователя по номеру телефона"""
    storage = Storage(database_session)

    for user in exists_users:
        database_session.add(user)
    database_session.commit()

    result = storage.user_by_phone(phone)
    print(result, expected_user)
    assert result == expected_user


@pytest.mark.parametrize(
    "exists_users,user_uuid,expected_user",
    (
        (
            (
                Users(
                    uuid=expected_user_uuid,
                    userphone=79001234567,
                    name="User",
                    patronymic="-",
                    email="email@localhost",
                    videotoken="TOKEN",
                    vttime=datetime(2022, 12, 31, 23, 59, 59),
                    strims=[],
                ),
            ),
            expected_user_uuid,
            Users(
                uuid=expected_user_uuid,
                userphone=79001234567,
                name="User",
                patronymic="-",
                email="email@localhost",
                videotoken="TOKEN",
                vttime=datetime(2022, 12, 31, 23, 59, 59),
                strims=[],
            ),
        ),
        (
            (
                Users(
                    uuid=expected_user_uuid,
                    userphone=79001234567,
                    name="User",
                    patronymic="-",
                    email="email@localhost",
                    videotoken="TOKEN",
                    vttime=datetime(2022, 12, 31, 23, 59, 59),
                    strims=[],
                ),
                Users(
                    uuid=uuid.uuid4(),
                    userphone=79001234568,
                    name="User",
                    patronymic="-",
                    email="email@localhost",
                    videotoken="TOKEN_1",
                    vttime=datetime(2022, 12, 31, 23, 59, 59),
                    strims=[],
                ),
            ),
            expected_user_uuid,
            Users(
                uuid=expected_user_uuid,
                userphone=79001234567,
                name="User",
                patronymic="-",
                email="email@localhost",
                videotoken="TOKEN",
                vttime=datetime(2022, 12, 31, 23, 59, 59),
                strims=[],
            ),
        ),
        (
            (
                Users(
                    uuid=uuid.uuid4(),
                    userphone=79001234568,
                    name="User",
                    patronymic="-",
                    email="email@localhost",
                    videotoken="TOKEN_1",
                    vttime=datetime(2022, 12, 31, 23, 59, 59),
                    strims=[],
                ),
            ),
            expected_user_uuid,
            None,
        ),
    ),
)
def test_user_by_uuid(
    database_session: sqlalchemy.orm.Session,
    exists_users: Iterable,
    user_uuid: str,
    expected_user: Users,
):
    """Тест поиска пользователя по уникальному идентификатору"""
    storage = Storage(database_session)

    for user in exists_users:
        database_session.add(user)
    database_session.commit()

    result = storage.user_by_uuid(user_uuid)

    assert result == expected_user


@pytest.mark.parametrize(
    "save_object",
    (
        Users(
            uuid=expected_user_uuid,
            userphone=79001234567,
            name="User",
            patronymic="-",
            email="email@localhost",
            videotoken="TOKEN",
            vttime=datetime(2022, 12, 31, 23, 59, 59),
            strims=[],
        ),
        Temps(79001234567, 1234),
    ),
)
def test_save(
    database_session: sqlalchemy.orm.Session,
    save_object: Union[Temps, Users],
):
    """Тест сохранения объектов в базе"""
    storage = Storage(database_session)

    assert len(database_session.query(type(save_object)).all()) == 0

    storage.save(save_object)

    assert len(database_session.query(type(save_object)).all()) == 1
