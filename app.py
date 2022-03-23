#!bin/python
import random, uuid, os, json, requests, binascii
from random import randint
from flask import Flask, jsonify, request, make_response, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import exists
from dotenv import load_dotenv
from requests.exceptions import HTTPError
import logging, sys

from smartyard.db import create_db_connection
from smartyard.api import api


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    print('not loaded .env file')
    exit()

app = Flask(__name__)

app.config['JSON_AS_ASCII'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://" + os.getenv('PG_USER') + ":" + os.getenv('PG_PASS') + "@" + os.getenv("PG_HOST") + ":5432/" + os.getenv('PG_DBNAME')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = create_db_connection()
db.init_app(app)
migrate = Migrate(app, db)

kannel_url = "http://%s:%d/cgi-bin/sendsms" % (os.getenv('KANNEL_HOST'), int(os.getenv('KANNEL_PORT')))
kannel_params = (('user', os.getenv('KANNEL_USER')), ('pass', os.getenv('KANNEL_PASS')), ('from', os.getenv('KANNEL_FROM')), ('coding', '2'))
billing_url=os.getenv('BILLING_URL')

app.register_blueprint(api)

if __name__ == '__main__':
    app.run(debug=True)
