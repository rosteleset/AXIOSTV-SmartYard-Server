#!bin/python

import clickhouse_connect
import tzlocal

tz_info = tzlocal.get_localzone()

def getPlogs(uid,date):
    client = clickhouse_connect.get_client(host='localhost', username='default', password='', compress=False)
    clickreq = f"select date, uuid, image, objectId, objectType, objectMechanizma, mechanizmaDescription, event, detail, preview, opened from smartyard.plog where (not hidden) and (toYYYYMMDD(date) = {date}) and (uid = {uid}) and (objectType = 0) order by date desc"
    try:
        result = client.query(clickreq, query_tz=tz_info)
        client.close()
        return result.result_rows
    except:
        client.close()
        return []

def getPlogDaysEvents(uid,events):
    client = clickhouse_connect.get_client(host='localhost', username='default', password='', compress=False)
    clickreq = f"select toYYYYMMDD(date) as day, count(date) as events from smartyard.plog where (not hidden) and (uid = {uid}) and (objectType = 0) and (event in {events}) group by toYYYYMMDD(date) order by toYYYYMMDD(date) desc"
    try:
        result = client.query(clickreq, query_tz=tz_info)
        client.close()
        return result.result_rows
    except:
        client.close()
        return []

def getPlogDays(uid):
    client = clickhouse_connect.get_client(host='localhost', username='default', password='', compress=False)
    clickreq = f"select toYYYYMMDD(date) as day, count(date) as events from smartyard.plog where (not hidden) and (uid = {uid}) and (objectType = 0) group by toYYYYMMDD(date) order by toYYYYMMDD(date) desc"
    try:
        result = client.query(clickreq, query_tz=tz_info)
        client.close()
        return result.result_rows
    except:
        client.close()
        return []

def getCamPlogs(camId,date):
    uid = 1
    client = clickhouse_connect.get_client(host='localhost', username='default', password='', compress=False)
    clickreq = f"select startTime, endTime, eventType, deviceDesc, uuid, image, preview, analisis, analisDesc from smartyard.event where (toYYYYMMDD(startTime) = {date}) and (deviceId = {camId}) order by startTime desc"
    try:
        result = client.query(clickreq, query_tz=tz_info)
        client.close()
        return result.result_rows
    except:
        client.close()
        return []

def getCamPlogDaysEvents(camId,events):
    uid = 1
    client = clickhouse_connect.get_client(host='localhost', username='default', password='', compress=False)
    clickreq = f"select toYYYYMMDD(startTime) as day, count(startTime) as events from smartyard.event where (deviceId = {camId}) and (eventType in {events}) group by toYYYYMMDD(startTime) order by toYYYYMMDD(startTime) desc"
    try:
        result = client.query(clickreq, query_tz=tz_info)
        client.close()
        return result.result_rows
    except:
        client.close()
        return []

def getCamPlogDays(camId):
    uid = 1
    client = clickhouse_connect.get_client(host='localhost', username='default', password='', compress=False)
    clickreq = f"select toYYYYMMDD(startTime) as day, count(startTime) as events from smartyard.event where (deviceId = {camId}) group by toYYYYMMDD(startTime) order by toYYYYMMDD(startTime) desc"
    try:
        result = client.query(clickreq, query_tz=tz_info)
        client.close()
        return result.result_rows
    except:
        client.close()
        return []

def putEvent(clickhouse_data, clickhouse_column):
    client = clickhouse_connect.get_client(host='localhost', username='default', password='', compress=False)
    try:
        result = client.insert('smartyard.plog', clickhouse_data, clickhouse_column)
        client.close()
        return result.result_rows
    except:
        client.close()
        return []
