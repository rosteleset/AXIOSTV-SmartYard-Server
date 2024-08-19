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
1:{'phone':['89272510551','89173365214','89997901321'],'login':10001,'address':'г. Волгоград, ул. Невская, д.18б кв. 10','cams_open':True,'cams_paid':True},
2:{'phone':['89997902450','89997901320'],'login':10002,'address':'г. Кстов, ул. Ленина, д. 1','cams_open':True,'cams_paid':True},
3:{'phone':['89880557820'],'login':10003,'address':'г. Волгоград, ул. Невская, д.18б кв. 8','cams_open':True,'cams_paid':True},
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

def camsActiv(uid):
    row = {}
    try:
        row['cams_open'] = uid_phones[int(uid)]['cams_open']
        row['cams_paid'] = uid_phones[int(uid)]['cams_paid']
    except:
        row['cams_open'] = False
        row['cams_paid'] = False
    return row

def addressList(userphone):
    uids = uidFrom(userphone)
    rows = []
    row = {}
    for uid in uids:
        row['uid'] = uid
        row['login'] = uid_phones[uid]['login']
        row['address'] = uid_phones[uid]['address']
        row['cams_open'] = uid_phones[uid]['cams_open']
        row['cams_paid'] = uid_phones[uid]['cams_paid']
        rows.append(row)
    return rows

def billingList(userphone):
    uids = uidFrom(userphone)
    rows = []
    row = {}
    for uid in uids:
        row['login'] = uid_phones[uid]['login']
        row['address'] = uid_phones[uid]['address']
        row['internet'] = float(0)
        row['internet_data'] = ''
        row['tv'] = float(0)
        row['tv_data'] = ''
        row['phone'] = float(0)
        row['phone_data'] = ''
        row['cams'] = float(261)
        row['cams_data'] = ''
        row['cams_name'] = 'Умное пространство'
        row['balans'] = float(0)
        row['payment'] = float(261)
        rows.append(row)
    return rows


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

def flatFromUid(uid):
    flat = int(uid_phones[int(uid)]['address'].split("\r")[0].split("кв.")[1])
    return flat

def userPhones(uid):
    try:
        return uid_phones[int(uid)]['phone']
    except:
        return []

def newInvoice(login, amount, phone):
    return 1
    
