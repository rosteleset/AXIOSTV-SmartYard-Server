import uuid
from datetime import datetime
from random import randint
from typing import Iterable

from smartyard.db import Temps, Users, create_db_connection
from smartyard.exceptions import NotFoundCodeAndPhone, NotFoundCodesForPhone


class UsersBank:
    def __init__(self) -> None:
        pass

    def search_by_uuid(self, uuid: str) -> int:
        db = create_db_connection()
        return db.session.query(Users.userphone).filter_by(uuid=uuid).first()

    def save_user(
        self, user_phone: int, sms_code: int, name: str, patronymic: str, email: str
    ) -> str:
        db = create_db_connection()
        phone_codes = db.session.query(Temps).filter_by(userphone=int(user_phone))
        with_sms_code = [code for code in phone_codes if code.sms_code == sms_code]

        if not phone_codes:
            raise NotFoundCodesForPhone(user_phone)

        if not with_sms_code:
            raise NotFoundCodeAndPhone(user_phone, sms_code)

        access_token = str(uuid.uuid4())
        if db.session.query(
            db.session.query(Users).filter_by(userphone=int(user_phone)).exists()
        ).scalar():
            db.session.query(Users).filter_by(userphone=int(user_phone)).update(
                {"uuid": access_token}
            )
        else:
            new_user = Users(
                uuid=access_token,
                userphone=int(user_phone),
                name=name,
                patronymic=patronymic,
                email=email,
            )
            db.session.add(new_user)
        db.session.query(Temps).filter_by(userphone=int(user_phone)).delete()
        db.session.commit()

        return access_token

    def generate_code(self, user_phone: int):
        db = create_db_connection()
        sms_code = randint(1000, 9999)
        user_phone = user_phone
        temp_user = Temps(userphone=user_phone, smscode=sms_code)
        db.session.query(Temps).filter_by(
            userphone=int(user_phone)
        ).delete()  # перед этим добавить проверку на время и ответ ошибкой!
        db.session.add(temp_user)
        db.session.commit()

    def update_video_token(self, user_phone: int, token: str, strims: Iterable):
        db = create_db_connection()
        db.session.query(Users).filter_by(userphone=int(user_phone)).update(
            {"videotoken": token, "vttime": datetime.now(), "strims": strims}
        )
        db.session.commit()

    def get_users_by_videotoken(self, token: str):
        db = create_db_connection()
        return db.session.query(Users).where(Users.videotoken == token)
