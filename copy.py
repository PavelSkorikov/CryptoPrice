from flask import Flask
from flask_sslify import SSLify
from flask import request
from flask import jsonify
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import re
import requests
import json


app = Flask(__name__)
sslify = SSLify(app)

proxies = {
    'https': 'http://176.9.202.125:3128',
}
URL = 'https://api.telegram.org/bot_token/'


def send_message(chat_id, text='Wait a second, please...'):
    url = URL + 'sendmessage?chat_id={}&text={}'.format(chat_id, text)
    answer = {'chat_id':chat_id, 'text':text}
    requests.post(url, json=answer, proxies=proxies)

def json_write(data):
     with open('updates.json', 'w') as file:
         json.dump(data, file, indent=2, ensure_ascii=False)

def get_btc():
    url = 'https://yobitex.net/api/2/btc_usd/ticker'
    r = requests.get(url).json()
    price = r['ticker']['last']
    return str(price)+' USD'

def responce_question(text):
    pattern = r'/(\w+)'
    ask = re.search(pattern, text).group(1)
    return ask

def crypto_price(crypto_name):
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    parameters = {
        'start': '1',
        'limit': '5000',
        'convert': 'USD',
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': '******************',
    }
    session = Session()
    session.headers.update(headers)
    response = session.get(url, params=parameters)
    data = json.loads(response.text)
    crypto = responce_question(crypto_name)
    for i in range(len(data['data'])):
        if data['data'][i]['slug'] == crypto:
            price = str(data['data'][i]['quote']['USD']['price']) + ' USD'
            return price



@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        r = request.get_json()
        chat_id = r['message']['chat']['id']
        message = r['message']['text']
        pattern=r'/\w+'
        if re.search(pattern, message):
            send_message(chat_id, text=crypto_price(message))
        return jsonify(r)
    return '<h1>Hello bot</h1>'
if __name__ == '__main__':
    app.run()