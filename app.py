#!bin/python
import random, uuid, os, json, requests, binascii, secrets, datetime, pytz, time, calendar
from datetime import timedelta
from random import randint
from flask import Flask, jsonify, request, make_response, abort
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

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://" + os.getenv('PG_USER') + ":" + os.getenv('PG_PASS') + "@" + os.getenv("PG_HOST") + ":5432/" + os.getenv('PG_DBNAME')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

kannel_url = "http://%s:%d/cgi-bin/sendsms" % (os.getenv('KANNEL_HOST'), int(os.getenv('KANNEL_PORT')))
kannel_params = (('user', os.getenv('KANNEL_USER')), ('pass', os.getenv('KANNEL_PASS')), ('from', os.getenv('KANNEL_FROM')), ('coding', '2'))
billing_url = os.getenv('BILLING_URL')
expire = int(os.getenv('EXPIRE'))
proxyfl = os.getenv('PROXYFL')

testuser = os.getenv('TEST_USER')
testpass = os.getenv('TEST_PASS')

android_upgrade = 6
android_force_ugrade = 5
ios_upgrade = 9
ios_force_ugrade = 9

class Temps(db.Model):
    __tablename__ = 'temps'

    userphone = db.Column(db.BigInteger, primary_key=True)
    smscode = db.Column(db.Integer, index=True, unique=True)

    def __init__(self, userphone, smscode):
        self.userphone = userphone
        self.smscode = smscode

    def __repr__(self):
        return f""

class Settings(db.Model):
    __tablename__ = 'settings'

    uid= db.Column(db.Integer, primary_key=True)
    intercom = db.Column(db.Boolean, default=True)
    asterisk = db.Column(db.Boolean, default=True)
    w_rabbit = db.Column(db.Boolean, default=False)
    frs = db.Column(db.Boolean, default=True)
    code = db.Column(db.Integer)
    guest = db.Column(db.DateTime(timezone=False))

    def __init__(self, uid, intercom, asterisk, w_rabbit, frs, code, guest ):
        self.uid = uid
        self.intercom = intercom
        self.asterisk = asterisk
        self.w_rabbit = w_rabbit
        self.frs = frs
        self.code = code
        self.guest = guest

    def __repr__(self):
        return f""


class Users(db.Model):
    __tablename__ = 'users'

    uuid = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    userphone = db.Column(db.BigInteger, index=True, unique=True)
    name = db.Column(db.String(24))
    patronymic = db.Column(db.String(24))
    email = db.Column(db.String(60))
    videotoken = db.Column(db.String(32))
    uid= db.Column(db.Integer)
    vttime = db.Column(db.DateTime(timezone=False))
    strims = db.Column(db.ARRAY(String(10)))
    pushtoken = db.Column(db.Text)
    platform = db.Column(db.String(7))
    version =  db.Column(db.String(10))
    notify = db.Column(db.Boolean, default=True)
    money = db.Column(db.Boolean, default=True)

    def __init__(self, uuid, userphone, name, patronymic, email, videotoken, uid, vttime, strims, pushtoken, platform, version, notify, money):
        self.uuid = uuid
        self.userphone = userphone
        self.name = name
        self.patronymic = patronymic
        self.email = email
        self.videotoken = videotoken
        self.uid = uid
        self.vttime = vttime
        self.strims = strims
        self.pushtoken = pushtoken
        self.platform = platform
        self.version = version
        self.notify = notify
        self.money = money

    def __repr__(self):
        return f""


class Records(db.Model):
    __tablename__ = 'records'

    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    uid = db.Column(db.Integer)
    url = db.Column(db.Text, index=True, unique=True )
    fileurl = db.Column(db.Text, index=True, unique=True)
    rtime = db.Column(db.DateTime(timezone=False), server_default=func.current_timestamp()) 
    rdone = db.Column(db.Boolean, default=False)

    def __init__(self, id, uid, url, fileurl, rtime, rdone):
        self.id = id
        self.uid = uid
        self.url = url
        self.fileurl = fileurl
        self.rtime = rtime
        self.rdone = rdone

    def __repr__(self):
        return f""

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
    if not db.session.query(db.session.query(Users).filter_by(uuid=key.get('Authorization')[7:]).exists()).scalar():
        response = {'code':401,'name':'Не авторизован','message':'Не авторизован'}
        abort (401)
    return db.session.query(Users.userphone).filter_by(uuid=key.get('Authorization')[7:]).first()[0]

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
    if db.session.query(db.exists().where(Users.videotoken==token)).scalar():
        row = [r._asdict() for r in db.session.query(Users.vttime, Users.strims).filter_by(videotoken = token).all()]
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
    response = requests.post(billing_url + "getaddresslist", headers={'Content-Type':'application/json'}, data=json.dumps({'phone': phone})).json()
    return jsonify(response)

