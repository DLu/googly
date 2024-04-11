from googly import CalendarAPI
from secret_auth import get_secrets


def test_basic_access():
    api = CalendarAPI(**get_secrets())

    events = list(api.get_events())

    # Should be at least one event
    assert events

    eclipse = [e for e in events if e['summary'] == 'Solar Eclipse'][0]

    assert eclipse['kind'] == 'calendar#event'
    assert eclipse['etag'] == '"3425433414708000"'
    assert eclipse['id'] == '0org5a0hnnubc1nbi8po3ah0hm'
    assert eclipse['status'] == 'confirmed'
    assert eclipse['htmlLink'] == ('https://www.google.com/calendar/event?'
                                   'eid=MG9yZzVhMGhubnViYzFuYmk4cG8zYWgwaG0gdGhlZ29vZ2x5YXBpQG0')
    assert eclipse['created'] == '2024-04-10T02:38:27.000Z'
    assert eclipse['updated'] == '2024-04-10T02:38:27.354Z'
    assert eclipse['description'] == ('<a href="https://www.timeanddate.com/eclipse/in/usa/orlando?'
                                      'iso=20450812">https://www.timeanddate.com/eclipse/in/usa/'
                                      'orlando?iso=20450812</a>')
    assert eclipse['location'] == '28.374382, -81.549416'
    assert eclipse['iCalUID'] == '0org5a0hnnubc1nbi8po3ah0hm@google.com'
    assert eclipse['eventType'] == 'default'

    assert eclipse['creator']['email'] == 'thegooglyapi@gmail.com'
    assert eclipse['organizer']['email'] == 'thegooglyapi@gmail.com'
    assert eclipse['start']['dateTime'] == '2045-08-12T12:09:00-04:00'
    assert eclipse['end']['dateTime'] == '2045-08-12T14:51:00-04:00'
