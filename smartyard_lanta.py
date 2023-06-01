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
from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP
from sqlalchemy.sql import exists, func
from dotenv import load_dotenv
from requests.exceptions import HTTPError
from geopandas.tools import geocode
import logging, sys
import pycurl
from camshot import getcamshot
from smartyard_db import Temps, Settings, Users, Records, Devices, Rights, Doors, Invoices, create_db_connection, db
from smartyard_bill import addressList, billingList, camsActiv, paySuccess, uidFromflatNumber, userPhones
from smartyard_click import getPlogs, getPlogDays, getPlogDaysEvents, putEvent
import firebase_admin
from firebase_admin import auth, credentials, messaging
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

#cred = credentials.Certificate("/opt/smartyard/smartyard-25ea6-firebase-adminsdk-ps2zk-db7eef3ab3.json")
cred = credentials.Certificate(os.getenv('GOOGLEFSM'))
default_app = firebase_admin.initialize_app(cred)

app = Flask(__name__)
create_db_connection(app)


kannel_url = "http://%s:%d/cgi-bin/sendsms" % (os.getenv('KANNEL_HOST'), int(os.getenv('KANNEL_PORT')))
kannel_params = (('user', os.getenv('KANNEL_USER')), ('pass', os.getenv('KANNEL_PASS')), ('from', os.getenv('KANNEL_FROM')), ('coding', '2'))
billing_url = os.getenv('BILLING_URL')
expire = int(os.getenv('EXPIRE'))
proxyfl = os.getenv('PROXYFL')

camshotdir = os.getenv('CAMSHOT_DIR')
imgarchivedir = os.getenv('IMG_ARСHIVE_DIR')
slideshowdir = os.getenv('SLIDESHOW_DIR')
videoarchivedir = os.getenv('VIDEO_ARСHIVE_DIR')


testuser = os.getenv('TEST_USER')
testpass = os.getenv('TEST_PASS')

android_upgrade = 10
android_force_ugrade = 16
ios_upgrade = 9
ios_force_ugrade = 17

def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")

def bool2str(v):
    if v == True:
        return 't'
    else:
        return 'f'

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

@app.route('/api/')
def index():
    return "Hello, World!"

@app.route('/api/accessfl', methods=['GET'])
def accessfl():
    global response
    token = request.args.get('token')
    if not token or token == '':
        response = {'code':403,'name':'Forbidden','message':'Нет токена'}
        abort (403)
    name = request.args.get('name', 0)
    extime = datetime.datetime.now() - timedelta(minutes=expire)
    exists = db.session.query(db.exists().where(Users.videotoken==token)).scalar()
    db.session.remove()
    if exists:
        row = [r._asdict() for r in db.session.query(Users.vttime, Users.strims).filter_by(videotoken = token).all()]
        db.session.remove()
        vttime = row[0]['vttime']
        strims = row[0]['strims']
        if vttime >= extime and name in strims:
            response = app.response_class(status=200)
            return response
    if not proxyfl:
        response = {'code':403,'name':'Forbidden','message':'Не верный токен'}
        abort (403)
    else:
        response = requests.get(proxyfl, params=request.args.to_dict(flat=False))
        if response.status_code != 200:
            response = {'code':403,'name':'Forbidden','message':'И здесь не верный токен'}
            abort (403)
        return response.text

@app.route('/api/paysuccess', methods=['GET'])
def paysuccess():
    global response
    orderNumber = request.args.get('orderNumber')
    operation = request.args.get('operation')
    status = request.args.get('status')
    checksum = request.args.get('checksum')
    argsget = request.args.to_dict(flat=True)
    signature = codecs.decode(checksum.lower(), 'hex')
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
            response = app.response_class(status=200)
            return response
    response = {'code':403,'name':'Forbidden','message':'Операция запрещена'}
    abort (403)

@app.route('/api/cams/caminit', methods=['POST'])
def cams_caminit():
    global response
    request_data = json_verification(request)

    if not 'protocol' in request_data:
        request_data['protocol'] = 'srt'
    if 'macaddress' in request_data:
        try:
            row = [r._asdict() for r in db.session.query(Devices.device_uuid, Devices.device_type, Devices.url, Devices.port, Devices.is_active).filter_by(device_mac = request_data['macaddress']).all()]
            db.session.remove()
        except TypeError:
            pass
        if not row:
            device_uuid = str(uuid.uuid4())
            new_cam = Devices(device_id = None, device_uuid = device_uuid, device_mac = request_data['macaddress'], device_type = 2, affiliation = None, owner = None, url = None, port = None, stream = None, is_active = False, title = None, address = None, longitude = None, latitude = None, server_id = None, tariff_id = None, domophoneid = None, sippassword = None, dtmf = None, camshot = None)
            db.session.add(new_cam)
            db.session.commit()
            db.session.remove()
        elif row[0]['device_type'] == 2 and row[0]['url'] and row[0]['port'] and row[0]['is_active']:
            response = {'code':200,'server':row[0]['url'].split('//',1)[1],'port':row[0]['port'],'name':str(row[0]['device_uuid'])}
            return jsonify(response)
    response = {'code':403,'name':'Forbidden','message':'Операция запрещена'}
    abort (403)

