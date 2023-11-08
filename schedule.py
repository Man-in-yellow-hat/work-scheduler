from __future__ import print_function

from datetime import datetime, timedelta
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import argparse

# Define the command-line argument parser
parser = argparse.ArgumentParser(description='Add events to Google Calendar from a text input file.')
parser.add_argument('input_file', type=str, help='the name of the input file')

# Parse the command-line arguments
args = parser.parse_args()

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']


def get_creds():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds


def parse_input(text_input):
    shifts = []
    current_year = datetime.now().year
    for line in text_input.split('\n'):
        if line.strip() == '':
            continue
        date, times = line.split(' ')
        start_time, end_time = times.split('–')
        start_datetime = f'{date} {start_time}m {current_year}'
        end_datetime = f'{date} {end_time}m {current_year}' 
        start_datetime = datetime.strptime(start_datetime, '%m/%d %I:%M%p %Y')
        end_datetime = datetime.strptime(end_datetime, '%m/%d %I:%M%p %Y')
        shifts.append([start_datetime.isoformat(), end_datetime.isoformat()])
    return shifts


def create_event(service, summary, start, end, calendar_id):
    event = {
        'summary': summary,
        'start': {
            'dateTime': start,
            'timeZone': 'America/New_York',
        },
        'end': {
            'dateTime': end,
            'timeZone': 'America/New_York',
        },
    }

    event = service.events().insert(calendarId=calendar_id, body=event).execute()
    print('Event created: %s' % (event.get('htmlLink')))


def main():
    creds = get_creds()

    with open(args.input_file, 'r') as f:
        text_input = f.read().strip()

    shifts = parse_input(text_input)

    try:
        service = build('calendar', 'v3', credentials=creds)
        calendar_id = "c_3s34it49k6mbjjovfo8pg0e2tg@group.calendar.google.com" # Nathan Work calendar

        for shift in shifts:
            summary = 'RHC Shift'
            start = shift[0]
            end = shift[1]
            create_event(service, summary, start, end, calendar_id)

        print("All shifts should be correctly input. Check calendar to confirm.")
   
    except HttpError as error:
        print('An error occurred: %s' % error)


if __name__ == '__main__':
    main()