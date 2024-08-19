#!bin/python
import random, uuid, os, json, requests, binascii
from dotenv import load_dotenv
from requests.exceptions import HTTPError
from sys import argv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    print('not loaded .env file')
    exit()
def smssend(phone,text):
    if os.getenv('SMS_TYPE') == 'kannel':
        kannel_url = "http://%s:%d/cgi-bin/sendsms" % (os.getenv('SMS_HOST'), int(os.getenv('SMS_PORT')))
        kannel_params = (('user', os.getenv('SMS_USER')), ('pass', os.getenv('SMS_PASS')), ('from', os.getenv('SMS_FROM')), ('coding', '2'))
        kannel_params2 = (('to', phone), ('text', text.encode('utf-16-be').decode('utf-8'))) #.upper()
        try:
            response = requests.get(url=kannel_url, params=kannel_params + kannel_params2)
            response.raise_for_status()
        except HTTPError as http_err:
#            print(f'HTTP error occurred: {http_err}')
            return http_err
        except Exception as err:
#            print(f'Other error occurred: {err}')
            return err
        else:
#            print(f'Success send sms to {user_phone} and text {sms_text}!')
            return response
    elif os.getenv('SMS_TYPE') == 'iqsms':
        phone = '+7' + str(phone)[1:]
        url = 'https://api.iqsms.ru/messages/v2/send/'
        response = requests.get(url,params={'login': os.getenv('SMS_USER'), 'password': os.getenv('SMS_PASS'), 'phone': phone, 'text': text})
#        print(f'Success send sms to {phone} and text {text}!')
        return response
    else:
        return 'error type'

#print(f"{smssend('89999999999', 'Код подтверждения')}")
