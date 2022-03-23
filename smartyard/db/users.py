import uuid

from sqlalchemy.dialects.postgresql import UUID

from smartyard.db.database import create_db_connection

_db = create_db_connection()


class Users(_db.Model):
    __tablename__ = "users"

    uuid = _db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    userphone = _db.Column(_db.BigInteger, index=True, unique=True)
    name = _db.Column(_db.String(24))
    patronymic = _db.Column(_db.String(24))
    email = _db.Column(_db.String(60))

    def __init__(self, uuid, userphone, name, patronymic, email):
        self.uuid = uuid
        self.userphone = userphone
        self.name = name
        self.patronymic = patronymic
        self.email = email

    def __repr__(self):
        return f""
