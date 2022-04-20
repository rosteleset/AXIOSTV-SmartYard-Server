"""Модуль описания таблицы пользователей сервиса"""
import uuid as std_uuid
from datetime import datetime
from typing import Iterable

from sqlalchemy import ARRAY, BigInteger, Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID

from smartyard.db.database import Base, BaseModel


class Users(Base, BaseModel):
    """Таблица с кодами для аутентификации

    Колонки:
    - uuid - идентификатор пользователя
    - userphone - номер телефона
    - name - имя пользователя
    - patronymic - отчество пользователя
    - email - электронная почта пользователя
    - videotoken - токен для видео-потоков
    - vttime - дата, до которой токен актуален
    - strims - доступные видео-потоки
    """

    __tablename__ = "users"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=std_uuid.uuid4)
    userphone = Column(BigInteger, index=True, unique=True)
    name = Column(String(24))
    patronymic = Column(String(24))
    email = Column(String(60))
    videotoken = Column(String(32))
    vttime = Column(DateTime(timezone=False))
    strims = Column(ARRAY(String(10)))

    def __init__(
        self,
        uuid: uuid,
        userphone: int,
        name: str,
        patronymic: str,
        email: str,
        videotoken: str,
        vttime: datetime,
        strims: Iterable,
    ):
        self.uuid = uuid
        self.userphone = userphone
        self.name = name
        self.patronymic = patronymic
        self.email = email
        self.videotoken = videotoken
        self.vttime = vttime
        self.strims = strims

    def __eq__(self, _users: object) -> bool:
        return (
            self.uuid == _users.uuid
            and self.userphone == _users.userphone
            and self.name == _users.name
            and self.patronymic == _users.patronymic
            and self.email == _users.email
            and self.videotoken == _users.videotoken
            and self.vttime == _users.vttime
            and self.strims == _users.strims
        )
