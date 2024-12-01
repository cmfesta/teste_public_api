# flask_ngrok_example.py
from flask import Flask
from flask import request, jsonify
import jwt

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello World!"


@app.route("/maik", methods=["GET", "POST"])
def maik_response():
    if request.method == "POST":
        response = request.json
        print(response)
        return response

    if request.method == "GET":
        response = request.json
        return response


if __name__ == "__main__":
    app.run()
