from evernoteQs import get_reminders
import argparse
import httplib2
import os
import datetime
from time import strftime
from datetime import datetime, timedelta

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools


try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API'

def get_credentials():
    """Gets valid user credentials
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'google-calendar.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()

    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:
            credentials = tools.run(flow, store)
        print 'Storing credentials to ' + credential_path
    return credentials

def get_calendar_events(service, maxResults=10, calenderId='primary'):
    """Gets calendar events
    """
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time

    eventsResult = service.events().list(
        calendarId=calenderId, timeMin=now, maxResults=10, singleEvents=True,
        orderBy='startTime').execute()
    return eventsResult.get('items', [])


def add_new_event(service, event_data, calenderId='primary'):
    """Adds a new event in the calendar
    """    
    event = service.events().insert(calendarId=calenderId, body=event_data).execute()
    return 'Added an event: {}'.format(event.get('htmlLink'))


def sync():
    reminders = get_reminders()
    for r in reminders:
        timeZone = strftime('%Z', r['time'])
        r['start'] = {'dateTime': datetime(*r['time'][:6]).isoformat(),
                      'timeZone': 'America/Los_Angeles'}
        r['end'] = {'dateTime': (datetime(*r['time'][:6])+timedelta()).isoformat(),
                    'timeZone': 'America/Los_Angeles'}
        r['summary'] = r['title']
        
        del r['time']
        print add_new_event(service, r)
    
def print_events(events):
    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print start, event['summary']

if __name__ == '__main__':
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    #events = get_calendar_events(service)
    #print_events(events)
    
    sync()
