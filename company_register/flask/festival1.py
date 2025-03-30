import requests
from datetime import datetime
import icalendar

def get_nearest_festival():
    today = datetime.today().date()
    ics_url = "https://calendar.google.com/calendar/ical/en.indian%23holiday%40group.v.calendar.google.com/public/basic.ics"

    try:
        response = requests.get(ics_url)
        response.raise_for_status()
        calendar = icalendar.Calendar.from_ical(response.text)

        events = []
        for event in calendar.walk('vevent'):
            event_name = str(event.get('summary'))
            event_date = event.get('dtstart').dt
            if isinstance(event_date, datetime):  
                event_date = event_date.date()  
            if event_date >= today:
                events.append((event_date, event_name))

        if events:
            events.sort()  # Sort by date
            nearest_festival = events[0]
            return f"Today's date: {today}\nNext Festival: {nearest_festival[1]} on {nearest_festival[0]}"
        else:
            return "No upcoming festivals found."

    except requests.exceptions.RequestException as e:
        return f"Error fetching festival data: {e}"

print(get_nearest_festival())
