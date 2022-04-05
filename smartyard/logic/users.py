"""Модуль бизнес-логики работы с пользователями"""
import dataclasses
import secrets
import uuid as std_uuid
from random import randint
from typing import Iterable, Union

from smartyard import db
from smartyard.exceptions import NotFoundCodeAndPhone, NotFoundCodesForPhone
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

    def get_auth_by_phone_and_code(
        self, phone: Union[int, str], code: Union[int, str]
    ) -> Auth:
        """Проверка(поиск) кода авторизации с учетом номера телефона

        Параметры:
        - phone - номер телефона
        - code - код для SMS
        """
        auth = db.Storage().auth_by_phone_and_code(phone=phone, code=code)
        return Auth(**auth.as_dict()) if auth else None

    def update_video_token(self, user_phone: int, strims: Iterable) -> str:
        """Обновление данных о доступных видео-потоках

        Параметры:
        - user_phone - номер телефона в целочисленном виде
        - strims - названия доступных потоков
        """
        user = self.user_by_phone(user_phone)
        user = user.set_values(videotoken=secrets.token_hex(16), strims=strims)
        user = self.save_user(user)
        return user.videotoken

    def create_user(
        self, user_phone: int, sms_code: int, name: str, patronymic: str, email: str
    ):
        """Создать или обновить пользователя

        Параметры:
        - user_phone - номер телефона в целочисленном виде
        - sms_code - код аутентификации в целочисленном виде
        - name - имя пользователя
        - patronymic - отчество пользователя
        - email - электронный адрес пользователя
        """
        storage = db.Storage()
        phone_codes = storage.auth_by_phone(phone=user_phone)
        with_sms_code = [code for code in phone_codes if code.sms_code == sms_code]

        if not phone_codes:
            raise NotFoundCodesForPhone(user_phone)

        if not with_sms_code:
            raise NotFoundCodeAndPhone(user_phone, sms_code)

        user = storage.user_by_phone(user_phone)
        if not user:
            user = User(
                userphone=user_phone,
                name=name,
                patronymic=patronymic,
                email=email,
                uuid=std_uuid.uuid4(),
                videotoken=None,
                vttime=None,
                strims=None,
            )
        else:
            user = user.set_values(
                name=name,
                patronymic=patronymic,
                email=email,
            )

        user = self.save_user(user)
        return str(user.uuid)
