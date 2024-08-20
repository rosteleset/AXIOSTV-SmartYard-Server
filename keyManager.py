#!bin/python3

import pycurl, json, requests
    #1: Beward
    #2: ISCom
    #3:

def keyAdd(key, flat, panelType, panelIp, panelLogin, panelPasswd):
    if panelType == 1:
        keyListUrl = 'http://' + panelLogin + ':' + panelPasswd + '@' + panelIp + '/cgi-bin/rfid_cgi'
        keyListresponse = requests.get(keyListUrl).status_code
        if keyListresponse != 404:
            keyAddUrl = 'http://' + panelLogin + ':' + panelPasswd + '@' + panelIp + '/cgi-bin/rfid_cgi'
            params = (('action', 'add'), ('Key', key), ('Apartment', flat))
            keyAddresponse = requests.get(keyAddUrl, params=params).status_code
        elif keyListresponse == 404:
            keyAddUrl = 'http://' + panelLogin + ':' + panelPasswd + '@' + panelIp + '/cgi-bin/mifare_cgi'
            params = (('action', 'add'), ('Key', key), ('Type', 1), ('Apartment', flat))
            keyAddresponse = requests.get(keyAddUrl, params=params).status_code
        else:
            return False
        if keyAddresponse != 200:
            return False
        else:
            return True
    elif panelType == 2:
        keyAddUrl = 'http://' + panelLogin + ':' + panelPasswd + '@' + panelIp + '/key/store'
        data = {'uuid': key, 'panelCode': flat, 'encryption': False}
        keyAddresponse = requests.post(keyAddUrl, headers={'Content-Type':'application/json'}, data=json.dumps({'uuid': key, 'panelCode': flat, 'encryption': False})).status_code
        if keyAddresponse != 200:
            return False
        else:
            return True
    elif panelType == 3:
        print(f"3")
    else:
        print(f"Uncnow")

def keyDell(key, flat, panelType, panelIp, panelLogin, panelPasswd):
    if panelType == 1:
        keyListUrl = 'http://' + panelLogin + ':' + panelPasswd + '@' + panelIp + '/cgi-bin/rfid_cgi'
        keyListresponse = requests.get(keyListUrl).status_code
        if keyListresponse != 404:
            keyDellUrl = 'http://' + panelLogin + ':' + panelPasswd + '@' + panelIp + '/cgi-bin/rfid_cgi'
            params = (('action', 'delete'), ('Key', key))
            keyDellresponse = requests.get(keyDellUrl, params=params).status_code
        elif keyListresponse == 404:
            keyDellUrl = 'http://' + panelLogin + ':' + panelPasswd + '@' + panelIp + '/cgi-bin/mifare_cgi'
            params = (('action', 'delete'), ('Key', key))
            keyDellresponse = requests.get(keyDellUrl, params=params).status_code
        else:
            return False
        if keyDellresponse != 200:
            return False
        else:
            return True
    elif panelType == 2:
        keyDellUrl = 'http://' + panelLogin + ':' + panelPasswd + '@' + panelIp + '/key/store/' + key
        keyDellresponse = requests.delete(keyDellUrl).status_code
        if keyDellresponse != 204:
            return False
        else:
            return True
    elif panelType == 3:
        print(f"3")
    else:
        print(f"Uncnow")

