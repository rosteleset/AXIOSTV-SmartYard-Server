import secrets
from typing import Iterable

from flask import abort

from smartyard.logic.users_bank import UsersBank


def access_verification(headers):
    auth_key = headers.get("Authorization")
    if not auth_key:
        abort(
            422,
            {
                "code": 422,
                "name": "Отсутствует токен авторизации",
                "message": "Отсутствует токен авторизации",
            },
        )
    user = UsersBank().search_by_uuid(auth_key[7:])
    if not user:
        abort(401, {"code": 401, "name": "Не авторизован", "message": "Не авторизован"})
    return user[0]


def json_verification(input_json):
    if not input_json:
        abort(
            422,
            {
                "code": 422,
                "name": "Unprocessable Entity",
                "message": "Необрабатываемый экземпляр",
            },
        )


def generate_video_token(user_phone: int, strims: Iterable) -> str:
    token = secrets.token_hex(16)
    UsersBank().update_video_token(user_phone, token, strims)
    return token
