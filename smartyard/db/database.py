"""Модуль для работы с подключением к базе данных"""
import functools

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class BaseModel:
    """Класс дополнительных функций для работы с моделями в базе данных"""

    def as_dict(self) -> dict:
        """Конвертация модели(объекта) из базы в dict"""
        return {
            column.name: self.__dict__.get(column.name)
            for column in self.__table__.columns
        }


@functools.lru_cache(None)
def create_db_connection():
    """Создание объекта подключения к базе данных"""
    return SQLAlchemy()
