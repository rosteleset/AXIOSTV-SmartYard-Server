import functools, os, uuid
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from pydantic import BaseModel
from sqlalchemy import create_engine, MetaData, Column, BigInteger, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, MACADDR, TIMESTAMP, ARRAY, BYTEA, INET, JSONB
from sqlalchemy.sql import exists, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from contextlib import asynccontextmanager
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    print('not loaded .env file')
    exit()

database_path = "postgresql://" + os.getenv('PG_USER') + ":" + os.getenv('PG_PASS') + "@" + os.getenv("PG_HOST") + ":5432/" + os.getenv('PG_DBNAME')

db = SQLAlchemy()
def create_db_connection(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config['JSON_AS_ASCII'] = False
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)
    with app.app_context():
        db.create_all()

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
    whiterabbit = db.Column(db.DateTime(timezone=False))

    def __init__(self, uid, intercom, asterisk, w_rabbit, frs, code, guest, whiterabbit ):
        self.uid = uid
        self.intercom = intercom
        self.asterisk = asterisk
        self.w_rabbit = w_rabbit
        self.frs = frs
        self.code = code
        self.guest = guest
        self.whiterabbit = whiterabbit

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
    strims = db.Column(db.ARRAY(String))
    pushtoken = db.Column(db.Text)
    platform = db.Column(db.Text)
    version =  db.Column(db.Text)
    manufacturer =  db.Column(db.Text)
    model =  db.Column(db.Text)
    osver =  db.Column(db.Text)
    notify = db.Column(db.Boolean, default=True)
    money = db.Column(db.Boolean, default=True)

    def __init__(self, uuid, userphone, name, patronymic, email, videotoken, uid, vttime, strims, pushtoken, platform, version, manufacturer, model, osver, notify, money):
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
        self.manufacturer = manufacturer
        self.model = model
        self.osver = osver
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

class Invoices(db.Model):
    __tablename__ = 'invoices'

    invoice_id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    invoice_time = db.Column(db.DateTime(timezone=False), server_default=func.current_timestamp())
    invoice_pay = db.Column(db.Boolean, default=False)
    contract = db.Column(db.Text, index=True)
    amount = db.Column(db.Integer, nullable=True)

    def __init__(self, invoice_id, invoice_time, invoice_pay, contract, amount):
        self.invoice_id = invoice_id
        self.invoice_time = invoice_time
        self.invoice_pay = invoice_pay
        self.contract = contract
        self.amount = amount

    def __repr__(self):
        return f""

class Types(db.Model):
    __tablename__ = 'types'

    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    type = db.Column(db.String(24), nullable=True)

    def __init__(self, id, type):
        self.id = id
        self.type = type

    def __repr__(self):
        return f""

class Devices(db.Model):
    __tablename__ = 'devices'

    device_id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True) # ID девайса
    device_uuid = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4) # UUID девайса
    device_mac = db.Column(MACADDR(), nullable=True) # MAC адрес девайса, заполняется только для камер подключенных по SRT
    device_type = db.Column(db.Integer, ForeignKey('types.id', ondelete='CASCADE'), nullable=False) # 1-камера 2-замок 3-srt камера
    affiliation = db.Column(db.Integer, nullable=True) # Fatkbhjdfyyjcnm, необязаьтельное поле
    owner = db.Column(db.Integer, nullable=True) # Пользователь, необязательное поле
    url = db.Column(db.String(64), nullable=True) # УРЛ на видеосервере
    port = db.Column(db.Integer, nullable=True) # Порт на видеосервере, только для srt камер
    stream = db.Column(db.String(64), nullable=True) # Адрес rtsp потока камеры
    is_active = db.Column(db.Boolean, default=False, nullable=False) # Включена ли камера
    title = db.Column(db.String(64), nullable=True) # Описание, видно в МП
    address = db.Column(db.String(110), nullable=True) # Адрес девайса, обязательное поле, по нему идет поиск устройств
    latitude = db.Column(db.Numeric(12,9), nullable=True) # Географические координаты для отображения в МП, обязательное поле
    longitude = db.Column(db.Numeric(12,9), nullable=True) # Географические координаты для отображения в МП, обязательное поле
    server_id = db.Column(db.Integer, nullable=True) # ID видеосервера, не обязательное поле
    record_days = db.Column(db.Integer, nullable=True) # Длина архива, не обязательное поле
    record_path = db.Column(db.Text, nullable=True) # Путь архива, не обязательное поле
    domophoneid = db.Column(db.Integer, nullable=True) # Логин SIP. Внимание, на панеле эта цифра + 100000
    monitorid = db.Column(db.Integer, nullable=True) # Логин SIP. Внимание, на мониторе эта цифра + 4000000000
    sippassword = db.Column(db.Text, nullable=True) # Gfhjkm ЫШЗ
    dtmf = db.Column(db.Integer, nullable=True) # Код открытия
    camshot = db.Column(db.Text, nullable=True) # УРЛ получения стоп кадра с камеры
    paneltype = db.Column(db.Integer, nullable=True) # 1-Бевард 2-Сокол
    panelip = db.Column(INET(), nullable=True) # IP адрес домофона
    panellogin = db.Column(db.Text, nullable=True) # Логин консоли домофона
    panelpasswd = db.Column(db.Text, nullable=True) # Пароль консоли домофона
    second_door = db.Column(db.Integer, nullable=True)
    onvifip = db.Column(INET(), nullable=True) # IP адрес onvif
    onvifport = db.Column(db.Integer, nullable=True) # Порт onvif
    onviflogin = db.Column(db.Text, nullable=True) # Логин onvif
    onvifpasswd = db.Column(db.Text, nullable=True) # Пароль onvif
    onviffilter = db.Column(db.Integer, default=0) # Таи фильтра onvif

    def __init__(self, device_id, device_uuid, device_mac, device_type, affiliation, owner, url, port, stream, is_active, title, address, latitude, longitude, server_id, record_days, record_path, domophoneid, monitorid, sippassword, dtmf, camshot, paneltype, panelip, panellogin, panelpasswd, second_door, onvifip, onvifport, onviflogin, onvifpasswd, onviffilter):
        self.device_id = device_id
        self.device_uuid = device_uuid
        self.device_mac = device_mac
        self.device_type = device_type
        self.affiliation = affiliation
        self.owner = owner
        self.url = url
        self.port = port
        self.stream = stream
        self.is_active = is_active
        self.title = title
        self.address = address
        self.latitude = latitude
        self.longitude = longitude
        self.server_id = server_id
        self.record_days = record_days
        self.record_path = record_path
        self.domophoneid = domophoneid
        self.monitorid = monitorid
        self.sippassword = sippassword
        self.dtmf = dtmf
        self.camshot = camshot
        self.paneltype = paneltype
        self.panelip = panelip
        self.panellogin = panellogin
        self.panelpasswd = panelpasswd
        self.second_door = second_door
        self.onvifip = onvifip
        self.onvifport = onvifport
        self.onviflogin = onviflogin
        self.onvifpasswd = onvifpasswd
        self.onviffilter = onviffilter

    def __repr__(self):
        return f""

