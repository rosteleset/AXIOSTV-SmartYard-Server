"""Модуль работы с пользователем"""
import uuid as std_uuid
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


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
    strims: Optional[List[str]] = None

    def set_values(
        self,
        userphone: Optional[int] = None,
        name: Optional[str] = None,
        patronymic: Optional[str] = None,
        email: Optional[str] = None,
        uuid: Optional[std_uuid.UUID] = None,
        videotoken: Optional[str] = None,
        vttime: Optional[datetime] = None,
        strims: Optional[List[str]] = None,
    ) -> "User":
        """Обновить значение.
        Возвращает новый объект с новыми значениями

        Параметры:
        - kwargs - dict с новыми значениями полей"""
        return User(
            userphone=userphone or self.userphone,
            name=name or self.name,
            patronymic=patronymic or self.patronymic,
            email=email or self.email,
            uuid=uuid or self.uuid,
            videotoken=videotoken or self.videotoken,
            vttime=vttime or self.vttime,
            strims=strims or self.strims,
        )
