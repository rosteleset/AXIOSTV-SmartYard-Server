import pytest
from flask.testing import FlaskClient
from pytest_mock import MockerFixture

from smartyard.logic.users_bank import UsersBank


endpoints = {
    ("post", "/api/address/access"),
    ("post", "/api/address/getAddressList"),
    ("post", "/api/address/getSettingsList"),
    ("post", "/api/address/intercom"),
    ("post", "/api/address/offices"),
    ("post", "/api/address/openDoor"),
    ("post", "/api/address/plog"),
    ("post", "/api/address/plogDays"),
    ("post", "/api/address/registerQR"),
    ("post", "/api/address/resend"),
    ("post", "/api/address/resetCode"),
    ("post", "/api/address/getHcsList"),
    ("post", "/api/cctv/all"),
    ("post", "/api/cctv/camMap"),
    ("post", "/api/cctv/overview"),
    ("post", "/api/cctv/recDownload"),
    ("post", "/api/cctv/recPrepare"),
    ("post", "/api/cctv/youtube"),
    ("post", "/api/ext/ext"),
    ("post", "/api/ext/list"),
    ("post", "/api/frs/disLike"),
    ("post", "/api/frs/like"),
    ("post", "/api/frs/listFaces"),
    ("post", "/api/geo/address"),
    ("post", "/api/geo/coder"),
    ("post", "/api/geo/getAllLocations"),
    ("post", "/api/geo/getAllServices"),
    ("post", "/api/geo/getHouses"),
    ("post", "/api/geo/getServices"),
    ("post", "/api/geo/getStreets"),
    ("post", "/api/inbox/alert"),
    ("post", "/api/inbox/chatReaded"),
    ("post", "/api/inbox/delivered"),
    ("post", "/api/inbox/inbox"),
    ("post", "/api/inbox/readed"),
    ("post", "/api/inbox/unreaded"),
    ("post", "/api/issues/action"),
    ("post", "/api/issues/comment"),
    ("post", "/api/issues/create"),
    ("post", "/api/issues/listConnect"),
    ("post", "/api/pay/prepare"),
    ("post", "/api/pay/process"),
    ("post", "/api/sip/helpMe"),
    ("post", "/api/user/addMyPhone"),
    ("post", "/api/user/appVersion"),
    ("post", "/api/user/getPaymentsList"),
    ("post", "/api/user/notification"),
    ("post", "/api/user/ping"),
    ("post", "/api/user/pushTokens"),
    ("post", "/api/user/registerPushToken"),
    ("post", "/api/user/restore"),
    ("post", "/api/user/sendName"),
    ("post", "/api/user/getBillingList"),
}


@pytest.mark.parametrize("method,url", endpoints)
def test_with_auth_without_authorization(
    flask_client: FlaskClient, method: str, url: str
) -> None:
    response = flask_client.open(url, method=method.upper())
    assert response.status_code == 422
    assert response.content_type == "application/json"
    assert response.get_json() == {
        "code": 422,
        "name": "Отсутствует токен авторизации",
        "message": "Отсутствует токен авторизации",
    }


@pytest.mark.parametrize("method,url", endpoints)
def test_with_auth_with_wrong_token(
    flask_client: FlaskClient, method: str, url: str, mocker: MockerFixture
) -> None:
    mocker.patch.object(UsersBank, "search_by_uuid", return_value=None)
    response = flask_client.open(
        url, method=method.upper(), headers={"Authorization": "auth"}
    )
    assert response.status_code == 401
    assert response.content_type == "application/json"
    assert response.get_json() == {
        "code": 401,
        "name": "Не авторизован",
        "message": "Не авторизован",
    }