class Rights(db.Model):
    __tablename__ = 'rights'

    uid = db.Column(db.Integer, nullable=False, primary_key=True)
    uid_right = db.Column(db.ARRAY(Integer), nullable=True)

    def __init__(self, uid, uid_right):
        self.uid = uid # UID пользователя
        self.uid_right = uid_right # массив ID девайсев, назначенных пользователю

    def __repr__(self):
        return f""

class Doors(db.Model):
    __tablename__ = 'doors'

    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    open = db.Column(db.String(64), nullable=False) # УРЛ открытия
    device_id = db.Column(db.Integer, ForeignKey('devices.id', ondelete='CASCADE'), nullable=False) # ID в талице devuces как замка
    cam = db.Column(db.Integer, ForeignKey('devices.id', ondelete='CASCADE'), nullable=False) # ID в талице devuces как камеры
    icon = db.Column(db.String(14), nullable=False) # Иконка в МП
    entrance = db.Column(db.Integer, nullable=False) # Подъезд, не обязательное поле
    name = db.Column(db.Text, nullable=False) # Название
    open_trait = db.Column(db.Text, nullable=True) # тип запроса на открытие (GET, PUT, POST)
    rubetek_uuid = db.Column(UUID(as_uuid=True), nullable=True) # Рубитек UUID, не обязательное поле
    rubetek_ext = db.Column(db.Integer, nullable=True) # Признак внешнего устройства Рубитек, не обязательное поле
    def __init__(self, id, open, device_id, cam, icon, entrance, name, open_trait, rubetek_uuid, rubetek_ext):
        self.id = id
        self.open = open
        self.device_id = device_id
        self.cam = cam
        self.icon = icon
        self.entrance = entrance
        self.name = name
        self.open_trait = open_trait
        self.rubetek_uuid = rubetek_uuid
        self.rubetek_ext = rubetek_ext

    def __repr__(self):
        return f""

class Keys(db.Model):
    __tablename__ = 'keys'

    key = db.Column(BYTEA(), nullable=False, primary_key=True)
    uid = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=True)

    def __init__(self, key, uid, comment):
        self.key = key
        self.uid = uid
        self.comment = comment

    def __repr__(self):
        return f""

class Upgrade(db.Model):
    __tablename__ = 'upgrade'

    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    androidupgrade = db.Column(db.Integer, nullable=False)
    androidforceupgrade = db.Column(db.Integer, nullable=False)
    harmonyupgrade = db.Column(db.Integer, nullable=False)
    harmonyforceupgrade = db.Column(db.Integer, nullable=False)
    iosupgrade = db.Column(db.Integer, nullable=False)
    iosforceupgrade = db.Column(db.Integer, nullable=False)

    def __init__(self, id, androidupgrade,androidforceupgrade,harmonyupgrade,harmonyforceupgrade,iosupgrade,iosforceupgrade):
        self.id = id
        self.androidupgrade = androidupgrade
        self.androidforceupgrade = androidforceupgrade
        self.harmonyupgrade = harmonyupgrade
        self.harmonyforceupgrade = harmonyforceupgrade
        self.iosupgrade = iosupgrade
        self.iosforceupgrade = iosforceupgrade

    def __repr__(self):
        return f""
