# flask_ngrok_example.py
from flask import Flask

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello World!"


@app.route("/maik", methods=["GET", "POST"])
def maik_assist():
    return "funcionou MAIK"


if __name__ == "__main__":
    app.run()
