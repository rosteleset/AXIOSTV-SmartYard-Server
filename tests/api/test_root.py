import uuid
from datetime import datetime, timedelta

import pytest
from flask.testing import FlaskClient
from pytest_mock import MockerFixture

from smartyard.db.users import Users
from smartyard.logic.users_bank import UsersBank


@pytest.mark.parametrize(
    "token,stream,users,expected",
    (
        (
            "token",
            "stream",
            (
                Users(
                    uuid.uuid4(),
                    79001234567,
                    "User",
                    "",
                    "",
                    "token",
                    datetime.now() + timedelta(minutes=1),
                    ["stream"],
                ),
            ),
            {
                "status_code": 200,
            },
        ),
        (
            "token",
            "stream2",
            (
                Users(
                    uuid.uuid4(),
                    79001234567,
                    "User",
                    "",
                    "",
                    "token",
                    datetime.now() + timedelta(minutes=1),
                    ["stream", "stream2", "stream3"],
                ),
            ),
            {
                "status_code": 200,
            },
        ),
        (
            "token",
            "stream2",
            (
                Users(
                    uuid.uuid4(),
                    79001234567,
                    "User",
                    "",
                    "",
                    "token",
                    datetime.now() + timedelta(minutes=1),
                    ["stream"],
                ),
            ),
            {
                "status_code": 403,
                "content": {
                    "code": 403,
                    "name": "Forbidden",
                    "message": "Неверный токен",
                },
            },
        ),
        (
            "token",
            "stream",
            (),
            {
                "status_code": 403,
                "content": {
                    "code": 403,
                    "name": "Forbidden",
                    "message": "Неверный токен",
                },
            },
        ),
    ),
)
def test_accessfl(
    flask_client: FlaskClient,
    token: str,
    stream: str,
    users: tuple,
    expected: dict,
    mocker: MockerFixture,
) -> None:
    mocker.patch.object(UsersBank, "get_users_by_videotoken", return_value=users)
    response = flask_client.get(f"/api/accessfl?token={token}&name={stream}")
    assert response.status_code == expected.get("status_code")
    if expected.get("content"):
        assert response.get_json() == expected.get("content")