@app.route('/api/address/access', methods=['POST'])
def address_access():
    global response
    access_verification(request.headers)
    request_data = json_verification(request)
    if not 'guestPhone' in request_data:
        response = {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'}
        abort (422)
    guestPhone = request_data['guestPhone']
    if not 'flatId' in request_data:
        response = {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'}
        abort (422)
    flatId = request_data['flatId']
    if not 'clientId' in request_data:
        response = {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'}
        abort (422)
    clientId = request_data['clientId']
    if not 'expire' in request_data:
        response = {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'}
        abort (422)
    expire = request_data['expire']
    response = app.response_class(status=204, mimetype='application/json')
    return response

@app.route('/api/address/getAddressList', methods=['POST'])
def address_getAddressList():
    global response
    phone = access_verification(request.headers)
    data = []
    addList = addressList(phone)
    doors0 = []
    doors0.append({'domophoneId':'4', 'doorId':0,'entrance':'1','icon':'entrance','name':'Подъезд'})
    doors0.append({'domophoneId':'4','doorId':1,'icon':'wicket','name':'Калитка'})
    doors0.append({'domophoneId':'4','doorId':2,'icon':'gate','name':'Ворота'})
    doors1 = []
    doors1.append({'domophoneId':'2', 'doorId':0,'entrance':'1','icon':'entrance','name':'Подъезд'})
    doors1.append({'domophoneId':'2','doorId':1,'icon':'wicket','name':'Калитка'})
    doors1.append({'domophoneId':'2','doorId':2,'icon':'gate','name':'Ворота'})
    if len(addList) == 0:
        data.append({'houseId':'0','address':'Здесь будет Ваш адрес','hasPlog':'t','cctv':99,'doors':doors0})
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
                    for item in rights:
                        device_type = db.session.query(Devices.device_type).filter_by(device_id=item, is_active=True).first()[0]
                        if device_type == 1 or device_type == 2:
                            cctv = cctv + 1
                        if device_type == 3:
                            door = door + 1
                            row = [r._asdict() for r in db.session.query(Doors.id, Doors.icon, Doors.entrance, Doors.name).filter_by(device_id=item).all()]
                            if cams_paid:
                                domophoneId = str(item)
                            else:
                                domophoneId = '2'
                            doorId = row[0]['id']
                            icon = row[0]['icon']
                            entrance = str(row[0]['entrance'])
                            name = row[0]['name']
                            doors.append({'domophoneId': domophoneId, 'doorId': doorId, 'entrance': entrance, 'icon': icon, 'name': name})
                except TypeError:
                    pass
            if cctv == 0:
                cctv = 99
            if door == 0 and cams_paid:
                doors = doors0
            if door == 0 and not cams_paid:
                doors = doors1
            data.append({"houseId":str(uid),"address":address,"hasPlog":"t","doors":doors,'cctv':cctv})
    Addressresponse = []
    Addressresponse = {'code':200,'name':'OK','message':'Хорошо','data':data}
    return jsonify(Addressresponse)

@app.route('/api/address/getSettingsList', methods=['POST'])
def address_getSettingsList():
    global response
    phone = access_verification(request.headers)
    data = []
    addList = addressList(phone)
    if len(addList) == 0:
        data.append({'address':'Здесь будет Ваш адрес','services':[],'hasPlog':'f','hasGates':'f','contractOwner':'f','flatId':'0'})
    else:
        for itemd in addList:
            uid = itemd['uid']
            clientId = str(itemd['login'])
            houseId = str(itemd['uid'])
            address = itemd['address']
            data.append({'address':address,'services':['internet','iptv','ctv','phone','cctv','domophone'],'hasPlog':'t','hasGates':'t','contractOwner':'t','clientId':clientId,'houseId':houseId,'flatId':houseId, 'flatNumber':'0'})
            exists = db.session.query(db.exists().where(Settings.uid==uid)).scalar()
            db.session.remove()
            if not exists:
                code = int(str(randint(6, 9)) + str(randint(0, 9)) + str(randint(0, 9)) + str(randint(0, 9)) + str(randint(0, 9)))
                new_uid = Settings(uid = uid, intercom = True, asterisk = True, w_rabbit = False, frs = True, code = code, guest = '2022-06-06 00:23:50')
                db.session.add(new_uid)
                db.session.commit()
                db.session.remove()
    Settingsresponse = []
    Settingsresponse = {'code':200,'name':'OK','message':'Хорошо','data':data}
    return jsonify(Settingsresponse)

@app.route('/api/address/intercom', methods=['POST'])
def address_intercom():
    global response
    access_verification(request.headers)
    request_data = json_verification(request)
    if not 'flatId' in request_data:
        response = {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'}
        abort (422)
    uid = request_data['flatId']
    exists = db.session.query(db.exists().where(Settings.uid==uid)).scalar()
    db.session.remove()
    if exists:
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
        row = [r._asdict() for r in db.session.query(Settings.intercom, Settings.asterisk, Settings.w_rabbit, Settings.frs, Settings.code, Settings.guest).filter_by(uid = uid).all()]
        db.session.remove()
        CMS = bool2str(row[0]['intercom'])
        VoIP = bool2str(row[0]['asterisk'])
        if row[0]['w_rabbit']:
            whiteRabbit = '5'
        else:
            whiteRabbit = '0'
        FRSDisabled = bool2str(not row[0]['frs'])
        code = str(row[0]['code'])
        guest = row[0]['guest'].strftime("%Y-%m-%d %H:%M:%S")
        response = {'code':200,'name':'OK','message':'Хорошо','data':{'allowDoorCode':'t','doorCode':code,'CMS':CMS,'VoIP':VoIP,'autoOpen':guest,'whiteRabbit':whiteRabbit,'disablePlog':'f', 'hiddenPlog':'f','FRSDisabled':FRSDisabled}}
        return jsonify(response)
    else:
        response = {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'}
        abort (422)

@app.route('/api/address/offices', methods=['POST'])
def address_offices():
    global response
    access_verification(request.headers)
    request_data = json_verification(request)
    response = {'code':200,'name':'OK','message':'Хорошо','data':[{'lat':52.730641,'lon':41.45234,'address':'Мичуринская улица, 2А','opening':'09:00-19:00 (без выходных)'},{'lat':52.767248,'lon':41.40488,'address':'улица Чичерина, 48А (ТЦ Апельсин)','opening':'09:00-19:00 (без выходных)'},{'lat':52.707399,'lon':41.397374,'address':'улица Сенько, 25А (Магнит)','opening':'09:00-19:00 (без выходных)'},{'lat':52.675463,'lon':41.465411,'address':'Астраханская улица, 189А (ТЦ МЖК)','opening':'09:00-19:00 (без выходных)'},{'lat':52.586785,'lon':41.497009,'address':'Октябрьская улица, 13 (ДК)','opening':'09:00-19:00 (вс, пн - выходной)'}]}
    return jsonify(response)

@app.route('/api/address/openDoor', methods=['POST'])
def address_openDoor():
    global response
    phone = access_verification(request.headers)
    request_data = json_verification(request)
    if not 'domophoneId' or not 'doorId' in request_data:
        response = {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'}
        abort (422)
    domophoneId = int(request_data['domophoneId'])
    doorId = int(request_data['doorId'])
    if domophoneId == 2 or domophoneId == 4:
        status = 400 + domophoneId
        response = app.response_class(status=status, mimetype='application/json')
        return response
    doorrow = [r._asdict() for r in db.session.query(Doors.open, Doors.cam).filter(Doors.id==int(request_data['doorId'])).all()]
    db.session.remove()
    urlopen = doorrow[0]['open']
    row = [r._asdict() for r in db.session.query(Devices.title, Devices.camshot).filter(Devices.device_id==doorrow[0]['cam']).all()]
    db.session.remove()
    status_code = requests.get(urlopen).status_code
    if status_code == 200:
        addList = addressList(phone)
        if len(addList) > 0:
            for itemd in addList:
                uid = itemd['uid']
                cams_open = itemd['cams_open']
                if cams_open:
                    rights = []
                    try:
                        rights = db.session.query(Rights.uid_right).filter_by(uid=uid).first()[0]
                        for right in rights:
                            device_type = db.session.query(Devices.device_type).filter_by(device_id=right, is_active=True).first()[0]
                            db.session.remove()
                            if device_type == 3:
                                id = db.session.query(Doors.id).filter_by(device_id=right).first()[0]
                                db.session.remove()
                                if domophoneId == right and doorId == id:
                                    device_id = doorrow[0]['cam']
                                    title = row[0]['title']
                                    date = datetime.datetime.now().replace(microsecond=0)
                                    eventuuid = uuid.uuid4()
                                    image = uuid.uuid4()
                                    detail = 'Телефон *' + str(phone)[-4:]
                                    fileurl = '/data/img/' + str(image)  + '.jpg'
                                    clickhousedata = [[date, eventuuid, image, int(uid), device_id, title, 4, detail, 1, str(phone)],]
                                    column_names = ['date', 'uuid', 'image', 'uid', 'objectId', 'mechanizmaDescription', 'event', 'detail', 'preview', 'phone']
                                    client.insert('smartyard.plog', clickhousedata, column_names)
                                    client.close()
                                    if row[0]['camshot']:
                                        getcamshot(row[0]['camshot'],fileurl)
                    except TypeError:
                        pass
    response = app.response_class(status=204, mimetype='application/json')
    return response

@app.route('/api/address/plog', methods=['POST'])
def address_plog():
    global response
    access_verification(request.headers)
    request_data = json_verification(request)
    if not 'flatId' in request_data:
        response = {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'}
        abort (422)
    uid = int(request_data['flatId'])
    camsactiv = camsActiv(uid)
    if not camsactiv['cams_paid'] or not camsactiv['cams_open']:
        status = 402
        if not camsactiv['cams_open']:
            status = 404
        plogresponse = app.response_class(status=status, mimetype='application/json')
        return plogresponse
    date = str(request_data['day'].replace('-', ''))
    plogs = []
    imgurl = 'https://sa.axiostv.ru/img/'
    resrows = getPlogs(uid,date)
    for res in resrows:
        preview = imgurl + str(res[2]) + '.jpg'
        plog = {'date':str(res[0])[:-6],'uuid':str(res[1]),'image':str(res[2]),'objectId':str(res[3]),'objectType':str(res[4]),'objectMechanizma':str(res[5]),'mechanizmaDescription':str(res[6]),'event':str(res[7]),'detail':str(res[8]),'preview':preview,'previewType':int(res[9]),'flags':['canLike']}
        if int(res[10]) == 1:
            try:
                plog['detailX']['opened'] = 't'
            except KeyError:
                plog['detailX'] = {}
                plog['detailX']['opened'] = 't'
        plogs.append(plog)
    plogresponse = {'code':200,'name':'OK','message':'Хорошо','data':plogs}
    #response = {'code':200,'name':'OK','message':'Хорошо','data':[{'date':'2023-01-20 13:03:23','uuid':'4d5082d2-f8a1-48ac-819e-c16f1f81a1e0','image':'3f99bdf6-96ef-4300-b709-1f557806c65b','objectId':'38','objectType':'0','objectMechanizma':'0','mechanizmaDescription':'Пионерская 5 б п 3 [Подъезд]','event':'1','detail':'1','preview':'https://static.dm.lanta.me/2023-01-18/3/f/9/9/3f99bdf6-96ef-4300-b709-1f557806c65b.jpg','previewType':2,'detailX':{'opened':'f','face':{'left':'614','top':'38','width':'174','height':'209'},'flags':['canLike']}},{'date':'2023-01-20 00:16:20','uuid':'bc1671b4-e01b-487e-b175-745e82be0ca9','image':'86ddb8e1-1122-4946-8495-a251b6320b99','objectId':'38','objectType':'0','objectMechanizma':'0','mechanizmaDescription':'Пионерская 5 б [Калитка]','event':'3','detail':'123456789123456789','preview':'https://static.dm.lanta.me/2023-01-18/8/6/d/d/86ddb8e1-1122-4946-8495-a251b6320b99.jpg','previewType':1,'detailX':{'key':'123456789'}},{'date':'2023-01-20 00:14:21','uuid':'32fd7c27-0d35-4d98-ab29-2544c3d0b9a7','image':'ad14c83a-126a-4f09-a659-f412fb11007e','objectId':'38','objectType':'0','objectMechanizma':'0','mechanizmaDescription':'Пионерская 5 б [Калитка]','event':'4','detail':'89103523377','preview':'https://static.dm.lanta.me/2023-01-18/a/d/1/4/ad14c83a-126a-4f09-a659-f412fb11007e.jpg','previewType':1,'detailX':{'phone':'89103523377'}},{'date':'2023-01-20 00:03:56','uuid':'ff42c747-3216-4fa7-8b68-128207d1a9ab','image':'0b335948-864f-41d6-b9a7-465f88f20ef1','objectId':'38','objectType':'0','objectMechanizma':'0','mechanizmaDescription':'Пионерская 5 б [Калитка]','event':'4','detail':'89103523377','preview':'https://static.dm.lanta.me/2023-01-18/0/b/3/3/0b335948-864f-41d6-b9a7-465f88f20ef1.jpg','previewType':1,'detailX':{'phone':'89103523377'}},{'date':'2023-01-20 00:01:28','uuid':'0e57d2c7-9e73-4083-98bb-2b140622be93','image':'8fc3224e-ef46-4ec6-9d5d-04e249ec2e31','objectId':'38','objectType':'0','objectMechanizma':'0','mechanizmaDescription':'Пионерская 5 б [Калитка]','event':'4','detail':'89103523377','preview':'https://static.dm.lanta.me/2023-01-18/8/f/c/3/8fc3224e-ef46-4ec6-9d5d-04e249ec2e31.jpg','previewType':1,'detailX':{'phone':'89103523377'}},{'date':'2023-01-20 00:00:02','uuid':'3bcac0af-677b-49d8-ba65-c18c3bcc8668','image':'c28c7e58-7797-4143-a2b8-2c513e216bb8','objectId':'38','objectType':'0','objectMechanizma':'0','mechanizmaDescription':'Пионерская 5 б [Калитка]','event':'4','detail':'89103523377','preview':'https://static.dm.lanta.me/2023-01-18/c/2/8/c/c28c7e58-7797-4143-a2b8-2c513e216bb8.jpg','previewType':1,'detailX':{'phone':'89103523377'}}]}
    return jsonify(plogresponse)

@app.route('/api/address/plogDays', methods=['POST'])
def address_plogDays():
    global response
    access_verification(request.headers)
    request_data = json_verification(request)
    if not 'flatId' in request_data:
        response = {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'}
        abort (422)
    uid = int(request_data['flatId'])
    camsactiv = camsActiv(uid)
    if not camsactiv['cams_paid']:
        return make_response(jsonify({'error': 'услуга не оплачена'}), 402)
    if not camsactiv['cams_open']:
        return make_response(jsonify({'error': 'услуга не подключена'}), 404)
    if 'events' in request_data:
        events = []
        for i in list(map(int, request_data['events'].split(','))):
            events.append(int(i))
        resrows = getPlogDaysEvents(uid,events)
    else:
        resrows = getPlogDays(uid)
    plogDay = []
    for row in resrows:
        plogDay.append({'day':str(row[0])[:-4] + '-' + str(row[0])[-4:-2] + '-' + str(row[0])[-2:],'events':str(row[1])})
    response = {'code':200,'name':'OK','message':'Хорошо','data':plogDay}
    return jsonify(response)

@app.route('/api/address/registerQR', methods=['POST'])
def address_registerQR():
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
        response = {'code':520,'message':'Некорректный QR-код!'}
        return jsonify(response)
    if QR != QR:
        response = {'code':200,'name':'OK','message':'Хорошо','data':'QR-код не является кодом для доступа к квартире'}
        return jsonify(response)
    if QR == QR:
        response = {'code':200,'name':'OK','message':'Хорошо','data':'Ваш запрос принят и будет обработан в течение одной минуты, пожалуйста подождите'}
        return jsonify(response)

@app.route('/api/address/resend', methods=['POST'])
def address_resend():
    global response
    access_verification(request.headers)
    request_data = json_verification(request)
    return "Hello, World!"

@app.route('/api/address/resetCode', methods=['POST'])
def address_resetCode():
    global response
    access_verification(request.headers)
    request_data = json_verification(request)
    if not 'flatId' in request_data:
        response = {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'}
        abort (422)
    uid = request_data['flatId']
    code = int(str(randint(1, 9)) + str(randint(0, 9)) + str(randint(0, 9)) + str(randint(0, 9)) + str(randint(0, 9)))
    db.session.query(Settings).filter_by(uid=uid).update({'code' : code})
    db.session.commit()
    db.session.remove()
    response = {'code':200,'name':'OK','message':'Хорошо','data':{'code':code}}
    return jsonify(response)

@app.route('/api/cctv/all', methods=['POST'])
def cctv_all():
    global response
    phone = access_verification(request.headers)
    request_data = json_verification(request)
    houseId = request_data['houseId']
    camsactiv = camsActiv(houseId)
    if not camsactiv['cams_paid']:
        return make_response(jsonify({'error': 'услуга не оплачена'}), 402)
    if not camsactiv['cams_open']:
        return make_response(jsonify({'error': 'услуга не подключена'}), 404)
    try:
        rights = []
        rights = db.session.query(Rights.uid_right).filter_by(uid=houseId).first()[0]
        db.session.remove()
        cctv_all_data = []
        strims = []
        for right in rights:
            row = [r._asdict() for r in db.session.query(Devices.device_uuid, Devices.url, Devices.title, Devices.device_type, Devices.longitude, Devices.latitude).filter_by(device_id=right, is_active=True).all()]
            db.session.remove()
            device_type = row[0]['device_type']
            if device_type == 1 or device_type == 2:
                device_uuid = row[0]['device_uuid']
                name = row[0]['title']
                lat = str(row[0]['longitude'])
                lon = str(row[0]['latitude'])
                url = str(row[0]['url']) + '/' + str(device_uuid)
                cctv_all_data.append({'id': right, 'name': name, 'lat': lat, 'lon': lon, 'url': url, 'token': ''})
                strims.append(str(device_uuid))
            videotoken = generate_video_token(phone,strims,houseId)
            for item in cctv_all_data:
                item['token'] = videotoken
        cctv_all_response = {'code':200,'name':'OK','message':'Хорошо','data':cctv_all_data}
        return jsonify(cctv_all_response)
    except TypeError:
        return make_response(jsonify({'error': 'услуга не подключена'}), 404)

@app.route('/api/cctv/camMap', methods=['POST'])
def cctv_camMap():
    global response
    phone = access_verification(request.headers)
    request_data = json_verification(request)
    if request_data['houseId']:
        houseId = request_data['houseId']
        camsactiv = camsActiv(houseId)
        if not camsactiv['cams_paid']:
            return make_response(jsonify({'error': 'услуга не оплачена'}), 402)
        if not camsactiv['cams_open']:
            return make_response(jsonify({'error': 'услуга не подключена'}), 404)
        data = []
        rights = []
        doors = []

    data = []
    addList = addressList(phone)
    if len(addList) > 0:
        for itemd in addList:
            strims = []
            uid = itemd['uid']
            cams_open = itemd['cams_open']
            cams_paid = itemd['cams_paid']
            if cams_open and cams_paid:
                rights = []
                doors = []
                try:
                    rights = db.session.query(Rights.uid_right).filter_by(uid=uid).first()[0]
                    db.session.remove()
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
                                device_uuid = 0 
                except TypeError:
                    rights = 0
            for item in data:
                strims.append(item['url'][8:].partition('/')[2])
            videotoken = generate_video_token(phone,strims,uid)
            for item in data:
                item['token'] = videotoken
    Cammapresponse = {'code':200,'name':'OK','message':'Хорошо','data':data}
    return jsonify(Cammapresponse)

@app.route('/api/cctv/overview', methods=['POST'])
def cctv_overview():
    global response
    access_verification(request.headers)
    return make_response(jsonify({'error': 'услуга не подключена'}), 404)
#    response = {'code':200,'name':'OK','message':'Хорошо','data':[]}
#    return jsonify(response)

@app.route('/api/cctv/ranges', methods=['POST'])
def cctv_ranges():
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
def cctv_recDownload():
    global response
    access_verification(request.headers)
    request_data = json_verification(request)
    recordid = request_data['id']
    fileurl = 'https://sa.axiostv.ru/' + db.session.query(Records.fileurl).filter_by(id = recordid).first()[0]
    db.session.remove()
    response = {'code':200,'name':'OK','message':'Хорошо', 'data':fileurl }
    #print(f'response =   {response}')
    return jsonify(response)

@app.route('/api/cctv/recPrepare', methods=['POST'])
def cctv_recPrepare():
    global response
    phone = access_verification(request.headers)
    request_data = json_verification(request)
    cam_id = request_data['id']
    row = [r._asdict() for r in db.session.query(Devices.device_uuid, Devices.url, Devices.title).filter_by(device_id=cam_id, is_active=True).all()]
    db.session.remove()
    if row:
        camurl = row[0]['url'] + '/' + str(row[0]['device_uuid'])
        camname = row[0]['title']
    else:
        camresponse = requests.post(billing_url + "getcctvcam", headers={'Content-Type':'application/json'}, data=json.dumps({'camid': cam_id})).json()
        camurl = camresponse['url']
        camname = camresponse['name']
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
def cctv_youtube():
    global response
    access_verification(request.headers)
    request_data = json_verification(request)
    return "Hello, World!"

@app.route('/api/ext/ext', methods=['POST'])
def ext_ext():
    global response
    access_verification(request.headers)
    request_data = json_verification(request)
    return "Hello, World!"

@app.route('/api/ext/list', methods=['POST'])
def ext_list():
    global response
    access_verification(request.headers)
    response = {'code':200,'name':'OK','message':'Хорошо', 'data':[]}
    return jsonify(response)

@app.route('/api/frs/disLike', methods=['POST'])
def frs_disLike():
    global response
    access_verification(request.headers)
    request_data = json_verification(request)
    response = {'code':200,'name':'OK','message':'Хорошо', 'data':''}
    return jsonify(response)

@app.route('/api/frs/like', methods=['POST'])
def frs_like():
    global response
    access_verification(request.headers)
    request_data = json_verification(request)
    return "Hello, World!"

@app.route('/api/frs/listFaces', methods=['POST'])
def frs_listFaces():
    global response
    access_verification(request.headers)
    request_data = json_verification(request)
    uid = request_data['flatId']
    response = {'code':200,'name':'OK','message':'Хорошо','data':[{'faceId': '144349','image':'https://faces.dm.lanta.me/3/9/9/c/d/399cd1a1-4545-2443-33de-a3dc8af728f7.jpg'}]}
    return jsonify(response)

@app.route('/api/geo/address', methods=['POST'])
def geo_address():
    global response
    access_verification(request.headers)
    request_data = json_verification(request)
    return "Hello, World!"

@app.route('/api/geo/coder', methods=['POST'])
def geo_coder():
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
def geo_getAllLocations():
    global response
    access_verification(request.headers)
    request_data = json_verification(request)
    return "Hello, World!"

@app.route('/api/geo/getAllServices', methods=['POST'])
def geo_getAllServices():
    global response
    access_verification(request.headers)
    request_data = json_verification(request)
    return "Hello, World!"

@app.route('/api/geo/getHouses', methods=['POST'])
def geo_getHouses():
    global response
    access_verification(request.headers)
    request_data = json_verification(request)
    return "Hello, World!"

@app.route('/api/geo/getServices', methods=['POST'])
def geo_getServices():
    global response
    access_verification(request.headers)
    request_data = json_verification(request)
    response = {'code':200,'name':'OK','message':'Хорошо','data':[{'icon':'internet','title':'internet','description':'internet','canChange':'f','byDefault':'t'},{'icon':'iptv','title':'iptv','description':'iptv','canChange':'f','byDefault':'t'},{'icon':'ctv','title':'ctv','description':'ctv','canChange':'f','byDefault':'t'},{'icon':'phone','title':'phone','description':'phone','canChange':'f','byDefault':'t'},{'icon':'cctv','title':'cctv','description':'cctv','canChange':'f','byDefault':'t'},{'icon':'domophone','title':'domophone','description':'domophone','canChange':'f','byDefault':'t'},{'icon':'gsm','title':'gsm','description':'gsm','canChange':'f','byDefault':'t'}]}
    return jsonify(response)

@app.route('/api/geo/getStreets', methods=['POST'])
def geo_getStreets():
    global response
    access_verification(request.headers)
    request_data = json_verification(request)
    return "Hello, World!"

@app.route('/api/inbox/alert', methods=['POST'])
def inbox_alert():
    global response
    access_verification(request.headers)
    request_data = json_verification(request)
    return "Hello, World!"

@app.route('/api/inbox/chatReaded', methods=['POST'])
def inbox_chatReaded():
    global response
    access_verification(request.headers)
    request_data = json_verification(request)
    return "Hello, World!"

@app.route('/api/inbox/delivered', methods=['POST'])
def inbox_delivered():
    global response
    access_verification(request.headers)
    request_data = json_verification(request)
    return "Hello, World!"

@app.route('/api/inbox/inbox', methods=['POST'])
def inbox_inbox():
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
def inbox_readed():
    global response
    access_verification(request.headers)
    request_data = json_verification(request)
    return "Hello, World!"

@app.route('/api/inbox/unreaded', methods=['POST'])
def inbox_unreaded():
    global response
    access_verification(request.headers)
#    if not request.get_json():
#        response = {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'}
#        abort (422)
#    request_data = request.get_json()
    response = {'code':200,'name':'OK','message':'Хорошо','data':{'count':0,'chat':0}}
    return jsonify(response)


@app.route('/api/issues/action', methods=['POST'])
def issues_action():
    global response
    access_verification(request.headers)
    request_data = json_verification(request)
    return "Hello, World!"

@app.route('/api/issues/comment', methods=['POST'])
def issues_comment():
    global response
    access_verification(request.headers)
    request_data = json_verification(request)
    return "Hello, World!"

@app.route('/api/issues/create', methods=['POST'])
def issues_create():
    global response
    access_verification(request.headers)
    request_data = json_verification(request)
    response = {'code':200,'name':'OK','message':'Хорошо', 'data':"123"}
    return jsonify(response)

@app.route('/api/issues/listConnect', methods=['POST'])
def issues_listConnect():
    global response
    access_verification(request.headers)
#    if not request.get_json():
#        response = {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'}
#        abort (422)
#    request_data = request.get_json()
    response = app.response_class(status=204, mimetype='application/json')
    return response

@app.route('/api/pay/prepare', methods=['POST'])
def pay_prepare():
    global response
    phone = access_verification(request.headers)
    request_data = json_verification(request)
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    logging.debug(repr(request_data['clientId']))
    logging.debug(repr(request_data['amount']))
    response = requests.post(billing_url + "createinvoice", headers={'Content-Type':'application/json'}, data=json.dumps({'login': request_data['clientId'], 'amount' : request_data['amount'], 'phone' : phone})).json()
    return jsonify(response)

@app.route('/api/pay/process', methods=['POST'])
def pay_process():
    global response
    access_verification(request.headers)
    request_data = json_verification(request)
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    logging.debug(repr(request_data['paymentId']))
    logging.debug(repr(request_data['sbId']))
    response = {'code':200,'name':'OK','message':'Хорошо','data':'Платеж в обработке'}
    return jsonify(response)

@app.route('/api/pay/register', methods=['POST'])
def pay_register():
    global response
    phone = access_verification(request.headers)
    request_data = json_verification(request)
    if not 'orderNumber' in request_data or not 'amount' in request_data:
        response = {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'}
        abort (422)
    bank_url = 'https://securepayments.sberbank.ru/payment/rest/register.do'
    orderNumber = request_data['orderNumber']
    amount = request_data['amount']
    username_api = 'axiostv-api'
    password_api = 'Gijo34fgkel'
    returnUrl = 'https://sa.axiostv.ru/success_payment.html'
    failUrl = 'https://sa.axiostv.ru/failed_payment.html'
    sber_params = (('userName',username_api),('password',password_api),('orderNumber',orderNumber),('amount',amount),('returnUrl',returnUrl),('failUrl',failUrl))
    sber_response = requests.get(bank_url, headers={'Content-Type':'application/x-www-form-urlencoded'}, params=sber_params)
    try:
        orderId = str(sber_response.json()['orderId'])
        formUrl = str(sber_response.json()['formUrl'])
        code = sber_response.status_code
        if code == 200:
            response = {'code':code,'name':'OK','message':'Хорошо','data':{'orderId':orderId, 'formUrl':formUrl}}
            return jsonify(response)
    except KeyError:
        code = sber_response.status_code
    response = {'code':code,'name':'Error Bank','message':'Ошибка Банка'}
    abort (sber_response.status_code)

@app.route('/api/sip/helpMe', methods=['POST'])
def sip_helpMe():
    global response
    access_verification(request.headers)
    response = {'code':200,'name':'OK','message':'Хорошо','data':{'server':'sa.axiostv.ru', 'port':5400, 'transport':'udp', 'extension':'123', 'pass':'123', 'dial':'+74742210001'}}
    return jsonify(response)

@app.route('/api/user/addMyPhone', methods=['POST'])
def user_addMyPhone():
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
def user_appVersion():
    global response
    phone = access_verification(request.headers)
    request_data = json_verification(request)
    if not 'version' in request_data or not 'platform' in request_data:
        response = {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'}
        abort (422)
    version = request_data['version']
    platform = request_data['platform']
    if version != None and (platform == 'android' or platform == 'ios'):
        db.session.query(Users).filter_by(userphone=int(phone)).update({'version' : version, 'platform' : platform})
        db.session.commit()
        db.session.remove()
        if platform == 'ios':
            upgrade = ios_upgrade
            force_upgrade = ios_force_ugrade
        else:
            upgrade = android_upgrade
            force_upgrade = android_force_ugrade
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
def user_confirmCode():
    global response
    request_data = json_verification(request)
    if (not 'userPhone' in request_data) or len(request_data['userPhone'])!=11 or (not 'smsCode' in request_data) or len(request_data['smsCode'])!=4:
        response = {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'}
        abort(422)
    userPhone = request_data['userPhone']
    exists = db.session.query(db.session.query(Temps).filter_by(userphone=int(userPhone)).exists()).scalar()
    db.session.remove()
    if not exists:
        response = {"code":404,"name":"Not Found","message":"Не найдено"}
        abort(404)
    smsCode = request_data['smsCode']
    exists = db.session.query(db.exists().where(Temps.userphone==int(userPhone) and Temps.smscode == int(smsCode))).scalar()
    db.session.remove()
    if not exists:
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
        new_user = Users(uuid = accessToken, userphone = int(request_data['userPhone']), name = request_data['name'], patronymic = request_data['patronymic'], email = request_data['email'], videotoken = None, uid = None, vttime = datetime.datetime.now(), strims = None, pushtoken = None, platform = None, version = None, notify = True, money = True)
        db.session.add(new_user)
        db.session.commit()
        db.session.remove()
    db.session.query(Temps).filter_by(userphone=int(userPhone)).delete()
    db.session.commit()
    db.session.remove()
    response = {'code':200,'name':'OK','message':'Хорошо','data':{'accessToken':accessToken,'names':{'name':request_data['name'],'patronymic':request_data['patronymic']}}}
    return jsonify(response)

@app.route('/api/user/getPaymentsList', methods=['POST'])
def user_getPaymentsList():
    global response
    phone = access_verification(request.headers)
    response = requests.post(billing_url + "getpaymentslist", headers={'Content-Type':'application/json'}, data=json.dumps({'phone': phone})).json()
    return jsonify(response)

@app.route('/api/user/notification', methods=['POST'])
def user_notification():
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
def user_ping():
    global response
    access_verification(request.headers)
    response = app.response_class(status=204, mimetype='application/json')
    return response

@app.route('/api/user/pushTokens', methods=['POST'])
def user_pushTokens():
    global response
    access_verification(request.headers)
    response = {'code':200,'name':'OK','message':'Хорошо','data':{'pushToken':'fnTGJUfJTIC61WfSKWHP_N:APA91bGbnS3ck-cEWO0aj4kExZLsmGGmhziTu2lfyvjIpbmia5ahfL4WlJrr8DOjcDMUo517HUjxH4yZm0m5tF89CssdSsmO6IjcrS1U_YM3ue2187rc9ow9rS0xL8Q48vwz2e6j42l1','voipToken':'off'}}
    return jsonify(response)

@app.route('/api/user/registerPushToken', methods=['POST'])
def user_registerPushToken():
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
def user_requestCode():
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
        sms_text = os.getenv('KANNEL_TEXT') + str(sms_code)
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
def user_restore():
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
def user_sendName():
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
def user_getBillingList():
    global response
    userphone = access_verification(request.headers)
    billList = billingList(userphone)
    data = []
    if len(billList) == 0:
        code = 204
        data.append({'login' : '','address' : '','balans' : '0.00','payment' : '0.00','internet' : '0.00','internet_data' : '','tv' : '0.00','tv_data' : '','phone' : '0.00','phone_data' : '','cams' : '0.00','cams_data' : '','cams_name' : ''})
    else:
        code = 200
        for itemd in billList:
            address = str(itemd['address'])
            login = str(itemd['login'])
            balans = itemd['balans']
            payment = itemd['payment']
            internet = str(itemd['internet'])
            internet_data = str(itemd['internet_data'])
            tv = str(itemd['tv'])
            tv_data = str(itemd['tv_data'])
            phone = str(itemd['phone'])
            phone_data = str(itemd['phone_data'])
            cams = str(itemd['cams'])
            cams_data = str(itemd['cams_data'])
            cams_name = str(itemd['cams_name'])
            data.append({'login':login,'address':address,'balans':balans,'payment':payment,'internet':internet,'internet_data':internet_data,'tv':tv,'tv_data' :tv_data,'phone':phone,'phone_data':phone_data,'cams':cams,'cams_data':cams_data,'cams_name':cams_name})
    Billingresponse = []
    Billingresponse = {'code':code,'name':'OK','message':'Хорошо','data':data}    
    return jsonify(Billingresponse)

@app.route('/api/images/<imgfile>', methods=['GET'])
def get_images(imgfile):
    global response
    #access_verification(request.headers)
    device_uuid = imgfile.split('.')[0]
    url = db.session.query(Devices.camshot).filter(Devices.device_uuid==device_uuid).first()[0]
    db.session.remove()
    fullfileurl = slideshowdir + '/' + imgfile
    getcamshot(url,fullfileurl)
    return send_file(fullfileurl)

@app.route('/api/hcs/appealsCategory', methods=['POST'])
def hcs_appealscategory():
    global response
    access_verification(request.headers)
    appealsCategory = []
    appealsCategory.append('Освещение')
    appealsCategory.append('Электроснабжение')
    appealsCategory.append('Водоотведение')
    appealsCategory.append('Водоснабжение')
    appealsCategory.append('Отопление')
    appealsCategory.append('Газоснабжение')
    appealsCategory.append('Лифт')
    appealsCategory.append('Интернет')
    appealsCategory.append('Телевидение')
    appealsCategory.append('Видеонаблюдение')
    appealsCategory.append('Домофон')
    appealsCategory.append('Уборка пом. ОП')
    appealsCategory.append('Придомовая тер-рия')
    response = {'code':200,'name':'OK','message':'Хорошо','data':{'appealscategory':appealsCategory}}
    return jsonify(response)

@app.route('/api/hcs/appealslist', methods=['POST'])
def hcs_appealslist():
    global response
    access_verification(request.headers)
    appealsList = []
    appealsList.append({'appealsId':1, 'createdUtc':'2023-04-20T11:30:00.000Z', 'type':'Водоотведение', 'description':'Забита канализация в ванной комнате', 'createdDoc':'https://sa.axiostv.ru/img/142212.jpg', 'status':1, 'statusDescription':[{'stDesc':'Принято', 'stUtc':'2023-04-20T11:36:00.000Z'},{'stDesc':'Назначен исполнитель', 'stUtc':'2023-04-20T11:37:00.000Z'},{'stDesc':'Принято исполнителем', 'stUtc':'2023-04-20T11:38:00.000Z'},{'stDesc':'Выполнено', 'stUtc':'2023-04-20T14:18:00.000Z'},{'stDesc':'Закрыто', 'stUtc':'2023-04-20T14:20:00.000Z'}], 'workerDescription':[{'wrDoc':'https://sa.axiostv.ru/img/111543.jpg', 'wrDesc':'Найден засор', 'wrUtc':'2023-04-20T12:00:00.000Z'},{'wrDoc':'https://sa.axiostv.ru/img/111623.jpg', 'wrDesc':'Прочищена часть трубы', 'wrUtc':'2023-04-20T12:30:00.000Z'},{'wrDoc':'https://sa.axiostv.ru/img/111641.jpg', 'wrDesc':'Заменено часть трубы и отвод', 'wrUtc':'2023-04-20T13:30:00.000Z'}]})
    appealsList.append({'appealsId':2, 'createdUtc':'2023-04-20T20:30:00.000Z', 'type':'Электричество', 'description':'Не горит лампочка в лифтовом холе 5-го этажа', 'createdDoc':'https://sa.axiostv.ru/img/203932.jpg', 'status':1, 'statusDescription':[{'stDesc':'Принято', 'stUtc':'2023-04-20T20:32:00.000Z'},{'stDesc':'Назначен исполнитель', 'stUtc':'2023-04-20T20:34:00.000Z'},{'stDesc':'Принято исполнителем', 'stUtc':'2023-04-20T20:35:00.000Z'},{'stDesc':'Выполнено', 'stUtc':'2023-04-20T20:45:00.000Z'},{'stDesc':'Закрыто', 'stUtc':'2023-04-20T20:46:00.000Z'}], 'workerDescription':[{'wrDoc':'', 'wrDesc':'', 'wrUtc':'2023-04-20T11:30:00.000Z'},{'wrDoc':'', 'wrDesc':'', 'wrUtc':'2023-04-20T11:30:00.000Z'}]})
    appealsList.append({'appealsId':3, 'createdUtc':'2023-04-21T11:30:00.000Z', 'type':'Водоснабжение', 'description':'В ванной вместо холодной воды идет теплая', 'createdDoc':'', 'status':0, 'statusDescription':[{'stDesc':'Принято', 'stUtc':'2023-04-21T11:40:00.000Z'},{'stDesc':'Назначен исполнитель', 'stUtc':'2023-04-21T11:42:00.000Z'},{'stDesc':'Принято исполнителем', 'stUtc':'2023-04-21T11:45:00.000Z'}], 'workerDescription':[{'wrDoc':'', 'wrDesc':'', 'wrUtc':'2023-04-20T11:30:00.000Z'},{'wrDoc':'', 'wrDesc':'', 'wrUtc':'2023-04-20T11:30:00.000Z'}]})
    appealsList.append({'appealsId':4, 'createdUtc':'2023-04-22T11:30:00.000Z', 'type':'Интернет', 'description':'Нет контакта в коннекторе', 'createdDoc':'', 'status':0, 'statusDescription':[{'stDesc':'Принято', 'stUtc':'2023-04-22T11:33:00.000Z'},{'stDesc':'Назначен исполнитель', 'stUtc':'2023-04-22T11:34:00.000Z'},{'stDesc':'Принято исполнителем', 'stUtc':'2023-04-22T11:36:00.000Z'}], 'workerDescription':[{'wrDoc':'', 'wrDesc':'', 'wrUtc':'2023-04-20T11:30:00.000Z'},{'wrDoc':'', 'wrDesc':'', 'wrUtc':'2023-04-20T11:30:00.000Z'}]})
    response = {'code':200,'name':'OK','message':'Хорошо','data':appealsList}
    return jsonify(response)

@app.route('/api/hcs/appealtype', methods=['POST'])
def hcs_appealtype():
    global response
    access_verification(request.headers)
    appealtype = {'1':'', '2':'', '3':'', '4':'', '5':'', '6':'', '7':'', '8':'', '9':'', '10':''}
    response = {'code':200,'name':'OK','message':'Хорошо','data':appealtype}
    return jsonify(response)

@app.route('/api/hcs/newappeal', methods=['POST'])
def hcs_newAppeal():
    global response
    #access_verification(request.headers)
    data = json.loads(request.form['Data'])
    print(f" houseId = {data['houseId']}, Category = {data['Category']}, AppealText = {data['AppealText']}")
    response = app.response_class(status=204, mimetype='application/json')
    return response

@app.route('/asterisk/aors/single', methods=['POST'])
def aors_single():
    #print(f"{str(request.form['id']).split('@',1)[0]}")
    if len(str(request.form['id']).split('@',1)[0]) == 6 and str(request.form['id']).split('@',1)[0][0] == '1':
        domophoneid = int(str(request.form['id']).split('@',1)[0]) - 100000
        row = [r._asdict() for r in db.session.query(Devices.domophoneid).filter(Devices.domophoneid == domophoneid).all()]
        db.session.remove()
        try:
            extension = str(row[0]['domophoneid'] + 100000)
            aors_data = {'id':extension, 'max_contacts':'1', 'remove_existing':'yes'}
        except IndexError:
            aors_data = ''
    elif len(str(request.form['id']).split('@',1)[0]) == 10 and str(request.form['id']).split('@',1)[0][0] == '2':
        extension = int(str(request.form['id']).split('@',1)[0])
        cred = r.get('mobile_extension_' + str(extension))
        if cred:
            aors_data = {'id':extension, 'max_contacts':'1', 'remove_existing':'yes'}
    else:
        aors_data = ''
    #print(f"{aors_data}")
    return urllib.parse.urlencode(aors_data)

@app.route('/asterisk/aors/multi', methods=['POST'])
def aors_multi():
    #print(f"{str(request.form)}")
    aors_data = []
    aors_response = ''
    rows = [r._asdict() for r in db.session.query(Devices.domophoneid).filter(Devices.domophoneid != 0).all()]
    db.session.remove()
    for row in rows:
        extension = str(row['domophoneid'] + 100000)
        aors_data.append({'id':extension, 'max_contacts':'1', 'remove_existing':'yes'})
    for item in aors_data:
        aors_response = aors_response + urllib.parse.urlencode(item) + '\n'
    #print(f"{aors_response}")
    return (aors_response)

@app.route('/asterisk/auths/single', methods=['POST'])
def auths_single():
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
    else:
        auths_data = ''
    #print(f"{auths_data}")
    return urllib.parse.urlencode(auths_data)

@app.route('/asterisk/auths/multi', methods=['POST'])
def auths_multi():
    #print(f"{str(request.form)}")
    auths_data = []
    auths_response = ''
    rows = [r._asdict() for r in db.session.query(Devices.domophoneid,Devices.sippassword).filter(Devices.domophoneid != 0).all()]
    db.session.remove()
    for row in rows:
        extension = str(row['domophoneid'] + 100000)
        auths_data.append({'id':extension, 'username':extension, 'auth_type':'userpass', 'password':row['sippassword']})
    for item in auths_data:
        auths_response = auths_response + urllib.parse.urlencode(item) + '\n'
    #print(f"{auths_response}")
    return (auths_response)

@app.route('/asterisk/endpoints/single', methods=['POST'])
def endpoints_single():
    #print(f"{str(request.form['id']).split('@',1)[0]}")
    if len(str(request.form['id']).split('@',1)[0]) == 6 and str(request.form['id']).split('@',1)[0][0] == '1':
        domophoneid = int(str(request.form['id']).split('@',1)[0]) - 100000
        row = [r._asdict() for r in db.session.query(Devices.domophoneid).filter(Devices.domophoneid == domophoneid).all()]
        db.session.remove()
        try:
            extension = str(row[0]['domophoneid'] + 100000)
            endpoints_data = {'id':extension, 'auth':extension, 'outbound_auth':extension, 'aors':extension, 'callerid':extension, 'context':'default', 'disallow':'all', 'allow':'alaw,h264', 'rtp_symmetric':'no', 'force_rport':'no', 'rewrite_contact':'yes', 'timers':'no', 'direct_media':'no', 'allow_subscribe':'yes', 'dtmf_mode':'rfc4733', 'ice_support':'no'}
            return_data = urllib.parse.urlencode(endpoints_data)
        except IndexError:
            return_data = ''
    elif len(str(request.form['id']).split('@',1)[0]) == 10 and str(request.form['id']).split('@',1)[0][0] == '2':
        extension = int(str(request.form['id']).split('@',1)[0])
        cred = r.get('mobile_extension_' + str(extension))
        if cred:
            endpoints_data = {'id':extension, 'auth':extension, 'outbound_auth':extension, 'aors':extension, 'callerid':extension, 'context':'default', 'disallow':'all', 'allow':'alaw,h264', 'rtp_symmetric':'yes', 'force_rport':'yes', 'rewrite_contact':'yes', 'timers':'no', 'direct_media':'no', 'allow_subscribe':'yes', 'dtmf_mode':'rfc4733', 'ice_support':'yes'}
            return_data = urllib.parse.urlencode(endpoints_data)
    else:
        return_data = ''
    #print(f"{endpoints_data}")
    return return_data

@app.route('/asterisk/endpoints/multi', methods=['POST'])
def endpoints_multi():
    #print(f"{str(request.form)}")
    endpoints_data = []
    endpoints_response = ''
    rows = [r._asdict() for r in db.session.query(Devices.domophoneid).filter(Devices.domophoneid != 0).all()]
    db.session.remove()
    for row in rows:
        extension = str(row['domophoneid'] + 100000)
        endpoints_data.append({'id':extension, 'auth':extension, 'outbound_auth':extension, 'aors':extension, 'callerid':extension, 'context':'default', 'disallow':'all', 'allow':'alaw,h264', 'rtp_symmetric':'no', 'force_rport':'no', 'rewrite_contact':'yes', 'timers':'no', 'direct_media':'no', 'allow_subscribe':'yes', 'dtmf_mode':'rfc4733', 'ice_support':'no'})
    for item in endpoints_data:
        endpoints_response = endpoints_response + urllib.parse.urlencode(item) + '\n'
    #print(f"{endpoints_response}")
    return (endpoints_response)

@app.route('/asterisk/extensions/uidFromflatNumber', methods=['POST'])
def extensions_uidFromflatNumber():
    request_data = json_verification(request)
    domophoneid = int(request_data['domophoneId'])
    address = db.session.query(Devices.address).filter(Devices.domophoneid==domophoneid).first()[0]
    db.session.remove()
    uid = uidFromflatNumber(address, int(request_data['flatNumber']))
    return ({'uid':uid})

@app.route('/asterisk/extensions/blacklist', methods=['POST'])
def extensions_blacklist():
    autoBlock = 1
    manualBlock = 0
    uid = request.data.decode("utf-8")
    activ = camsActiv(uid)
    if activ['cams_open'] == 1 and activ['cams_paid'] == 1:
        autoBlock = 0
    asterisk = db.session.query(Settings.asterisk).filter_by(uid = request.data.decode("utf-8")).first()[0]
    db.session.remove()
    if not asterisk:
        manualBlock = 1
    return ({'autoBlock':autoBlock, 'manualBlock':manualBlock})

@app.route('/asterisk/extensions/autoopen', methods=['POST'])
def extensions_autoopen():
    guest = db.session.query(Settings.guest).filter_by(uid = request.data.decode("utf-8")).first()[0]
    db.session.remove()
    if guest >= datetime.datetime.now():
        autoopen = 'true'
    else:
        autoopen = 'false'
    uid = request.data.decode("utf-8")
    return (autoopen)

@app.route('/asterisk/extensions/domophone', methods=['POST'])
def extensions_domophone():
    domophoneid = int(request.data.decode("utf-8"))
    row = [r._asdict() for r in db.session.query(Devices.device_id, Devices.device_uuid, Devices.title, Devices.dtmf).filter(Devices.domophoneid==domophoneid).all()]
    db.session.remove()
    return ({'deviceId': row[0]['device_id'], 'device_uuid': row[0]['device_uuid'], 'dtmf':row[0]['dtmf'], 'callerId':row[0]['title']})

@app.route('/asterisk/extensions/camshot', methods=['POST'])
def extensions_camshot():
    request_data = json_verification(request)
    domophoneid = int(request_data['domophoneId'])
    row = [r._asdict() for r in db.session.query(Devices.device_uuid, Devices.camshot).filter(Devices.domophoneid==domophoneid).all()]
    db.session.remove()
    fullfileurl = camshotdir + '/' + str(row[0]['device_uuid']) + '.jpg'
    getcamshot(row[0]['camshot'],fullfileurl)
    return ('')

@app.route('/asterisk/extensions/subscribers', methods=['POST'])
def extensions_subscribers():
    phones = userPhones(int(request.data.decode("utf-8")))
    subscribers_response = []
    for phone in phones:
        row = [r._asdict() for r in db.session.query(Users.userphone, Users.pushtoken, Users.platform).filter(Users.userphone == int(phone)).all()]
        db.session.remove()
        platform = 0
        try:
            if row[0]['platform'] == 'ios':
                platform = 1
            subscribers_response.append({'mobile':str(row[0]['userphone']),'voipEnabled':1,'platform':platform,'tokenType':0,'voipToken':'off','pushToken':row[0]['pushtoken']})
        except IndexError:
            platform = 0
    return jsonify(subscribers_response)

@app.route('/asterisk/extensions/push', methods=['POST'])
def extensions_push():
    #print(f"{str(json_verification(request))}")
    req = json_verification(request)
    registration_token = req['token']
    image = camshotdir + '/' + str(req['device_uuid']) + ".jpg"
    live = 'https://sa.axiostv.ru/api/images/' + str(req['device_uuid']) + ".jpg"
    if req['platform'] == 1:
        data = {'server':'sa.axiostv.ru','port':'5401','transport':'tcp','extension':str(req['extension']),'pass':req['hash'],'dtmf':str(req['dtmf']),'image':image,'live':live,'timestamp':str(int(datetime.datetime.now().timestamp())),'ttl':'30','callerId':req['callerId'],'platform':'ios','flatId':str(req['uid']),'flatNumber':str(req['flatNumber']),'stun': 'stun:37.235.209.140:3478','stun_transport':'udp','stunTransport':'udp',}
        message = messaging.Message(apns=messaging.APNSConfig(headers={'apns-priority':'10'},payload=messaging.APNSPayload(aps=messaging.Aps(alert=messaging.ApsAlert(title='Входящий вызов',body=req['callerId'],),badge=1,),),), data=data, token=registration_token,)
    else:
        data = {'server':'sa.axiostv.ru','port':'5401','transport':'tcp','extension':str(req['extension']),'pass':req['hash'],'dtmf':str(req['dtmf']),'image':image,'live':live,'timestamp':str(int(datetime.datetime.now().timestamp())),'ttl':'30','callerId':req['callerId'],'platform':'android','flatId':str(req['uid']),'flatNumber':str(req['flatNumber']),'stun': 'stun:37.235.209.140:3478','stun_transport':'udp','stunTransport':'udp',}
        message = messaging.Message(android=messaging.AndroidConfig(ttl=datetime.timedelta(seconds=30), priority='high',), data=data, token=registration_token,)
    response = messaging.send(message)
    return ('')

@app.route('/api/worker/workflow', methods=['POST'])
def worker_workflow():
    workflow = [{'links':{'patch':{'small':'https://images2.imgbox.com/94/f2/NN6Ph45r_o.png','large':'https://images2.imgbox.com/5b/02/QcxHUb5V_o.png'},'article':'https://www.space.com/3590-spacex-falcon-1-rocket-fails-reach-orbit.html'},'success':False,'details':'Забита канализация в кухне','flight_number':1,'name':'Водоотведение','date_utc':'2023-03-24T22:30:00.000Z'},
    {'links':{'patch':{'small':'https://images2.imgbox.com/94/f2/NN6Ph45r_o.png','large':'https://images2.imgbox.com/5b/02/QcxHUb5V_o.png'},'article':'https://www.space.com/3590-spacex-falcon-1-rocket-fails-reach-orbit.html'},'success':True,'details':'Не горит лампочка в лифтовом холе 5-го этажа','flight_number':1,'name':'Электричество','date_utc':'2023-03-24T22:30:00.000Z'},
    {'links':{'patch':{'small':'https://images2.imgbox.com/94/f2/NN6Ph45r_o.png','large':'https://images2.imgbox.com/5b/02/QcxHUb5V_o.png'},'article':'https://www.space.com/3590-spacex-falcon-1-rocket-fails-reach-orbit.html'},'success':False,'details':'В ванной вместо холодной воды идет теплая','flight_number':1,'name':'Водоснабжение','date_utc':'2023-03-24T22:30:00.000Z'},
    {'links':{'patch':{'small':'https://images2.imgbox.com/94/f2/NN6Ph45r_o.png','large':'https://images2.imgbox.com/5b/02/QcxHUb5V_o.png'},'article':'https://www.space.com/3590-spacex-falcon-1-rocket-fails-reach-orbit.html'},'success':True,'details':'Лифт пропускае 5-ый этаж, приезжает на 6-ой','flight_number':1,'name':'Лифт','date_utc':'2023-03-24T22:30:00.000Z'},
    {'links':{'patch':{'small':'https://images2.imgbox.com/94/f2/NN6Ph45r_o.png','large':'https://images2.imgbox.com/5b/02/QcxHUb5V_o.png'},'article':'https://www.space.com/3590-spacex-falcon-1-rocket-fails-reach-orbit.html'},'success':False,'details':'Нет контакта в коннекторе','flight_number':1,'name':'Интернет','date_utc':'2023-03-24T22:30:00.000Z'},
    ]
    return jsonify(workflow)

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
    
