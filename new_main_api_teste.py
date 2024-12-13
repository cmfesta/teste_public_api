from main_ai_v2 import AssistantAI

from langchain_core.tools import StructuredTool

from flask import Flask, request
from database import messageDB
from langchain_groq import ChatGroq
from calendar_class import GoogleCalendarAPIClient
import requests
import json
from agent_tools import *

# creating a Flask app
app = Flask(__name__)


# instructions = open("scripts/instrucao_dif.txt", "r", encoding="utf-8").read()
instructions = open(
    "scripts/malu_prompt.txt", "r", encoding="utf-8"
).read()
calendar_obj = GoogleCalendarAPIClient()

llm = ChatGroq(
    model="llama-3.1-70b-versatile",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=4,
)


def create_meet_event(
    summary: str,
    start_datetime: str,
    end_datetime: str,
    attendees: str = "",
) -> str:
    """Schedule a meeting"""
    response, flag = calendar_obj.create_meet_event(
        summary, start_datetime, end_datetime, attendees
    )

    return response


def reschedule_meet_event(
    summary: str,
    start_datetime: str,
    end_datetime: str,
    attendees: str = "",
) -> str:
    """Reschedule a meeting"""
    response, flag = calendar_obj.reschedule_v2(
        summary, start_datetime, end_datetime, attendees
    )

    return response


def delete_meet_event(
    input: str,
) -> str:
    """Delete a meeting
    Return:
        String with the answer"""
    response, flag = calendar_obj.delete_event(input)

    return response



create_meet_event_tool = StructuredTool.from_function(
    name="meet_create_event",
    func=create_meet_event,
    description="Create event in calendar",
    args_schema=SearchInput,
    handle_tool_error=True,  # add this
)

reschedule_meet_event_tool = StructuredTool.from_function(
    name="meet_reschedule_event",
    func=reschedule_meet_event,
    description="Reschedule event in calendar",
    args_schema=SearchInput,
    handle_tool_error=True,  # add this
)

delete_meet_event_tool = StructuredTool.from_function(
    name="meet_delete_event",
    func=delete_meet_event,
    description="Delete event from calendar",
    args_schema=ValidInput,
    handle_tool_error=True,  # add this
)

pythonInterpreter_tool = StructuredTool.from_function(
    name="python_code_executor",
    func=pythonInterpreter,
    description="Executar código Python",
    args_schema=ValidInput,
    handle_tool_error=True,  # add this
)

tools = [create_meet_event_tool, reschedule_meet_event_tool, delete_meet_event_tool]

message_db = messageDB("sqlite:///sqlite.db")
ai_agent = AssistantAI(
    instructions=instructions,
    llm=llm,
    db_path="sqlite:///sqlite.db",
    tools=tools,
)

with open('wpp_conn_key.json', 'r') as file:
    wpp_creds = json.load(file)


def send_msg(url, token, number, msg_text):

    payload = json.dumps(
        {
            "phoneNumber": number,
            "text": msg_text,
        }
    )

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


@app.route("/", methods=["POST"])
def home():
    if request.method == "POST":
        response = request.json
        ai_message = ai_agent.call_chat(response["message"], response["user_id"])
        return ai_message["output"]


@app.route("/maik", methods=["GET", "POST"])
def maik_response():
    if request.method == "POST":
        print(request.json)
        data = dict(request.json)
        client_msg = data["messageText"]["text"]
        number = data["recipient"]["id"]
        ai_message = ai_agent.call_chat(client_msg, number)
        send_msg(
            url=wpp_creds["url"], token=wpp_creds["token"], number=number, msg_text=str(ai_message["output"])
        )
        return ai_message["output"]
    return "ok"


if __name__ == "__main__":
    app.run(debug=True)
