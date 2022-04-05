from flask.testing import FlaskClient
from pytest_mock import MockerFixture

from smartyard.logic.user import User
from smartyard.logic.users import Users


def test_dislike(
    flask_client: FlaskClient, logic_user: User, mocker: MockerFixture
) -> None:
    mocker.patch.object(Users, "user_by_uuid", return_value=logic_user)
    response = flask_client.post(
        "/api/frs/disLike",
        headers={"Authorization": "auth"},
        json={"1": "1"},
        content_type="application/json",
    )
    assert response.status_code == 200


def test_like(
    flask_client: FlaskClient, logic_user: User, mocker: MockerFixture
) -> None:
    mocker.patch.object(Users, "user_by_uuid", return_value=logic_user)
    response = flask_client.post(
        "/api/frs/like",
        headers={"Authorization": "auth"},
        json={"1": "1"},
        content_type="application/json",
    )
    assert response.status_code == 200


def test_list_faces(
    flask_client: FlaskClient, logic_user: User, mocker: MockerFixture
) -> None:
    mocker.patch.object(Users, "user_by_uuid", return_value=logic_user)
    response = flask_client.post(
        "/api/frs/listFaces",
        headers={"Authorization": "auth"},
        json={"1": "1"},
        content_type="application/json",
    )
    assert response.status_code == 200
