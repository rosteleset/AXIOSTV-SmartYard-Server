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


@app.route('/api/sip/helpMe', methods=['POST'])
def sip_helpMe():
    access_verification(request.headers)
    if not request.get_json():
        abort (422, {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'})
    request_data = request.get_json()
    return "Hello, World!"

@app.route('/api/user/addMyPhone', methods=['POST'])
def user_addMyPhone():
    access_verification(request.headers)
    if not request.get_json():
        abort (422, {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'})
    request_data = request.get_json()
    if not 'login' in request_data or not 'password' in request_data:
        abort (422, {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'})
    login = request_data['login']
    password = request_data['password']
    if 'comment' in request_data:
        comment = request_data['comment']
    if 'notification' in request_data:
        notification = request_data['notification']
    return app.response_class(status=204, mimetype='application/json')

@app.route('/api/user/appVersion', methods=['POST'])
def user_appVersion():
    access_verification(request.headers)
    if not request.get_json():
        abort (422, {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'})
    request_data = request.get_json()
    if not 'version' in request_data or not 'platform' in request_data:
        abort (422, {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'})
    version = request_data['version']
    platform = request_data['platform']
    if  version != None and (platform == 'android' or platform == 'ios'):
        return jsonify({'code':200,'name':'OK','message':'Хорошо','data':'upgrade'})
    else:
        abort (422, {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'})

@app.route('/api/user/confirmCode', methods=['POST'])
def user_confirmCode():
    if not request.get_json():
        abort(422, {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'})
    request_data = request.get_json()
    if (not 'userPhone' in request_data) or len(request_data['userPhone'])!=11 or (not 'smsCode' in request_data) or len(request_data['smsCode'])!=4:
        abort(422, {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'})
    userPhone = request_data['userPhone']
    if not db.session.query(db.session.query(Temps).filter_by(userphone=int(userPhone)).exists()).scalar():
        abort(404, {"code":404,"name":"Not Found","message":"Не найдено"})
    smsCode = request_data['smsCode']
    if not db.session.query(db.exists().where(Temps.userphone==int(userPhone) and Temps.smscode == int(smsCode))).scalar():
        abort(403, {"code":403,"name":"Пин-код введен неверно","message":"Пин-код введен неверно"})
    accessToken = str(uuid.uuid4())
    if not 'name' in request_data:
        request_data['name'] = None
    if not 'patronymic' in request_data:
        request_data['patronymic'] = None
    if not 'email' in request_data:
        request_data['email'] = None
    if db.session.query(db.session.query(Users).filter_by(userphone=int(userPhone)).exists()).scalar():
        db.session.query(Users).filter_by(userphone=int(userPhone)).update({'uuid' : accessToken})
    else:
        new_user = Users(uuid = accessToken, userphone = int(request_data['userPhone']), name = request_data['name'], patronymic = request_data['patronymic'], email = request_data['email'])
        db.session.add(new_user)
    db.session.query(Temps).filter_by(userphone=int(userPhone)).delete()
    db.session.commit()
    return jsonify({
        'code':200,
        'name':'OK',
        'message':'Хорошо',
        'data': {
            'accessToken': accessToken,
            'names': {
                'name': request_data['name'],
                'patronymic': request_data['patronymic']
            }
        }
    })

@app.route('/api/user/getPaymentsList', methods=['POST'])
def user_getPaymentsList():
    phone = access_verification(request.headers)
    response = requests.post(billing_url + "getlist", headers={'Content-Type':'application/json'}, data=json.dumps({'phone': phone})).json()
    return jsonify(response)

@app.route('/api/user/notification', methods=['POST'])
def user_notification():
    access_verification(request.headers)
    money = 't'
    enable = 't'
    return jsonify({'code':200,'name':'OK','message':'Хорошо','data':{'money':money,'enable':enable}})

@app.route('/api/user/ping', methods=['POST'])
def user_ping():
    access_verification(request.headers)
    return app.response_class(status=204, mimetype='application/json')

@app.route('/api/user/pushTokens', methods=['POST'])
def user_pushTokens():
    access_verification(request.headers)
    return jsonify({
        'code':200,
        'name':'OK',
        'message':'Хорошо',
        'data': {
            'pushToken':'fnTGJUfJTIC61WfSKWHP_N:APA91bGbnS3ck-cEWO0aj4kExZLsmGGmhziTu2lfyvjIpbmia5ahfL4WlJrr8DOjcDMUo517HUjxH4yZm0m5tF89CssdSsmO6IjcrS1U_YM3ue2187rc9ow9rS0xL8Q48vwz2e6j42l1',
            'voipToken':'off'
        }
    })

@app.route('/api/user/registerPushToken', methods=['POST'])
def user_registerPushToken():
    access_verification(request.headers)
    if not request.get_json():
        abort (422, {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'})
    request_data = request.get_json()
    if not 'platform' in request_data:
        abort (422, {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'})
    platform = request_data['platform']
    if 'pushToken' in request_data:
        pushToken = request_data['pushToken']
    if 'voipToken' in request_data:
        voipToken = request_data['voipToken']
    if 'production' in request_data:
        production = request_data['production']
    return app.response_class(status=204, mimetype='application/json')

@app.route('/api/user/requestCode', methods=['POST'])
def user_requestCode():
    if not request.get_json():
        abort (422,
               {
                   'code':422,
                   'name':'Unprocessable Entity',
                   'message':'Необрабатываемый экземпляр'
                })
    request_data = request.get_json()
    if (not 'userPhone' in request_data) or len(request_data['userPhone'])!=11:
        abort (422,
               {
                   'code':422,
                   'name':'Unprocessable Entity',
                   'message':'Необрабатываемый экземпляр'
                })
    sms_code = int(str(randint(1, 9)) + str(randint(0, 9)) + str(randint(0, 9)) + str(randint(0, 9)))
    sms_text = os.getenv('KANNEL_TEXT') + str(sms_code)
    user_phone = int(request_data['userPhone'])
    temp_user = Temps(userphone=user_phone, smscode=sms_code)
    #db.session.query(Temps).filter_by(userphone=int(user_phone)).delete()
    db.session.add(temp_user)
    db.session.commit()
    kannel_params2 = (('to', user_phone), ('text', sms_text.encode('utf-16-be').decode('utf-8').upper()))
    try:
        response = requests.get(url=kannel_url, params=kannel_params + kannel_params2)
        response.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')
    else:
        print(f'Success send sms to {user_phone} and text {sms_text}!')
    return app.response_class(status=204, mimetype='application/json')

@app.route('/api/user/restore', methods=['POST'])
def user_restore():
    access_verification(request.headers)
    if not request.get_json():
        abort (422,
               {
                   'code':422,
                   'name':'Unprocessable Entity',
                   'message':'Необрабатываемый экземпляр'
                })
    request_data = request.get_json()
    if not 'contract' in request_data:
        abort (422,
               {
                   'code':422,
                   'name':'Unprocessable Entity',
                   'message':'Необрабатываемый экземпляр'
                })
    contract = request_data['contract']
    if (not 'contactId' in request_data) and (not 'code' in request_data):
        return jsonify({
            'code':200,
            'name':'OK',
            'message':'Хорошо',
            'data': [
                {
                    'id':'bfe5bc9e5d2b2501767a7589ec3c485c',
                    'contact':'sb**@*********.ru',
                    'type':'email'
                },
                {
                    'id':'064601c186c73c5e47e8dedbab90dd11',
                    'contact':'8 (964) ***-*000','type':'phone'
                }
            ]
        })
    if 'contactId' in request_data and (not 'code' in request_data):
        contactId = request_data['contactId']
        print(f"Кто-то сделал POST запрос contactId и передал {contactId}")
        return app.response_class(status=204, mimetype='application/json')
    if (not 'contactId' in request_data) and 'code' in request_data:
        code = request_data['code']
        if code ==  code:
            print(f"Кто-то сделал POST запрос code и передал {code}")
            return app.response_class(status=204, mimetype='application/json')
        else:
            abort (403, {'code':403,'name':'Forbidden','message':'Запрещено'})
    if 'comment' in request_data:
        comment = request_data['comment']
    if 'notification' in request_data:
        notification = request_data['notification']

@app.route('/api/user/sendName', methods=['POST'])
def user_sendName():
    access_verification(request.headers)
    if not request.get_json():
        abort (422,
               {
                   'code':422,
                   'name':'Unprocessable Entity',
                   'message':'Необрабатываемый экземпляр'
                })
    request_data = request.get_json()
    if not 'name' in request_data:
        abort (422,
               {
                   'code':422,
                   'name':'Unprocessable Entity',
                   'message':'Необрабатываемый экземпляр'
                })
    name = request_data['name']
    if not 'patronymic' in request_data:
        request_data['patronymic'] = None
    return app.response_class(status=204, mimetype='application/json')

@app.route('/api/user/getBillingList', methods=['POST'])
def user_getBillingList():
    phone = access_verification(request.headers)
    sub_response = requests.post(billing_url + "getlist", headers={'Content-Type':'application/json'}, data=json.dumps({'phone': phone})).json()
    return jsonify(sub_response)

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
