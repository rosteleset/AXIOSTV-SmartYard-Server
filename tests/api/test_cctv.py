"""Модуль тестирования API, ветка /api/cctv"""

from flask.testing import FlaskClient
from pytest_mock import MockerFixture

from smartyard.logic.user import User
from smartyard.logic.users import Users


def test_all(
    flask_client: FlaskClient, logic_user: User, mocker: MockerFixture
) -> None:
    """Тест запроса списка камер"""
    mocker.patch.object(Users, "user_by_uuid", return_value=logic_user)
    response = flask_client.post(
        "/api/cctv/all",
        headers={"Authorization": "auth"},
        json={"1": "1"},
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert response.get_json()


def test_cam_map(
    flask_client: FlaskClient, logic_user: User, mocker: MockerFixture
) -> None:
    """Тест запроса привязки домофонов и камер"""
    mocker.patch.object(Users, "user_by_uuid", return_value=logic_user)
    response = flask_client.post("/api/cctv/camMap", headers={"Authorization": "auth"})
    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert response.get_json()


def test_overview(
    flask_client: FlaskClient, logic_user: User, mocker: MockerFixture
) -> None:
    """Тест запроса списка видовых камер"""
    mocker.patch.object(Users, "user_by_uuid", return_value=logic_user)
    response = flask_client.post(
        "/api/cctv/overview",
        headers={"Authorization": "auth"},
        json={"1": "1"},
        content_type="application/json",
    )
    assert response.status_code == 200


def test_rec_download(
    flask_client: FlaskClient, logic_user: User, mocker: MockerFixture
) -> None:
    """Тест запроса ссылки для скачивания из архива"""
    mocker.patch.object(Users, "user_by_uuid", return_value=logic_user)
    response = flask_client.post(
        "/api/cctv/recDownload",
        headers={"Authorization": "auth"},
        json={"1": "1"},
        content_type="application/json",
    )
    assert response.status_code == 200


def test_rec_prepare(
    flask_client: FlaskClient, logic_user: User, mocker: MockerFixture
) -> None:
    """Тест запроса подготовки фрагмента из архива"""
    mocker.patch.object(Users, "user_by_uuid", return_value=logic_user)
    response = flask_client.post(
        "/api/cctv/recPrepare",
        headers={"Authorization": "auth"},
        json={"1": "1"},
        content_type="application/json",
    )
    assert response.status_code == 200


def test_youtube(
    flask_client: FlaskClient, logic_user: User, mocker: MockerFixture
) -> None:
    """Тест запроса списка роликов на YouTube"""
    mocker.patch.object(Users, "user_by_uuid", return_value=logic_user)
    response = flask_client.post(
        "/api/cctv/youtube",
        headers={"Authorization": "auth"},
        json={"1": "1"},
        content_type="application/json",
    )
    assert response.status_code == 200
