"""Модуль тестирования API, ветка /api/geo"""

from flask.testing import FlaskClient
from pytest_mock import MockerFixture

from smartyard.logic.user import User
from smartyard.logic.users import Users


def test_address(
    flask_client: FlaskClient, logic_user: User, mocker: MockerFixture
) -> None:
    """Тест запроса адреса дома"""
    mocker.patch.object(Users, "user_by_uuid", return_value=logic_user)
    response = flask_client.post(
        "/api/geo/address",
        headers={"Authorization": "auth"},
        json={"1": "1"},
        content_type="application/json",
    )
    assert response.status_code == 200


def test_coder(
    flask_client: FlaskClient, logic_user: User, mocker: MockerFixture
) -> None:
    """Тест запроса гео координат дома"""
    mocker.patch.object(Users, "user_by_uuid", return_value=logic_user)
    response = flask_client.post(
        "/api/geo/coder",
        headers={"Authorization": "auth"},
        json={"1": "1"},
        content_type="application/json",
    )
    assert response.status_code == 200


def test_get_all_locations(
    flask_client: FlaskClient, logic_user: User, mocker: MockerFixture
) -> None:
    """Тест запроса населенных пунктов"""
    mocker.patch.object(Users, "user_by_uuid", return_value=logic_user)
    response = flask_client.post(
        "/api/geo/getAllLocations",
        headers={"Authorization": "auth"},
        json={"1": "1"},
        content_type="application/json",
    )
    assert response.status_code == 200


def test_get_all_services(
    flask_client: FlaskClient, logic_user: User, mocker: MockerFixture
) -> None:
    """Тест запроса всех услуг"""
    mocker.patch.object(Users, "user_by_uuid", return_value=logic_user)
    response = flask_client.post(
        "/api/geo/getAllServices",
        headers={"Authorization": "auth"},
        json={"1": "1"},
        content_type="application/json",
    )
    assert response.status_code == 200


def test_get_houses(
    flask_client: FlaskClient, logic_user: User, mocker: MockerFixture
) -> None:
    """Тест запроса списка домов"""
    mocker.patch.object(Users, "user_by_uuid", return_value=logic_user)
    response = flask_client.post(
        "/api/geo/getHouses",
        headers={"Authorization": "auth"},
        json={"1": "1"},
        content_type="application/json",
    )
    assert response.status_code == 200


def test_get_services(
    flask_client: FlaskClient, logic_user: User, mocker: MockerFixture
) -> None:
    """Тест запроса доступных услуг"""
    mocker.patch.object(Users, "user_by_uuid", return_value=logic_user)
    response = flask_client.post(
        "/api/geo/getServices",
        headers={"Authorization": "auth"},
        json={"1": "1"},
        content_type="application/json",
    )
    assert response.status_code == 200


def test_get_streets(
    flask_client: FlaskClient, logic_user: User, mocker: MockerFixture
) -> None:
    """Тест запроса списка улиц"""
    mocker.patch.object(Users, "user_by_uuid", return_value=logic_user)
    response = flask_client.post(
        "/api/geo/getStreets",
        headers={"Authorization": "auth"},
        json={"1": "1"},
        content_type="application/json",
    )
    assert response.status_code == 200
