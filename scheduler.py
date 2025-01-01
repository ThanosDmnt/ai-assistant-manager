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
    # Check if token.json exists to load saved credentials
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # If credentials are invalid or missing, perform the OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save credentials for the next session
        with open("token.json", "w") as token:
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



def main():
    """
    Main function to authenticate and manage calendar events.
    """
    print("Authenticating with Google Calendar...")
    service = authenticate_google_calendar()
    if service:
        print("Authentication successful!")
        # Create a test event
        create_test_event(service)


if __name__ == "__main__":
    main()


