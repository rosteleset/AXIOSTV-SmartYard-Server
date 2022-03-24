from typing import Tuple

from flask import Flask
from flask_migrate import Migrate

from smartyard.api import api
from smartyard.config import Config
from smartyard.db import create_db_connection


def create_app(config: Config) -> Tuple[Flask, Migrate]:
    app = Flask(__name__)

    app.config.update(
        {
            "CONFIG": config,
            "JSON_AS_ASCII": False,
            "SQLALCHEMY_DATABASE_URI": (
                f"postgresql://{config.PG_USER}:{config.PG_PASS}@"
                f"{config.PG_HOST}:{config.PG_PORT}/{config.PG_DBNAME}"
            ),
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        }
    )

    db = create_db_connection()
    db.init_app(app)
    migrate = Migrate(app, db)

    app.register_blueprint(api)
    return app, migrate
