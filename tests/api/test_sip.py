"""Модуль тестирования API, ветка /api/sip"""

from flask.testing import FlaskClient
from pytest_mock import MockerFixture

from smartyard.logic.user import User
from smartyard.logic.users import Users


def test_help_me(
    flask_client: FlaskClient, logic_user: User, mocker: MockerFixture
) -> None:
    """Тест запроса звонка техническую поддержку"""
    mocker.patch.object(Users, "user_by_uuid", return_value=logic_user)
    response = flask_client.post(
        "/api/sip/helpMe",
        headers={"Authorization": "auth"},
        json={"1": "1"},
        content_type="application/json",
    )
    assert response.status_code == 200
