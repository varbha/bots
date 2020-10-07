import requests
from flask import Flask, request, Response

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

URL_HOST = "https://gitlab.com/api/v4/issues"
URL_PRIV = "private_token=pLEY6MtfGVF8FCx"

headers = {"private_token" : "pLEY6MtfGVF8FCx"}

@app.route('/webhook', methods=['POST'])
def respond():
    print(request.json);
    print('-------')
    r = requests.get(URL_HOST, headers=headers, params={'iid[]': '1'})
    print(r.json())
    return Response(status=200)
    
