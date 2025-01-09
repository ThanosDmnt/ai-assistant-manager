"""
scheduler.py
-------------

Integrates with Google Calendar to enable scheduling and retrieving events. 
Allows the assistant to handle conversational scheduling requests, 
such as creating new events or checking upcoming meetings.
"""

import datetime
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Define the scope (read/write access to calendar events)
SCOPES = ["https://www.googleapis.com/auth/calendar"]

def authenticate_google_calendar():
    """
    Authenticates the user and returns the Google Calendar API service object.
    """
    creds = None
    token_path = "token.json"
    
    # Check if token.json exists to load saved credentials
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    # If credentials are invalid or missing, perform the OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save credentials for the next session
        with open(token_path, "w") as token:
            token.write(creds.to_json())

    try:
        # Build the Google Calendar service
        service = build("calendar", "v3", credentials=creds)
        return service
    except HttpError as error:
        print(f"An error occurred during authentication: {error}")
        return None


def create_test_event(service):
    """
    Creates a test event for tomorrow at 11 PM in the user's Google Calendar.
    """
    # Calculate the date and time for tomorrow at 11 PM
    now = datetime.datetime.now()  # Local time
    tomorrow = now + datetime.timedelta(days=1)
    event_start = tomorrow.replace(hour=23, minute=0, second=0, microsecond=0).isoformat()
    event_end = tomorrow.replace(hour=23, minute=30, second=0, microsecond=0).isoformat()

    # Define the event details with the Greece timezone
    event = {
        "summary": "Test Event",
        "description": "This is a test event created via Google Calendar API.",
        "start": {
            "dateTime": event_start,
            "timeZone": "Europe/Athens",
        },
        "end": {
            "dateTime": event_end,
            "timeZone": "Europe/Athens",
        },
    }

    try:
        # Insert the event into the calendar
        created_event = service.events().insert(calendarId="primary", body=event).execute()
        print(f"Event created: {created_event.get('htmlLink')}")
    except HttpError as error:
        print(f"An error occurred while creating the event: {error}")


def add_event(event_details):
    """
    Adds an event to the Google Calendar.

    Args:
        event_details (dict): Event details including title, description, start_time, end_time, and time_zone.

    Returns:
        str: Confirmation message or error message.
    """
    try:
        service = authenticate_google_calendar()
        event = {
            "summary": event_details.get("title"),
            "description": event_details.get("description"),
            "start": {
                "dateTime": event_details.get("start_time"),
                "timeZone": event_details.get("time_zone"),
            },
            "end": {
                "dateTime": event_details.get("end_time"),
                "timeZone": event_details.get("time_zone"),
            },
        }
        created_event = service.events().insert(calendarId="primary", body=event).execute()
        return f"Event {event_details.get('title')} created: {created_event.get('htmlLink')}"
    except HttpError as error:
        return f"An error occurred while adding the event: {error}"
    except Exception as e:
        return f"Unexpected error: {e}"


def view_events(start_time, end_time, time_zone):
    """
    Retrieves events from Google Calendar within the specified time range.

    Args:
        start_time (str): Start time in ISO 8601 format with timezone.
        end_time (str): End time in ISO 8601 format with timezone.
        time_zone (str): Time zone of the events.

    Returns:
        str: A list of events or a message indicating no events found.
    """
    try:
        # Convert times to ensure proper formatting
        start_time_obj = datetime.datetime.fromisoformat(start_time)
        end_time_obj = datetime.datetime.fromisoformat(end_time)

        # Add timezone information
        start_time_iso = start_time_obj.isoformat() + "Z"
        end_time_iso = end_time_obj.isoformat() + "Z"

        service = authenticate_google_calendar()
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=start_time_iso,
                timeMax=end_time_iso,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])
        if not events:
            return "No events found in the specified time range."
        
        event_list = []
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            event_list.append(f"{start}: {event.get('summary')}")
        
        return "\n".join(event_list)
    except HttpError as error:
        return f"An error occurred while retrieving events: {error}"
    except Exception as e:
        return f"Unexpected error: {e}"




def handle_schedule_action(schedule_json):
    """
    Handles scheduling actions (add or view) based on the provided JSON.

    Args:
        schedule_json (dict): JSON containing schedule_action and event_details.

    Returns:
        str: The result of the schedule action.
    """
    action = schedule_json.get("schedule_action")
    
    if action == "add":
        event_details = schedule_json.get("event_details")
        return add_event(event_details)
    elif action == "view":
        # Extract start and end time from event_details for viewing events
        time_range = schedule_json.get("time_range")
        start_time = time_range.get("start_time")
        end_time = time_range.get("end_time")
        time_zone = time_range.get("time_zone")
        return view_events(start_time, end_time, time_zone)
    else:
        return "Unsupported schedule action. Please use 'add' or 'view'."


# Example Usage
if __name__ == "__main__":
    
    # print(datetime.datetime.utcnow().isoformat() + "Z")
    # exit()
    
    # Example JSON for adding an event
    add_example = {
        "schedule_action": "add",
        "event_details": {
            "title": "Team Meeting",
            "description": "Discuss project updates",
            "start_time": "2025-01-02T15:00:00",
            "end_time": "2025-01-02T16:00:00",
            "time_zone": "Europe/Athens"
        }
    }
    # print(handle_schedule_action(add_example))
    
    # Example JSON for viewing events
    view_example = {
        "schedule_action": "view",
        "time_range": {
            "start_time": "2025-01-02T00:00:00:00",
            "end_time": "2025-01-10T00:00:00:00",
            "time_zone": "Europe/Athens"
        }
    }
    print(handle_schedule_action(view_example))


