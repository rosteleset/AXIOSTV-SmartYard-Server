"""Модуль бизнес-логики работы с пользователями"""
import dataclasses
import uuid as std_uuid
from typing import Union
from random import randint

from smartyard import db
from smartyard.logic.auth import Auth
from smartyard.logic.user import User


class Users:
    """Бизнес-логика работы с пользователями системы: сохранение, поиск и сохранение"""

    def __init__(self) -> None:
        pass

    def user_by_uuid(self, _uuid: Union[str, std_uuid.UUID]) -> User:
        """Поиск пользователя по uuid пользователя

        Параметры:
        - uuid - идентификатор пользователя
        """
        _uuid = std_uuid.UUID(_uuid) if not isinstance(_uuid, std_uuid.UUID) else _uuid
        user = db.Storage().user_by_uuid(_uuid)
        return User(**user.as_dict()) if user else None

    def user_by_phone(self, phone: Union[int, str]) -> User:
        """Поиск пользователя по номеру телефона

        Параметры:
        - phone - номер телефона
        """
        phone = int(phone) if not isinstance(phone, int) else phone
        user = db.Storage().user_by_phone(phone)
        return User(**user.as_dict()) if user else None

    def user_by_video_token(self, token: str) -> User:
        """Поиск пользователя по номеру телефона

        Параметры:
        - token - уникальный идентификатор для доступа к видеопотокам
        """
        user = db.Storage().user_by_video_token(token)
        return User(**user.as_dict()) if user else None

    def save_user(self, user: User) -> User:
        """Сохранение пользователя в базе

        Параметры:
        - user - пользователь
        """
        _user = db.Users(**dataclasses.asdict(user))
        return User(**db.Storage().save(_user).as_dict())

    def set_auth_code(self, phone: Union[int, str]) -> Auth:
        """Сохранение в базе кода аутентификации

        Параметры:
        - phone - номер телефона
        """
        storage = db.Storage()
        storage.clear_codes_for_phone(phone)
        auth = db.Temps(userphone=int(phone), smscode=randint(1000, 9999))
        return Auth(**storage.save(auth).as_dict())

    def get_auth_by_phone_and_code(self, phone: Union[int, str], code: Union[int, str]) -> Auth:
        """Проверка(поиск) кода авторизации с учетом номера телефона

        Параметры:
        - phone - номер телефона
        - code - код для SMS
        """
        auth = db.Storage().auth_by_phone_and_code(phone=phone, code=code)
        return Auth(**auth.as_dict()) if auth else None
