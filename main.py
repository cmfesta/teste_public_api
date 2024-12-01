# flask_ngrok_example.py
from flask import Flask
from flask import request, jsonify

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello World!"


@app.route("/1", methods=["GET", "POST"])
def a1():
    if request.method == "GET":
        if "hub.challenge" in request.args:
            print(request.json)
            print(request.args.get("hub.challenge"))
            return "hub challenge"
        return "no hub challenge"


@app.route("/maik", methods=["GET", "POST"])
def maik_response():
    if request.method == "GET":

        return "teste maik"


if __name__ == "__main__":
    app.run()
