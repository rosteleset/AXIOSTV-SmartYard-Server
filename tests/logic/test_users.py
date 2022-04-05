import uuid
from datetime import datetime
from typing import Union

import pytest
from pytest_mock import MockerFixture

from smartyard.db.storage import Storage
from smartyard.db.temps import Temps
from smartyard.db.users import Users as Users_db
from smartyard.logic.auth import Auth
from smartyard.logic.user import User
from smartyard.logic.users import Users

NOW = datetime.now()


@pytest.mark.parametrize(
    "_uuid,user,expected",
    (
        (
            "2ef001df-1909-4112-9265-bd7ec5b4bad3",
            Users_db(
                uuid=uuid.UUID("2ef001df-1909-4112-9265-bd7ec5b4bad3"),
                userphone="89001234567",
                name="User",
                patronymic="Patronomic",
                email="email@localhost",
                videotoken="Token",
                vttime=NOW,
                strims=[
                    "stream_1",
                ],
            ),
            User(
                userphone="89001234567",
                name="User",
                patronymic="Patronomic",
                email="email@localhost",
                uuid=uuid.UUID("2ef001df-1909-4112-9265-bd7ec5b4bad3"),
                videotoken="Token",
                vttime=NOW,
                strims=[
                    "stream_1",
                ],
            ),
        ),
        (
            "2ef001df-1909-4112-9265-bd7ec5b4bad3",
            None,
            None,
        ),
    ),
)
def test_user_by_uuid(
    _uuid: str, user: Users_db, expected: User, mocker: MockerFixture
):
    mocker.patch.object(Storage, "user_by_uuid", return_value=user)
    users = Users()

    found_user = users.user_by_uuid(_uuid)

    assert found_user == expected


@pytest.mark.parametrize(
    "phone,user,expected",
    (
        (
            "89001234567",
            Users_db(
                uuid=uuid.UUID("2ef001df-1909-4112-9265-bd7ec5b4bad3"),
                userphone="89001234567",
                name="User",
                patronymic="Patronomic",
                email="email@localhost",
                videotoken="Token",
                vttime=NOW,
                strims=[
                    "stream_1",
                ],
            ),
            User(
                userphone="89001234567",
                name="User",
                patronymic="Patronomic",
                email="email@localhost",
                uuid=uuid.UUID("2ef001df-1909-4112-9265-bd7ec5b4bad3"),
                videotoken="Token",
                vttime=NOW,
                strims=[
                    "stream_1",
                ],
            ),
        ),
        (
            "89001234567",
            None,
            None,
        ),
    ),
)
def test_user_by_phone(
    phone: str, user: Users_db, expected: User, mocker: MockerFixture
):
    mocker.patch.object(Storage, "user_by_phone", return_value=user)
    users = Users()

    found_user = users.user_by_phone(phone)

    assert found_user == expected


@pytest.mark.parametrize(
    "user,raw_user,expected",
    (
        (
            User(
                userphone="89001234567",
                name="User",
                patronymic="Patronomic",
                email="email@localhost",
                uuid=None,
                videotoken="Token",
                vttime=NOW,
                strims=[
                    "stream_1",
                ],
            ),
            Users_db(
                uuid=uuid.UUID("2ef001df-1909-4112-9265-bd7ec5b4bad3"),
                userphone="89001234567",
                name="User",
                patronymic="Patronomic",
                email="email@localhost",
                videotoken="Token",
                vttime=NOW,
                strims=[
                    "stream_1",
                ],
            ),
            User(
                userphone="89001234567",
                name="User",
                patronymic="Patronomic",
                email="email@localhost",
                uuid=uuid.UUID("2ef001df-1909-4112-9265-bd7ec5b4bad3"),
                videotoken="Token",
                vttime=NOW,
                strims=[
                    "stream_1",
                ],
            ),
        ),
        (
            User(
                userphone="89001234567",
                name="User",
                patronymic="Patronomic",
                email="email@localhost",
                uuid=uuid.UUID("2ef001df-1909-4112-9265-bd7ec5b4bad3"),
                videotoken="Token",
                vttime=NOW,
                strims=[
                    "stream_1",
                ],
            ),
            Users_db(
                uuid=uuid.UUID("2ef001df-1909-4112-9265-bd7ec5b4bad3"),
                userphone="89001234567",
                name="User",
                patronymic="Patronomic",
                email="email@localhost",
                videotoken="Token",
                vttime=NOW,
                strims=[
                    "stream_1",
                ],
            ),
            User(
                userphone="89001234567",
                name="User",
                patronymic="Patronomic",
                email="email@localhost",
                uuid=uuid.UUID("2ef001df-1909-4112-9265-bd7ec5b4bad3"),
                videotoken="Token",
                vttime=NOW,
                strims=[
                    "stream_1",
                ],
            ),
        ),
    ),
)
def test_save_user(
    user: User, raw_user: Users_db, expected: User, mocker: MockerFixture
):
    mocker.patch.object(Storage, "save", return_value=raw_user)
    users = Users()

    found_user = users.save_user(user)

    assert found_user == expected


@pytest.mark.parametrize(
    "phone,code,mock,expected",
    (
        (
            "89001234567",
            "1234",
            Temps(userphone=89001234567, smscode=1234),
            Auth(userphone=89001234567, smscode=1234),
        ),
        (
            "89001234567",
            1234,
            Temps(userphone=89001234567, smscode=1234),
            Auth(userphone=89001234567, smscode=1234),
        ),
        (
            89001234567,
            "1234",
            Temps(userphone=89001234567, smscode=1234),
            Auth(userphone=89001234567, smscode=1234),
        ),
        (
            89001234567,
            1234,
            Temps(userphone=89001234567, smscode=1234),
            Auth(userphone=89001234567, smscode=1234),
        ),
    ),
)
def test_set_auth_code(
    phone: Union[int, str],
    code: Union[int, str],
    mock: Temps,
    expected: Auth,
    mocker: MockerFixture,
):
    mocker.patch.object(Storage, "save", return_value=mock)
    users = Users()

    auth = users.set_auth_code(phone, code)

    assert auth == expected


@pytest.mark.parametrize(
    "phone,code,mock,expected",
    (
        (
            "89001234567",
            "1234",
            Temps(userphone=89001234567, smscode=1234),
            Auth(userphone=89001234567, smscode=1234),
        ),
        (
            "89001234567",
            1234,
            Temps(userphone=89001234567, smscode=1234),
            Auth(userphone=89001234567, smscode=1234),
        ),
        (
            89001234567,
            "1234",
            Temps(userphone=89001234567, smscode=1234),
            Auth(userphone=89001234567, smscode=1234),
        ),
        (
            89001234567,
            1234,
            Temps(userphone=89001234567, smscode=1234),
            Auth(userphone=89001234567, smscode=1234),
        ),
        (
            89001234567,
            1234,
            None,
            None,
        ),
    ),
)
def test_get_auth_by_phone_and_code(
    phone: Union[int, str],
    code: Union[int, str],
    mock: Temps,
    expected: Auth,
    mocker: MockerFixture,
):
    mocker.patch.object(Storage, "auth_by_phone_and_code", return_value=mock)
    users = Users()

    auth = users.get_auth_by_phone_and_code(phone, code)

    assert auth == expected
