#!bin/python
import random, uuid, os, json, requests, binascii, secrets, datetime, pytz, time, calendar, codecs, binascii, urllib.parse
from binascii import a2b_base64
from Cryptodome.Hash import SHA512
from Cryptodome.PublicKey import RSA
from Cryptodome.Signature import PKCS1_v1_5 as PKCS
from Cryptodome.Util.asn1 import DerSequence
from datetime import timedelta
from random import randint
from flask import Flask, jsonify, request, make_response, abort, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column, Integer, String, update, or_, any_
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP
from sqlalchemy.sql import exists, func
from sqlalchemy.future import select
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth as HTTPBA
from requests.exceptions import HTTPError
from geopandas.tools import geocode
import logging, sys, base64
import pycurl
from camshot import getcamshot
from invoiceGenerator import create_invoice
from receiptGenerator import create_receipt
from keyManager import keyAdd, keyDell
from getPanel import getPanel
from smser import smssend
from smartyard_db import Temps, Types, Settings, Users, Records, Devices, Rights, Doors, Invoices, Keys, Appeals, Categorys, Statuss, create_db_connection, db, async_session, get_session
from smartyard_bill import addressList, billingList, isActiv, paySuccess, uidFromUidsAndFlat, userPhones, flatFromUid, addressFromUid, fullAddressFromUid, newInvoice, getDetail, getReceipt
from smartyard_click import getPlogs, getPlogsIds, getPlogDays, getPlogDaysIds, getPlogDaysEvents, getPlogDaysEventsIds, putEvent, getCamPlogs, getCamPlogDays, getCamPlogDaysEvents
import firebase_admin
from firebase_admin import auth, credentials, messaging
from harmony_send_message import harmony_send_message
import redis
r = redis.Redis()

try:
    from io import BytesIO
except ImportError:
    from StringIO import StringIO as BytesIO

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    print('not loaded .env file')
    exit()

cred = credentials.Certificate(os.getenv('GOOGLEFSM'))
default_app = firebase_admin.initialize_app(cred)

app = Flask(__name__)
create_db_connection(app)
auth = HTTPBasicAuth()

users = {
    "z5rweb": generate_password_hash("Password"),
}

@auth.verify_password
# функция проверки пароля
def verify_pwd(username, password):
    if (username in users and 
        check_password_hash(users.get(username), password)):
        return username

kannel_url = "http://%s:%d/cgi-bin/sendsms" % (os.getenv('SMS_HOST'), int(os.getenv('SMS_PORT')))
kannel_params = (('user', os.getenv('SMS_USER')), ('pass', os.getenv('SMS_PASS')), ('from', os.getenv('SMS_FROM')), ('coding', '2'))
billing_url = os.getenv('BILLING_URL')
expire = int(os.getenv('EXPIRE'))
proxyfl = os.getenv('PROXYFL')

camshotdir = os.getenv('CAMSHOT_DIR')
imgarchivedir = os.getenv('IMG_ARСHIVE_DIR')
slideshowdir = os.getenv('SLIDESHOW_DIR')
videoarchivedir = os.getenv('VIDEO_ARСHIVE_DIR')
appealdocdir = os.getenv('APPEALDOC_DIR')
serverurl = os.getenv('SERVER_URL')
shortserverurl = serverurl.split('//')[1]

sber_user = os.getenv('BANCK_USERNAME')
sber_passwd = os.getenv('BANCK_PASSWD')
ukassa_user = os.getenv('UKASSA_USERNAME')
ukassa_passwd = os.getenv('UKASSA_PASSWD')

testuser = os.getenv('TEST_USER')
testpass = os.getenv('TEST_PASS')

android_upgrade = 64
android_force_ugrade = 63
harmony_upgrade = 64
harmony_force_ugrade = 63
ios_upgrade = 28
ios_force_ugrade = 27

welcome = False
hasCctv = True
hasPlog = True
hasHcs = True
hasSh = True

def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")

def bool2str(v):
    if v == True:
        return 't'
    else:
        return 'f'

doorsDemo = [{'domophoneId':'0', 'doorId':0,'entrance':'1','icon':'entrance','name':'Подъезд'},{'domophoneId':'0','doorId':1,'icon':'wicket','name':'Калитка'},{'domophoneId':'0','doorId':2,'icon':'gate','name':'Ворота'}]

def access_verification(key):
    global response
    if not key.get('Authorization'):
        response = {'code':422,'name':'Отсутствует токен авторизации','message':'Отсутствует токен авторизации'}
        abort (422)
    try:
        phone = db.session.query(Users.userphone).filter_by(uuid=key.get('Authorization')[7:]).first()[0]
        db.session.remove()
        return phone
    except TypeError:
        response = {'code':401,'name':'Не авторизован','message':'Не авторизован'}
        abort (401)

