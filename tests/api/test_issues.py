from flask.testing import FlaskClient
from pytest_mock import MockerFixture

from smartyard.logic.user import User
from smartyard.logic.users import Users


def test_action(
    flask_client: FlaskClient, logic_user: User, mocker: MockerFixture
) -> None:
    mocker.patch.object(Users, "user_by_uuid", return_value=logic_user)
    response = flask_client.post(
        "/api/issues/action",
        headers={"Authorization": "auth"},
        json={"1": "1"},
        content_type="application/json",
    )
    assert response.status_code == 200


def test_comment(
    flask_client: FlaskClient, logic_user: User, mocker: MockerFixture
) -> None:
    mocker.patch.object(Users, "user_by_uuid", return_value=logic_user)
    response = flask_client.post(
        "/api/issues/comment",
        headers={"Authorization": "auth"},
        json={"1": "1"},
        content_type="application/json",
    )
    assert response.status_code == 200


def test_create(
    flask_client: FlaskClient, logic_user: User, mocker: MockerFixture
) -> None:
    mocker.patch.object(Users, "user_by_uuid", return_value=logic_user)
    response = flask_client.post(
        "/api/issues/create",
        headers={"Authorization": "auth"},
        json={"1": "1"},
        content_type="application/json",
    )
    assert response.status_code == 200


def test_list_connect(
    flask_client: FlaskClient, logic_user: User, mocker: MockerFixture
) -> None:
    mocker.patch.object(Users, "user_by_uuid", return_value=logic_user)
    response = flask_client.post(
        "/api/issues/listConnect",
        headers={"Authorization": "auth"},
        json={"1": "1"},
        content_type="application/json",
    )
    assert response.status_code == 204
    assert response.content_type == "application/json"
