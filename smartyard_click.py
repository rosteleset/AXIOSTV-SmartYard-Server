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

def putEvent(clickhouse_data, clickhouse_column):
    client = clickhouse_connect.get_client(host='localhost', username='default', password='', compress=False)
    try:
        result = client.insert('smartyard.plog', clickhouse_data, clickhouse_column)
        client.close()
        return result.result_rows
    except:
        client.close()
        return []

#print(f"{getPlogs(52120,'20230517')}")