@app.route('/api/address/getSettingsList', methods=['POST'])
def address_getSettingsList():
    global response
    phone = access_verification(request.headers)
    response = requests.post(billing_url + "getsettingslist", headers={'Content-Type':'application/json'}, data=json.dumps({'phone': phone})).json()
    for item in response['data']:
        if 'flatId' in item:
            uid = item['flatId']
            if not db.session.query(db.exists().where(Settings.uid==uid)).scalar():
                code = int(str(randint(1, 9)) + str(randint(0, 9)) + str(randint(0, 9)) + str(randint(0, 9)) + str(randint(0, 9)))
                new_uid = Settings(uid = uid, intercom = True, asterisk = True, w_rabbit = False, frs = True, code = code, guest = '2022-06-06 00:23:50')
                db.session.add(new_uid)
                db.session.commit()
    return jsonify(response)

@app.route('/api/address/intercom', methods=['POST'])
def address_intercom():
    global response
    access_verification(request.headers)
    request_data = json_verification(request)
    if not 'flatId' in request_data:
        response = {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'}
        abort (422)
    uid = request_data['flatId']
    if db.session.query(db.exists().where(Settings.uid==uid)).scalar():
        if 'settings' in request_data:
            settings = request_data['settings']
            if 'CMS' in settings:
                intercom = str2bool(settings['CMS'])
                db.session.query(Settings).filter_by(uid=uid).update({'intercom' : intercom})
                db.session.commit()
            if 'VoIP' in settings:
                asterisk = str2bool(settings['VoIP'])
                db.session.query(Settings).filter_by(uid=uid).update({'asterisk' : asterisk})
                db.session.commit()
            if 'autoOpen' in settings:
                guest = settings['autoOpen']
                db.session.query(Settings).filter_by(uid=uid).update({'guest' : guest})
                db.session.commit()
            if 'whiteRabbit' in settings:
                if str(settings['whiteRabbit']) == '0':
                    w_rabbit = False
                else:
                    w_rabbit = True
                db.session.query(Settings).filter_by(uid=uid).update({'w_rabbit' : w_rabbit})
                db.session.commit()
            if 'FRSDisabled' in settings:
                frs = not str2bool(settings['FRSDisabled'])
                db.session.query(Settings).filter_by(uid=uid).update({'frs' : frs})
                db.session.commit()
        row = [r._asdict() for r in db.session.query(Settings.intercom, Settings.asterisk, Settings.w_rabbit, Settings.frs, Settings.code, Settings.guest).filter_by(uid = uid).all()]
        CMS = bool2str(row[0]['intercom'])
        VoIP = bool2str(row[0]['asterisk'])
        if row[0]['w_rabbit']:
            whiteRabbit = '5'
        else:
            whiteRabbit = '0'
        FRSDisabled = bool2str(not row[0]['frs'])
        code = str(row[0]['code'])
        guest = row[0]['guest'].strftime("%Y-%m-%d %H:%M:%S")
        response = {'code':200,'name':'OK','message':'Хорошо','data':{'allowDoorCode':'t','doorCode':code,'CMS':CMS,'VoIP':VoIP,'autoOpen':guest,'whiteRabbit':whiteRabbit,'FRSDisabled':FRSDisabled}}
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
    access_verification(request.headers)
    request_data = json_verification(request)
    if not 'domophoneId' in request_data:
        response = {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'}
        abort (422)
    domophoneId = request_data['domophoneId']
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
    flatId = request_data['flatId']
    response = {'code':200,'name':'OK','message':'Хорошо','data':[{'date':'2021-12-15 13:03:23','uuid':'4d5082d2-f8a1-48ac-819e-c16f1f81a1e0','image':'3f99bdf6-96ef-4300-b709-1f557806c65b','objectId':'79','objectType':'0','objectMechanizma':'0','mechanizmaDescription':'Пионерская 5 б п 3 [Подъезд]','event':'1','detail':'1','preview':'https:\/\/static.dm.lanta.me\/2021-12-15\/3\/f\/9\/9\/3f99bdf6-96ef-4300-b709-1f557806c65b.jpg','previewType':2,'detailX':{'opened':'f','face':{'left':'614','top':'38','width':'174','height':'209'},'flags':['canLike']}},{'date':'2021-12-15 00:16:20','uuid':'bc1671b4-e01b-487e-b175-745e82be0ca9','image':'86ddb8e1-1122-4946-8495-a251b6320b99','objectId':'75','objectType':'0','objectMechanizma':'0','mechanizmaDescription':'Пионерская 5 б [Калитка]','event':'4','detail':'89103523377','preview':'https:\/\/static.dm.lanta.me\/2021-12-15\/8\/6\/d\/d\/86ddb8e1-1122-4946-8495-a251b6320b99.jpg','previewType':1,'detailX':{'phone':'89103523377'}},{'date':'2021-12-15 00:14:21','uuid':'32fd7c27-0d35-4d98-ab29-2544c3d0b9a7','image':'ad14c83a-126a-4f09-a659-f412fb11007e','objectId':'75','objectType':'0','objectMechanizma':'0','mechanizmaDescription':'Пионерская 5 б [Калитка]','event':'4','detail':'89103523377','preview':'https:\/\/static.dm.lanta.me\/2021-12-15\/a\/d\/1\/4\/ad14c83a-126a-4f09-a659-f412fb11007e.jpg','previewType':1,'detailX':{'phone':'89103523377'}},{'date':'2021-12-15 00:03:56','uuid':'ff42c747-3216-4fa7-8b68-128207d1a9ab','image':'0b335948-864f-41d6-b9a7-465f88f20ef1','objectId':'75','objectType':'0','objectMechanizma':'0','mechanizmaDescription':'Пионерская 5 б [Калитка]','event':'4','detail':'89103523377','preview':'https:\/\/static.dm.lanta.me\/2021-12-15\/0\/b\/3\/3\/0b335948-864f-41d6-b9a7-465f88f20ef1.jpg','previewType':1,'detailX':{'phone':'89103523377'}},{'date':'2021-12-15 00:01:28','uuid':'0e57d2c7-9e73-4083-98bb-2b140622be93','image':'8fc3224e-ef46-4ec6-9d5d-04e249ec2e31','objectId':'75','objectType':'0','objectMechanizma':'0','mechanizmaDescription':'Пионерская 5 б [Калитка]','event':'4','detail':'89103523377','preview':'https:\/\/static.dm.lanta.me\/2021-12-15\/8\/f\/c\/3\/8fc3224e-ef46-4ec6-9d5d-04e249ec2e31.jpg','previewType':1,'detailX':{'phone':'89103523377'}},{'date':'2021-12-15 00:00:02','uuid':'3bcac0af-677b-49d8-ba65-c18c3bcc8668','image':'c28c7e58-7797-4143-a2b8-2c513e216bb8','objectId':'75','objectType':'0','objectMechanizma':'0','mechanizmaDescription':'Пионерская 5 б [Калитка]','event':'4','detail':'89103523377','preview':'https:\/\/static.dm.lanta.me\/2021-12-15\/c\/2\/8\/c\/c28c7e58-7797-4143-a2b8-2c513e216bb8.jpg','previewType':1,'detailX':{'phone':'89103523377'}}]}
    return jsonify(response)

@app.route('/api/address/plogDays', methods=['POST'])
def address_plogDays():
    global response
    access_verification(request.headers)
    request_data = json_verification(request)
    if not 'flatId' in request_data:
        response = {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'}
        abort (422)
    flatId = request_data['flatId']
    response = {'code':200,'name':'OK','message':'Хорошо','data':[{'day':'2021-12-15','events':'6'},{'day':'2021-12-13','events':'2'},{'day':'2021-12-11','events':'3'},{'day':'2021-12-09','events':'3'},{'day':'2021-12-07','events':'1'},{'day':'2021-12-06','events':'4'},{'day':'2021-12-05','events':'1'},{'day':'2021-12-04','events':'1'},{'day':'2021-11-30','events':'1'},{'day':'2021-11-29','events':'6'},{'day':'2021-11-27','events':'7'},{'day':'2021-11-26','events':'13'},{'day':'2021-11-25','events':'5'},{'day':'2021-11-23','events':'2'},{'day':'2021-11-22','events':'2'},{'day':'2021-11-20','events':'2'},{'day':'2021-11-17','events':'3'},{'day':'2021-11-16','events':'1'},{'day':'2021-11-15','events':'1'},{'day':'2021-11-13','events':'1'},{'day':'2021-11-12','events':'6'},{'day':'2021-11-11','events':'2'},{'day':'2021-11-09','events':'3'},{'day':'2021-11-05','events':'1'},{'day':'2021-10-30','events':'1'},{'day':'2021-10-29','events':'3'},{'day':'2021-10-28','events':'3'},{'day':'2021-10-27','events':'3'},{'day':'2021-10-26','events':'2'},{'day':'2021-10-23','events':'2'},{'day':'2021-10-22','events':'3'},{'day':'2021-10-21','events':'4'},{'day':'2021-10-19','events':'3'},{'day':'2021-10-18','events':'2'},{'day':'2021-10-16','events':'4'},{'day':'2021-10-15','events':'1'},{'day':'2021-10-14','events':'3'},{'day':'2021-10-09','events':'1'},{'day':'2021-10-08','events':'6'},{'day':'2021-10-07','events':'4'},{'day':'2021-10-06','events':'7'},{'day':'2021-10-05','events':'6'},{'day':'2021-10-03','events':'1'},{'day':'2021-10-02','events':'7'},{'day':'2021-10-01','events':'12'},{'day':'2021-09-30','events':'5'},{'day':'2021-09-29','events':'6'},{'day':'2021-09-28','events':'17'},{'day':'2021-09-27','events':'7'},{'day':'2021-09-25','events':'2'},{'day':'2021-09-22','events':'1'},{'day':'2021-09-20','events':'1'},{'day':'2021-09-18','events':'4'},{'day':'2021-09-17','events':'3'},{'day':'2021-09-16','events':'5'},{'day':'2021-09-15','events':'1'},{'day':'2021-09-13','events':'12'},{'day':'2021-09-11','events':'1'},{'day':'2021-09-06','events':'2'},{'day':'2021-09-05','events':'2'}]}
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
    response = {'code':200,'name':'OK','message':'Хорошо','data':{'code':code}}
    return jsonify(response)

@app.route('/api/cctv/all', methods=['POST'])
def cctv_all():
    global response
    phone = access_verification(request.headers)
    request_data = json_verification(request)
    houseId = request_data['houseId']
    response = requests.post(billing_url + "getcctvlist", headers={'Content-Type':'application/json'}, data=json.dumps({'houseId': houseId})).json()
    if response['data'] == 402 or response['data'] == 404:
        response = app.response_class(status=response['data'], mimetype='application/json')
        return response
    strims = []
    for item in response['data']:
        strims.append(item['url'][8:].partition('/')[2])
    videotoken = generate_video_token(phone,strims,houseId)
    for item in response['data']:
        item['token'] = videotoken
    return jsonify(response)

@app.route('/api/cctv/camMap', methods=['POST'])
def cctv_camMap():
    global response
    access_verification(request.headers)
    #print(f'Generate videotoken  {videotoken}!')
#    if not request.get_json():
#        response = {'code':422,'name':'Unprocessable Entity','message':'Необрабатываемый экземпляр'}
#        abort (422)
#    request_data = request.get_json()
#    response = {'code':200,'name':'OK','message':'Хорошо','data':[{'id':'70','url':'https://fl2.lanta.me:8443/91052','token':'acd0c17657395ff3f69d68e74907bb3a','frs':'t'},{'id':'75','url':'https://fl2.lanta.me:8443/91078','token':'acd0c17657395ff3f69d68e74907bb3a','frs':'t'},{'id':'79','url':'https://fl2.lanta.me:8443/91072','token':'acd0c17657395ff3f69d68e74907bb3a','frs':'t'},{'id':'124','url':'https://fl2.lanta.me:8443/95594','token':'acd0c17657395ff3f69d68e74907bb3a','frs':'t'},{'id':'131','url':'https://fl2.lanta.me:8443/91174','token':'acd0c17657395ff3f69d68e74907bb3a','frs':'f'},{'id':'343','url':'https://fl2.lanta.me:8443/90753','token':'acd0c17657395ff3f69d68e74907bb3a','frs':'t'}]}
    response = {'code':200,'name':'OK','message':'Хорошо','data':[{'id':'5','url':'https://fl2.lanta.me:8443/91052','token':'acd0c17657395ff3f69d68e74907bb3a','frs':'t'}]}
    return jsonify(response)

@app.route('/api/cctv/overview', methods=['POST'])
def cctv_overview():
    global response
    access_verification(request.headers)
    response = {'code':200,'name':'OK','message':'Хорошо','data':[]}
    return jsonify(response)

@app.route('/api/cctv/recDownload', methods=['POST'])
def cctv_recDownload():
    global response
    access_verification(request.headers)
    request_data = json_verification(request)
    recordid = request_data['id']
    fileurl = 'https://sa.axiostv.ru/' + db.session.query(Records.fileurl).filter_by(id = recordid).first()[0]
    response = {'code':200,'name':'OK','message':'Хорошо', 'data':fileurl }
    return jsonify(response)

@app.route('/api/cctv/recPrepare', methods=['POST'])
def cctv_recPrepare():
    global response
    phone = access_verification(request.headers)
    request_data = json_verification(request)
    cam_id = request_data['id']
    camresponse = requests.post(billing_url + "getcctvcam", headers={'Content-Type':'application/json'}, data=json.dumps({'camid': cam_id})).json()
    time_from = datetime.datetime.strptime(request_data['from'], '%Y-%m-%d %H:%M:%S')
    time_to = datetime.datetime.strptime(request_data['to'], '%Y-%m-%d %H:%M:%S')
    time_rec = time_to - time_from
    if int(time_rec.seconds) > 900:
        response = {'code':403,'name':'Set less than 15 min.','message':'Установите менее 15 мин.'}
        abort (403)
    row = [r._asdict() for r in db.session.query(Users.videotoken, Users.uid).filter_by(userphone = phone).all()]
    url = camresponse['url'] + '/' + 'archive-'+str(int(time.mktime(time_from.timetuple())))+'-'+str(time_rec.seconds)+'.mp4?token='+'100'+str(row[0]['videotoken'])
    fileurl = '/wwwsa/public/' + camresponse['name'].lower().replace(",", "_").replace(".", "_").replace(" ", "_") + '_' + time_from.strftime("%H-%M-%S_%m_%d_%Y") + '_-_' + time_to.strftime("%H-%M-%S_%m_%d_%Y") + '.mp4'
    db.session.add(Records(id = None, uid = row[0]['uid'], url = url, fileurl = fileurl, rtime = None, rdone = False))
    db.session.commit()
    recordId = db.session.query(Records.id).filter_by(url = url, fileurl = fileurl).first()[0]
    resCode=403
    fil = open(fileurl,'wb')
    cur = pycurl.Curl()
    cur.setopt(cur.URL, url)
    cur.setopt(cur.WRITEDATA, fil)
    cur.perform()
    resCode = cur.getinfo(cur.RESPONSE_CODE)
    resText = cur.getinfo(cur.HTTP_CODE)
    cur.close()
    fil.close()
    #print(f'resCode =   {resCode}    resText =   {resText} url = {url}    fileurl + {fileurl} !')
    if resCode == 200:
        db.session.query(Records).filter_by(id=recordId).update({'rdone' : True})
        db.session.commit()
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
    ##response = {'code':200,'name':'OK','message':'Хорошо','data':{"basePath": "https:\/\/dm.lanta.me\/", "code": "<!DOCTYPE html>\n<html lang=\"ru\">\n<head>\n    <meta charset=\"UTF-8\">\n    <title>inbox<\/title>\n    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0, minimum-scale=1.0, maximum-scale=1.0, user-scalable=no\">\n    <!--\n    <link rel=\"stylesheet\" href=\"reset.css\">\n    <link rel=\"stylesheet\" href=\"styles.css\">\n    -->\n    <style type=\"text\/css\">\n        @font-face {\n            font-family: \"SourceSansPro\";\n            src: url(\"static\/fonts\/sourcesanspro\/sourcesanspro.ttf\");\n        }\n\n        @font-face {\n            font-family: \"SourceSansProBold\";\n            src: url(\"static\/fonts\/sourcesanspro\/sourcesansprobold.ttf\");\n        }\n\n        @font-face {\n            font-family: \"SourceSansProItalic\";\n            src: url(\"static\/fonts\/sourcesanspro\/sourcesansproitalic.ttf\");\n        }\n\n        @font-face {\n            font-family: \"SourceSansProLight\";\n            src: url(\"static\/fonts\/sourcesanspro\/sourcesansprolight.ttf\");\n        }\n\n        @font-face {\n            font-family: \"SourceSansProSemiBold\";\n            src: url(\"static\/fonts\/sourcesanspro\/sourcesansprosemibold.ttf\");\n        }\n\n        *, *::before, *::after {\n            box-sizing: border-box;\n        }\n\n        html, body {\n            width: 100%;\n            height: 100%;\n            font-family: SourceSansPro, sans-serif;\n            font-size: 14px;\n            background: #f3f4fa;\n            overflow-x: hidden;\n        }\n\n        h1, .h1,\n        h2, .h2,\n        h3, .h3,\n        h4, .h4,\n        h5, .h5,\n        h6, .h6 {\n            margin-top: 0;\n            margin-bottom: 0;\n            font-family: SourceSansProBold, sans-serif;\n            font-weight: normal;\n            color: #28323e;\n        }\n\n        h1, .h1 {\n            font-size: 32px;\n            line-height: 120%;\n        }\n\n        h2, .h2 {\n            font-size: 28px;\n            line-height: 120%;\n        }\n\n        h3, .h3 {\n            font-size: 24px;\n            line-height: 24px;\n        }\n\n        h4, .h4 {\n            font-size: 20px;\n            line-height: 24px;\n        }\n\n        h5, .h5 {\n            font-size: 18px;\n            line-height: 24px;\n        }\n\n        h6, .h6 {\n            font-size: 16px;\n            line-height: 24px;\n        }\n\n        .text-1,\n        .text-2,\n        .text-3,\n        .text-4,\n        .text-5 {\n            font-family: SourceSansPro, sans-serif;\n            line-height: 100%;\n        }\n\n        .text-1 {\n            font-family: SourceSansProSemiBold, sans-serif;\n            font-size: 18px;\n        }\n\n        .text-2 {\n            font-size: 16px;\n        }\n\n        .text-3 {\n            font-size: 14px;\n        }\n\n        .text-4 {\n            font-size: 13px;\n        }\n\n        .text-5 {\n            font-size: 12px;\n        }\n\n        .inbox-block {\n            padding: 20px 16px;\n        }\n\n        .inbox-date,\n        .inbox-message-time {\n            display: block;\n            font-size: 14px;\n            line-height: 18px;\n            color: #6d7a8a;\n            opacity: .5;\n        }\n\n        .inbox-date {\n            margin-bottom: 16px;\n            text-align: center;\n        }\n\n        .inbox-message-time {\n            margin-top: 6px;\n            font-size: 10px;\n            text-align: right;\n        }\n\n        .inbox-message-primary,\n        .inbox-message-secondary {\n            display: flex;\n            margin-bottom: 10px;\n        }\n\n        .inbox-message-content {\n            margin-left: 16px;\n            padding: 20px 12px;\n            padding-bottom: 8px;\n            width: 100%;\n            background: #fff;\n            border-radius: 20px;\n            border-top-left-radius: 0;\n        }\n\n        .inbox-message-secondary .inbox-message-content {\n            margin-left: 50px;\n        }\n\n        .inbox-message-content a {\n            margin-bottom: 10px;\n            line-height: 18px;\n            text-decoration: none;\n            color: #007bff;\n        }\n\n        .inbox-message-content p {\n            margin-bottom: 10px;\n            line-height: 18px;\n            color: #6d7a8a;\n        }\n\n        .inbox-message-primary .inbox-message-content p:first-child {\n            margin-bottom: 16px;\n            font-family: SourceSansProSemiBold;\n            font-size: 18px;\n            line-height: 22px;\n            color: #28323e;\n        }\n\n        .inbox-message-content p:last-child {\n            margin-bottom: 0;\n        }\n\n        .inbox-message-icon {\n            display: inline-block;\n            width: 36px;\n            height: 37px;\n        }\n\n        .inbox-message-icon.icon-avatar {\n            background: url('static\/icon\/avatar.png') 0 0 no-repeat;\n            background-size: 100%;\n        }\n\n        .clearfix:before,\n        .clearfix:after {\n            content: \" \";\n            display: table;\n            clear: both;\n        }\n    <\/style>\n<\/head>\n<body>\n<div class=\"inbox-block\"><span class=\"inbox-date\">19 дек 2021<\/span><div class=\"inbox-message-primary\"><i class=\"inbox-message-icon icon-avatar\"><\/i><div class=\"inbox-message-content\"><p><p>Уважаемые пользователи системы распознавания лиц! В понедельник, 20 декабря, в интервале с 10:00 до 12:00 распознавание лиц на вашем домофоне будет временно недоступно. Приносим извинения за возможные неудобства.<\/p><\/p><span class=\"inbox-message-time\">12:35<\/span><\/div><\/div><span class=\"inbox-date\">19 июл 2021<\/span><div class=\"inbox-message-primary\"><i class=\"inbox-message-icon icon-avatar\"><\/i><div class=\"inbox-message-content\"><p><p>Дорогие жители дома №59а корп. 5 по улице Рылеева! У вас появилась бесплатная возможность протестировать систему открывания домофона с распознаванием по лицу.<br \/>\n<br \/><\/p>\n<ol>\n<li>Установите самую свежую версию приложения «ЛАНТА».<br \/><\/li>\n<li>В приложении в настройках адреса включите опции «Распознавание лиц» и «Вести журнал событий» (журнал событий ведётся для каждой квартиры в отдельности, доступа к событиям других квартир нет).<br \/><\/li>\n<li>Откройте дверь подъезда электронным ключом или совершите вызов в свою квартиру через домофон, чтобы в истории событий появились фотографии с вашим изображением.<br \/><\/li>\n<li>В приложении в журнале событий под вашим фото нажмите кнопку «Свой», чтобы добавить лицо в список лиц для открывания домофона.<br \/><\/li>\n<li>При необходимости можно добавить несколько своих лиц для лучшего распознавания (в головном уборе, в очках, с макияжем, с разными причёсками, в инфракрасной подсветке в тёмное время суток).<\/li>\n<\/ol><\/p><span class=\"inbox-message-time\">15:15<\/span><\/div><\/div><span class=\"inbox-date\">16 июл 2021<\/span><div class=\"inbox-message-primary\"><i class=\"inbox-message-icon icon-avatar\"><\/i><div class=\"inbox-message-content\"><p><p><a target=\"_blank\" href=\"https:\/\/stat.lanta-net.ru\">https:\/\/stat.lanta-net.ru<\/a> Имя пользователя: f101182 Пароль: 964f0d7a5<\/p><\/p><span class=\"inbox-message-time\">11:09<\/span><\/div><\/div><span class=\"inbox-date\">29 июн 2021<\/span><div class=\"inbox-message-primary\"><i class=\"inbox-message-icon icon-avatar\"><\/i><div class=\"inbox-message-content\"><p><p>Дорогие жители дома №5б по улице Пионерской! У вас появилась бесплатная возможность протестировать систему открывания домофона с распознаванием по лицу.<br \/>\n<br \/><\/p>\n<ol>\n<li>Установите самую свежую версию приложения «ЛАНТА».<br \/><\/li>\n<li>В приложении в настройках адреса включите опции «Распознавание лиц» и «Вести журнал событий» (журнал событий ведётся для каждой квартиры в отдельности, доступа к событиям других квартир нет).<br \/><\/li>\n<li>Откройте дверь подъезда электронным ключом или совершите вызов в свою квартиру через домофон, чтобы в истории событий появились фотографии с вашим изображением.<br \/><\/li>\n<li>В приложении в журнале событий под вашим фото нажмите кнопку «Свой», чтобы добавить лицо в список лиц для открывания домофона.<br \/><\/li>\n<li>При необходимости можно добавить несколько своих лиц для лучшего распознавания (в головном уборе, в очках, с макияжем, с разными причёсками, в инфракрасной подсветке в тёмное время суток).<\/li>\n<\/ol><\/p><span class=\"inbox-message-time\">20:27<\/span><\/div><\/div><span class=\"inbox-date\">15 янв 2021<\/span><div class=\"inbox-message-primary\"><i class=\"inbox-message-icon icon-avatar\"><\/i><div class=\"inbox-message-content\"><p><p>В вашу учетную запись добавлен новый адрес<\/p><\/p><span class=\"inbox-message-time\">10:38<\/span><\/div><\/div><div class=\"inbox-message-secondary\"><div class=\"inbox-message-content\"><p><p>В вашу учетную запись добавлен новый адрес<\/p><\/p><span class=\"inbox-message-time\">10:32<\/span><\/div><\/div><div class=\"inbox-message-secondary\"><div class=\"inbox-message-content\"><p><p>В вашу учетную запись добавлен новый адрес<\/p><\/p><span class=\"inbox-message-time\">10:30<\/span><\/div><\/div><div class=\"inbox-message-secondary\"><div class=\"inbox-message-content\"><p><p>Ваш пароль на портале видеонаблюдения tD3dcU<\/p><\/p><span class=\"inbox-message-time\">10:30<\/span><\/div><\/div><div class=\"inbox-message-secondary\"><div class=\"inbox-message-content\"><p><p>Ваш код подтверждения: 5749<\/p><\/p><span class=\"inbox-message-time\">10:23<\/span><\/div><\/div><\/div>\n<script type=\"application\/javascript\">\n\/\/    scrollingElement = (document.scrollingElement || document.body)\n\/\/    scrollingElement.scrollTop = scrollingElement.scrollHeight;\n<\/script>\n<\/body>\n<\/html>"}}
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

@app.route('/api/sip/helpMe', methods=['POST'])
def sip_helpMe():
    global response
    access_verification(request.headers)
    request_data = json_verification(request)
    return "Hello, World!"

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
    if not db.session.query(db.session.query(Temps).filter_by(userphone=int(userPhone)).exists()).scalar():
        response = {"code":404,"name":"Not Found","message":"Не найдено"}
        abort(404)
    smsCode = request_data['smsCode']
    if not db.session.query(db.exists().where(Temps.userphone==int(userPhone) and Temps.smscode == int(smsCode))).scalar():
        response = {"code":403,"name":"Пин-код введен неверно","message":"Пин-код введен неверно"}
        abort(403)
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
        new_user = Users(uuid = accessToken, userphone = int(request_data['userPhone']), name = request_data['name'], patronymic = request_data['patronymic'], email = request_data['email'], videotoken = None, uid = None, vttime = datetime.datetime.now(), strims = None, pushtoken = None, platform = None, version = None, notify = True, money = True)
        db.session.add(new_user)
    db.session.query(Temps).filter_by(userphone=int(userPhone)).delete()
    db.session.commit()
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
        if 'enable' in request_data:
            enable = str2bool(request_data['enable'])
            db.session.query(Users).filter_by(userphone=int(phone)).update({'notify' : enable})
            db.session.commit()
    row = [r._asdict() for r in db.session.query(Users.money, Users.notify).filter_by(userphone=int(phone)).all()]
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
    if 'voipToken' in request_data:
        voipToken = request_data['voipToken']
    if 'production' in request_data:
        production = request_data['production']
    db.session.commit()
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
    phone = access_verification(request.headers)
    response = requests.post(billing_url + "getlist", headers={'Content-Type':'application/json'}, data=json.dumps({'phone': phone})).json()
    return jsonify(response)

@app.route('/api/address/getHcsList', methods=['POST'])
def address_getHcsList():
    global response
    access_verification(request.headers)
    response = {'code':200,'name':'OK','message':'Хорошо','data':[{'houseId':'19260','address':'Липецк, ул. Катукова, дом 36 кв 18'},{'houseId':'6694','address':'Липецк, ул. Московская, дом 145 кв 3'}]}
    return jsonify(response)

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
