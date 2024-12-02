# flask_ngrok_example.py
from flask import Flask
from flask import request, jsonify
import json
import requests

app = Flask(__name__)

token = "i8tzMul6vNgKfnYfQJImULbFm3JILJah1"
conn_key = "w-api_FFCR1GDPPZ"
host = "host01.serverapi.dev"
url = f"https://{host}/message/send-text?connectionKey={conn_key}"

payload = json.dumps(
    {
        "phoneNumber": "555384562222",
        "text": "teste retorno",
    }
)


def send_msg(url, token, payload):

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }

    data = requests.post(
        url=url,
        data=payload,
        headers=headers,
    )

    print(data)


@app.route("/")
def hello():
    return "Hello World!"


@app.route("/1", methods=["GET", "POST"])
def a1():
    if request.method == "GET":
        if "12" in request.args:
            return "hub challenge"
        print(request.json)
        return "no hub challenge"


@app.route("/facebook", methods=["GET"])
def get_facebook():
    my_token = "abc123"  # The token you setup on the App dashboard

    if request.args.get("hub.verify_token") == my_token:
        return str(request.args.get("hub.challenge"))

    return "invalid", 403


@app.route("/maik", methods=["GET", "POST"])
def maik_response():
    if request.method == "GET":
        print(request.json)
        return str(jsonify(request.json))
    if request.method == "POST":
        data = dict(request.json)
        print(data["messageText"]["text"])
        send_msg(url=url, token=token, payload=payload)
        return "ok"
    return "ok"


if __name__ == "__main__":
    app.run()
