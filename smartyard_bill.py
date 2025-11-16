#!bin/python
import os, pymysql, uuid, subprocess, datetime, calendar
from dotenv import load_dotenv
from datetime import datetime, timedelta
from werkzeug.datastructures import ImmutableMultiDict
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    print('not loaded .env file')
    exit()

host=os.getenv('MY_HOST')
user=os.getenv('MY_USER')
password=os.getenv('MY_PASS')
database=os.getenv('MY_DBNAME')
billapiurl=os.getenv('BILLAPI_URL')
billapilogin=os.getenv('BILLAPI_LOGIN')
billapipass=os.getenv('BILLAPI_PASS')
charset='utf8mb4'

uid_phones = {
1:{'phone':['89103523378','89624380887','89997901331'],'login':10001,'address':'г. Пятигорск, ул. Невская, д.18б кв. 10','cams_open':True,'cams_paid':True,'camsdata':'2025-11-11'},
2:{'phone':['89103523378','89624380887','89997901331'],'login':10002,'address':'г. Пятигорск, ул. Ленина, д.1 кв. 5','cams_open':True,'cams_paid':False,'camsdata':'2025-09-09'},
3:{'phone':['89880553131'],'login':10003,'address':'г. Волгоград, ул. Невская, д.18б кв. 8','cams_open':True,'cams_paid':True},
}


def lastDay():
    dt = datetime.now()
    day = calendar.monthrange(dt.year, dt.month)[1]
    ld = str(dt.year) + '-' + str(dt.month) + '-' + str(day)
    return ld

def uidFrom(phone):
    uid = []
    for key,value in uid_phones.items():
        if str(phone) in value['phone']:
            uid.append(key)
    return uid

def isActiv(uid, deviceIds):
    rows = {}
    for deviceId in deviceIds:
        rows[deviceId] = 2
    return rows

def addressList(userphone):
    uids = uidFrom(userphone)
    rows = []
    for uid in uids:
        row = {}
        row['uid'] = uid
        row['login'] = uid_phones[uid]['login']
        row['address'] = uid_phones[uid]['address']
        row['cams_open'] = uid_phones[uid]['cams_open']
        row['cams_paid'] = uid_phones[uid]['cams_paid']
        rows.append(row)
    return rows

def billingList(userphone):
    uids = uidFrom(userphone)
    billingList = []
    for uid in uids:
        row = {}
        row['login'] = str(uid_phones[uid]['login'])
        row['address'] = uid_phones[uid]['address']
        row['internet'] = str(float(0))
        row['internetdata'] = ''
        row['tv'] = str(float(0))
        row['tvdata'] = ''
        row['phone'] = str(float(0))
        row['phonedata'] = ''
        row['cams'] = str(float(261))
        row['camsdata'] = str(uid_phones[uid]['camsdata'])
        row['camsname'] = 'Умное пространство'
        row['balans'] = float(0)
        row['payment'] = float(261)
        row['invoice'] = True
        row['detail'] = True
        row['receipt'] = True
        billingList.append(row)
    return billingList

def paySuccess(amount, agrmid):
    #print (f" {amount/100} {agrmid} {str(uuid.uuid4())}")
    pay = subprocess.run(['/opt/smartyard/curl.sh %s %s %s %s %s %s' %(amount/100, agrmid, str(uuid.uuid4()), billapiurl, billapilogin, billapipass)], shell=True)
    return

def uidFromflatNumber(address, flat):
    uid = 0
    fulladdress = address + ' кв. ' + str(flat)
    for key,value in uid_phones.items():
        if fulladdress == value['address']:
            uid = key
    return uid

def uidFromAddress(address):
    uid = None
    for key,value in uid_phones.items():
        if address == value['address']:
            uid = key
    return uid

def addressFromUid(uid):
    address = uid_phones[int(uid)]['address']
    return address

def fullAddressFromUid(uid):
    address = uid_phones[int(uid)]['address']
    return address

def flatFromUid(uid):
    flat = int(uid_phones[int(uid)]['address'].split("\r")[0].split("кв.")[1])
    return flat

def userPhones(uid):
    try:
        return uid_phones[int(uid)]['phone']
    except:
        return []

def newInvoice(login, amount, phone, customer):
    if customer != "SmartYard":
        customer = 'Пупкин Иван Иванович'
    rows = {'clientName': customer, 'invoice_id': 1, 'invoice_num': 1}
    return rows

def getDetail(login, year):
    return [{'id': 31519, 'date': '00:00 01.10.2025', 'sum': -2160.0, 'dsc': 'Активация тарифного плана'}, {'id': 22244, 'date': '14:06 19.09.2025', 'sum': 8640.0, 'dsc': 'Банк'}, {'id': 30872, 'date': '09:25 01.09.2025', 'sum': -2160.0, 'dsc': 'Активация тарифного плана'}, {'id': 30195, 'date': '00:00 01.08.2025', 'sum': -2160.0, 'dsc': 'Активация тарифного плана'}, {'id': 29270, 'date': '12:41 25.06.2025', 'sum': -2160.0, 'dsc': 'CHANGE_TP'}]

def getReceipt(login, receiptId):
    return {'date': '30.10.2025', 'customer': 'ООО «БАРБАРИС» БАРБАРИСОВ Сергей Владимирович', 'sum': 2160.0, 'dsc': 'Активация тарифного плана', 'start': '01.10.2025г.', 'end': '30.10.2025г.', 'service': 'доступ в сеть Интернет'}

