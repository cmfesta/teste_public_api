from main_ai import AssistantAI
from pydantic.v1 import BaseModel, Field, validator
from langchain_core.tools import StructuredTool
from langchain_core.tools import ToolException
from flask import Flask, request
from cria_banco import messageDB
from langchain_groq import ChatGroq
from langchain_experimental.utilities import PythonREPL
from calendar_class import GoogleCalendarAPIClient
import re
import requests
import json

# creating a Flask app
app = Flask(__name__)


# instructions = open("scripts/instrucao_dif.txt", "r", encoding="utf-8").read()
instructions = open(
    "scripts/instrucao_direta_com_ferramentas.txt", "r", encoding="utf-8"
).read()
calendar_obj = GoogleCalendarAPIClient()

llm = ChatGroq(
    model="llama-3.1-70b-versatile",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=4,
)


class SearchInput(BaseModel):
    summary: str = Field(description="Description of the meeting")
    start_datetime: str = Field(
        description="The time the meeting will start, the data should be in yyyy-mm-dd HH:mm:ss"
    )
    end_datetime: str = Field(
        description="The time the meeting will end, the data should be yyyy-mm-dd HH:mm:ss"
    )
    attendees: str = Field(description="attendees of the meeting")

    @validator("summary")
    def validate_summary(cls, v):
        if not type(v) == str:
            raise ToolException("Tipo errado")
        return v

    @validator("start_datetime")
    def validate_start_datetime(cls, v):
        regex_exp = "^(\d{4})\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01]) ([0-1][0-9]|[2][0-3]):([0-5][0-9]):([0-5][0-9])$"
        if not re.match(regex_exp, v):
            raise ToolException("Incorrect data format, should be yyyy-mm-dd HH:mm:ss")
        return v

    @validator("end_datetime")
    def validate_end_datetime(cls, v):
        regex_exp = "^(\d{4})\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01]) ([0-1][0-9]|[2][0-3]):([0-5][0-9]):([0-5][0-9])$"
        if not re.match(regex_exp, v):
            raise ToolException("Incorrect data format, should be yyyy-mm-dd HH:mm:ss")
        return v

    @validator("attendees")
    def validate_attendees(cls, v):
        if not re.match(r"\"?([-a-zA-Z0-9.`?{}]+@\w+\.\w+)\"?", v):
            raise ToolException("Não é um email valido")
        return v


class ValidInput(BaseModel):
    input: str = Field(description="Python code ready to be executed")

    @validator("input")
    def validate_input(cls, v):
        if not type(v) == str:
            raise ToolException("Tipo errado")
        return v


def pythonInterpreter(input: str) -> str:
    """Function that recieves a python code and prints the answer with print() function

    Args:
    input: Python code ready to be executed. It MUST print the final result of the code using print() function.

    Return:
    String with the answer
    """
    input = input.replace("```python", "").replace("```", "").strip()
    return PythonREPL().run(input)


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


def pythonInterpreter(input: str) -> str:
    """Function that recieves a python code and prints the answer with print() function

    Args:
    input: Python code ready to be executed. It MUST print the final result of the code using print() function.

    Return:
      String with the answer
    """
    input = input.replace("```python", "").replace("```", "").strip()
    return PythonREPL().run(input)


create_meet_event_tool = StructuredTool.from_function(
    func=create_meet_event,
    args_schema=SearchInput,
    handle_tool_error=True,  # add this
)

reschedule_meet_event_tool = StructuredTool.from_function(
    func=reschedule_meet_event,
    args_schema=SearchInput,
    handle_tool_error=True,  # add this
)

delete_meet_event_tool = StructuredTool.from_function(
    func=delete_meet_event,
    args_schema=ValidInput,
    handle_tool_error=True,  # add this
)

pythonInterpreter_tool = StructuredTool.from_function(
    func=pythonInterpreter,
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

token = "i8tzMul6vNgKfnYfQJImULbFm3JILJah1"
conn_key = "w-api_FFCR1GDPPZ"
host = "host01.serverapi.dev"
url = f"https://{host}/message/send-text?connectionKey={conn_key}"


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
        data = dict(request.json)
        client_msg = data["messageText"]["text"]
        number = data["recipient"]["id"]
        ai_message = ai_agent.call_chat(client_msg, number)
        send_msg(url=url, token=token, number=number, msg_text=ai_message)
        return "ok"
    return "ok"


if __name__ == "__main__":
    app.run(debug=True)
