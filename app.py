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

from smartyard.db import create_db_connection, Temps, Users
from smartyard.utils import access_verification
from smartyard.api.address import address_branch
from smartyard.api.cctv import cctv_branch
from smartyard.api.ext import ext_branch
from smartyard.api.frs import frs_branch
from smartyard.api.geo import geo_branch
from smartyard.api.inbox import inbox_branch
from smartyard.api.issues import issues_branch
from smartyard.api.pay import pay_branch
from smartyard.api.sip import sip_branch
from smartyard.api.user import user_branch


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




@app.route('/api/')
def index():
    return "Hello, World!"

app.register_blueprint(address_branch, url_prefix="/api")
app.register_blueprint(cctv_branch, url_prefix="/api")
app.register_blueprint(ext_branch, url_prefix="/api")
app.register_blueprint(frs_branch, url_prefix="/api")
app.register_blueprint(geo_branch, url_prefix="/api")
app.register_blueprint(inbox_branch, url_prefix="/api")
app.register_blueprint(issues_branch, url_prefix="/api")
app.register_blueprint(pay_branch, url_prefix="/api")
app.register_blueprint(sip_branch, url_prefix="/api")
app.register_blueprint(user_branch, url_prefix="/api")


@app.errorhandler(401)
def not_found(error):
    return make_response(jsonify(error), 401)

@app.errorhandler(403)
def not_found(error):
    return make_response(jsonify(error), 403)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'пользователь не найден'}), 404)

@app.errorhandler(410)
def not_found(error):
    return make_response(jsonify({'error': 'авторизация отозвана'}), 410)

@app.errorhandler(422)
def not_found(error):
    return make_response(jsonify(error), 422)

@app.errorhandler(424)
def not_found(error):
    return make_response(jsonify({'error': 'неверный токен'}), 424)

@app.errorhandler(429)
def not_found(error):
    return make_response(jsonify({'code':429,'name':'Too Many Requests','message':'Слишком много запросов'}), 429)

if __name__ == '__main__':
    app.run(debug=True)
