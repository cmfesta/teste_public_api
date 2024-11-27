import json
from flask import Flask, render_template
import flask
from message_helper import get_text_message_input, send_message

app = Flask(__name__)


app.config.update(
    {
        "APP_ID": "898144499094484",
        "APP_SECRET": "9c6b98cee688bbb57305bbbf60757e7e",
        "TO_NUMBER": "5553991798189",
        "VERSION": "v13.0",
        "PHONE_NUMBER_ID": "518260918028868",
        "ACCESS_TOKEN": "EAAMw24ZCTU9QBOxdat1NgmrrzzoecMxGeEa3FqBcKV9a3NCX2uZBluiqTljSprXDflHn54tOxKZAbZADbLUqexWKdXQjeZAX8dqlm7QkPeKJdmJgwh7Wz8uiSM55HYHIQSwS56Kg3y40PuIMlN3i3DkkEz6rCv1MDezxMaziDAB4To198urGC94svumahPDPFyCmfzKyaG6dZBlvw0gVkcZBZA90YZC6kSrwty98ZD",
    }
)


@app.route("/")
def index():
    return render_template("index.html", name=__name__)


@app.route("/welcome", methods=["POST"])
async def welcome():
    data = get_text_message_input(
        app.config["TO_NUMBER"],
        "Testando mandar mensagens",
    )
    await send_message(data)
    return flask.redirect(flask.url_for("index"))
