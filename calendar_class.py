import os
from googleapiclient.discovery import build
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import pandas
import time


class GoogleCalendarAPIClient:
    def __init__(self):
        self.calendar_id = "primary"
        self.SCOPES = ["https://www.googleapis.com/auth/calendar"]

        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", self.SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", self.SCOPES
                )
                creds = flow.run_local_server(port=0)

            with open("token.json", "w") as token:
                token.write(creds.to_json())

        try:
            self.service = build("calendar", "v3", credentials=creds)
        except Exception as e:
            pass

    def list_events(self, time_min, time_max):
        """Function that recieves a python code and prints the answer with print() function

        Args:
        input: Python code ready to be executed. It MUST print the final result of the code using print() function.

        Return:
            String with the answer
        """
        events = (
            self.service.events()
            .list(
                calendarId=self.calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                orderBy="startTime",
                singleEvents=True,
            )
            .execute()
        )

        return events.get("items", [])

    def return_meet(self):
        """Function that recieves a python code and prints the answer with print() function

        Args:
        input: Python code ready to be executed. It MUST print the final result of the code using print() function.

        Return:
            String with the answer
        """
        data_list = []
        start_date = datetime.datetime.now()
        end_date = datetime.datetime.now() + datetime.timedelta(days=15)
        start_date = start_date.isoformat() + "Z"
        end_date = end_date.isoformat() + "Z"
        for i in self.list_events(time_min=start_date, time_max=end_date):
            data_list.append(
                {
                    "id": i["id"],
                    "dateTime": i["start"].get("dateTime"),
                    "displayName": i["attendees"][0].get("displayName"),
                    "email": i["attendees"][0].get("email"),
                }
            )
        return data_list

    def check_meet_by_email(self, email):
        for info in self.return_meet():
            if info["email"] == email:
                return info

    def check_datetime_is_free(
        self,
        start_datetime: str,
        end_datetime: str,
    ):
        print(start_datetime, start_datetime)
        events = (
            self.service.events()
            .list(
                calendarId=self.calendar_id,
                timeMin=start_datetime,
                timeMax=end_datetime,
                orderBy="startTime",
                singleEvents=True,
            )
            .execute()
        )
        if events.get("items", []):
            return False

        return True

    def check_not_past_day(self, date_string):
        this_date = pandas.Timestamp(date_string).date()
        now = datetime.date.today()
        if this_date >= now:
            return True
        return False

    def create_meet_event(
        self,
        summary: str,
        start_datetime: str,
        end_datetime: str,
        attendees: str = "",
        hide_participants_list: bool = True,
    ):
        """Function that register a meet call in google calendar

        Args:
        summary: It will always be a description of what will be done at the meeting.
        start_datetime: the time the meeting will start, It MUST be a timestamp string.
        end_datetime: the time the meeting will end, its It MUST be a timestamp string.
        attendees: The email addresses of the people attending the meeting.
        hide_participants_list: If the guest's name is visible.

        Return:
            A boolean indicating if the meeting was schedule
        """

        attendees = [attendees.strip()]

        if not self.check_not_past_day(start_datetime):
            return "Você não pode marcar um horario de reunião para um dia que ja passou, apenas para hoje ou outro dia futuro"

        start_datetime = pandas.Timestamp(start_datetime) + datetime.timedelta(hours=3)
        start_datetime = start_datetime.isoformat() + "Z"
        end_datetime = pandas.Timestamp(end_datetime) + datetime.timedelta(hours=3)
        end_datetime = end_datetime.isoformat() + "Z"

        print("summary", summary)
        print("start_datetime", start_datetime)
        print("end_datetime", end_datetime)
        print("attendees", attendees)

        if self.check_datetime_is_free(start_datetime, end_datetime):

            event = {
                "summary": summary,
                "start": {"dateTime": start_datetime, "timeZone": "UTC"},
                "end": {"dateTime": end_datetime, "timeZone": "UTC"},
                "conferenceData": {
                    "createRequest": {
                        "requestId": "random_string",
                        "conferenceSolutionKey": {"type": "hangoutsMeet"},
                    }
                },
            }

            if hide_participants_list:
                event["visibility"] = "private"
                event["guestsCanSeeOtherGuests"] = False

            if attendees:
                event["attendees"] = [{"email": attendee} for attendee in attendees]

            created_event = (
                self.service.events()
                .insert(
                    calendarId=self.calendar_id,
                    body=event,
                    conferenceDataVersion=1,
                    sendUpdates="all",
                )
                .execute()
            )

            # meet_link = created_event.get("hangoutLink", None)
            # event_id = created_event.get("id", None)

            return "Reunião marcada com sucesso", True

        return "Já existe uma reunião marcada nesse horario", False

    def reschedule_v2(
        self,
        summary: str,
        start_datetime: str,
        end_datetime: str,
        attendees: str = "",
    ):
        """Function that recive email,start_datetime,end_datetime about the client and reschedule the meeting, when you pass the email, the function will look for the meeting and reschedule based on start_datetime and end_datetime

        Args:
        summary: It will always be a description of what will be done at the meeting.
        start_datetime: the time the meeting will start, It MUST be a timestamp string.
        end_datetime: the time the meeting will end, its It MUST be a timestamp string.
        email: the clients email

        Return:
            A boolean indicating if the meeting was reschedule
        """

        start_time = pandas.Timestamp(start_datetime) + datetime.timedelta(hours=3)
        start_time = start_time.isoformat() + "Z"
        end_time = pandas.Timestamp(end_datetime) + datetime.timedelta(hours=3)
        end_time = end_time.isoformat() + "Z"
        if self.check_datetime_is_free(end_time, end_time):
            self.delete_event(email=attendees)
            self.create_meet_event(summary, start_datetime, end_datetime, attendees)
            return "Reunião remarcada com sucesso", True
        return "Não foi possivel remarcar a reunião", False

    def delete_event(self, email: str):
        """Function that recieves an email and delete an event based on that

        Args:
        email: Email of the client that will have the meeting cancelled.

        Return:
            String with the answer
        """

        email = email.strip()
        start_date = datetime.datetime.now()
        end_date = datetime.datetime.now() + datetime.timedelta(days=20)
        start_date = start_date.isoformat() + "Z"
        end_date = end_date.isoformat() + "Z"
        for i in self.list_events(time_min=start_date, time_max=end_date):
            if i["attendees"][0].get("email") == email:
                cancelled_event = (
                    self.service.events()
                    .delete(calendarId=self.calendar_id, eventId=i["id"])
                    .execute()
                )
            return "Reunião deletada com sucesso", True
        return "Problema ao deletar reunião", False
