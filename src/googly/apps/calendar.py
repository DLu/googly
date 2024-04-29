import googly


class CalendarAPI(googly.API):
    # https://developers.google.com/calendar/api/guides/overview

    class Scope(googly.Scope):
        CALENDAR_READONLY = 1

    def __init__(self, scopes=Scope.all(), **kwargs):
        googly.API.__init__(self, 'calendar', 'v3', scopes, **kwargs)

    def get_events(self, calendarId='primary', maxResults=250, **kwargs):
        yield from self.get_paged_result(
            self.service.events().list,
            'items',
            max_results=maxResults,
            max_results_param_name='maxResults',
            calendarId=calendarId,
            interpret=True,
            **kwargs
        )
