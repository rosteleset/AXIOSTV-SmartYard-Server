"""Модуль описания таблицы, хранящей коды аутентификации"""
from smartyard.db.database import BaseModel, create_db_connection

_db = create_db_connection()


class Temps(_db.Model, BaseModel):
    """Таблица с кодами для аутентификации

    Колонки:
    - userphone - номер телефона
    - smscode - код для SMS
    """

    __tablename__ = "temps"

    userphone = _db.Column(_db.BigInteger, primary_key=True)
    smscode = _db.Column(_db.Integer, index=True, unique=True)

    def __init__(self, userphone, smscode):
        self.userphone = userphone
        self.smscode = smscode