def json_verification(request):
    global response
    if not request.get_json():
        response = {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'}
        abort (422)
    return request.get_json()

def generate_video_token(userPhone,strims,uid):
    videotoken = secrets.token_hex(16)
    db.session.query(Users).filter_by(userphone=int(userPhone)).update({'videotoken' : videotoken, 'uid' : uid, 'vttime' : datetime.datetime.now(), 'strims' : strims})
    db.session.commit()
    db.session.remove()
    return videotoken

def searchPanel(uid):
    panel = []
    try:
        rights = db.session.query(Rights.uid_right).filter_by(uid=uid).first()[0]
        db.session.remove()
        for right in rights:
            try:
                device_id = db.session.query(Devices.device_id).filter_by(device_id=right, is_active=True, device_type = 3).first()[0]
                db.session.remove()
                row = [r._asdict() for r in db.session.query(Doors.id,Doors.cam).filter_by(device_id=device_id).all()][0]
                db.session.remove()
                row2 = [r._asdict() for r in db.session.query(Devices.paneltype, Devices.panelip, Devices.panellogin, Devices.panelpasswd).filter(Devices.device_id==row['cam']).filter(Devices.is_active==True).filter((Devices.device_type==1)|(Devices.device_type==2)).all()][0]
                db.session.remove()
                panel.append(row|row2)
            except:
                pass
    except:
        device_id = getPanel(addressFromUid(uid), flatFromUid(uid))
        try:
            row = [r._asdict() for r in db.session.query(Devices.paneltype, Devices.panelip, Devices.panellogin, Devices.panelpasswd).filter(Devices.device_id==device_id).filter(Devices.is_active==True).filter((Devices.device_type==1)|(Devices.device_type==2)).all()][0]
            db.session.remove()
            panel.append(row)
        except:
            pass
    return panel

@app.route('/bill/api/auth/', methods=['POST'])
def apiauth():
    return {'token':'eyJzdWIiOiJ1c2VyMTIzIiwicHJvZHVjdElkcyI6WzEsMl19'}


@app.route('/bill/api/types_list/', methods=['POST'])
def apitypes_list():
    types = []
    try:
        types = [r._asdict() for r in db.session.query(Types.id,Types.type).all()]
        db.session.remove()
    except:
        pass
    return {"types": types}

@app.route('/bill/api/devices_list/', methods=['POST'])
def apidevices_list():
    devices = []
    try:
        devices = [r._asdict() for r in db.session.query(Devices.device_id, Devices.device_type, Devices.url, Devices.stream, Devices.is_active, Devices.title, Devices.address, Devices.longitude, Devices.latitude, Devices.record_days, Devices.domophoneid, Devices.monitorid, Devices.sippassword, Devices.dtmf, Devices.camshot, Devices.paneltype, Devices.panelip, Devices.panellogin, Devices.panelpasswd).all()]
        db.session.remove()
#        matching_types = [r._asdict() for r in db.session.query(Types.id,Types.type).all()]
#        db.session.remove()
#        for item in devices:
#            item['device_type'] = [matching_type for matching_type in matching_types if matching_type['id'] == item['device_type']][0]['type']
    except:
        pass
    return {"devices": devices}

@app.route('/bill/api/devices_add/', methods=['POST'])
def apidevices_add():
    request_data = json_verification(request)
    try:
        new_devices = Devices(device_id = None, device_uuid = str(uuid.uuid4()), device_mac = None, device_type = request_data['device_type'], affiliation = None, owner = None, url = request_data['url'], port = None, stream = request_data['stream'], is_active = request_data['is_active'], title = request_data['title'], address = request_data['address'], longitude = request_data['longitude'], latitude = request_data['latitude'], server_id = None, record_days = request_data['record_days'], domophoneid = request_data['domophoneid'], monitorid = request_data['monitorid'], sippassword = request_data['sippassword'], dtmf = request_data['dtmf'], camshot = request_data['camshot'], paneltype = request_data['paneltype'], panelip = request_data['panelip'], panellogin = request_data['panellogin'], panelpasswd = request_data['panelpasswd'])
        db.session.add(new_devices)
        db.session.commit()
        new_device_id = new_devices.device_id
        db.session.remove()
    except:
        return make_response('Ошибка запроса', 422)
    return {'message': 'создано', 'device_id': new_device_id}

@app.route('/bill/api/devices_mod/', methods=['POST'])
def apidevices_mod():
    request_data = json_verification(request)
    try:
        db.session.query(Devices).filter_by(device_id=request_data['device_id']).update({'device_type': request_data['device_type'], 'url': request_data['url'], 'stream': request_data['stream'], 'is_active': request_data['is_active'], 'title': request_data['title'], 'address': request_data['address'], 'longitude': request_data['longitude'], 'latitude': request_data['latitude'], 'record_days': request_data['record_days'], 'domophoneid': request_data['domophoneid'], 'monitorid': request_data['monitorid'], 'sippassword': request_data['sippassword'], 'dtmf': request_data['dtmf'], 'camshot': request_data['camshot'], 'paneltype': request_data['paneltype'], 'panelip': request_data['panelip'], 'panellogin': request_data['panellogin'], 'panelpasswd': request_data['panelpasswd']})
        db.session.commit()
        db.session.remove()
    except:
        return make_response('Ошибка запроса', 422)
    return ""

@app.route('/bill/api/devices_del/', methods=['POST'])
def apidevices_del():
    request_data = json_verification(request)
    devices_id = request_data['device_id']
    try:
        db.session.query(Devices).filter_by(device_id=devices_id).delete()
        db.session.commit()
        db.session.remove()
    except:
        return make_response('Ошибка запроса', 422)
    return ""

@app.route('/bill/api/doors_list/', methods=['POST'])
def apidoors_list():
    doors = []
    try:
        doors = [r._asdict() for r in db.session.query(Doors.id, Doors.open, Doors.device_id, Doors.cam, Doors.icon, Doors.entrance, Doors.name, Doors.open_trait).all()]
        db.session.remove()
    except:
        pass
    return {"doors": doors}

@app.route('/bill/api/doors_add/', methods=['POST'])
def apidoors_add():
    request_data = json_verification(request)
    try:
        new_doors = Doors(id = None, device_id = request_data['device_id'], cam = request_data['cam'], entrance = request_data['entrance'], icon = request_data['icon'], name = request_data['name'], open = request_data['open'], open_trait = request_data['open_trait'])
        db.session.add(new_doors)
        db.session.commit()
        db.session.remove()
    except:
        return make_response('Ошибка запроса', 422)
    return ""

@app.route('/bill/api/doors_mod/', methods=['POST'])
def apidoors_mod():
    request_data = json_verification(request)
    try:
        db.session.query(Doors).filter_by(id=request_data['doors_id']).update({'device_id': request_data['device_id'], 'cam': request_data['cam'], 'entrance': request_data['entrance'], 'icon': request_data['icon'], 'name': request_data['name'], 'open': request_data['open'], 'open_trait': request_data['open_trait']})
        db.session.commit()
        db.session.remove()
    except:
        return make_response('Ошибка запроса', 422)
    return ""

@app.route('/bill/api/doors_del/', methods=['POST'])
def apidoors_del():
    request_data = json_verification(request)
    doors_id = request_data['doors_id']
    try:
        db.session.query(Doors).filter_by(id=doors_id).delete()
        db.session.commit()
        db.session.remove()
    except:
        return make_response('Ошибка запроса', 422)
    return ""

@app.route('/bill/api/address_devices_list/', methods=['POST'])
def apiaddress_devices_list():
    request_data = json_verification(request)
    address = request_data['address']
    devices = []
    try:
        devices = [r._asdict() for r in db.session.query(Devices.device_id, Devices.title, Devices.longitude, Devices.latitude).filter_by(address=address).all()]
        db.session.remove()
    except:
        pass
    return {"devices": devices}

@app.route('/bill/api/address_devices_update/', methods=['POST'])
def apiaddress_devices_update():
    request_data = json_verification(request)
    devices = request_data['data']
    for item in devices:
        db.session.query(Devices).filter_by(device_id=item['device_id']).update({'latitude': item['latitude'], 'longitude': item['longitude']})
        db.session.commit()
        db.session.remove()
    return ""

@app.route('/bill/api/keys_list/', methods=['POST'])
def apikeys_list():
    request_data = json_verification(request)
    uid = int(request_data['uid'])
    keys = []
    try:
        keys = [r._asdict() for r in db.session.query(Keys.key,Keys.comment).filter_by(uid = uid).all()]
        db.session.remove()
        for item in keys:
            item['key'] = item['key'].hex()
    except:
        pass
    return {'keys':keys}

@app.route('/bill/api/keys_add/', methods=['POST'])
def apikeys_add():
    request_data = json_verification(request)
    uid = int(request_data['uid'])
    comment = request_data['comment']
#    try:
    key = bytes.fromhex(request_data['key'])
    new_key = Keys(key = key, uid = uid, comment = comment)
    db.session.add(new_key)
    db.session.commit()
    db.session.remove()
    flat = flatFromUid(uid)
    dompanel = searchPanel(uid)
    for item in dompanel:
        keyAdd(request_data['key'], flat, item['paneltype'], item['panelip'], item['panellogin'], item['panelpasswd'])
#    except:
#        pass
    return ""

@app.route('/bill/api/keys_del/', methods=['POST'])
def apikeys_del():
    request_data = json_verification(request)
    key = bytes.fromhex(request_data['key'])
    uid = int(request_data['uid'])
    try:
        key = bytes.fromhex(request_data['key'])
        db.session.query(Keys).filter_by(key = key, uid = uid).delete()
        db.session.commit()
        db.session.remove()
        flat = flatFromUid(uid)
        dompanel = searchPanel(uid)
        for item in dompanel:
            keyDell(request_data['key'], flat, item['paneltype'], item['panelip'], item['panellogin'], item['panelpasswd'])
    except:
        pass
    return ""

@app.route('/bill/api/rights_list/', methods=['POST'])
def apirights_list():
    request_data = json_verification(request)
    uid = int(request_data['uid'])
    rights = []
    devices = []
    try:
        rights = db.session.query(Rights.uid_right).filter_by(uid=uid).first()[0]
        db.session.remove()
        for item in rights:
            row = [r._asdict() for r in db.session.query(Devices.device_id,Devices.device_type,Devices.title).filter_by(device_id=item).all()]
            db.session.remove()
            device_type = db.session.query(Types.type).filter_by(id=row[0]['device_type']).first()[0]
            db.session.remove()
            row[0]['device_type'] = device_type
            devices.append(row[0])
    except:
        pass
    return {'rights':devices}

@app.route('/bill/api/rights_add/', methods=['POST'])
def apirights_add():
    request_data = json_verification(request)
    uid = int(request_data['uid'])
    rights_add = request_data['device_id']
    rights = []
    try:
        rights = db.session.query(Rights.uid_right).filter_by(uid=uid).first()[0]
        db.session.remove()
        for v in rights_add:
            if str(v) not in rights:
                rights.append(v)
        db.session.query(Rights).filter_by(uid=uid).update({'uid_right':rights})
        db.session.commit()
        db.session.remove()
    except:
        new_rights = Rights(uid = uid, uid_right = rights_add)
        db.session.add(new_rights)
        db.session.commit()
        db.session.remove()
    return ""

@app.route('/bill/api/rights_del/', methods=['POST'])
def apirights_del():
    request_data = json_verification(request)
    uid = int(request_data['uid'])
    rights_del = request_data['device_id']
    rights_old = []
    rights_new = []
    try:
        rights_old = db.session.query(Rights.uid_right).filter_by(uid=uid).first()[0]
        db.session.remove()
        for v in rights_old:
            if str(v) not in rights_del:
                rights_new.append(v)
        db.session.query(Rights).filter_by(uid=uid).update({'uid_right':rights_new})
        db.session.commit()
        db.session.remove()
    except:
        pass
    return ""

@app.route('/bill/api/users/clients/', methods=['POST'])
def apiusersclients():
    return ''

@app.route('/bill/api/users/clients/edit/', methods=['POST'])
def apiusersclientsedit():
    return ''

@app.route('/bill/api/users/clients/change_password/', methods=['POST'])
def apiusersclientschange_password():
    return ''

@app.route('/bill/api/users/clients/create/', methods=['POST'])
def apiusersclientscreate():
    request_data = json_verification(request)
    uid = int(request_data['uid'])
    return {'id':uid}

@app.route('/bill/api/users/clients/delete/', methods=['POST'])
def apiusersclientsdelete():
    return ''

@app.route('/api/')
def index():
    return "Hello, World!"

@app.route('/api/402')
def index402():
    return app.response_class(status=402, mimetype='application/json')

@app.route('/api/404')
def index404():
    return app.response_class(status=404, mimetype='application/json')

@app.route('/api/accessfl', methods=['GET'])
async def accessfl():
    global response
    token = request.args.get('token')
    if not token or token == '':
        response = {'code':403,'name':'Forbidden','message':'Нет токена'}
        abort (403)
    name = request.args.get('name', 0)
    extime = datetime.datetime.now() - timedelta(minutes=expire)
    try:
        row = [r._asdict() for r in db.session.query(Users.vttime, Users.strims).filter_by(videotoken = token).all()]
        db.session.remove()
        vttime = row[0]['vttime']
        strims = row[0]['strims']
        if vttime >= extime and name in strims:
            response = app.response_class(status=200)
            return response
    except:
        pass
    if not proxyfl:
        response = {'code':403,'name':'Forbidden','message':'Не верный токен'}
        abort (403)
    else:
        response = requests.get(proxyfl, params=request.args.to_dict(flat=False))
        if response.status_code != 200:
            response = {'code':403,'name':'Forbidden','message':'И здесь не верный токен'}
            abort (403)
        return response.text

@app.route('/api/spaysuccess', methods=['GET'])
def spaysuccess():
    global response
    try:
        orderNumber = int(request.args.get('orderNumber'))
        operation = request.args.get('operation')
        status = request.args.get('status')
        checksum = request.args.get('checksum')
        argsget = request.args.to_dict(flat=True)
        signature = codecs.decode(checksum.lower(), 'hex')
    except:
        return make_response('Ошибка запроса', 403)
    del argsget['checksum']
    del argsget['sign_alias']
    args = sorted(argsget.items(), key=lambda x: x[0])
    largs = ''.join(str(x) for x in args).replace(')(', ';').replace(', ', ';').replace('(', '').replace(')', '').replace('\'', '') + ';'
    message = f'{largs}'.encode()
    with open('pub.pem',"r",encoding='utf-8') as f:
        pem = f.read()
        lines = pem.replace(" ", '').split()
        der = a2b_base64(''.join(lines[1:-1]))
        cert = DerSequence()
        cert.decode(der)
        tbsCertificate = DerSequence()
        tbsCertificate.decode(cert[0])
        subjectPublicKeyInfo = tbsCertificate[6]
        publicKey = RSA.importKey(subjectPublicKeyInfo)
        h = SHA512.new()
        h.update(message)
        verifier = PKCS.new(publicKey.publickey())
        #if (operation == 'deposited' or operation == 'declinedByTimeout') and status == '1' and verifier.verify(h, signature):
        if operation == 'deposited' and status == '1' and verifier.verify(h, signature):
#            row = [r._asdict() for r in db.session.query(Invoices.amount, Invoices.contract).filter_by(invoice_id=orderNumber).all()]
            db.session.remove()
            db.session.query(Invoices).filter_by(invoice_id=orderNumber).update({'invoice_pay' : True})
            db.session.commit()
            db.session.remove()
#            paySuccess(row[0]['amount'], row[0]['agrmid'])
            response = app.response_class(status=200)
            return response
    return make_response('Операция запрещена', 403)

@app.route('/api/upaysuccess', methods=['POST'])
def upaysuccess():
    global response
    request_data = json_verification(request)
    signature = request.headers.get('Signature')
    amount = float(request_data['object']['amount']['value'])
    #print(f"Юкасса!!!! {request_data['object']}")
    #print(f"Юкасса!!!! {signature}")
    if request_data['event'] =='payment.succeeded' and request_data['object']['paid'] == True and request_data['object']['status'] == 'succeeded':
        #print(f"Платеж прошел!!!! Юкасса!!!! {int(request_data['object']['metadata']['orderNumber'])}  {uuid.UUID(request_data['object']['id'])}    {float(request_data['object']['amount']['value'])}")
        orderNumber = int(request_data['object']['metadata']['orderNumber'])
        db.session.query(Invoices).filter_by(invoice_id=orderNumber).update({'invoice_pay' : True, 'amount': int(amount*100)})
        db.session.commit()
        db.session.remove()
        contract = db.session.query(Invoices.contract).filter_by(invoice_id=orderNumber).first()[0]
        db.session.remove()
        paySuccess(amount, contract, orderNumber)
    return make_response('OK', 200)

@app.route('/api/cams/caminit', methods=['POST'])
async def cams_caminit():
    global response
    request_data = json_verification(request)

    if not 'protocol' in request_data:
        request_data['protocol'] = 'srt'
    if 'macaddress' in request_data:
        try:
            row = [r._asdict() for r in db.session.query(Devices.device_uuid, Devices.device_type, Devices.url, Devices.port, Devices.is_active).filter_by(device_mac = request_data['macaddress']).all()]
            db.session.remove()
#            print(f"Есть в табице mac адрес камеры {row}")
        except TypeError:
#            print(f"Нет в табице mac адреса камеры")
            pass
        if not row:
            device_uuid = str(uuid.uuid4())
            new_cam = Devices(device_id = None, device_uuid = device_uuid, device_mac = request_data['macaddress'], device_type = 2, affiliation = None, owner = None, url = None, port = None, stream = None, is_active = False, title = None, address = None, longitude = None, latitude = None, server_id = None, record_days = None, domophoneid = None, monitorid = None, sippassword = None, dtmf = None, camshot = None, paneltype = None, panelip = None, panellogin = None, panelpasswd = None)
#            print(f"{new_cam}")
            db.session.add(new_cam)
            db.session.commit()
            db.session.remove()
        elif row[0]['device_type'] == 2 and row[0]['url'] and row[0]['port'] and row[0]['is_active']:
            response = {'code':200,'server':row[0]['url'].split('//',1)[1],'port':row[0]['port'],'name':str(row[0]['device_uuid'])}
            return jsonify(response)
#        print(f"Есть в табице mac адрес камеры, но она запрещена")
    response = {'code':403,'name':'Forbidden','message':'Операция запрещена'}
    abort (403)

@app.route('/api/address/access', methods=['POST'])
async def address_access():
    global response
    access_verification(request.headers)
    request_data = json_verification(request)
    if not 'guestPhone' in request_data:
        response = {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'}
        abort (422)
    guestPhone = request_data['guestPhone']
    if 'houseId' in request_data:
        uid = int(request_data['houseId'])
    else:
        response = app.response_class(status=404, mimetype='application/json')
        return jsonify(response)
    if not 'clientId' in request_data:
        status = 404
        response = app.response_class(status=status, mimetype='application/json')
        return response
#        response = {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'}
#        abort (422)
#    clientId = request_data['clientId']
    if not 'expire' in request_data:
        response = {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'}
        abort (422)
    expire = request_data['expire']
    response = app.response_class(status=204, mimetype='application/json')
    return response

@app.route('/api/address/getAddressList', methods=['POST'])
async def address_getAddressList():
    global response
    phone = access_verification(request.headers)
    data = []
    addList = addressList(phone)
    if len(addList) == 0:
        data.append({'houseId':'0','address':'Здесь будет Ваш адрес',"frsEnabled":True,'hasFrs':bool2str(True),'hasCctv':bool2str(hasCctv),'hasPlog':bool2str(hasPlog),'hasHcs':bool2str(hasHcs),'hasSh':bool2str(hasSh),'cctv':99,'doors':doorsDemo})
    else:
        for itemd in addList:
            uid = itemd['uid']
            address = itemd['address']
            cams_open = itemd['cams_open']
            cams_paid = itemd['cams_paid']
            cctv = 0
            door = 0
            if cams_open:
                rights = []
                doors = []
                try:
                    rights = db.session.query(Rights.uid_right).filter_by(uid=uid).first()[0]
                    db.session.remove()
                    for item in rights:
                        device_type = db.session.query(Devices.device_type).filter_by(device_id=item, is_active=True).first()[0]
                        db.session.remove()
                        if device_type == 1 or device_type == 2:
                            cctv = cctv + 1
                        if device_type == 3:
                            door = door + 1
                            row = [r._asdict() for r in db.session.query(Doors.id, Doors.icon, Doors.entrance, Doors.name).filter_by(device_id=item).all()][0]
                            if cams_paid:
                                domophoneId = str(item)
                            else:
                                domophoneId = '2'
                            doors.append({'domophoneId': domophoneId, 'doorId': row['id'], 'entrance': str(row['entrance']), 'icon': row['icon'], 'name': row['name']})
                except TypeError:
                    pass
            if cctv == 0:
                cctv = 99
            if door == 0:
                doors = doorsDemo
            data.append({'houseId':str(uid),'address':address,'frsEnabled':True,'hasFrs':bool2str(True),'hasCctv':bool2str(hasCctv),'hasPlog':bool2str(hasPlog),'hasHcs':bool2str(hasHcs),'hasSh':bool2str(hasSh),'doors':doors,'cctv':cctv})
    Addressresponse = {'code':200,'name':'OK','message':'Хорошо','data':data}
    return jsonify(Addressresponse)

@app.route('/api/address/getSettingsList', methods=['POST'])
async def address_getSettingsList():
    global response
    phone = access_verification(request.headers)
    data = []
    addList = addressList(phone)
    if len(addList) == 0:
        data.append({'address':'Здесь будет Ваш адрес','services':[],'hasPlog':'f','hasGates':'f','contractOwner':'f','houseId':'0'})
    else:
        for itemd in addList:
            uid = itemd['uid']
            clientId = str(itemd['login'])
            contractName = "Договор " + clientId
            houseId = str(itemd['uid'])
            address = itemd['address']
            data.append({'address':address,'services':['internet','iptv','ctv','phone','cctv','domophone'],'hasPlog':'t','hasGates':'t','contractOwner':'t','clientId':clientId,'contractName':contractName,'houseId':houseId, 'flatNumber':'0'})
            exists = db.session.query(db.exists().where(Settings.uid==uid)).scalar()
            db.session.remove()
            if not exists:
                code = int(str(randint(6, 9)) + str(randint(0, 9)) + str(randint(0, 9)) + str(randint(0, 9)) + str(randint(0, 9)))
                new_uid = Settings(uid = uid, intercom = True, asterisk = True, w_rabbit = True, frs = True, code = code, guest = '2022-06-06 00:23:50', whiterabbit = None)
                db.session.add(new_uid)
                db.session.commit()
                db.session.remove()
    Settingsresponse = {'code':200,'name':'OK','message':'Хорошо','data':data}
    return jsonify(Settingsresponse)

@app.route('/api/address/intercom', methods=['POST'])
async def address_intercom():
    global response
    access_verification(request.headers)
    request_data = json_verification(request)
    if 'houseId' in request_data:
        uid = int(request_data['houseId'])
    else:
        response = app.response_class(status=404, mimetype='application/json')
        return response
    exists = db.session.query(db.exists().where(Settings.uid==uid)).scalar()
    db.session.remove()
    try:
        row = [r._asdict() for r in db.session.query(Settings.intercom, Settings.asterisk, Settings.w_rabbit, Settings.frs, Settings.code, Settings.guest).filter_by(uid = uid).all()][0]
        db.session.remove()
        if 'settings' in request_data:
            settings = request_data['settings']
            if 'CMS' in settings:
                intercom = str2bool(settings['CMS'])
                db.session.query(Settings).filter_by(uid=uid).update({'intercom' : intercom})
                db.session.commit()
                db.session.remove()
            if 'VoIP' in settings:
                asterisk = str2bool(settings['VoIP'])
                db.session.query(Settings).filter_by(uid=uid).update({'asterisk' : asterisk})
                db.session.commit()
                db.session.remove()
            if 'autoOpen' in settings:
                guest = settings['autoOpen']
                db.session.query(Settings).filter_by(uid=uid).update({'guest' : guest})
                db.session.commit()
                db.session.remove()
            if 'whiteRabbit' in settings:
                if str(settings['whiteRabbit']) == '0':
                    w_rabbit = False
                else:
                    w_rabbit = True
                db.session.query(Settings).filter_by(uid=uid).update({'w_rabbit' : w_rabbit})
                db.session.commit()
                db.session.remove()
            if 'FRSDisabled' in settings:
                frs = not str2bool(settings['FRSDisabled'])
                db.session.query(Settings).filter_by(uid=uid).update({'frs' : frs})
                db.session.commit()
                db.session.remove()
            row = [r._asdict() for r in db.session.query(Settings.intercom, Settings.asterisk, Settings.w_rabbit, Settings.frs, Settings.code, Settings.guest).filter_by(uid = uid).all()][0]
            db.session.remove()
        CMS = bool2str(row['intercom'])
        VoIP = bool2str(row['asterisk'])
        if row['w_rabbit']:
            whiteRabbit = '3'
        else:
            whiteRabbit = '0'
        FRSDisabled = bool2str(not row['frs'])
        code = str(row['code'])
        guest = row['guest'].strftime("%Y-%m-%d %H:%M:%S")
        response = {'code':200,'name':'OK','message':'Хорошо','data':{'allowDoorCode':'t','doorCode':code,'CMS':CMS,'VoIP':VoIP,'autoOpen':guest,'whiteRabbit':whiteRabbit,'disablePlog':'f', 'hiddenPlog':'f','FRSDisabled':FRSDisabled}}
        return jsonify(response)
    except:
        response = app.response_class(status=404, mimetype='application/json')
        return response

@app.route('/api/address/offices', methods=['POST'])
async def address_offices():
    global response
    access_verification(request.headers)
    request_data = json_verification(request)
    response = {'code':200,'name':'OK','message':'Хорошо','data':[{'lat':52.730641,'lon':41.45234,'address':'Мичуринская улица, 2А','opening':'09:00-19:00 (без выходных)'},{'lat':52.767248,'lon':41.40488,'address':'улица Чичерина, 48А (ТЦ Апельсин)','opening':'09:00-19:00 (без выходных)'},{'lat':52.707399,'lon':41.397374,'address':'улица Сенько, 25А (Магнит)','opening':'09:00-19:00 (без выходных)'},{'lat':52.675463,'lon':41.465411,'address':'Астраханская улица, 189А (ТЦ МЖК)','opening':'09:00-19:00 (без выходных)'},{'lat':52.586785,'lon':41.497009,'address':'Октябрьская улица, 13 (ДК)','opening':'09:00-19:00 (вс, пн - выходной)'}]}
    return jsonify(response)

@app.route('/api/address/openDoor', methods=['POST'])
async def address_openDoor():
    global response
    phone = access_verification(request.headers)
    request_data = json_verification(request)
    if not 'domophoneId' or not 'doorId' or not 'houseId' in request_data:
        response = {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'}
        abort (422)
    domophoneId = int(request_data['domophoneId'])
    doorId = int(request_data['doorId'])
    uid = request_data['houseId']
    if domophoneId == 0 or doorId == 0:
        return app.response_class(status=404, mimetype='application/json')
    doorsrow = [r._asdict() for r in db.session.query(Doors.open, Doors.device_id, Doors.cam, Doors.open_trait).filter(Doors.id==int(request_data['doorId'])).all()][0]
    db.session.remove()
    rights = db.session.query(Rights.uid_right).filter_by(uid=uid).first()[0]
    db.session.remove()
    deviceIds = []
    deviceIds.append(doorsrow['device_id'])
    isactiv = isActiv(uid, deviceIds)
    if isactiv[doorsrow['device_id']] == 0 or not doorsrow['device_id'] in rights:
        return app.response_class(status=404, mimetype='application/json')
    if isactiv[doorsrow['device_id']] == 1:
        return app.response_class(status=402, mimetype='application/json')
    urlopen = doorsrow['open']
    trait = doorsrow['open_trait']
    device_id = doorsrow['cam']
    if trait == 'PUT':
        status_code = requests.put(urlopen).status_code
    elif trait == 'POST':
        status_code = requests.post(urlopen).status_code
    else:
        status_code = requests.get(urlopen).status_code
    if status_code == 200 or status_code == 204:
        camsrow = [r._asdict() for r in db.session.query(Devices.title, Devices.camshot).filter(Devices.device_id==device_id).all()][0]
        db.session.remove()
        title = camsrow['title']
        date = datetime.datetime.now().replace(microsecond=0)
        eventuuid = uuid.uuid4()
        image = uuid.uuid4()
        detail = 'Телефон *' + str(phone)[-4:]
        fileurl = imgarchivedir + '/' + str(image)  + '.jpg'
        clickhouse_data = [[date, eventuuid, image, int(uid), device_id, title, 4, detail, 1, str(phone)],]
        clickhouse_column = ['date', 'uuid', 'image', 'uid', 'objectId', 'mechanizmaDescription', 'event', 'detail', 'preview', 'phone']
        putEvent(clickhouse_data, clickhouse_column)
        if camsrow['camshot']:
            getcamshot(camsrow['camshot'],fileurl)
    odresponse = app.response_class(status=204, mimetype='application/json')
    return odresponse

@app.route('/api/address/plog', methods=['POST'])
async def address_plog():
    global response
    access_verification(request.headers)
    request_data = json_verification(request)
    if 'houseId' in request_data:
        uid = int(request_data['houseId'])
    else:
        response = {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'}
        abort (422)
    try:
        rights = []
        rights = db.session.query(Rights.uid_right).filter_by(uid=uid).first()[0]
        db.session.remove()
        isactiv = isActiv(uid, rights)
        if 2 not in isactiv.values():
            if 1 not in isactiv.values():
                return make_response(jsonify({'error': 'услуга не подключена'}), 404)
            else:
                return make_response(jsonify({'error': 'услуга не оплачена'}), 402)
        if 'day' in request_data:
            date = str(request_data['day'].replace('-', ''))
        if 0 in isactiv.values() or 1 in isactiv.values():
            deviceIds = [k for k, v in isactiv.items() if v == 2]
            resrows = getPlogsIds(uid,date,deviceIds)
        else:
            resrows = getPlogs(uid,date)
        plogs = []
        imgurl = serverurl + '/img/'
        for res in resrows:
            preview = imgurl + str(res[2]) + '.jpg'
            plog = {'date':str(res[0])[:-6],'uuid':str(res[1]),'image':str(res[2]),'objectId':str(res[3]),'objectType':str(res[4]),'objectMechanizma':str(res[5]),'mechanizmaDescription':str(res[6]),'event':str(res[7]),'detail':str(res[8]),'preview':preview,'previewType':int(res[9]),'detailX':{'flags':['canLike']}}
            if int(res[10]) == 1:
                try:
                    plog['detailX']['opened'] = 't'
                except KeyError:
                    plog['detailX'] = {}
                    plog['detailX']['opened'] = 't'
            plogs.append(plog)
        plogresponse = {'code':200,'name':'OK','message':'Хорошо','data':plogs}
        return jsonify(plogresponse)
    except:
        return make_response(jsonify({'error': 'услуга не подключена'}), 404)

@app.route('/api/address/plogDays', methods=['POST'])
async def address_plogDays():
    global response
    access_verification(request.headers)
    request_data = json_verification(request)
    if 'houseId' in request_data:
        uid = int(request_data['houseId'])
    else:
        response = {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'}
        abort (422)
    try:
        rights = []
        rights = db.session.query(Rights.uid_right).filter_by(uid=uid).first()[0]
        db.session.remove()
        isactiv = isActiv(uid, rights)
        if 2 not in isactiv.values():
            if 1 not in isactiv.values():
                return make_response(jsonify({'error': 'услуга не подключена'}), 404)
            else:
                return make_response(jsonify({'error': 'услуга не оплачена'}), 402)
        if 'events' in request_data:
            events = []
            for i in list(map(int, request_data['events'].split(','))):
                events.append(int(i))
            if 0 in isactiv.values() or 1 in isactiv.values():
                deviceIds = [k for k, v in isactiv.items() if v == 2]
                resrows = getPlogDaysEventsIds(uid,events,deviceIds)
            else:
                resrows = getPlogDaysEvents(uid,events)
        else:
            if 0 in isactiv.values() or 1 in isactiv.values():
                deviceIds = [k for k, v in isactiv.items() if v == 2]
                resrows = getPlogDaysIds(uid,deviceIds)
            else:
                resrows = getPlogDays(uid)
        plogDay = []
        for row in resrows:
            plogDay.append({'day':str(row[0])[:-4] + '-' + str(row[0])[-4:-2] + '-' + str(row[0])[-2:],'events':str(row[1])})
        plogdayresponse = {'code':200,'name':'OK','message':'Хорошо','data':plogDay}
        return jsonify(plogdayresponse)
    except:
        return make_response(jsonify({'error': 'услуга не подключена'}), 404)

@app.route('/api/address/registerQR', methods=['POST'])
async def address_registerQR():
    global response
    access_verification(request.headers)
    request_data = json_verification(request)
    if not 'QR' in request_data:
        response = {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'}
        abort (422)
    QR = request_data['QR']
    QRcurrent = QR + "1"
    if QR == QRcurrent:
        response = {'code':520,'message':'Этот пользователь уже зарегистрирован в системе'}
        return jsonify(response)
    if QR != QR:
        response = {'code':200,'name':'OK','message':'Хорошо','data':'QR-код не является кодом для доступа к квартире'}
        return jsonify(response)
    if QR == QR:
        response = {'code':200,'name':'OK','message':'Хорошо','data':'Ваш запрос принят и будет обработан в течение одной минуты, пожалуйста подождите'}
        return jsonify(response)

@app.route('/api/address/resend', methods=['POST'])
async def address_resend():
    global response
    access_verification(request.headers)
    request_data = json_verification(request)
    if 'houseId' in request_data:
        uid = int(request_data['houseId'])
    else:
        response = app.response_class(status=404, mimetype='application/json')
        return jsonify(response)
    return "Hello, World!"

@app.route('/api/address/resetCode', methods=['POST'])
async def address_resetCode():
    global response
    access_verification(request.headers)
    request_data = json_verification(request)
    if 'houseId' in request_data:
        uid = int(request_data['houseId'])
    else:
        response = app.response_class(status=404, mimetype='application/json')
        return jsonify(response)
    code = int(str(randint(1, 9)) + str(randint(0, 9)) + str(randint(0, 9)) + str(randint(0, 9)) + str(randint(0, 9)))
    db.session.query(Settings).filter_by(uid=uid).update({'code' : code})
    db.session.commit()
    db.session.remove()
    response = {'code':200,'name':'OK','message':'Хорошо','data':{'code':code}}
    return jsonify(response)

@app.route('/api/cctv/all', methods=['POST'])
async def cctv_all():
    global response
    phone = access_verification(request.headers)
    request_data = json_verification(request)
    uid = request_data['houseId']
    try:
        rights = []
        rights = db.session.query(Rights.uid_right).filter_by(uid=uid).first()[0]
        db.session.remove()
        isactiv = isActiv(uid, rights)
        if 2 not in isactiv.values():
            if 1 not in isactiv.values():
                return make_response(jsonify({'error': 'услуга не подключена'}), 404)
            else:
                return make_response(jsonify({'error': 'услуга не оплачена'}), 402)
        cctv_all_data = []
        strims = []
        for right, val in isactiv.items():
            rows = [r._asdict() for r in db.session.query(Devices.device_uuid, Devices.url, Devices.title, Devices.device_type, Devices.longitude, Devices.latitude).filter(Devices.is_active==True,(Devices.device_type==1)|(Devices.device_type==2),Devices.device_id==right).all()]
            db.session.remove()
            for row in rows:
                name = row['title']
                lat = str(row['latitude'])
                lon = str(row['longitude'])
                if val == 2:
                    device_uuid = row['device_uuid']
                    url = str(row['url']) + '/' + str(device_uuid)
                    strims.append(str(device_uuid))
                elif val == 1:
                    url = serverurl + '/api/402'
                else:
                    url = serverurl + '/api/404'
                cctv_all_data.append({'id': right, 'name': name, 'lat': lat, 'lon': lon, 'url': url, 'token': ''})
        videotoken = generate_video_token(phone,strims,uid)
        for item in cctv_all_data:
            item['token'] = videotoken
        cctv_all_response = {'code':200,'name':'OK','message':'Хорошо','data':cctv_all_data}
        return jsonify(cctv_all_response)
    except:
        return make_response(jsonify({'error': 'услуга не подключена'}), 404)

@app.route('/api/cctv/door', methods=['POST'])
async def cctv_door():
    global response
    phone = access_verification(request.headers)
    request_data = json_verification(request)
    uid = request_data['houseId']
    doorId = request_data['doorId']
    try:
        cam = db.session.query(Doors.cam).filter(Doors.id==doorId).first()[0]
        db.session.remove()
        rights = []
        rights = db.session.query(Rights.uid_right).filter_by(uid=uid).first()[0]
        db.session.remove()
    except:
        return app.response_class(status=404, mimetype='application/json')
    deviceIds = []
    deviceIds.append(cam)
    isactiv = isActiv(uid, deviceIds)
    if isactiv[cam] == 0 or not cam in rights:
        return app.response_class(status=404, mimetype='application/json')
    if isactiv[cam] == 1:
        return app.response_class(status=402, mimetype='application/json')
    row = [r._asdict() for r in db.session.query(Devices.device_uuid, Devices.url, Devices.title).filter_by(device_id=cam, is_active=True).all()][0]
    db.session.remove()
    device_uuid = str(row['device_uuid'])
    strims = []
    strims.append(device_uuid)
    videotoken = generate_video_token(phone,strims,uid)
    name = row['title']
    url = str(row['url']) + '/' + device_uuid
    cctv_door_data = {'doorId': doorId, 'name': name, 'url': url, 'token': videotoken}
    cctv_door_response = {'code':200,'name':'OK','message':'Хорошо','data':cctv_door_data}
    return jsonify(cctv_door_response)

@app.route('/api/cctv/camMap', methods=['POST'])
async def cctv_camMap():
    global response
    phone = access_verification(request.headers)
    request_data = json_verification(request)
    if not 'houseId' in request_data:
        response = {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'}
        abort (422)
    uid = request_data['houseId']
    try:
        rights = []
        rights = db.session.query(Rights.uid_right).filter_by(uid=uid).first()[0]
        db.session.remove()
        isactiv = isActiv(uid, rights)
        if 2 not in isactiv.values():
            if 1 not in isactiv.values():
                return make_response(jsonify({'error': 'услуга не подключена'}), 404)
            else:
                return make_response(jsonify({'error': 'услуга не оплачена'}), 402)
        data = []
        doors = []
        strims = []
        for right in rights:
            device_type = db.session.query(Devices.device_type).filter_by(device_id=right, is_active=True).first()[0]
            db.session.remove()
            if device_type == 3:
                camid = db.session.query(Doors.cam).filter_by(device_id=right).first()[0]
                db.session.remove()
                row = [r._asdict() for r in db.session.query(Devices.device_uuid, Devices.url).filter(Devices.device_id==camid).filter(Devices.is_active==True).filter((Devices.device_type==1)|(Devices.device_type==2)).all()]
                db.session.remove()
                try:
                    device_uuid = row[0]['device_uuid']
                    url = str(row[0]['url']) + '/' + str(device_uuid)
                    data.append({'id': str(camid), 'url': url, 'token': '', 'frs':'t', 'serverType': 'flussonic'})
                except IndexError:
                    pass
        for item in data:
            strims.append(item['url'][8:].partition('/')[2])
        videotoken = generate_video_token(phone,strims,uid)
        for item in data:
            item['token'] = videotoken
        print(f"{data}")
        Cammapresponse = {'code':200,'name':'OK','message':'Хорошо','data':data}
        return jsonify(Cammapresponse)
    except:
        return make_response(jsonify({'error': 'услуга не подключена'}), 404)

@app.route('/api/cctv/overview', methods=['POST'])
async def cctv_overview():
    global response
    access_verification(request.headers)
    return make_response(jsonify({'error': 'услуга не подключена'}), 404)
#    response = {'code':200,'name':'OK','message':'Хорошо','data':[]}
#    return jsonify(response)

@app.route('/api/cctv/ranges', methods=['POST'])
async def cctv_ranges():
    global response
    phone = access_verification(request.headers)
    request_data = json_verification(request)
    cameraId = request_data['cameraId']
    videotoken = db.session.query(Users.videotoken).filter_by(userphone=phone).first()[0]
    row = [r._asdict() for r in db.session.query(Devices.device_uuid, Devices.url, Devices.server_id).filter_by(device_id=cameraId, is_active=True).all()]
    camurl = row[0]['url'] + '/' + str(row[0]['device_uuid'])
    ranges = requests.get(camurl + '/recording_status.json?from=1525186456&token='+'100'+str(videotoken)).json()[0]['ranges']
    data = [{'stream':str(row[0]['device_uuid']), 'ranges':ranges}]
    response = {'code':200,'name':'OK','message':'Хорошо','data':data}
    return jsonify(response)

@app.route('/api/cctv/recDownload', methods=['POST'])
async def cctv_recDownload():
    global response
    access_verification(request.headers)
    request_data = json_verification(request)
    recordid = request_data['id']
    fileurl = serverurl + '/' + db.session.query(Records.fileurl).filter_by(id = recordid).first()[0]
    db.session.remove()
    response = {'code':200,'name':'OK','message':'Хорошо', 'data':fileurl }
    #print(f'response =   {response}')
    return jsonify(response)

@app.route('/api/cctv/recPrepare', methods=['POST'])
async def cctv_recPrepare():
    global response
    phone = access_verification(request.headers)
    request_data = json_verification(request)
    cam_id = request_data['id']
    row = [r._asdict() for r in db.session.query(Devices.device_uuid, Devices.url, Devices.title).filter_by(device_id=cam_id, is_active=True).all()]
    db.session.remove()
    camurl = row[0]['url'] + '/' + str(row[0]['device_uuid'])
    camname = row[0]['title']
    time_from = datetime.datetime.strptime(request_data['from'], '%Y-%m-%d %H:%M:%S')
    time_to = datetime.datetime.strptime(request_data['to'], '%Y-%m-%d %H:%M:%S')
    time_rec = time_to - time_from
    if int(time_rec.seconds) > 900:
        response = {'code':403,'name':'Set less than 15 min.','message':'Установите менее 15 мин.'}
        abort (403)
    row = [r._asdict() for r in db.session.query(Users.videotoken, Users.uid).filter_by(userphone = phone).all()]
    db.session.remove()
    url = camurl + '/' + 'archive-'+str(int(time.mktime(time_from.timetuple())))+'-'+str(time_rec.seconds)+'.mp4?token='+'100'+str(row[0]['videotoken'])
    fileurl = camname.lower().replace(",", "_").replace(".", "_").replace(" ", "_") + '_' + time_from.strftime("%H-%M-%S_%m_%d_%Y") + '__' + time_to.strftime("%H-%M-%S_%m_%d_%Y") + '.mp4'
    fullfileurl = videoarchivedir + '/' + fileurl
    db.session.add(Records(id = None, uid = row[0]['uid'], url = url, fileurl = fileurl, rtime = None, rdone = False))
    db.session.commit()
    db.session.remove()
    recordId = db.session.query(Records.id).filter_by(url = url, fileurl = fileurl).first()[0]
    db.session.remove()
    resCode=403
    fil = open(fullfileurl,'wb')
    cur = pycurl.Curl()
    cur.setopt(cur.URL, url)
    cur.setopt(cur.WRITEDATA, fil)
    cur.perform()
    resCode = cur.getinfo(cur.RESPONSE_CODE)
    resText = cur.getinfo(cur.HTTP_CODE)
    cur.close()
    fil.close()
    #print(f'resCode =   {resCode}    resText =   {resText} url = {url}    fullfileurl = {fullfileurl} !')
    if resCode == 200:
        db.session.query(Records).filter_by(id=recordId).update({'rdone' : True})
        db.session.commit()
        db.session.remove()
        response = {'code':200,'name':'OK','message':'Хорошо', 'data':recordId }
        return jsonify(response)
    else:
        response = {'code':resCode,'name':resText,'message':resTex}
        abort (resCode)

@app.route('/api/cctv/youtube', methods=['POST'])
async def cctv_youtube():
    global response
    access_verification(request.headers)
    request_data = json_verification(request)
    return "Hello, World!"

@app.route('/api/cctv/plog', methods=['POST'])
async def cctv_plog():
    global response
    access_verification(request.headers)
    request_data = json_verification(request)
    if 'houseId' and 'camId' and 'day' in request_data:
        uid = request_data['houseId']
        camId = request_data['camId']
        date = str(request_data['day'].replace('-', ''))
    else:
        response = {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'}
        abort (422)
    try:
        rights = []
        rights = db.session.query(Rights.uid_right).filter_by(uid=uid).first()[0]
        db.session.remove()
        isactiv = isActiv(uid, rights)
        if 2 not in isactiv.values():
            if 1 not in isactiv.values():
                return make_response(jsonify({'error': 'услуга не подключена'}), 404)
            else:
                return make_response(jsonify({'error': 'услуга не оплачена'}), 402)
        camPlogs = []
        imgurl = serverurl + '/img/'
        resrows = getCamPlogs(camId,date)
        for res in resrows:
            preview = imgurl + str(res[2]) + '.jpg'
            camPlog = {'date':str(res[0])[:-6],'uuid':str(res[1]),'image':str(res[2]),'objectId':str(res[3]),'objectType':str(res[4]),'objectMechanizma':str(res[5]),'mechanizmaDescription':str(res[6]),'event':str(res[7]),'detail':str(res[8]),'preview':preview,'previewType':int(res[9]),'detailX':{'flags':['canLike']}}
            camPlogs.append(camPlog)
        print(f"{plogs}")
        camplogresponse = {'code':200,'name':'OK','message':'Хорошо','data':camPlogs}
        #response = {'code':200,'name':'OK','message':'Хорошо','data':[{'date':'2023-01-20 13:03:23','uuid':'4d5082d2-f8a1-48ac-819e-c16f1f81a1e0','image':'3f99bdf6-96ef-4300-b709-1f557806c65b','objectId':'38','objectType':'0','objectMechanizma':'0','mechanizmaDescription':'Пионерская 5 б п 3 [Подъезд]','event':'1','detail':'1','preview':'https://static.dm.lanta.me/2023-01-18/3/f/9/9/3f99bdf6-96ef-4300-b709-1f557806c65b.jpg','previewType':2,'detailX':{'opened':'f','face':{'left':'614','top':'38','width':'174','height':'209'},'flags':['canLike']}},{'date':'2023-01-20 00:16:20','uuid':'bc1671b4-e01b-487e-b175-745e82be0ca9','image':'86ddb8e1-1122-4946-8495-a251b6320b99','objectId':'38','objectType':'0','objectMechanizma':'0','mechanizmaDescription':'Пионерская 5 б [Калитка]','event':'3','detail':'123456789123456789','preview':'https://static.dm.lanta.me/2023-01-18/8/6/d/d/86ddb8e1-1122-4946-8495-a251b6320b99.jpg','previewType':1,'detailX':{'key':'123456789'}},{'date':'2023-01-20 00:14:21','uuid':'32fd7c27-0d35-4d98-ab29-2544c3d0b9a7','image':'ad14c83a-126a-4f09-a659-f412fb11007e','objectId':'38','objectType':'0','objectMechanizma':'0','mechanizmaDescription':'Пионерская 5 б [Калитка]','event':'4','detail':'89103523377','preview':'https://static.dm.lanta.me/2023-01-18/a/d/1/4/ad14c83a-126a-4f09-a659-f412fb11007e.jpg','previewType':1,'detailX':{'phone':'89103523377'}},{'date':'2023-01-20 00:03:56','uuid':'ff42c747-3216-4fa7-8b68-128207d1a9ab','image':'0b335948-864f-41d6-b9a7-465f88f20ef1','objectId':'38','objectType':'0','objectMechanizma':'0','mechanizmaDescription':'Пионерская 5 б [Калитка]','event':'4','detail':'89103523377','preview':'https://static.dm.lanta.me/2023-01-18/0/b/3/3/0b335948-864f-41d6-b9a7-465f88f20ef1.jpg','previewType':1,'detailX':{'phone':'89103523377'}},{'date':'2023-01-20 00:01:28','uuid':'0e57d2c7-9e73-4083-98bb-2b140622be93','image':'8fc3224e-ef46-4ec6-9d5d-04e249ec2e31','objectId':'38','objectType':'0','objectMechanizma':'0','mechanizmaDescription':'Пионерская 5 б [Калитка]','event':'4','detail':'89103523377','preview':'https://static.dm.lanta.me/2023-01-18/8/f/c/3/8fc3224e-ef46-4ec6-9d5d-04e249ec2e31.jpg','previewType':1,'detailX':{'phone':'89103523377'}},{'date':'2023-01-20 00:00:02','uuid':'3bcac0af-677b-49d8-ba65-c18c3bcc8668','image':'c28c7e58-7797-4143-a2b8-2c513e216bb8','objectId':'38','objectType':'0','objectMechanizma':'0','mechanizmaDescription':'Пионерская 5 б [Калитка]','event':'4','detail':'89103523377','preview':'https://static.dm.lanta.me/2023-01-18/c/2/8/c/c28c7e58-7797-4143-a2b8-2c513e216bb8.jpg','previewType':1,'detailX':{'phone':'89103523377'}}]}
        return jsonify(camplogresponse)
    except:
        return make_response(jsonify({'error': 'услуга не подключена'}), 404)

@app.route('/api/cctv/plogDays', methods=['POST'])
async def cctv_plogDays():
    global response
    access_verification(request.headers)
    request_data = json_verification(request)
    if 'houseId' and 'camId' in request_data:
        uid = request_data['houseId']
        camId = request_data['camId']
    else:
        response = {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'}
        abort (422)
    try:
        rights = []
        rights = db.session.query(Rights.uid_right).filter_by(uid=uid).first()[0]
        db.session.remove()
        isactiv = isActiv(uid, rights)
        if 2 not in isactiv.values():
            if 1 not in isactiv.values():
                return make_response(jsonify({'error': 'услуга не подключена'}), 404)
            else:
                return make_response(jsonify({'error': 'услуга не оплачена'}), 402)
        if 'events' in request_data:
            events = []
            for i in list(map(int, request_data['events'].split(','))):
                events.append(int(i))
            resrows = getCamPlogDaysEvents(camId,events)
        else:
            resrows = getCamPlogDays(camId)
        camPlogDay = []
        for row in resrows:
            camPlogDay.append({'day':str(row[0])[:-4] + '-' + str(row[0])[-4:-2] + '-' + str(row[0])[-2:],'events':str(row[1])})
        camplogdayresponse = {'code':200,'name':'OK','message':'Хорошо','data':camPlogDay}
        return jsonify(camplogdayresponse)
    except:
        return make_response(jsonify({'error': 'услуга не подключена'}), 404)

@app.route('/api/ext/ext', methods=['POST'])
async def ext_ext():
    global response
    access_verification(request.headers)
    request_data = json_verification(request)
    return "Hello, World!"

@app.route('/api/ext/list', methods=['POST'])
async def ext_list():
    global response
    access_verification(request.headers)
    response = {'code':200,'name':'OK','message':'Хорошо', 'data':[]}
    return jsonify(response)

@app.route('/api/frs/disLike', methods=['POST'])
async def frs_disLike():
    global response
    access_verification(request.headers)
    request_data = json_verification(request)
    if 'houseId' in request_data:
        uid = int(request_data['houseId'])
    else:
        response = app.response_class(status=404, mimetype='application/json')
        return response
    response = app.response_class(status=404, mimetype='application/json')
    return response
    response = {'code':200,'name':'OK','message':'Хорошо', 'data':''}
    return jsonify(response)

@app.route('/api/frs/like', methods=['POST'])
async def frs_like():
    global response
    access_verification(request.headers)
    request_data = json_verification(request)
    if 'houseId' in request_data:
        uid = int(request_data['houseId'])
    else:
        response = app.response_class(status=404, mimetype='application/json')
        return response
    response = app.response_class(status=404, mimetype='application/json')
    return response
    response = {'code':200,'name':'OK','message':'Хорошо', 'data':''}
    return jsonify(response)

@app.route('/api/frs/listFaces', methods=['POST'])
async def frs_listFaces():
    global response
    access_verification(request.headers)
    request_data = json_verification(request)
    if 'houseId' in request_data:
        uid = int(request_data['houseId'])
    else:
        response = app.response_class(status=404, mimetype='application/json')
        return response
    response = {'code':200,'name':'OK','message':'Хорошо','data':[{'faceId': '144349','image':'https://faces.dm.lanta.me/3/9/9/c/d/399cd1a1-4545-2443-33de-a3dc8af728f7.jpg'}]}
    return jsonify(response)

@app.route('/api/geo/address', methods=['POST'])
async def geo_address():
    global response
    access_verification(request.headers)
    request_data = json_verification(request)
    return "Hello, World!"

@app.route('/api/geo/coder', methods=['POST'])
async def geo_coder():
    global response
    access_verification(request.headers)
    request_data = json_verification(request)
    address = request_data['address']
    loc = 'Липецк Победы 106а 38'
    location = geocode(loc, provider="nominatim" , user_agent = 'my_request')
    point = location.geometry.iloc[0]
#    print('Name: '+ loc )
#    print('complete address: '+ location.address.iloc[0])
#    print('longitude: {} '.format(point.x))
#    print('latitude: {} '.format(point.y))
    response = {'code':200,'name':'OK','message':'Хорошо','data':{'address':address,'lat':'52.609296', 'lon':'39.59851'}}
    return jsonify(response)

@app.route('/api/geo/getAllLocations', methods=['POST'])
async def geo_getAllLocations():
    global response
#    access_verification(request.headers)
#    request_data = json_verification(request)
    response = {'code':200,'name':'OK','message':'Хорошо','data':[{'locationId':'1', 'locationName':'Липецк', 'name':'Липецк'},]}
    return jsonify(response)

@app.route('/api/geo/getAllServices', methods=['POST'])
async def geo_getAllServices():
    global response
    access_verification(request.headers)
    request_data = json_verification(request)
    return "Hello, World!"

@app.route('/api/geo/getHouses', methods=['POST'])
async def geo_getHouses():
    global response
    access_verification(request.headers)
    request_data = json_verification(request)
    return "Hello, World!"

@app.route('/api/geo/getServices', methods=['POST'])
async def geo_getServices():
    global response
    access_verification(request.headers)
    request_data = json_verification(request)
    response = {'code':200,'name':'OK','message':'Хорошо','data':[{'icon':'internet','title':'internet','description':'internet','canChange':'f','byDefault':'t'},{'icon':'iptv','title':'iptv','description':'iptv','canChange':'f','byDefault':'t'},{'icon':'ctv','title':'ctv','description':'ctv','canChange':'f','byDefault':'t'},{'icon':'phone','title':'phone','description':'phone','canChange':'f','byDefault':'t'},{'icon':'cctv','title':'cctv','description':'cctv','canChange':'f','byDefault':'t'},{'icon':'domophone','title':'domophone','description':'domophone','canChange':'f','byDefault':'t'},{'icon':'gsm','title':'gsm','description':'gsm','canChange':'f','byDefault':'t'}]}
    return jsonify(response)

@app.route('/api/geo/getStreets', methods=['POST'])
async def geo_getStreets():
    global response
    access_verification(request.headers)
    request_data = json_verification(request)
    return "Hello, World!"

@app.route('/api/inbox/alert', methods=['POST'])
async def inbox_alert():
    global response
    access_verification(request.headers)
    request_data = json_verification(request)
    return "Hello, World!"

@app.route('/api/inbox/chatReaded', methods=['POST'])
async def inbox_chatReaded():
    global response
    access_verification(request.headers)
    request_data = json_verification(request)
    return "Hello, World!"

@app.route('/api/inbox/delivered', methods=['POST'])
async def inbox_delivered():
    global response
    access_verification(request.headers)
    request_data = json_verification(request)
    return "Hello, World!"

@app.route('/api/inbox/inbox', methods=['POST'])
async def inbox_inbox():
    global response
    access_verification(request.headers)
    #if not request.get_json():
    #    response = {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'}
    #    abort (422)
    #request_data = request.get_json()
    #response = {'code':200,'name':'OK','message':'Хорошо','data':{'count':0,'chat':0}}
    ##response = {'code':200,'name':'OK','message':'Хорошо','data':{"basePath": "https://dm.lanta.me\/", "code": "<!DOCTYPE html>\n<html lang=\"ru\">\n<head>\n    <meta charset=\"UTF-8\">\n    <title>inbox<\/title>\n    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0, minimum-scale=1.0, maximum-scale=1.0, user-scalable=no\">\n    <!--\n    <link rel=\"stylesheet\" href=\"reset.css\">\n    <link rel=\"stylesheet\" href=\"styles.css\">\n    -->\n    <style type=\"text\/css\">\n        @font-face {\n            font-family: \"SourceSansPro\";\n            src: url(\"static\/fonts\/sourcesanspro\/sourcesanspro.ttf\");\n        }\n\n        @font-face {\n            font-family: \"SourceSansProBold\";\n            src: url(\"static\/fonts\/sourcesanspro\/sourcesansprobold.ttf\");\n        }\n\n        @font-face {\n            font-family: \"SourceSansProItalic\";\n            src: url(\"static\/fonts\/sourcesanspro\/sourcesansproitalic.ttf\");\n        }\n\n        @font-face {\n            font-family: \"SourceSansProLight\";\n            src: url(\"static\/fonts\/sourcesanspro\/sourcesansprolight.ttf\");\n        }\n\n        @font-face {\n            font-family: \"SourceSansProSemiBold\";\n            src: url(\"static\/fonts\/sourcesanspro\/sourcesansprosemibold.ttf\");\n        }\n\n        *, *::before, *::after {\n            box-sizing: border-box;\n        }\n\n        html, body {\n            width: 100%;\n            height: 100%;\n            font-family: SourceSansPro, sans-serif;\n            font-size: 14px;\n            background: #f3f4fa;\n            overflow-x: hidden;\n        }\n\n        h1, .h1,\n        h2, .h2,\n        h3, .h3,\n        h4, .h4,\n        h5, .h5,\n        h6, .h6 {\n            margin-top: 0;\n            margin-bottom: 0;\n            font-family: SourceSansProBold, sans-serif;\n            font-weight: normal;\n            color: #28323e;\n        }\n\n        h1, .h1 {\n            font-size: 32px;\n            line-height: 120%;\n        }\n\n        h2, .h2 {\n            font-size: 28px;\n            line-height: 120%;\n        }\n\n        h3, .h3 {\n            font-size: 24px;\n            line-height: 24px;\n        }\n\n        h4, .h4 {\n            font-size: 20px;\n            line-height: 24px;\n        }\n\n        h5, .h5 {\n            font-size: 18px;\n            line-height: 24px;\n        }\n\n        h6, .h6 {\n            font-size: 16px;\n            line-height: 24px;\n        }\n\n        .text-1,\n        .text-2,\n        .text-3,\n        .text-4,\n        .text-5 {\n            font-family: SourceSansPro, sans-serif;\n            line-height: 100%;\n        }\n\n        .text-1 {\n            font-family: SourceSansProSemiBold, sans-serif;\n            font-size: 18px;\n        }\n\n        .text-2 {\n            font-size: 16px;\n        }\n\n        .text-3 {\n            font-size: 14px;\n        }\n\n        .text-4 {\n            font-size: 13px;\n        }\n\n        .text-5 {\n            font-size: 12px;\n        }\n\n        .inbox-block {\n            padding: 20px 16px;\n        }\n\n        .inbox-date,\n        .inbox-message-time {\n            display: block;\n            font-size: 14px;\n            line-height: 18px;\n            color: #6d7a8a;\n            opacity: .5;\n        }\n\n        .inbox-date {\n            margin-bottom: 16px;\n            text-align: center;\n        }\n\n        .inbox-message-time {\n            margin-top: 6px;\n            font-size: 10px;\n            text-align: right;\n        }\n\n        .inbox-message-primary,\n        .inbox-message-secondary {\n            display: flex;\n            margin-bottom: 10px;\n        }\n\n        .inbox-message-content {\n            margin-left: 16px;\n            padding: 20px 12px;\n            padding-bottom: 8px;\n            width: 100%;\n            background: #fff;\n            border-radius: 20px;\n            border-top-left-radius: 0;\n        }\n\n        .inbox-message-secondary .inbox-message-content {\n            margin-left: 50px;\n        }\n\n        .inbox-message-content a {\n            margin-bottom: 10px;\n            line-height: 18px;\n            text-decoration: none;\n            color: #007bff;\n        }\n\n        .inbox-message-content p {\n            margin-bottom: 10px;\n            line-height: 18px;\n            color: #6d7a8a;\n        }\n\n        .inbox-message-primary .inbox-message-content p:first-child {\n            margin-bottom: 16px;\n            font-family: SourceSansProSemiBold;\n            font-size: 18px;\n            line-height: 22px;\n            color: #28323e;\n        }\n\n        .inbox-message-content p:last-child {\n            margin-bottom: 0;\n        }\n\n        .inbox-message-icon {\n            display: inline-block;\n            width: 36px;\n            height: 37px;\n        }\n\n        .inbox-message-icon.icon-avatar {\n            background: url('static\/icon\/avatar.png') 0 0 no-repeat;\n            background-size: 100%;\n        }\n\n        .clearfix:before,\n        .clearfix:after {\n            content: \" \";\n            display: table;\n            clear: both;\n        }\n    <\/style>\n<\/head>\n<body>\n<div class=\"inbox-block\"><span class=\"inbox-date\">19 дек 2021<\/span><div class=\"inbox-message-primary\"><i class=\"inbox-message-icon icon-avatar\"><\/i><div class=\"inbox-message-content\"><p><p>Уважаемые пользователи системы распознавания лиц! В понедельник, 20 декабря, в интервале с 10:00 до 12:00 распознавание лиц на вашем домофоне будет временно недоступно. Приносим извинения за возможные неудобства.<\/p><\/p><span class=\"inbox-message-time\">12:35<\/span><\/div><\/div><span class=\"inbox-date\">19 июл 2021<\/span><div class=\"inbox-message-primary\"><i class=\"inbox-message-icon icon-avatar\"><\/i><div class=\"inbox-message-content\"><p><p>Дорогие жители дома №59а корп. 5 по улице Рылеева! У вас появилась бесплатная возможность протестировать систему открывания домофона с распознаванием по лицу.<br \/>\n<br \/><\/p>\n<ol>\n<li>Установите самую свежую версию приложения «ЛАНТА».<br \/><\/li>\n<li>В приложении в настройках адреса включите опции «Распознавание лиц» и «Вести журнал событий» (журнал событий ведётся для каждой квартиры в отдельности, доступа к событиям других квартир нет).<br \/><\/li>\n<li>Откройте дверь подъезда электронным ключом или совершите вызов в свою квартиру через домофон, чтобы в истории событий появились фотографии с вашим изображением.<br \/><\/li>\n<li>В приложении в журнале событий под вашим фото нажмите кнопку «Свой», чтобы добавить лицо в список лиц для открывания домофона.<br \/><\/li>\n<li>При необходимости можно добавить несколько своих лиц для лучшего распознавания (в головном уборе, в очках, с макияжем, с разными причёсками, в инфракрасной подсветке в тёмное время суток).<\/li>\n<\/ol><\/p><span class=\"inbox-message-time\">15:15<\/span><\/div><\/div><span class=\"inbox-date\">16 июл 2021<\/span><div class=\"inbox-message-primary\"><i class=\"inbox-message-icon icon-avatar\"><\/i><div class=\"inbox-message-content\"><p><p><a target=\"_blank\" href=\"https:\/\/stat.lanta-net.ru\">https:\/\/stat.lanta-net.ru<\/a> Имя пользователя: f101182 Пароль: 964f0d7a5<\/p><\/p><span class=\"inbox-message-time\">11:09<\/span><\/div><\/div><span class=\"inbox-date\">29 июн 2021<\/span><div class=\"inbox-message-primary\"><i class=\"inbox-message-icon icon-avatar\"><\/i><div class=\"inbox-message-content\"><p><p>Дорогие жители дома №5б по улице Пионерской! У вас появилась бесплатная возможность протестировать систему открывания домофона с распознаванием по лицу.<br \/>\n<br \/><\/p>\n<ol>\n<li>Установите самую свежую версию приложения «ЛАНТА».<br \/><\/li>\n<li>В приложении в настройках адреса включите опции «Распознавание лиц» и «Вести журнал событий» (журнал событий ведётся для каждой квартиры в отдельности, доступа к событиям других квартир нет).<br \/><\/li>\n<li>Откройте дверь подъезда электронным ключом или совершите вызов в свою квартиру через домофон, чтобы в истории событий появились фотографии с вашим изображением.<br \/><\/li>\n<li>В приложении в журнале событий под вашим фото нажмите кнопку «Свой», чтобы добавить лицо в список лиц для открывания домофона.<br \/><\/li>\n<li>При необходимости можно добавить несколько своих лиц для лучшего распознавания (в головном уборе, в очках, с макияжем, с разными причёсками, в инфракрасной подсветке в тёмное время суток).<\/li>\n<\/ol><\/p><span class=\"inbox-message-time\">20:27<\/span><\/div><\/div><span class=\"inbox-date\">15 янв 2021<\/span><div class=\"inbox-message-primary\"><i class=\"inbox-message-icon icon-avatar\"><\/i><div class=\"inbox-message-content\"><p><p>В вашу учетную запись добавлен новый адрес<\/p><\/p><span class=\"inbox-message-time\">10:38<\/span><\/div><\/div><div class=\"inbox-message-secondary\"><div class=\"inbox-message-content\"><p><p>В вашу учетную запись добавлен новый адрес<\/p><\/p><span class=\"inbox-message-time\">10:32<\/span><\/div><\/div><div class=\"inbox-message-secondary\"><div class=\"inbox-message-content\"><p><p>В вашу учетную запись добавлен новый адрес<\/p><\/p><span class=\"inbox-message-time\">10:30<\/span><\/div><\/div><div class=\"inbox-message-secondary\"><div class=\"inbox-message-content\"><p><p>Ваш пароль на портале видеонаблюдения tD3dcU<\/p><\/p><span class=\"inbox-message-time\">10:30<\/span><\/div><\/div><div class=\"inbox-message-secondary\"><div class=\"inbox-message-content\"><p><p>Ваш код подтверждения: 5749<\/p><\/p><span class=\"inbox-message-time\">10:23<\/span><\/div><\/div><\/div>\n<script type=\"application\/javascript\">\n\/\/    scrollingElement = (document.scrollingElement || document.body)\n\/\/    scrollingElement.scrollTop = scrollingElement.scrollHeight;\n<\/script>\n<\/body>\n<\/html>"}}
    response = {'code':200,'name':'OK','message':'Хорошо','data':{'basePath': 'https:\/\/dm.lanta.me\/', 'code': 'Hello Word'}}
    return jsonify(response)

@app.route('/api/inbox/readed', methods=['POST'])
async def inbox_readed():
    global response
    access_verification(request.headers)
    request_data = json_verification(request)
    return "Hello, World!"

@app.route('/api/inbox/unreaded', methods=['POST'])
async def inbox_unreaded():
    global response
    access_verification(request.headers)
#    if not request.get_json():
#        response = {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'}
#        abort (422)
#    request_data = request.get_json()
    response = {'code':200,'name':'OK','message':'Хорошо','data':{'count':0,'chat':0}}
    return jsonify(response)


@app.route('/api/issues/action', methods=['POST'])
async def issues_action():
    global response
    access_verification(request.headers)
    request_data = json_verification(request)
    return "Hello, World!"

@app.route('/api/issues/comment', methods=['POST'])
async def issues_comment():
    global response
    access_verification(request.headers)
    request_data = json_verification(request)
    return "Hello, World!"

@app.route('/api/issues/create', methods=['POST'])
async def issues_create():
    global response
    access_verification(request.headers)
    request_data = json_verification(request)
    response = {'code':200,'name':'OK','message':'Хорошо', 'data':"123"}
    return jsonify(response)

@app.route('/api/issues/listConnect', methods=['POST'])
async def issues_listConnect():
    global response
    access_verification(request.headers)
#    if not request.get_json():
#        response = {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'}
#        abort (422)
#    request_data = request.get_json()
    response = app.response_class(status=204, mimetype='application/json')
    return response

@app.route('/api/pay/getDetail', methods=['POST'])
async def pay_getDetail():
    global response
    phone = access_verification(request.headers)
    request_data = json_verification(request)
    login = str(request_data['clientId'])
    year = str(request_data['year'])
    response = {'code':200,'name':'OK','message':'Хорошо','data':getDetail(login, year)}
    return jsonify(response)

@app.route('/api/pay/getInvoice', methods=['POST'])
async def pay_getInvoice():
    global response
    phone = access_verification(request.headers)
    request_data = json_verification(request)
    login = str(request_data['clientId'])
    amount = float(request_data['amount'])
    row = newInvoice(login, amount, phone, "")
    number = str(row['invoice_num'])
    clientName = row['clientName']
    date = datetime.datetime.now().strftime('%d.%m.%Y')
    new_invoice = create_invoice(number,date,clientName,login,amount)
    response = {'code':200,'name':'OK','message':'Хорошо','data':{"invoice":str(new_invoice),"number":number,"date":date}}
    return jsonify(response)

@app.route('/api/pay/getReceipt', methods=['POST'])
async def pay_getReceipt():
    global response
    phone = access_verification(request.headers)
    request_data = json_verification(request)
    login = str(request_data['clientId'])
    receiptId = int(request_data['receiptId'])
    row =getReceipt(login, receiptId)
    number = str(request_data['receiptId'])
    receipt = create_receipt(number, row['end'], login, row['customer'], row['dsc'], row['service'], row['start'], row['end'], row['sum'])
    response = {'code':200,'name':'OK','message':'Хорошо','data':{"receipt":receipt,"number":number,"date":row['date']}}
    return jsonify(response)

@app.route('/api/pay/prepare', methods=['POST'])
async def pay_prepare():
    global response
    phone = access_verification(request.headers)
    request_data = json_verification(request)
    new_invoice = Invoices(invoice_id = None, invoice_time = None, invoice_pay = None, contract = str(request_data['clientId']), amount = int(request_data['amount']))
    db.session.add(new_invoice)
    db.session.commit()
#    response = []
#    response = {'code':200,'name':'OK','message':'Хорошо','data':str(new_invoice.invoice_id)}
#    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
#    logging.debug(repr(request_data['clientId']))
#    logging.debug(repr(request_data['amount']))
#    response = requests.post(billing_url + "createinvoice", headers={'Content-Type':'application/json'}, data=json.dumps({'login': request_data['clientId'], 'amount' : request_data['amount'], 'phone' : phone})).json()
#    response = {'code':200,'name':'OK','message':'Хорошо','data':str(newInvoice(request_data['clientId'], float(request_data['amount'])/100, phone, "SmartYard")['invoice_id'])}
    response = {'code':200,'name':'OK','message':'Хорошо','data':str(new_invoice.invoice_id)}
    return jsonify(response)

@app.route('/api/pay/process', methods=['POST'])
async def pay_process():
    global response
    access_verification(request.headers)
    request_data = json_verification(request)
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    logging.debug(repr(request_data['paymentId']))
    logging.debug(repr(request_data['sbId']))
    response = {'code':200,'name':'OK','message':'Хорошо','data':'Платеж в обработке'}
    return jsonify(response)

@app.route('/api/pay/register', methods=['POST'])
async def pay_register():
    global response
    phone = access_verification(request.headers)
    request_data = json_verification(request)
    if not 'orderNumber' in request_data or not 'amount' in request_data:
        response = {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'}
        abort (422)
    orderNumber = request_data['orderNumber']
    contract = 'Оплата по договору ' #+ str(db.session.query(Invoices.contract).filter_by(invoice_id=int(orderNumber)).first()[0])
    #db.session.remove()
    amount = request_data['amount']

    kassa = 'ukassa'

    if kassa == 'ukassa':
        #ukassa_user = '460423'
        #ukassa_passwd = 'test_t8_ifceDzSLHkX9zcJqhQ48h07qEt6Nh_KzsCVp5kLo'
        uurl = 'https://' + ukassa_user + ':' + ukassa_passwd  + '@api.yookassa.ru/v3/payments/'
        udata = {'amount': {'value': str(float(amount)/100),'currency': 'RUB'},'capture': True,'confirmation': {'type': 'redirect','return_url': 'https://axiostv.ru' },'description': contract, 'metadata': {'orderNumber': str(request_data['orderNumber'])}}
        uheaders = {'Content-Type':'application/json','Idempotence-Key':str(uuid.uuid4())}
        uresponse = requests.post(uurl, headers=uheaders, data=json.dumps(udata))
        #print(f"{uresponse.json()}")
        #print(f"{uuid.UUID(uresponse.json()['id'])}")
        #print(f"{uresponse.json()['amount']['value']}")
        #print(f"{uresponse.json()['metadata']['orderNumber']}")
        #print(f"{uresponse.json()['confirmation']['confirmation_url']}")
    elif kassa == 'sber':
        bank_url = 'https://securepayments.sberbank.ru/payment/rest/register.do'
        returnUrl = serverurl + '/success_payment.html'
        failUrl = serverurl + '/failed_payment.html'
        sber_params = (('userName',sber_user),('password',sber_passwd),('orderNumber',orderNumber),('amount',amount),('returnUrl',returnUrl),('failUrl',failUrl))
        #print(f"Sber params:  {sber_params}")
        sresponse = requests.get(bank_url, headers={'Content-Type':'application/x-www-form-urlencoded'}, params=sber_params)
        #print(f"Sber params:  {sresponse.json()}")
    elif kassa == 'ckassa':
        contract = db.session.query(Invoices.contract).filter_by(invoice_id=int(orderNumber)).first()[0]
        db.session.remove()
        if int(amount) < 5000:
            amount = 5000
        bank_url = 'https://oapi.ckassa.ru/api-shop/rs/pay-url/create-qr?service-code=111-11159-2&amount=' + str(amount) + '&property=НОМЕР_ДОГОВОРА|' + str(contract)
        cresponse = requests.get(bank_url)
    else:
        return ''
    try:
        if kassa == 'ukassa':
            orderId = str(uresponse.json()['metadata']['orderNumber'])
            formUrl = str(uresponse.json()['confirmation']['confirmation_url'])
            code = uresponse.status_code
        elif kassa == 'sber':
            orderId = str(sresponse.json()['orderId'])
            formUrl = str(sresponse.json()['formUrl'])
            code = sresponse.status_code
        elif kassa == 'ckassa':
            orderId = str(orderNumber)
            formUrl = str(cresponse.text)
            code = cresponse.status_code
        else:
            return ''
        print(f"PAY params:  {orderNumber}  {orderId}  {formUrl}")
        #formUrl = 'https://axiostv.ru'
        if code == 200:
            response = {'code':code,'name':'OK','message':'Хорошо','data':{'orderId':orderId, 'formUrl':formUrl}}
            return jsonify(response)
        else:
            print(f"Error kassa:  {code}")
    except KeyError:
        pass
    response = {'code':403,'name':'Error Bank','message':'Ошибка Банка'}
    return jsonify(response)

@app.route('/api/sip/helpMe', methods=['POST'])
async def sip_helpMe():
    global response
    access_verification(request.headers)
    helpdeskphone = os.getenv('HELPDESKPHONE')
    response = {'code':200,'name':'OK','message':'Хорошо','data':{'server':shortserverurl, 'port':5401, 'transport':'udp', 'extension':'123', 'pass':'123', 'dial':helpdeskphone}}
    return jsonify(response)

@app.route('/api/user/addMyPhone', methods=['POST'])
async def user_addMyPhone():
    global response
    access_verification(request.headers)
    request_data = json_verification(request)
    if not 'login' in request_data or not 'password' in request_data:
        response = {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'}
        abort (422)
    login = request_data['login']
    password = request_data['password']
    if 'comment' in request_data:
        comment = request_data['comment']
    if 'notification' in request_data:
        notification = request_data['notification']
    response = app.response_class(status=204, mimetype='application/json')
    return response

@app.route('/api/user/appVersion', methods=['POST'])
async def user_appVersion():
    global response
    phone = access_verification(request.headers)
    request_data = json_verification(request)
    if not 'version' in request_data or not 'platform' in request_data:
        response = {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'}
        abort (422)
    version = request_data['version']
    platform = request_data['platform']
    try:
        manufacturer = request_data['manufacturer']
        model = request_data['model']
        osver= request_data['osVer']
    except:
        manufacturer = ''
        model = ''
        osver = ''
    if version != None and (platform == 'android' or platform == 'ios' or platform == 'harmony'):
        db.session.query(Users).filter_by(userphone=int(phone)).update({'version' : version, 'platform' : platform, 'manufacturer': manufacturer, 'model': model, 'osver': osver})
        db.session.commit()
        db.session.remove()
        if platform == 'ios':
            upgrade = ios_upgrade
            force_upgrade = ios_force_ugrade
        elif platform == 'android':
            upgrade = android_upgrade
            force_upgrade = android_force_ugrade
        else:
            upgrade = harmony_upgrade
            force_upgrade = harmony_force_ugrade
        if int(version) < force_upgrade:
            data_response = 'force_upgrade'
        elif int(version) < upgrade:
            data_response = 'upgrade'
        else:
            data_response = 'none'
        response = {'code':200,'name':'OK','message':'Хорошо','data':data_response}
        return jsonify(response)
    else:
        response = {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'}
        abort (422)

@app.route('/api/user/confirmCode', methods=['POST'])
async def user_confirmCode():
    global response
    request_data = json_verification(request)
    if (not 'userPhone' in request_data) or len(request_data['userPhone'])!=11 or (not 'smsCode' in request_data) or len(request_data['smsCode'])!=4:
        response = {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'}
        abort(422)
    userPhone = request_data['userPhone']
    try:
        smsCode = db.session.query(Temps.smscode).filter(Temps.userphone==int(userPhone)).first()[0]
        db.session.remove()
    except:
        response = {"code":404,"name":"Not Found","message":"Не найдено"}
        abort(404)
    if smsCode != int(request_data['smsCode']):
        response = {"code":403,"name":"Пин-код введен неверно","message":"Пин-код введен неверно"}
        abort(403)
    accessToken = str(uuid.uuid4())
    if not 'name' in request_data:
        request_data['name'] = None
    if not 'patronymic' in request_data:
        request_data['patronymic'] = None
    if not 'email' in request_data:
        request_data['email'] = None
    exists = db.session.query(db.session.query(Users).filter_by(userphone=int(userPhone)).exists()).scalar()
    db.session.remove()
    if exists:
        db.session.query(Users).filter_by(userphone=int(userPhone)).update({'uuid' : accessToken})
        db.session.commit()
        db.session.remove()
    else:
        new_user = Users(uuid = accessToken, userphone = int(request_data['userPhone']), name = request_data['name'], patronymic = request_data['patronymic'], email = request_data['email'], videotoken = None, uid = None, vttime = datetime.datetime.now(), strims = None, pushtoken = None, platform = None, version = None, manufacturer = None, model = None, osver = None, notify = True, money = True)
        db.session.add(new_user)
        db.session.commit()
        db.session.remove()
    db.session.query(Temps).filter_by(userphone=int(userPhone)).delete()
    db.session.commit()
    db.session.remove()
    response = {'code':200,'name':'OK','message':'Хорошо','data':{'accessToken':accessToken,'names':{'name':request_data['name'],'patronymic':request_data['patronymic']}}}
    return jsonify(response)

@app.route('/api/user/notification', methods=['POST'])
async def user_notification():
    global response
    phone = access_verification(request.headers)
    if request.get_json():
        request_data = request.get_json()
        if 'money' in request_data:
            money = str2bool(request_data['money'])
            db.session.query(Users).filter_by(userphone=int(phone)).update({'money' : money})
            db.session.commit()
            db.session.remove()
        if 'enable' in request_data:
            enable = str2bool(request_data['enable'])
            db.session.query(Users).filter_by(userphone=int(phone)).update({'notify' : enable})
            db.session.commit()
            db.session.remove()
    row = [r._asdict() for r in db.session.query(Users.money, Users.notify).filter_by(userphone=int(phone)).all()]
    db.session.remove()
    money = bool2str(row[0]['money'])
    enable = bool2str(row[0]['notify'])
    response = {'code':200,'name':'OK','message':'Хорошо','data':{'money':money,'enable':enable}}
    return jsonify(response)

@app.route('/api/user/ping', methods=['POST'])
async def user_ping():
    global response
    access_verification(request.headers)
    response = app.response_class(status=204, mimetype='application/json')
    return response

@app.route('/api/user/pushTokens', methods=['POST'])
async def user_pushTokens():
    global response
    access_verification(request.headers)
    response = {'code':200,'name':'OK','message':'Хорошо','data':{'pushToken':'fnTGJUfJTIC61WfSKWHP_N:APA91bGbnS3ck-cEWO0aj4kExZLsmGGmhziTu2lfyvjIpbmia5ahfL4WlJrr8DOjcDMUo517HUjxH4yZm0m5tF89CssdSsmO6IjcrS1U_YM3ue2187rc9ow9rS0xL8Q48vwz2e6j42l1','voipToken':'off'}}
    return jsonify(response)

@app.route('/api/user/registerPushToken', methods=['POST'])
async def user_registerPushToken():
    global response
    phone = access_verification(request.headers)
    request_data = json_verification(request)
    if not 'platform' in request_data:
        response = {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'}
        abort (422)
    platform = request_data['platform']
    if 'pushToken' in request_data:
        pushtoken = request_data['pushToken']
        db.session.query(Users).filter_by(userphone=int(phone)).update({'pushtoken' : pushtoken, 'platform' : platform})
        db.session.commit()
        db.session.remove()
    if 'voipToken' in request_data:
        voipToken = request_data['voipToken']
    if 'production' in request_data:
        production = request_data['production']
    response = app.response_class(status=204, mimetype='application/json')
    return response

@app.route('/api/user/requestCode', methods=['POST'])
async def user_requestCode():
    global response
    request_data = json_verification(request)
    if (not 'userPhone' in request_data) or len(request_data['userPhone'])!=11:
        response = {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'}
        abort (422)
    user_phone = int(request_data['userPhone'])
    if user_phone == int(testuser):
        sms_code = int(testpass)
    else:
        sms_code = int(str(randint(1, 9)) + str(randint(0, 9)) + str(randint(0, 9)) + str(randint(0, 9)))
        sms_text = os.getenv('SMS_TEXT') + str(sms_code)
    temp_user = Temps(userphone=user_phone, smscode=sms_code)
    db.session.query(Temps).filter_by(userphone=int(user_phone)).delete()#перед этим добавить проверку на время и ответ ошибкой!
    db.session.add(temp_user)
    db.session.commit()
    db.session.remove()
    if not user_phone == int(testuser):
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
    response = app.response_class(status=204, mimetype='application/json')
    return response

@app.route('/api/user/restore', methods=['POST'])
async def user_restore():
    global response
    access_verification(request.headers)
    request_data = json_verification(request)
    if not 'contract' in request_data:
        response = {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'}
        abort (422)
    contract = request_data['contract']
    if (not 'contactId' in request_data) and (not 'code' in request_data):
        response = {'code':200,'name':'OK','message':'Хорошо','data':[{'id':'bfe5bc9e5d2b2501767a7589ec3c485c','contact':'sb**@*********.ru','type':'email'},{'id':'064601c186c73c5e47e8dedbab90dd11','contact':'8 (964) ***-*000','type':'phone'}]}
        return jsonify(response)
    if 'contactId' in request_data and (not 'code' in request_data):
        contactId = request_data['contactId']
        #print(f"Кто-то сделал POST запрос contactId и передал {contactId}")
        response = app.response_class(status=204, mimetype='application/json')
        return response
    if (not 'contactId' in request_data) and 'code' in request_data:
        code = request_data['code']
        if code ==  code:
            #print(f"Кто-то сделал POST запрос code и передал {code}")
            response = app.response_class(status=204, mimetype='application/json')
            return response
        else:
            response = {'code':403,'name':'Forbidden','message':'Запрещено'}
            abort (403)
    if 'comment' in request_data:
        comment = request_data['comment']
    if 'notification' in request_data:
        notification = request_data['notification']

@app.route('/api/user/sendName', methods=['POST'])
async def user_sendName():
    global response
    phone = access_verification(request.headers)
    request_data = json_verification(request)
    if not 'name' in request_data:
        response = {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'}
        abort (422)
    if not 'patronymic' in request_data:
        request_data['patronymic'] = None
    name = request_data['name']
    patronymic = request_data['patronymic']
    db.session.query(Users).filter_by(userphone=int(phone)).update({'name' : name, 'patronymic' : patronymic})
    db.session.commit()
    response = app.response_class(status=204, mimetype='application/json')
    return response

@app.route('/api/user/getBillingList', methods=['POST'])
async def user_getBillingList():
    global response
    userphone = access_verification(request.headers)
    if welcome:
        code = 201
        billList = []
    else:
        billList = billingList(userphone)
        if len(billList) == 0:
            code = 204
        else:
            code = 200
    Billingresponse = {'code':code,'name':'OK','message':'Хорошо','data':billList}
    return jsonify(Billingresponse)

@app.route('/api/images/<imgfile>', methods=['GET'])
async def get_images(imgfile):
    global response
    #access_verification(request.headers)
    device_uuid = imgfile.split('.')[0]
    url = db.session.query(Devices.camshot).filter(Devices.device_uuid==device_uuid).first()[0]
    db.session.remove()
    fullfileurl = slideshowdir + '/' + imgfile
    getcamshot(url,fullfileurl)
    return send_file(fullfileurl)

@app.route('/api/hcs/appealsCategory', methods=['POST'])
async def hcs_appealscategory():
    global response
    access_verification(request.headers)
    request_data = json_verification(request)
    companyId = 1
    appealCategory = []
    async with get_session() as session:
        result = (await session.execute(select(Categorys.categoryId, Categorys.categoryName).where(or_(Categorys.companyId==None, Categorys.companyId==companyId)))).all()
    for i in result:
        appealCategory.append({'categoryId':i[0], 'categoryName':i[1]})
    response = {'code':200,'name':'OK','message':'Хорошо','data':appealCategory}
    return jsonify(response)

@app.route('/api/hcs/appealsList', methods=['POST'])
async def hcs_appealsList():
    global response
    access_verification(request.headers)
    request_data = json_verification(request)
    if not 'houseId' in request_data:
        response = {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'}
        return response
    if int(request_data['houseId']) == 0:
        response = app.response_class(status=404, mimetype='application/json')
        return response
    companyId = 1
    docPath = 'https://sa.axiostv.ru/appealdoc/'
    uid = request_data['houseId']
    appealsList = []
    async with get_session() as session:
        types = (await session.execute(select(Categorys.categoryId, Categorys.categoryName).where(or_(Categorys.companyId==None, Categorys.companyId==companyId)))).all()
        appeals = (await session.execute(select(Appeals.appealId, Appeals.createdUtc, Appeals.category, Appeals.description, Appeals.createdDoc , Appeals.status, Appeals.statusDescription, Appeals.workerDescription).where(Appeals.companyId==companyId, Appeals.uid==uid).order_by(Appeals.appealId.desc()))).all()
        #await session.close()
    for i in appeals:
        for t in types:
            if t[0] == i[2]:
                type = t[1]
                break
        createdDoc = docPath + i[4] if i[4] else ''
        statusDescription = [] if i[6] == None else i[6]
        workerDescription = [] if i[7] == None else i[7]
        appealsList.append({'appealsId':i[0], 'createdUtc':i[1].strftime("%Y-%m-%d %H:%M:%S"), 'type':type, 'description':i[3], 'createdDoc':createdDoc, 'status':i[5], 'statusDescription':statusDescription, 'workerDescription':workerDescription})
    appealsList.append({'appealsId':10, 'createdUtc':'2023-04-20 1:30:00', 'type':'Водоотведение', 'description':'Демо - Забита канализация в ванной комнате', 'createdDoc':'https://sa.axiostv.ru/appealdoc/142212.jpg', 'status':14, 'statusDescription':[{'stDesc':'Принято', 'stUtc':'2023-04-20 11:36:00'},{'stDesc':'Назначен исполнитель', 'stUtc':'2023-04-20 11:37:00'},{'stDesc':'Принято исполнителем', 'stUtc':'2023-04-20 11:38:00'},{'stDesc':'Выполнено', 'stUtc':'2023-04-20 14:18:00'},{'stDesc':'Закрыто', 'stUtc':'2023-04-20 14:20:00'}], 'workerDescription':[{'wrDoc':'https://sa.axiostv.ru/appealdoc/111543.jpg', 'wrDesc':'Найден засор', 'wrUtc':'2023-04-20 12:00:00'},{'wrDoc':'https://sa.axiostv.ru/appealdoc/111623.jpg', 'wrDesc':'Прочищена часть трубы', 'wrUtc':'2023-04-20 12:30:00'},{'wrDoc':'https://sa.axiostv.ru/appealdoc/111641.jpg', 'wrDesc':'Заменено часть трубы и отвод', 'wrUtc':'2023-04-20 13:30:00'}]})
    appealsList.append({'appealsId':11, 'createdUtc':'2023-04-20 20:30:00', 'type':'Электричество', 'description':'Демо - Не горит лампочка в лифтовом холе 5-го этажа', 'createdDoc':'https://sa.axiostv.ru/appealdoc/203932.jpg', 'status':14, 'statusDescription':[{'stDesc':'Принято', 'stUtc':'2023-04-20 20:32:00'},{'stDesc':'Назначен исполнитель', 'stUtc':'2023-04-20 20:34:00'},{'stDesc':'Принято исполнителем', 'stUtc':'2023-04-20 20:35:00'},{'stDesc':'Выполнено', 'stUtc':'2023-04-20 20:45:00'},{'stDesc':'Закрыто', 'stUtc':'2023-04-20 20:46:00'}], 'workerDescription':[{'wrDoc':'https://sa.axiostv.ru/appealdoc/111623.jpg', 'wrDesc':'Работал не покладая рук', 'wrUtc':'2023-04-20 11:30:00'},{'wrDoc':'https://sa.axiostv.ru/appealdoc/111641.jpg', 'wrDesc':'Закончил работу', 'wrUtc':'2023-04-20 11:30:00'}]})
    appealsList.append({'appealsId':12, 'createdUtc':'2023-04-21 11:30:00', 'type':'Водоснабжение', 'description':'Демо - 1234567890123456789012345678901234567890123456', 'createdDoc':'https://sa.axiostv.ru/appealdoc/203932.jpg', 'status':14, 'statusDescription':[{'stDesc':'Принято', 'stUtc':'2023-04-21 11:40:00'},{'stDesc':'Назначен исполнитель', 'stUtc':'2023-04-21 11:42:00'},{'stDesc':'Принято исполнителем', 'stUtc':'2023-04-21 11:45:00'}], 'workerDescription':[{'wrDoc':'https://sa.axiostv.ru/appealdoc/111623.jpg', 'wrDesc':'Прибыл на место', 'wrUtc':'2023-04-20 11:30:00'},{'wrDoc':'https://sa.axiostv.ru/appealdoc/111641.jpg', 'wrDesc':'Начал осмотр', 'wrUtc':'2023-04-20 11:30:00'}]})
    print(f"{appealsList}")
    response = {'code':200,'name':'OK','message':'Хорошо','data':appealsList}
    return jsonify(response)

@app.route('/api/hcs/newAppeal', methods=['POST'])
async def hcs_newAppeal():
    global response
    phone = access_verification(request.headers)
    request_data = json_verification(request)
    appealdoc = None
    if request_data['createdDoc'] != "":
        binary_content = base64.b64decode(request_data['createdDoc'])
        appealdoc = str(uuid.uuid4()) + ".jpg"
        fullappealdoc = appealdocdir + "/" + appealdoc
        with open(fullappealdoc, 'wb') as file:
            file.write(binary_content)
    companyId = 1
    phone = int('7' + str(phone)[1:])
    uid = request_data['houseId']
    address = fullAddressFromUid(uid)
    category = int(request_data['type'])
    description = request_data['description']
    createdDoc = appealdoc
    async with get_session() as session:
        new_appeal = Appeals(appealId=(await session.execute(select(func.count(Appeals.appealId)).where(Appeals.companyId==companyId))).scalar()+1, companyId=companyId, phone=phone, uid = uid, address=address, category=category, description=description, createdDoc=createdDoc, status=1)
        session.add(new_appeal)
        await session.commit()
        #await session.close()
#    response = app.response_class(status=204, mimetype='application/json')
#    return response
    code = 204
    newAppealResponse = {'code':code,'name':'OK','message':'Хорошо'}
    return jsonify(newAppealResponse)

@app.route('/api/hcs/listPay', methods=['POST'])
async def list_pay():
    global response
    phone = access_verification(request.headers)
    request_data = json_verification(request)
    listPayData = []
    if phone == 89103523377:
        listPayData.append({'name':'ООО УК \"Парус\"','client':'И***в Иван Иванович', 'paymentlink':'https://oapi.ckassa.ru/api-shop/rs/pay-url/create-qr?service-code=111-11159-2&amount=95000&property=НОМЕР_ДОГОВОРА|10077','fakeLink':True,'balance':0,'amount':95000,'currentpayment':95000,'arrears':0})
        listPayData.append({'name':'ООО \"РВК-Липецк\"','client':'И***в Иван Иванович', 'paymentlink':'https://oapi.ckassa.ru/api-shop/rs/pay-url/create-qr?service-code=111-11159-2&amount=63200&property=НОМЕР_ДОГОВОРА|10077','fakeLink':True,'balance':0,'amount':63200,'currentpayment':63200,'arrears':0})
    listPayResponse = {'code':200,'name':'OK','message':'Хорошо', 'data':listPayData}
    return jsonify(listPayResponse)

@app.route('/api/sh/getRooms', methods=['POST'])
async def sh_getRooms():
    global response
    access_verification(request.headers)
    resRooms = []
    resRooms.append({'roomId':'20553542-be86-4209-b74c-75b3db3269be', 'name':'Спальня', 'priority':3, 'visible':True})
    resRooms.append({'roomId':'5367a867-198d-4559-ab94-4e1ac99bf2dc', 'name':'Зал', 'priority':2, 'visible':True})
    resRooms.append({'roomId':'2b4379b4-469b-45d3-b52e-2e0131656ace', 'name':'Прихожая', 'priority':1, 'visible':True})
    resRooms.append({'roomId':'7a30101b-058a-499f-9f12-3961320d24c1', 'name':'Ванная', 'priority':4, 'visible':True})
    resRooms.append({'roomId':'168b1156-e9df-433b-8a5c-7937f18af323', 'name':'Кухня', 'priority':5, 'visible':True})
    response = {'code':200,'name':'OK','message':'Хорошо','data':resRooms}
    return jsonify(response)

@app.route('/api/sh/setRoom', methods=['POST'])
async def sh_setRoom():
    global response
    access_verification(request.headers)
    request_data = json_verification(request)
    code = 204
    setRoomResponse = {'code':code,'name':'OK','message':'Хорошо'}
    return jsonify(setRoomResponse)

@app.route('/api/sh/getItems', methods=['POST'])
async def sh_getItems():
    global response
    access_verification(request.headers)
    resItemsTypes = ['lamp', 'relay', 'conditioner', 'boiler', 'openedSensor', 'motionSensor', 'presenceSensor', 'fireSensor', 'smokeSensor', 'oxygenSensor', 'carbonSensor']
    resItems = []
    resItems.append({'roomId':'2b4379b4-469b-45d3-b52e-2e0131656ace','itemId':'ec851578-c64e-42df-ba12-9257a1d82f18','type':'lamp','name':'Торшер','priority':2,'visible':True,'getItemData':{}})
    resItems.append({'roomId':'2b4379b4-469b-45d3-b52e-2e0131656ace','itemId':'ff3c2ecd-2a9a-4d45-a209-a97c5e1f2366','type':'conditioner','name':'Кондиционер','priority':1,'visible':True,'getItemData':{}})
    resItems.append({'roomId':'2b4379b4-469b-45d3-b52e-2e0131656ace','itemId':'8e00c1cf-bc2b-4938-aa28-9a4b887ad58b','type':'relay','name':'Реле1','priority':3,'visible':True,'getItemData':{}})
    resItems.append({'roomId':'2b4379b4-469b-45d3-b52e-2e0131656ace','itemId':'a40a3881-ddac-4433-a3cb-48d8fd1a55ae','type':'lamp','name':'Люстра','priority':4,'visible':True,'getItemData':{}})
    resItems.append({'roomId':'2b4379b4-469b-45d3-b52e-2e0131656ace','itemId':'e1607546-35ef-4434-b51a-02f6805da1b1','type':'lamp','name':'Бра','priority':5,'visible':True,'getItemData':{}})
    resItems.append({'roomId':'2b4379b4-469b-45d3-b52e-2e0131656ace','itemId':'82f6894d-ccce-492f-b42f-82ada9d32a9f','type':'lamp','name':'Настольная лампа','priority':6,'visible':True,'getItemData':{}})
    resItems.append({'roomId':'2b4379b4-469b-45d3-b52e-2e0131656ace','itemId':'15fdca24-9fc1-40f4-babd-b41856f785eb','type':'lamp','name':'Зеркало','priority':7,'visible':True,'getItemData':{}})
    resItems.append({'roomId':'2b4379b4-469b-45d3-b52e-2e0131656ace','itemId':'3f3c9051-7d84-4a44-a9f0-b8aabff6a012','type':'relay','name':'Реле2','priority':8,'visible':True,'getItemData':{}})
    resItems.append({'roomId':'5367a867-198d-4559-ab94-4e1ac99bf2dc','itemId':'36c69310-b6a9-4613-8dd9-ced7cde6b65b','type':'relay','name':'Реле3','priority':3,'visible':True,'getItemData':{}})
    resItems.append({'roomId':'5367a867-198d-4559-ab94-4e1ac99bf2dc','itemId':'031b7fea-0942-494c-974f-ca10fc556312','type':'lamp','name':'Люстра','priority':1,'visible':True,'getItemData':{}})
    resItems.append({'roomId':'5367a867-198d-4559-ab94-4e1ac99bf2dc','itemId':'77ccb241-063d-41b4-b7c6-c88637bae303','type':'relay','name':'Реле4','priority':2,'visible':True,'getItemData':{}})
    resItems.append({'roomId':'5367a867-198d-4559-ab94-4e1ac99bf2dc','itemId':'9fcea3bd-9476-4ead-a963-14330f2203f7','type':'relay','name':'Реле5','priority':4,'visible':True,'getItemData':{}})
    resItems.append({'roomId':'5367a867-198d-4559-ab94-4e1ac99bf2dc','itemId':'8235d102-b414-4459-a25c-18607cb12399','type':'relay','name':'Реле6','priority':5,'visible':True,'getItemData':{}})
    resItems.append({'roomId':'5367a867-198d-4559-ab94-4e1ac99bf2dc','itemId':'19abccb4-1a2a-4870-9e15-82121a82e393','type':'relay','name':'Реле7','priority':6,'visible':True,'getItemData':{}})
    response = {'code':200,'name':'OK','message':'Хорошо','data':resItems}
    return jsonify(response)

@app.route('/api/sh/setItem', methods=['POST'])
async def sh_setItem():
    global response
    access_verification(request.headers)
    request_data = json_verification(request)
    code = 204
    setItemResponse = {'code':code,'name':'OK','message':'Хорошо'}
    return jsonify(setItemResponse)

@app.route('/asterisk/aors/single', methods=['POST'])
async def aors_single():
    #print(f"{str(request.form['id']).split('@',1)[0]}")
    aors_data = ''
    if len(str(request.form['id']).split('@',1)[0]) == 6 and str(request.form['id']).split('@',1)[0][0] == '1':
        domophoneid = int(str(request.form['id']).split('@',1)[0]) - 100000
        row = [r._asdict() for r in db.session.query(Devices.domophoneid).filter(Devices.domophoneid == domophoneid).all()]
        db.session.remove()
        try:
            extension = str(row[0]['domophoneid'] + 100000)
            aors_data = {'id':extension, 'max_contacts':'1', 'remove_existing':'yes', 'default_expiration':'600', 'maximum_expiration':'720'}
        except:
            pass
    elif len(str(request.form['id']).split('@',1)[0]) == 10 and str(request.form['id']).split('@',1)[0][0] == '2':
        extension = int(str(request.form['id']).split('@',1)[0])
        cred = r.get('mobile_extension_' + str(extension))
        if cred:
            aors_data = {'id':extension, 'max_contacts':'1', 'remove_existing':'yes'}
    elif len(str(request.form['id']).split('@',1)[0]) == 10 and str(request.form['id']).split('@',1)[0][0] == '4':
        monitorid = int(str(request.form['id']).split('@',1)[0]) - 4000000000
        row = [r._asdict() for r in db.session.query(Devices.monitorid).filter(Devices.monitorid == monitorid).all()]
        db.session.remove()
        try:
            extension = str(row[0]['monitorid'] + 4000000000)
            aors_data = {'id':extension, 'max_contacts':'1', 'remove_existing':'yes', 'default_expiration':'600', 'maximum_expiration':'720'}
        except:
            pass
    #print(f"{aors_data}")
    return urllib.parse.urlencode(aors_data)

@app.route('/asterisk/aors/multi', methods=['POST'])
async def aors_multi():
    #print(f"{str(request.form)}")
    aors_data = []
    aors_response = ''
    rows = [r._asdict() for r in db.session.query(Devices.domophoneid,Devices.monitorid).filter((Devices.domophoneid != 0)|(Devices.monitorid != 0)).all()]
    db.session.remove()
    for row in rows:
        extension = '0'
        if row['domophoneid'] != 0:
            extension = str(row['domophoneid'] + 100000)
        elif row['monitorid'] != 0:
            extension = str(row['monitorid'] + 4000000000)
        aors_data.append({'id':extension, 'max_contacts':'1', 'remove_existing':'yes', 'default_expiration':'600', 'maximum_expiration':'720'})
    for item in aors_data:
        aors_response = aors_response + urllib.parse.urlencode(item) + '\n'
    #print(f"{aors_response}")
    return (aors_response)

@app.route('/asterisk/auths/single', methods=['POST'])
async def auths_single():
    #print(f"{str(request.form['id']).split('@',1)[0]}")
    if len(str(request.form['id']).split('@',1)[0]) == 6 and str(request.form['id']).split('@',1)[0][0] == '1':
        domophoneid = int(str(request.form['id']).split('@',1)[0]) - 100000
        row = [r._asdict() for r in db.session.query(Devices.domophoneid,Devices.sippassword).filter(Devices.domophoneid == domophoneid).all()]
        db.session.remove()
        try:
            extension = str(row[0]['domophoneid'] + 100000)
            password = row[0]['sippassword']
            auths_data = {'id':extension, 'username':extension, 'auth_type':'userpass', 'password':password}
        except IndexError:
            auths_data = ''
    elif len(str(request.form['id']).split('@',1)[0]) == 10 and str(request.form['id']).split('@',1)[0][0] == '2':
        extension = int(str(request.form['id']).split('@',1)[0])
        cred = r.get('mobile_extension_' + str(extension))
        if cred:
            auths_data = {'id':extension, 'username':extension, 'auth_type':'userpass', 'password':cred}
    elif len(str(request.form['id']).split('@',1)[0]) == 10 and str(request.form['id']).split('@',1)[0][0] == '4':
        monitorid = int(str(request.form['id']).split('@',1)[0]) - 4000000000
        row = [r._asdict() for r in db.session.query(Devices.monitorid,Devices.sippassword).filter(Devices.monitorid == monitorid).all()]
        db.session.remove()
        try:
            extension = str(row[0]['monitorid'] + 4000000000)
            password = row[0]['sippassword']
            auths_data = {'id':extension, 'username':extension, 'auth_type':'userpass', 'password':password}
        except IndexError:
            auths_data = ''
    else:
        auths_data = ''
    #print(f"{auths_data}")
    return urllib.parse.urlencode(auths_data)

@app.route('/asterisk/auths/multi', methods=['POST'])
async def auths_multi():
    #print(f"{str(request.form)}")
    auths_data = []
    auths_response = ''
    rows = [r._asdict() for r in db.session.query(Devices.domophoneid,Devices.monitorid,Devices.sippassword).filter((Devices.domophoneid != 0)|(Devices.monitorid != 0)).all()]
    db.session.remove()
    for row in rows:
        extension = '0'
        if row['domophoneid'] != 0:
            extension = str(row['domophoneid'] + 100000)
        elif row['monitorid'] != 0:
            extension = str(row['monitorid'] + 4000000000)
        auths_data.append({'id':extension, 'username':extension, 'auth_type':'userpass', 'password':row['sippassword']})
    for item in auths_data:
        auths_response = auths_response + urllib.parse.urlencode(item) + '\n'
    #print(f"{auths_response}")
    return (auths_response)

@app.route('/asterisk/endpoints/single', methods=['POST'])
async def endpoints_single():
    #print(f"{str(request.form['id']).split('@',1)[0]}")
    return_data = ''
    if len(str(request.form['id']).split('@',1)[0]) == 6 and str(request.form['id']).split('@',1)[0][0] == '1':
        domophoneid = int(str(request.form['id']).split('@',1)[0]) - 100000
        row = [r._asdict() for r in db.session.query(Devices.domophoneid).filter(Devices.domophoneid == domophoneid).all()]
        db.session.remove()
        try:
            extension = str(row[0]['domophoneid'] + 100000)
            endpoints_data = {'id':extension, 'auth':extension, 'outbound_auth':extension, 'aors':extension, 'callerid':extension, 'context':'default', 'disallow':'all', 'allow':'alaw,h264', 'rtp_symmetric':'no', 'force_rport':'no', 'rewrite_contact':'yes', 'timers':'no', 'direct_media':'no', 'allow_subscribe':'yes', 'dtmf_mode':'rfc4733', 'ice_support':'no'}
            return_data = urllib.parse.urlencode(endpoints_data)
        except IndexError:
            pass
    elif len(str(request.form['id']).split('@',1)[0]) == 10 and str(request.form['id']).split('@',1)[0][0] == '2':
        extension = int(str(request.form['id']).split('@',1)[0])
        cred = r.get('mobile_extension_' + str(extension))
        if cred:
            endpoints_data = {'id':extension, 'auth':extension, 'outbound_auth':extension, 'aors':extension, 'callerid':extension, 'context':'default', 'disallow':'all', 'allow':'alaw,h264', 'rtp_symmetric':'yes', 'force_rport':'yes', 'rewrite_contact':'yes', 'timers':'no', 'direct_media':'no', 'allow_subscribe':'yes', 'dtmf_mode':'rfc4733', 'ice_support':'yes'}
            return_data = urllib.parse.urlencode(endpoints_data)
    elif len(str(request.form['id']).split('@',1)[0]) == 10 and str(request.form['id']).split('@',1)[0][0] == '4':
        monitorid = int(str(request.form['id']).split('@',1)[0]) - 4000000000
        row = [r._asdict() for r in db.session.query(Devices.monitorid).filter(Devices.monitorid == monitorid).all()]
        db.session.remove()
        try:
            extension = str(row[0]['monitorid'] + 4000000000)
            endpoints_data = {'id':extension, 'auth':extension, 'outbound_auth':extension, 'aors':extension, 'callerid':extension, 'context':'default', 'disallow':'all', 'allow':'alaw,h264', 'rtp_symmetric':'no', 'force_rport':'no', 'rewrite_contact':'yes', 'timers':'no', 'direct_media':'no', 'allow_subscribe':'yes', 'dtmf_mode':'rfc4733', 'ice_support':'no'}
            return_data = urllib.parse.urlencode(endpoints_data)
        except IndexError:
            pass
    #print(f"{endpoints_data}")
    return return_data

@app.route('/asterisk/endpoints/multi', methods=['POST'])
async def endpoints_multi():
    #print(f"{str(request.form)}")
    endpoints_data = []
    endpoints_response = ''
    rows = [r._asdict() for r in db.session.query(Devices.domophoneid,Devices.monitorid).filter((Devices.domophoneid != 0)|(Devices.monitorid != 0)).all()]
    db.session.remove()
    for row in rows:
        extension = '0'
        if row['domophoneid'] != 0:
            extension = str(row['domophoneid'] + 100000)
        elif row['monitorid'] != 0:
            extension = str(row['monitorid'] + 4000000000)
        endpoints_data.append({'id':extension, 'auth':extension, 'outbound_auth':extension, 'aors':extension, 'callerid':extension, 'context':'default', 'disallow':'all', 'allow':'alaw,h264', 'rtp_symmetric':'no', 'force_rport':'no', 'rewrite_contact':'yes', 'timers':'no', 'direct_media':'no', 'allow_subscribe':'yes', 'dtmf_mode':'rfc4733', 'ice_support':'no'})
    for item in endpoints_data:
        endpoints_response = endpoints_response + urllib.parse.urlencode(item) + '\n'
    #print(f"{endpoints_response}")
    return (endpoints_response)

@app.route('/asterisk/extensions/uidFromflatNumber', methods=['POST'])
async def extensions_uidFromflatNumber():
    request_data = json_verification(request)
    domophoneid = int(request_data['domophoneId'])
    result = db.session.query(Rights.uid).join(Devices, Devices.device_id == any_(Rights.uid_right)).filter(Devices.domophoneid == domophoneid).all()
    db.session.remove()
    uids = [row[0] for row in result]
    uid = uidFromUidsAndFlat(uids, int(request_data['flatNumber']))
    return ({'uid':uid})

@app.route('/asterisk/extensions/precall', methods=['POST'])
async def extensions_precall():
    precreq = json_verification(request)
    domophoneid = int(precreq['domophoneId'])
    uid = precreq['uid']
    row = [r._asdict() for r in db.session.query(Devices.device_id, Devices.dtmf, Devices.panelip).filter(Devices.domophoneid==domophoneid).all()][0]
    db.session.remove()
    deviceId = row['device_id']
    panelIp = row['panelip']
    dtmf = row['dtmf']
    autoBlock = 1
    manualBlock = 0
    autoOpen = 0
    whiteRabbit = 0
    intercoms = []
    try:
        rights = []
        rights = db.session.query(Rights.uid_right).filter_by(uid=uid).first()[0]
        db.session.remove()
        deviceIds = []
        deviceIds.append(deviceId)
        isactiv = isActiv(uid, deviceIds)
        if isactiv[deviceId] == 2 and deviceId in rights:
            rows = [r._asdict() for r in db.session.query(Devices.monitorid).filter(Devices.device_id.in_(rights),Devices.device_type==5).all()]
            db.session.remove()
            for intercom in rows:
                intercoms.append(intercom['monitorid'])
            autoBlock = 0
            row = [r._asdict() for r in db.session.query(Settings.asterisk, Settings.guest, Settings.w_rabbit, Settings.whiterabbit).filter_by(uid = uid).all()][0]
            db.session.remove()
            if not row['asterisk']:
                manualBlock = 1
            if row['guest'] >= datetime.datetime.now():
                autoOpen = 1
            if row['w_rabbit'] and row['whiterabbit'] != None and row['whiterabbit'] >= datetime.datetime.now():
                whiteRabbit = 1
    except:
        pass
    precallres = {'autoBlock':autoBlock, 'manualBlock':manualBlock, 'autoOpen':autoOpen, 'whiteRabbit':whiteRabbit, 'deviceId': deviceId, 'deviceIP': panelIp, 'dtmf':dtmf, 'intercoms':intercoms}
    return (precallres)

@app.route('/asterisk/extensions/domophone', methods=['POST'])
async def extensions_domophone():
    domophoneid = int(request.data.decode("utf-8"))
    row = [r._asdict() for r in db.session.query(Devices.device_id, Devices.device_uuid, Devices.title, Devices.dtmf, Devices.panelip).filter(Devices.domophoneid==domophoneid).all()]
    db.session.remove()
    return ({'deviceId': row[0]['device_id'], 'device_uuid': row[0]['device_uuid'], 'deviceIP': row[0]['panelip'], 'dtmf':row[0]['dtmf'], 'callerId':row[0]['title']})

@app.route('/asterisk/extensions/camshot', methods=['POST'])
async def extensions_camshot():
    request_data = json_verification(request)
    domophoneid = int(request_data['domophoneId'])
    row = [r._asdict() for r in db.session.query(Devices.device_uuid, Devices.camshot).filter(Devices.domophoneid==domophoneid).all()]
    db.session.remove()
    fullfileurl = camshotdir + '/' + str(row[0]['device_uuid']) + '.jpg'
    getcamshot(row[0]['camshot'],fullfileurl)
    return ('')

@app.route('/asterisk/extensions/subscribers', methods=['POST'])
async def extensions_subscribers():
    uid = int(request.data.decode("utf-8"))
    subscribers_response = []
    try:
        rights = []
        rights = db.session.query(Rights.uid_right).filter_by(uid=uid).first()[0]
        db.session.remove()
        isactiv = isActiv(uid, rights)
        if 2 in isactiv.values():
            phones = userPhones(uid)
            for phone in phones:
                row = [r._asdict() for r in db.session.query(Users.userphone, Users.pushtoken, Users.platform).filter(Users.userphone == int(phone)).all()]
                db.session.remove()
                platform = 0
                try:
                    if row[0]['platform'] == 'ios':
                        platform = 1
                    if row[0]['platform'] == 'harmony':
                        platform = 2
                    subscribers_response.append({'mobile':str(row[0]['userphone']),'voipEnabled':1,'platform':platform,'tokenType':0,'voipToken':'off','pushToken':row[0]['pushtoken']})
                except IndexError:
                    pass
    except:
        pass
    return jsonify(subscribers_response)

@app.route('/asterisk/extensions/push', methods=['POST'])
async def extensions_push():
    #print(f"{str(json_verification(request))}")
    req = json_verification(request)
    registration_token = req['token']
    image = serverurl + '/camshot' + '/' + str(req['device_uuid']) + ".jpg"
    live = serverurl + '/api/images' + '/' + str(req['device_uuid']) + ".jpg"
    webRtcUrl = ''
    noVideoSip = 'false'
    extime = datetime.datetime.now() - timedelta(minutes=(expire-5))

    try:
        row = [r._asdict() for r in db.session.query(Users.videotoken, Users.vttime, Users.strims).filter_by(pushtoken = req['token']).all()]
        db.session.remove()
        videotoken = row[0]['videotoken']
        vttime = row[0]['vttime']
        strims = row[0]['strims']
        url = 'https://vd.axiostv.ru'
#        if vttime >= extime and req['device_uuid'] in strims:
#            webRtcUrl = url + '/' + str(req['device_uuid']) + '/whep?token=' + str(videotoken)
    except:
        pass

    if req['platform'] == 1:
        platform = 'ios'
    else:
        platform = 'android'
    data = {'server':shortserverurl,'port':'5401','transport':'tcp','extension':str(req['extension']),'pass':req['hash'],'dtmf':str(req['dtmf']),'image':image,'live':live,'webRtcUrl':webRtcUrl,'noVideoSip':noVideoSip,'timestamp':str(int(datetime.datetime.now().timestamp())),'ttl':'30','callerId':req['callerId'],'platform':platform,'houseId':str(req['uid']),'flatNumber':str(req['flatNumber']),'stun': '','stun_transport':'udp','stunTransport':'udp','type':'call'}
    data_old = {'server':shortserverurl,'port':'5401','transport':'tcp','extension':str(req['extension']),'pass':req['hash'],'dtmf':str(req['dtmf']),'image':image,'live':live,'timestamp':str(int(datetime.datetime.now().timestamp())),'ttl':'30','callerId':req['callerId'],'platform':platform,'flatNumber':str(req['flatNumber']),'stun': 'stun:37.235.209.140:3478','stun_transport':'udp','stunTransport':'udp',}
    if req['platform'] == 0:
        message = messaging.Message(android=messaging.AndroidConfig(ttl=datetime.timedelta(seconds=30), priority='high',), data=data, token=registration_token,)
        response = messaging.send(message)
    if req['platform'] == 1:
        print(f"push for iOS")
        message = messaging.Message(apns=messaging.APNSConfig(headers={'apns-priority':'10', 'apns-expiration':str(int(datetime.datetime.now().timestamp()) + 60)},payload=messaging.APNSPayload(aps=messaging.Aps(alert=messaging.ApsAlert(title='Входящий вызов',body=req['callerId'],),category="INCOMING_DOOR_CALL",mutable_content=True,badge=1,sound="default",),),), data=data, token=registration_token,)
#        message = messaging.Message(apns=messaging.APNSConfig(headers={'apns-priority':'10', 'apns-expiration':str(int(datetime.datetime.now().timestamp()) + 60)},payload=messaging.APNSPayload(aps=messaging.Aps(alert=messaging.ApsAlert(title='Входящий вызов',body=req['callerId'],),mutable_content=True,badge=1,sound="default",),),), data=data, token=registration_token,)
        response = messaging.send(message)
        print(f"push {response}")
    if req['platform'] == 2:
        harmony_send_message(data,registration_token)
    return ('')

@app.route('/indoor/uidfromuids', methods=['POST'])
async def uid_from_uids():
    req = json_verification(request)
    uid = uidFromUidsAndFlat(req.get('uids'), int(req.get('flat')))
    return (str(uid))

@app.route('/indoor/newEvent', methods=['POST'])
async def new_event():
    req = json_verification(request)
    data = req.get('sendData')
    uid = 0
    if req.get('uid'):
        uid = int( req.get('uid'))
    else:
        return ""
    data["houseId"] = str(uid)
    title =""
    if req.get('title'):
        title = req.get('title')
    deviceIds = []
    if req.get('deviceId'):
        deviceIds.append(req.get('deviceId'))
    else:
        try:
            deviceIds = db.session.query(Rights.uid_right).filter_by(uid=uid).first()[0]
            db.session.remove()
        except:
            pass
    isactiv = isActiv(uid, deviceIds)
    if 2 in isactiv.values():
        phones = userPhones(uid)
        for phone in phones:
            row = [r._asdict() for r in db.session.query(Users.pushtoken, Users.platform).filter(Users.userphone == int(phone)).all()]
            db.session.remove()
            try:
                registration_token = row[0]['pushtoken']
                if row[0]['platform'] == 'android':
                    message = messaging.Message(android=messaging.AndroidConfig(ttl=datetime.timedelta(seconds=60), priority='high',), data=data, token=registration_token,)
                    response = messaging.send(message)
                if row[0]['platform'] == 'ios':
                    message = messaging.Message(apns=messaging.APNSConfig(headers={'apns-priority':'10', 'apns-expiration':str(int(datetime.datetime.now().timestamp()) + 60)},payload=messaging.APNSPayload(aps=messaging.Aps(alert=messaging.ApsAlert(title=title,body='',),category="INCOMING_DOOR_CALL",mutable_content=True,badge=1,sound="default",),),), data=data, token=registration_token,)
                    response = messaging.send(message)
                if row[0]['platform'] == 'harmony':
                    harmony_send_message(data,registration_token)
            except:
                pass
    return ""

@app.route('/api/worker/workflow', methods=['POST'])
async def worker_workflow():
    workflow = [{'links':{'patch':{'small':'https://images2.imgbox.com/94/f2/NN6Ph45r_o.png','large':'https://images2.imgbox.com/5b/02/QcxHUb5V_o.png'},'article':'https://www.space.com/3590-spacex-falcon-1-rocket-fails-reach-orbit.html'},'success':False,'details':'Забита канализация в кухне','flight_number':1,'name':'Водоотведение','date_utc':'2023-03-24T22:30:00.000Z'},
    {'links':{'patch':{'small':'https://images2.imgbox.com/94/f2/NN6Ph45r_o.png','large':'https://images2.imgbox.com/5b/02/QcxHUb5V_o.png'},'article':'https://www.space.com/3590-spacex-falcon-1-rocket-fails-reach-orbit.html'},'success':True,'details':'Не горит лампочка в лифтовом холе 5-го этажа','flight_number':1,'name':'Электричество','date_utc':'2023-03-24T22:30:00.000Z'},
    {'links':{'patch':{'small':'https://images2.imgbox.com/94/f2/NN6Ph45r_o.png','large':'https://images2.imgbox.com/5b/02/QcxHUb5V_o.png'},'article':'https://www.space.com/3590-spacex-falcon-1-rocket-fails-reach-orbit.html'},'success':False,'details':'В ванной вместо холодной воды идет теплая','flight_number':1,'name':'Водоснабжение','date_utc':'2023-03-24T22:30:00.000Z'},
    {'links':{'patch':{'small':'https://images2.imgbox.com/94/f2/NN6Ph45r_o.png','large':'https://images2.imgbox.com/5b/02/QcxHUb5V_o.png'},'article':'https://www.space.com/3590-spacex-falcon-1-rocket-fails-reach-orbit.html'},'success':True,'details':'Лифт пропускае 5-ый этаж, приезжает на 6-ой','flight_number':1,'name':'Лифт','date_utc':'2023-03-24T22:30:00.000Z'},
    {'links':{'patch':{'small':'https://images2.imgbox.com/94/f2/NN6Ph45r_o.png','large':'https://images2.imgbox.com/5b/02/QcxHUb5V_o.png'},'article':'https://www.space.com/3590-spacex-falcon-1-rocket-fails-reach-orbit.html'},'success':False,'details':'Нет контакта в коннекторе','flight_number':1,'name':'Интернет','date_utc':'2023-03-24T22:30:00.000Z'},
    ]
    return jsonify(workflow)

@app.route('/z5rweb', methods=['POST'])
@auth.login_required
async def z5rweb():
#    print(f"{format(auth.current_user())}")
    if auth.current_user():
        request_data = json_verification(request)
        res_mes_for_z5rweb = []
        mes_for_z5rweb = []
        if 'messages' in request_data:
            messages = request_data['messages']
            for message in messages:
#                print(f"{message}")
                messid = message['id']
                if 'operation' in message:
                    operation = message['operation']
#                    if operation == 'ping':
#                        with open("/var/log/z5rweb_ping.log", "a") as file:
#                            file.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " " + json.dumps(message) + '\n')
#                        controller_ip = '192.168.67.48'
#                        #message['controller_ip']
#                        controller_url = 'http://' + controller_ip
#                        mes_for_z5rweb.append({'id':1, 'operation':'open_door', 'direction': 0})
#                        data= {'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'interval': 10, 'messages': mes_for_z5rweb}
#                        response = requests.post(controller_url, auth=HTTPBA('z5rweb', 'passwd'), headers={'Content-Type':'application/json'}, json=data)
#                        print(f"{response}")
                    if operation == 'power_on':
                        res_mes_for_z5rweb.append({'id':messid, 'operation':'set_active', 'active':1, 'online':1})
                    if operation == 'events':
                        events = len(message['events'])
                        res_mes_for_z5rweb.append({'id':messid,'operation':'events', 'events_success':events})
                    if operation == 'check_access':
                        uid = 0
                        granted = 0
                        card = message['card'][:12]
                        try:
                            uid = db.session.query(Keys.uid).filter_by(key = bytes.fromhex(card)).first()[0]
                            db.session.remove()
                        except:
                            pass
                        if uid > 0:
                            try:
                                rights = []
                                rights = db.session.query(Rights.uid_right).filter_by(uid=uid).first()[0]
                                db.session.remove()
                                isactiv = isActiv(uid, rights)
                                if 2 in isactiv.values():
                                    granted = 1
                            except:
                                pass
                        res_mes_for_z5rweb.append({'id':messid,'operation':'check_access','granted':granted})
                        with open("/var/log/z5rweb_access.log", "a") as file:
                            file.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "uid:" + str(uid) + "card" + card + "granted:" + str(granted) + "message:" + json.dumps(message) + '\n')
        res_for_z5rweb = {'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'interval': 10, 'messages': res_mes_for_z5rweb}
#        print(f"{request_data} \n {res_for_z5rweb} \n")
    return jsonify(res_for_z5rweb)

@app.errorhandler(401)
def not_found(error):
    return make_response(jsonify(response), 401)

@app.errorhandler(403)
def not_found(error):
    return make_response(jsonify(response), 403)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'пользователь не найден'}), 404)

@app.errorhandler(410)
def not_found(error):
    return make_response(jsonify({'error': 'авторизация отозвана'}), 410)

@app.errorhandler(422)
def not_found(error):
    return make_response(jsonify(response), 422)

@app.errorhandler(424)
def not_found(error):
    return make_response(jsonify({'error': 'неверный токен'}), 424)

@app.errorhandler(429)
def not_found(error):
    return make_response(jsonify({'code':429,'name':'Too Many Requests','message':'Слишком много запросов'}), 429)

if __name__ == '__main__':
    app.run(debug=True)
