"""Модуль описания таблицы пользователей сервиса"""
import uuid as std_uuid
from datetime import datetime
from typing import Iterable

from sqlalchemy.dialects.postgresql import UUID

from smartyard.db.database import BaseModel, create_db_connection

_db = create_db_connection()


class Users(_db.Model, BaseModel):
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

    uuid = _db.Column(UUID(as_uuid=True), primary_key=True, default=std_uuid.uuid4)
    userphone = _db.Column(_db.BigInteger, index=True, unique=True)
    name = _db.Column(_db.String(24))
    patronymic = _db.Column(_db.String(24))
    email = _db.Column(_db.String(60))
    videotoken = _db.Column(_db.String(32))
    vttime = _db.Column(_db.DateTime(timezone=False))
    strims = _db.Column(_db.ARRAY(_db.String(10)))

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
