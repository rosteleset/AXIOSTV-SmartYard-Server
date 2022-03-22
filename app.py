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

@app.route('/api/address/access', methods=['POST'])
def address_access():
    access_verification(request.headers)
    if not request.get_json():
        abort (422, {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'})
    request_data = request.get_json()
    if not 'guestPhone' in request_data:
        abort (422, {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'})
    guestPhone = request_data['guestPhone']
    if not 'flatId' in request_data:
        abort (422, {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'})
    flatId = request_data['flatId']
    if not 'clientId' in request_data:
        abort (422, {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'})
    clientId = request_data['clientId']
    if not 'expire' in request_data:
        abort (422, {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'})
    expire = request_data['expire']
    return app.response_class(status=204, mimetype='application/json')

@app.route('/api/address/getAddressList', methods=['POST'])
def address_getAddressList():
    access_verification(request.headers)
    return jsonify({
        'code':200,
        'name':'OK',
        'message':'Хорошо',
        'data': [
            {
                'houseId':'19260',
                'address':'Тамбов, ул. Верховая, дом 17',
                'hasPlog':'t',
                'doors': [
                    {
                        'domophoneId':'343',
                        'doorId':0,
                        'entrance':'1',
                        'icon':'entrance',
                        'name':'Подъезд'
                    },
                    {
                        'domophoneId':'70',
                        'doorId':0,
                        'entrance':'1',
                        'icon':'entrance',
                        'name':'Подъезд 1'
                    },
                    {
                        'domophoneId':'124',
                        'doorId':0,
                        'icon':'entrance',
                        'name':'Подъезд 2'
                    }
                ],
                'cctv':2
            },
            {
                'houseId':'6694',
                'address':'Тамбов, ул. Пионерская, дом 5\'б\'',
                'hasPlog':'t',
                'doors': [
                    {
                        'domophoneId':'79',
                        'doorId':0,
                        'entrance':'3',
                        'icon':'entrance',
                        'name':'Подъезд'
                    },
                    {
                        'domophoneId':'75',
                        'doorId':0,
                        'icon':'wicket',
                        'name':'Калитка'
                    },
                    {
                        'domophoneId':'297',
                        'doorId':0,
                        'icon':'wicket',
                        'name':'Калитка доп'
                    },
                    {
                        'domophoneId':'131',
                        'doorId':0,
                        'icon':'gate',
                        'name':'Ворота'
                    }
                ],
                'cctv':14
            }
        ]
    })

@app.route('/api/address/getSettingsList', methods=['POST'])
def address_getSettingsList():
    access_verification(request.headers)
    return jsonify({
        'code':200,
        'name':'OK',
        'message':'Хорошо',
        'data': [
            {
                'hasPlog':'t',
                'contractName':'ФЛ-85973\/20',
                'clientId':'91052',
                'contractOwner':'t',
                'clientName':'Бивард-00011 (Чемодан 2)',
                'services': ['internet', 'cctv', 'domophone'],
                'lcab':'https:\/\/lc.lanta.me\/?auth=Zjg1OTczOmY5NzkzNTQzM2U5YmQ5ZThkYTJiZmU2MWMwNDlkZGMy',
                'houseId':'19260',
                'flatId':'136151',
                'flatNumber':'1',
                'flatOwner':'t',
                'address':'Тамбов, ул. Верховая, дом 17, кв 1',
                'hasGates':'f',
                'roommates': [
                    {
                        'phone':'79051202936',
                        'expire':'3001-01-01 00:00:00',
                        'type':'inner'
                    },
                    {
                        'phone':'79106599009',
                        'expire':'3001-01-01 00:00:00',
                        'type':'inner'
                    },
                    {
                        'phone':'79156730435',
                        'expire':'3001-01-01 00:00:00',
                        'type':'inner'
                    },
                    {
                        'phone':'79641340000',
                        'expire':'3000-01-01 00:00:00',
                        'type':'inner'
                    },
                    {
                        'phone':'79641340000',
                        'expire':'3001-01-01 00:00:00',
                        'type':'inner'
                    }
                ]
            },
            {
                'hasPlog':'t',
                'services':['cctv','domophone'],
                'houseId':'19260',
                'flatId':'136162',
                'flatNumber':'12',
                'flatOwner':'f',
                'address':'Тамбов, ул. Верховая, дом 17, кв 12',
                'hasGates':'f',
                'roommates': [
                    {
                        'phone':'79176194895',
                        'expire':'3001-01-01 00:00:00','type':'inner'
                    },
                    {
                        'phone':'79202313789',
                        'expire':'3001-01-01 00:00:00','type':'inner'
                    }
                ]
            },
            {
                'hasPlog':'t',
                'services': ['cctv', 'domophone'],
                'houseId':'6694',
                'flatId':'306',
                'flatNumber':'69',
                'flatOwner':'f',
                'address':'Тамбов, ул. Пионерская, дом 5\'б\', кв 69',
                'hasGates':'t',
                'roommates': [
                    {
                        'phone':'79069202020',
                        'expire':'3001-01-01 00:00:00',
                        'type':'inner'
                    },
                    {
                        'phone':'79641349232',
                        'expire':'3001-01-01 00:00:00',
                        'type':'inner'
                    },
                    {
                        'phone':'79091215044',
                        'expire':'3001-01-01 00:00:00',
                        'type':'inner'
                    },
                    {
                        'phone':'79127600769',
                        'expire':'3001-01-01 00:00:00',
                        'type':'inner'
                    },
                    {
                        'phone':'79106500155',
                        'expire':'3001-01-01 00:00:00',
                        'type':'inner'
                    },
                    {
                        'phone':'79514470944',
                        'expire':'3001-01-01 00:00:00',
                        'type':'inner'
                    },
                    {
                        'phone':'79107567265',
                        'expire':'3001-01-01 00:00:00',
                        'type':'inner'
                    },
                    {
                        'phone':'79203409810',
                        'expire':'3001-01-01 00:00:00',
                        'type':'inner'
                    },
                    {
                        'phone':'79227063593',
                        'expire':'3001-01-01 00:00:00',
                        'type':'inner'
                    },
                    {
                        'phone':'79220144401',
                        'expire':'3001-01-01 00:00:00',
                        'type':'inner'
                    },
                    {
                        'phone':'79114688286',
                        'expire':'3001-01-01 00:00:00',
                        'type':'inner'
                    },
                    {
                        'phone':'79661840298',
                        'expire':'3001-01-01 00:00:00',
                        'type':'inner'
                    },
                    {
                        'phone':'79641340000',
                        'expire':'3001-01-01 00:00:00',
                        'type':'owner'
                    },
                    {
                        'phone':'79275807272',
                        'expire':'3001-01-01 00:00:00',
                        'type':'inner'
                    },
                    {
                        'phone':'79107567249',
                        'expire':'3001-01-01 00:00:00',
                        'type':'inner'
                    }
                ]
            },
            {
                'hasPlog':'t',
                'services': ['cctv', 'domophone'],
                'houseId':'6694',
                'flatId':'307',
                'flatNumber':'70',
                'flatOwner':'f',
                'address':'Тамбов, ул. Пионерская, дом 5\'б\', кв 70','hasGates':'t'
            }
        ]
    })

@app.route('/api/address/intercom', methods=['POST'])
def address_intercom():
    access_verification(request.headers)
    if not request.get_json():
        abort (422, {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'})
    request_data = request.get_json()
    if not 'flatId' in request_data:
        abort (422, {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'})
    flatId = request_data['flatId']
    return jsonify({
        'code':200,
        'name':'OK',
        'message':'Хорошо',
        'data': {
            'allowDoorCode':'t',
            'doorCode':'22438',
            'CMS':'t',
            'VoIP':'t',
            'autoOpen':'2020-06-03 18:32:10',
            'whiteRabbit':'0',
            'FRSDisabled':'f'
        }
    })

@app.route('/api/address/offices', methods=['POST'])
def address_offices():
    access_verification(request.headers)
    if not request.get_json():
        abort (422, {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'})
    request_data = request.get_json()
    return jsonify({
        'code':200,
        'name':'OK',
        'message':'Хорошо',
        'data': [
            {
                'lat':52.730641,
                'lon':41.45234,
                'address':'Мичуринская улица, 2А',
                'opening':'09:00-19:00 (без выходных)'
            },
            {
                'lat':52.767248,
                'lon':41.40488,
                'address':'улица Чичерина, 48А (ТЦ Апельсин)',
                'opening':'09:00-19:00 (без выходных)'
            },
            {
                'lat':52.707399,
                'lon':41.397374,
                'address':'улица Сенько, 25А (Магнит)',
                'opening':'09:00-19:00 (без выходных)'
            },
            {
                'lat':52.675463,
                'lon':41.465411,
                'address':'Астраханская улица, 189А (ТЦ МЖК)',
                'opening':'09:00-19:00 (без выходных)'
            },
            {
                'lat':52.586785,
                'lon':41.497009,
                'address':'Октябрьская улица, 13 (ДК)',
                'opening':'09:00-19:00 (вс, пн - выходной)'
            }
        ]
    })

@app.route('/api/address/openDoor', methods=['POST'])
def address_openDoor():
    access_verification(request.headers)
    if not request.get_json():
        abort (422, {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'})
    request_data = request.get_json()
    if not 'domophoneId' in request_data:
        abort (422, {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'})
    domophoneId = request_data['domophoneId']
    return app.response_class(status=204, mimetype='application/json')

@app.route('/api/address/plog', methods=['POST'])
def address_plog():
    access_verification(request.headers)
    if not request.get_json():
        abort (422, {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'})
    request_data = request.get_json()
    if not 'flatId' in request_data:
        abort (422, {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'})
    flatId = request_data['flatId']
    return jsonify({
        'code':200,
        'name':'OK',
        'message':'Хорошо',
        'data': [
            {
                'date':'2021-12-15 13:03:23',
                'uuid':'4d5082d2-f8a1-48ac-819e-c16f1f81a1e0',
                'image':'3f99bdf6-96ef-4300-b709-1f557806c65b',
                'objectId':'79',
                'objectType':'0',
                'objectMechanizma':'0',
                'mechanizmaDescription':'Пионерская 5 б п 3 [Подъезд]',
                'event':'1',
                'detail':'1',
                'preview':'https:\/\/static.dm.lanta.me\/2021-12-15\/3\/f\/9\/9\/3f99bdf6-96ef-4300-b709-1f557806c65b.jpg',
                'previewType':2,
                'detailX': {
                    'opened':'f',
                    'face': {
                        'left':'614',
                        'top':'38',
                        'width':'174',
                        'height':'209'
                    },
                    'flags': ['canLike']
                }
            },
            {
                'date':'2021-12-15 00:16:20',
                'uuid':'bc1671b4-e01b-487e-b175-745e82be0ca9',
                'image':'86ddb8e1-1122-4946-8495-a251b6320b99',
                'objectId':'75',
                'objectType':'0',
                'objectMechanizma':'0',
                'mechanizmaDescription':'Пионерская 5 б [Калитка]',
                'event':'4',
                'detail':'89103523377',
                'preview':'https:\/\/static.dm.lanta.me\/2021-12-15\/8\/6\/d\/d\/86ddb8e1-1122-4946-8495-a251b6320b99.jpg',
                'previewType':1,
                'detailX': {'phone':'89103523377'}
            },
            {
                'date':'2021-12-15 00:14:21',
                'uuid':'32fd7c27-0d35-4d98-ab29-2544c3d0b9a7',
                'image':'ad14c83a-126a-4f09-a659-f412fb11007e',
                'objectId':'75',
                'objectType':'0',
                'objectMechanizma':'0',
                'mechanizmaDescription':'Пионерская 5 б [Калитка]',
                'event':'4',
                'detail':'89103523377',
                'preview':'https:\/\/static.dm.lanta.me\/2021-12-15\/a\/d\/1\/4\/ad14c83a-126a-4f09-a659-f412fb11007e.jpg',
                'previewType':1,
                'detailX': {'phone':'89103523377'}
            },
            {
                'date':'2021-12-15 00:03:56',
                'uuid':'ff42c747-3216-4fa7-8b68-128207d1a9ab',
                'image':'0b335948-864f-41d6-b9a7-465f88f20ef1',
                'objectId':'75',
                'objectType':'0',
                'objectMechanizma':'0',
                'mechanizmaDescription':'Пионерская 5 б [Калитка]',
                'event':'4',
                'detail':'89103523377',
                'preview':'https:\/\/static.dm.lanta.me\/2021-12-15\/0\/b\/3\/3\/0b335948-864f-41d6-b9a7-465f88f20ef1.jpg',
                'previewType':1,
                'detailX': {'phone':'89103523377'}
            },
            {
                'date':'2021-12-15 00:01:28',
                'uuid':'0e57d2c7-9e73-4083-98bb-2b140622be93',
                'image':'8fc3224e-ef46-4ec6-9d5d-04e249ec2e31',
                'objectId':'75',
                'objectType':'0',
                'objectMechanizma':'0',
                'mechanizmaDescription':'Пионерская 5 б [Калитка]',
                'event':'4',
                'detail':'89103523377',
                'preview':'https:\/\/static.dm.lanta.me\/2021-12-15\/8\/f\/c\/3\/8fc3224e-ef46-4ec6-9d5d-04e249ec2e31.jpg',
                'previewType':1,
                'detailX': {'phone':'89103523377'}
            },
            {
                'date':'2021-12-15 00:00:02',
                'uuid':'3bcac0af-677b-49d8-ba65-c18c3bcc8668',
                'image':'c28c7e58-7797-4143-a2b8-2c513e216bb8',
                'objectId':'75',
                'objectType':'0',
                'objectMechanizma':'0',
                'mechanizmaDescription':'Пионерская 5 б [Калитка]',
                'event':'4',
                'detail':'89103523377',
                'preview':'https:\/\/static.dm.lanta.me\/2021-12-15\/c\/2\/8\/c\/c28c7e58-7797-4143-a2b8-2c513e216bb8.jpg',
                'previewType':1,
                'detailX': {'phone':'89103523377'}
            }
        ]
    })

@app.route('/api/address/plogDays', methods=['POST'])
def address_plogDays():
    access_verification(request.headers)
    if not request.get_json():
        abort (422, {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'})
    request_data = request.get_json()
    if not 'flatId' in request_data:
        abort (422, {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'})
    flatId = request_data['flatId']
    return jsonify({
        'code':200,
        'name':'OK',
        'message':'Хорошо',
        'data': [
            {
                'day':'2021-12-15',
                'events':'6'
            },
            {
                'day':'2021-12-13',
                'events':'2'
            },
            {
                'day':'2021-12-11',
                'events':'3'
            },
            {
                'day':'2021-12-09',
                'events':'3'
            },
            {
                'day':'2021-12-07',
                'events':'1'
            },
            {
                'day':'2021-12-06',
                'events':'4'
            },
            {
                'day':'2021-12-05',
                'events':'1'
            },
            {
                'day':'2021-12-04',
                'events':'1'
            },
            {
                'day':'2021-11-30',
                'events':'1'
            },
            {
                'day':'2021-11-29',
                'events':'6'
            },
            {
                'day':'2021-11-27',
                'events':'7'
            },
            {
                'day':'2021-11-26',
                'events':'13'
            },
            {
                'day':'2021-11-25',
                'events':'5'
            },
            {
                'day':'2021-11-23',
                'events':'2'
            },
            {
                'day':'2021-11-22',
                'events':'2'
            },
            {
                'day':'2021-11-20',
                'events':'2'
            },
            {
                'day':'2021-11-17',
                'events':'3'
            },
            {
                'day':'2021-11-16',
                'events':'1'
            },
            {
                'day':'2021-11-15',
                'events':'1'
            },
            {
                'day':'2021-11-13',
                'events':'1'
            },
            {
                'day':'2021-11-12',
                'events':'6'
            },
            {
                'day':'2021-11-11',
                'events':'2'
            },
            {
                'day':'2021-11-09',
                'events':'3'
            },
            {
                'day':'2021-11-05',
                'events':'1'
            },
            {
                'day':'2021-10-30',
                'events':'1'
            },
            {
                'day':'2021-10-29',
                'events':'3'
            },
            {
                'day':'2021-10-28',
                'events':'3'
            },
            {
                'day':'2021-10-27',
                'events':'3'
            },
            {
                'day':'2021-10-26',
                'events':'2'
            },
            {
                'day':'2021-10-23',
                'events':'2'
            },
            {
                'day':'2021-10-22',
                'events':'3'
            },
            {
                'day':'2021-10-21',
                'events':'4'
            },
            {
                'day':'2021-10-19',
                'events':'3'
            },
            {
                'day':'2021-10-18',
                'events':'2'
            },
            {
                'day':'2021-10-16',
                'events':'4'
            },
            {
                'day':'2021-10-15',
                'events':'1'
            },
            {
                'day':'2021-10-14',
                'events':'3'
            },
            {
                'day':'2021-10-09',
                'events':'1'
            },
            {
                'day':'2021-10-08',
                'events':'6'
            },
            {
                'day':'2021-10-07',
                'events':'4'
            },
            {
                'day':'2021-10-06',
                'events':'7'
            },
            {
                'day':'2021-10-05',
                'events':'6'
            },
            {
                'day':'2021-10-03',
                'events':'1'
            },
            {
                'day':'2021-10-02',
                'events':'7'
            },
            {
                'day':'2021-10-01',
                'events':'12'
            },
            {
                'day':'2021-09-30',
                'events':'5'
            },
            {
                'day':'2021-09-29',
                'events':'6'
            },
            {
                'day':'2021-09-28',
                'events':'17'
            },
            {
                'day':'2021-09-27',
                'events':'7'
            },
            {
                'day':'2021-09-25',
                'events':'2'
            },
            {
                'day':'2021-09-22',
                'events':'1'
            },
            {
                'day':'2021-09-20',
                'events':'1'
            },
            {
                'day':'2021-09-18',
                'events':'4'
            },
            {
                'day':'2021-09-17',
                'events':'3'
            },
            {
                'day':'2021-09-16',
                'events':'5'
            },
            {
                'day':'2021-09-15',
                'events':'1'
            },
            {
                'day':'2021-09-13',
                'events':'12'
            },
            {
                'day':'2021-09-11',
                'events':'1'
            },
            {
                'day':'2021-09-06',
                'events':'2'
            },
            {
                'day':'2021-09-05',
                'events':'2'
            }
        ]
    })

@app.route('/api/address/registerQR', methods=['POST'])
def address_registerQR():
    access_verification(request.headers)
    if not request.get_json():
        abort (422, {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'})
    request_data = request.get_json()
    if not 'QR' in request_data:
        abort (422, {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'})
    QR = request_data['QR']
    QRcurrent = QR + "1"
    if QR == QRcurrent:
        response = {'code':520,'message':'Этот пользователь уже зарегистрирован в системе'}
    if QR != QR:
        response = {'code':520,'message':'Некорректный QR-код!'}
    if QR != QR:
        response = {'code':200,'name':'OK','message':'Хорошо','data':'QR-код не является кодом для доступа к квартире'}
    if QR == QR:
        response = {'code':200,'name':'OK','message':'Хорошо','data':'Ваш запрос принят и будет обработан в течение одной минуты, пожалуйста подождите'}
    return jsonify(response)

@app.route('/api/address/resend', methods=['POST'])
def address_resend():
    access_verification(request.headers)
    if not request.get_json():
        abort (422, {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'})
    request_data = request.get_json()
    return "Hello, World!"

@app.route('/api/address/resetCode', methods=['POST'])
def address_resetCode():
    access_verification(request.headers)
    if not request.get_json():
        abort (422, {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'})
    request_data = request.get_json()
    return "Hello, World!"

@app.route('/api/cctv/all', methods=['POST'])
def cctv_all():
    access_verification(request.headers)
    if not request.get_json():
        abort (422, {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'})
    request_data = request.get_json()
    return "Hello, World!"

@app.route('/api/cctv/camMap', methods=['POST'])
def cctv_camMap():
    access_verification(request.headers)
    return jsonify({
        'code':200,
        'name':'OK',
        'message':'Хорошо',
        'data': [
            {
                'id':'70',
                'url':'https:\/\/fl2.lanta.me:8443\/91052',
                'token':'acd0c17657395ff3f69d68e74907bb3a',
                'frs':'t'
            },
            {
                'id':'75',
                'url':'https:\/\/fl2.lanta.me:8443\/91078',
                'token':'acd0c17657395ff3f69d68e74907bb3a',
                'frs':'t'
            },
            {
                'id':'79',
                'url':'https:\/\/fl2.lanta.me:8443\/91072',
                'token':'acd0c17657395ff3f69d68e74907bb3a',
                'frs':'t'
            },
            {
                'id':'124',
                'url':'https:\/\/fl2.lanta.me:8443\/95594',
                'token':'acd0c17657395ff3f69d68e74907bb3a',
                'frs':'t'
            },
            {
                'id':'131',
                'url':'https:\/\/fl2.lanta.me:8443\/91174',
                'token':'acd0c17657395ff3f69d68e74907bb3a',
                'frs':'f'
            },
            {
                'id':'343',
                'url':'https:\/\/fl2.lanta.me:8443\/90753',
                'token':'acd0c17657395ff3f69d68e74907bb3a',
                'frs':'t'
            }
        ]
    })

@app.route('/api/cctv/overview', methods=['POST'])
def cctv_overview():
    access_verification(request.headers)
    if not request.get_json():
        abort (422, {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'})
    request_data = request.get_json()
    return "Hello, World!"

@app.route('/api/cctv/recDownload', methods=['POST'])
def cctv_recDownload():
    access_verification(request.headers)
    if not request.get_json():
        abort (422, {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'})
    request_data = request.get_json()
    return "Hello, World!"

@app.route('/api/cctv/recPrepare', methods=['POST'])
def cctv_recPrepare():
    access_verification(request.headers)
    if not request.get_json():
        abort (422, {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'})
    request_data = request.get_json()
    return "Hello, World!"

@app.route('/api/cctv/youtube', methods=['POST'])
def cctv_youtube():
    access_verification(request.headers)
    if not request.get_json():
        abort (422, {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'})
    request_data = request.get_json()
    return "Hello, World!"

@app.route('/api/ext/ext', methods=['POST'])
def ext_ext():
    access_verification(request.headers)
    if not request.get_json():
        abort (422, {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'})
    request_data = request.get_json()
    return "Hello, World!"

@app.route('/api/ext/list', methods=['POST'])
def ext_list():
    access_verification(request.headers)
    if not request.get_json():
        abort (422, {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'})
    request_data = request.get_json()
    return "Hello, World!"

@app.route('/api/frs/disLike', methods=['POST'])
def frs_disLike():
    access_verification(request.headers)
    if not request.get_json():
        abort (422, {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'})
    request_data = request.get_json()
    return "Hello, World!"

@app.route('/api/frs/like', methods=['POST'])
def frs_like():
    access_verification(request.headers)
    if not request.get_json():
        abort (422, {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'})
    request_data = request.get_json()
    return "Hello, World!"

@app.route('/api/frs/listFaces', methods=['POST'])
def frs_listFaces():
    access_verification(request.headers)
    if not request.get_json():
        abort (422, {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'})
    request_data = request.get_json()
    return "Hello, World!"

@app.route('/api/geo/address', methods=['POST'])
def geo_address():
    access_verification(request.headers)
    if not request.get_json():
        abort (422, {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'})
    request_data = request.get_json()
    return "Hello, World!"

@app.route('/api/geo/coder', methods=['POST'])
def geo_coder():
    access_verification(request.headers)
    if not request.get_json():
        abort (422, {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'})
    request_data = request.get_json()
    return "Hello, World!"

@app.route('/api/geo/getAllLocations', methods=['POST'])
def geo_getAllLocations():
    access_verification(request.headers)
    if not request.get_json():
        abort (422, {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'})
    request_data = request.get_json()
    return "Hello, World!"

@app.route('/api/geo/getAllServices', methods=['POST'])
def geo_getAllServices():
    access_verification(request.headers)
    if not request.get_json():
        abort (422, {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'})
    request_data = request.get_json()
    return "Hello, World!"

@app.route('/api/geo/getHouses', methods=['POST'])
def geo_getHouses():
    access_verification(request.headers)
    if not request.get_json():
        abort (422, {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'})
    request_data = request.get_json()
    return "Hello, World!"

@app.route('/api/geo/getServices', methods=['POST'])
def geo_getServices():
    access_verification(request.headers)
    if not request.get_json():
        abort (422, {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'})
    request_data = request.get_json()
    return "Hello, World!"

@app.route('/api/geo/getStreets', methods=['POST'])
def geo_getStreets():
    access_verification(request.headers)
    if not request.get_json():
        abort (422, {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'})
    request_data = request.get_json()
    return "Hello, World!"

@app.route('/api/inbox/alert', methods=['POST'])
def inbox_alert():
    access_verification(request.headers)
    if not request.get_json():
        abort (422, {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'})
    request_data = request.get_json()
    return "Hello, World!"

@app.route('/api/inbox/chatReaded', methods=['POST'])
def inbox_chatReaded():
    access_verification(request.headers)
    if not request.get_json():
        abort (422, {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'})
    request_data = request.get_json()
    return "Hello, World!"

@app.route('/api/inbox/delivered', methods=['POST'])
def inbox_delivered():
    access_verification(request.headers)
    if not request.get_json():
        abort (422, {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'})
    request_data = request.get_json()
    return "Hello, World!"

@app.route('/api/inbox/inbox', methods=['POST'])
def inbox_inbox():
    access_verification(request.headers)
    return jsonify({'code':200,'name':'OK','message':'Хорошо','data':{'count':0,'chat':0}})

@app.route('/api/inbox/readed', methods=['POST'])
def inbox_readed():
    access_verification(request.headers)
    if not request.get_json():
        abort (422, {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'})
    request_data = request.get_json()
    return "Hello, World!"

@app.route('/api/inbox/unreaded', methods=['POST'])
def inbox_unreaded():
    access_verification(request.headers)
    return jsonify({'code':200,'name':'OK','message':'Хорошо','data':{'count':0,'chat':0}})


@app.route('/api/issues/action', methods=['POST'])
def issues_action():
    access_verification(request.headers)
    if not request.get_json():
        abort (422, {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'})
    request_data = request.get_json()
    return "Hello, World!"

@app.route('/api/issues/comment', methods=['POST'])
def issues_comment():
    access_verification(request.headers)
    if not request.get_json():
        abort (422, {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'})
    request_data = request.get_json()
    return "Hello, World!"

@app.route('/api/issues/create', methods=['POST'])
def issues_create():
    access_verification(request.headers)
    if not request.get_json():
        abort (422, {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'})
    request_data = request.get_json()
    return "Hello, World!"

@app.route('/api/issues/listConnect', methods=['POST'])
def issues_listConnect():
    access_verification(request.headers)
    return app.response_class(status=204, mimetype='application/json')

@app.route('/api/pay/prepare', methods=['POST'])
def pay_prepare():
    phone = access_verification(request.headers)
    if not request.get_json():
        abort (422, {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'})
    request_data = request.get_json()
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    logging.debug(repr(request_data['clientId']))
    logging.debug(repr(request_data['amount']))
    sub_response = requests.post(billing_url + "createinvoice", headers={'Content-Type':'application/json'}, data=json.dumps({'login': request_data['clientId'], 'amount' : request_data['amount'], 'phone' : phone})).json()
    return jsonify(sub_response)

@app.route('/api/pay/process', methods=['POST'])
def pay_process():
    access_verification(request.headers)
    if not request.get_json():
        abort (422, {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'})
    request_data = request.get_json()
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    logging.debug(repr(request_data['paymentId']))
    logging.debug(repr(request_data['sbId']))
    return jsonify({'code':200,'name':'OK','message':'Хорошо','data':'Платеж в обработке'})

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
