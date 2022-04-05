"""Модуль работы с пользователем"""
import uuid as std_uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class User:
    """Класс для работы с пользователем

    Колонки:
    - userphone - номер телефона
    - name - имя пользователя
    - patronymic - отчество пользователя
    - email - электронная почта пользователя
    - uuid - идентификатор пользователя, опциональное поле
    - videotoken - токен для видео-потоков, опциональное поле
    - vttime - дата, до которой токен актуален, опциональное поле
    - strims - доступные видео-потоки, опциональное поле
    """

    userphone: int
    name: str
    patronymic: str
    email: str
    uuid: Optional[std_uuid.UUID] = None
    videotoken: Optional[str] = None
    vttime: Optional[datetime] = None
    strims: Optional[list] = None

    def set_values(self, **kwargs: dict) -> "User":
        """Обновить значение.
        Возвращает новый объект с новыми значениями

        Параметры:
        - kwargs - dict с новыми значениями полей"""
        values = {
            "userphone": self.userphone,
            "name": self.name,
            "patronymic": self.patronymic,
            "email": self.email,
            "uuid": self.uuid,
            "videotoken": self.videotoken,
            "vttime": self.vttime,
            "strims": self.strims,
        }
        kwargs = {key: item for key, item in kwargs.items() if key in values}
        values.update(kwargs)
        return User(**values)
