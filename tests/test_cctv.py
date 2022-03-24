import os

import pytest
from flask import Flask
from flask.testing import FlaskClient
from pytest_mock import MockerFixture

from smartyard import create_app
from smartyard.config import get_config
from smartyard.logic.users_bank import UsersBank


@pytest.fixture
def env_file() -> str:
    return os.path.join(os.path.dirname(__file__), "data", "test.env")


@pytest.fixture
def app(env_file) -> Flask:
    app, _ = create_app(get_config(env_file))
    app.config.update(
        {
            "TESTING": True,
        }
    )
    yield app


@pytest.fixture
def client(app) -> FlaskClient:
    return app.test_client()


def test_all(client: FlaskClient, mocker: MockerFixture) -> None:
    mocker.patch.object(UsersBank, "search_by_uuid", return_value=(79001234567,))
    mocker.patch.object(UsersBank, "update_video_token", return_value=None)
    response = client.post(
        "/api/cctv/all",
        headers={"Authorization": "auth"},
        json={"1": "1"},
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert response.get_json()


def test_cam_map(client: FlaskClient, mocker: MockerFixture) -> None:
    mocker.patch.object(UsersBank, "search_by_uuid", return_value=(79001234567,))
    response = client.post("/api/cctv/camMap", headers={"Authorization": "auth"})
    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert response.get_json()


def test_overview(client: FlaskClient, mocker: MockerFixture) -> None:
    mocker.patch.object(UsersBank, "search_by_uuid", return_value=(79001234567,))
    response = client.post(
        "/api/cctv/overview",
        headers={"Authorization": "auth"},
        json={"1": "1"},
        content_type="application/json",
    )
    assert response.status_code == 200


def test_rec_download(client: FlaskClient, mocker: MockerFixture) -> None:
    mocker.patch.object(UsersBank, "search_by_uuid", return_value=(79001234567,))
    response = client.post(
        "/api/cctv/recDownload",
        headers={"Authorization": "auth"},
        json={"1": "1"},
        content_type="application/json",
    )
    assert response.status_code == 200


def test_rec_prepare(client: FlaskClient, mocker: MockerFixture) -> None:
    mocker.patch.object(UsersBank, "search_by_uuid", return_value=(79001234567,))
    response = client.post(
        "/api/cctv/recPrepare",
        headers={"Authorization": "auth"},
        json={"1": "1"},
        content_type="application/json",
    )
    assert response.status_code == 200


def test_youtube(client: FlaskClient, mocker: MockerFixture) -> None:
    mocker.patch.object(UsersBank, "search_by_uuid", return_value=(79001234567,))
    response = client.post(
        "/api/cctv/youtube",
        headers={"Authorization": "auth"},
        json={"1": "1"},
        content_type="application/json",
    )
    assert response.status_code == 200
