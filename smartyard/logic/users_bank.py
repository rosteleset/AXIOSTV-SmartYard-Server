from smartyard.db import Users, create_db_connection


class UsersBank:
    def __init__(self) -> None:
        pass

    def search_by_uuid(self, uuid: str) -> int:
        db = create_db_connection()
        return db.session.query(Users.userphone).filter_by(uuid=uuid).first()
