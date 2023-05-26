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

uid_phones = {1:{'phone':['89997902451','89997901321'],'login':10001,'address':'г. Ярославль, ул. Советская, д.1 кв. 10','cams_open':True,'cams_paid':True},2:{'phone':['89997902450','89997901320'],'login':10002,'address':'','cams_open':True,'cams_paid':True}}


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
        row['internet'] = float(500)
        row['internet_data'] = ''
        row['tv'] = float(200)
        row['tv_data'] = ''
        row['phone'] = float(300)
        row['phone_data'] = ''
        row['cams'] = float(100)
        row['cams_data'] = ''
        row['cams_name'] = 'Умное пространство'
        row['balans'] = float(100)
        row['payment'] = float(1000)
        rows.append(row)
    return rows


def paySuccess(amount, agrmid):
    #print (f" {amount/100} {agrmid} {str(uuid.uuid4())}")
    pay = subprocess.run(['/opt/smartyard/curl.sh %s %s %s %s %s %s' %(amount/100, agrmid, str(uuid.uuid4()), billapiurl, billapilogin, billapipass)], shell=True)
    return

def uidFromflatNumber(address, flat):
    uid = 1
    return uid

def userPhones(uid):
    try:
        return uid_phones[int(uid)]['phone']
    except:
        return []
