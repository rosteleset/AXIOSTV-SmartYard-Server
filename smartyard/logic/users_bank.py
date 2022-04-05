"""Модуль работы с пользователями сервиса"""
import uuid
from datetime import datetime
from random import randint
from typing import Iterable

from smartyard.db import Temps, Users, create_db_connection
from smartyard.exceptions import NotFoundCodeAndPhone, NotFoundCodesForPhone


class UsersBank:
    """Класс работы с пользователями сервиса"""

    def __init__(self) -> None:
        pass

    def save_user(
        self, user_phone: int, sms_code: int, name: str, patronymic: str, email: str
    ) -> str:
        """Создать или обновить пользователя

        Параметры:
        - user_phone - номер телефона в целочисленном виде
        - sms_code - код аутентификации в целочисленном виде
        - name - имя пользователя
        - patronymic - отчество пользователя
        - email - электронный адрес пользователя
        """
        datebase = create_db_connection()
        phone_codes = datebase.session.query(Temps).filter_by(userphone=int(user_phone))
        with_sms_code = [code for code in phone_codes if code.sms_code == sms_code]

        if not phone_codes:
            raise NotFoundCodesForPhone(user_phone)

        if not with_sms_code:
            raise NotFoundCodeAndPhone(user_phone, sms_code)

        access_token = str(uuid.uuid4())
        if datebase.session.query(
            datebase.session.query(Users).filter_by(userphone=int(user_phone)).exists()
        ).scalar():
            datebase.session.query(Users).filter_by(userphone=int(user_phone)).update(
                {"uuid": access_token}
            )
        else:
            new_user = Users(
                uuid=access_token,
                userphone=int(user_phone),
                name=name,
                patronymic=patronymic,
                email=email,
                videotoken=None,
                vttime=None,
                strims=None,
            )
            datebase.session.add(new_user)
        datebase.session.query(Temps).filter_by(userphone=int(user_phone)).delete()
        datebase.session.commit()

        return access_token
