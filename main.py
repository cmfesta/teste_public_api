# flask_ngrok_example.py
from flask import Flask
from flask import request, jsonify
import datetime

app = Flask(__name__)


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
        return jsonify(request.json)


if __name__ == "__main__":
    app.run()
