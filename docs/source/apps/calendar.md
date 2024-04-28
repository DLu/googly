# Google Calendar

## Listing Events

```python
from googly import CalendarAPI

api = CalendarAPI()
for event in api.get_events():
    print(event)
```

This method will produce [Events](https://developers.google.com/calendar/api/v3/reference/events)
