from googly import CalendarAPI
from googly.util import make_date
from creds import get_credentials


def test_basic_access():
    api = CalendarAPI(**get_credentials())

    events = list(api.get_events())

    # Should be at least one event
    assert events

    eclipse = [e for e in events if e['summary'] == 'Solar Eclipse'][0]

    assert eclipse['kind'] == 'calendar#event'
    assert eclipse['etag'] == '3425433414708000'
    assert eclipse['id'] == '0org5a0hnnubc1nbi8po3ah0hm'
    assert eclipse['status'] == 'confirmed'
    assert eclipse['htmlLink'] == ('https://www.google.com/calendar/event?'
                                   'eid=MG9yZzVhMGhubnViYzFuYmk4cG8zYWgwaG0gdGhlZ29vZ2x5YXBpQG0')
    assert eclipse['created'] == make_date(2024, 4, 10, 2, 38, 27)
    assert eclipse['updated'] == make_date(2024, 4, 10, 2, 38, 27, 354000)
    assert eclipse['description'] == ('<a href="https://www.timeanddate.com/eclipse/in/usa/orlando?'
                                      'iso=20450812">https://www.timeanddate.com/eclipse/in/usa/'
                                      'orlando?iso=20450812</a>')
    assert eclipse['location'] == (28.374382, -81.549416)
    assert eclipse['iCalUID'] == '0org5a0hnnubc1nbi8po3ah0hm@google.com'
    assert eclipse['eventType'] == 'default'

    assert eclipse['creator']['email'] == 'thegooglyapi@gmail.com'
    assert eclipse['organizer']['email'] == 'thegooglyapi@gmail.com'
    assert eclipse['start']['dateTime'] == make_date(2045, 8, 12, 12, 9, tzinfo=-4)
    assert eclipse['end']['dateTime'] == make_date(2045, 8, 12, 14, 51, tzinfo=-4)
