from ast import literal_eval
from datetime import datetime, timezone, timedelta
import re

DATE_PATTERN = re.compile(r'^\d{4}\-\d{2}\-\d{2}.*')


def destring(o):
    if isinstance(o, str):
        try:
            m = DATE_PATTERN.match(o)
            if m:
                # Edge case when Python version < 3.11
                # https://stackoverflow.com/questions/127803/how-do-i-parse-an-iso-8601-formatted-date-and-time#comment94022430_49784038
                if o.endswith('Z'):
                    o = o[:-1] + '+00:00'
                return datetime.fromisoformat(o)
            else:
                return literal_eval(o)
        except (ValueError, SyntaxError):
            pass

        return o
    elif isinstance(o, list):
        return [destring(e) for e in o]
    elif isinstance(o, dict):
        return {k: destring(v) for k, v in o.items()}
    else:
        return o


def make_date(*args, tzinfo=None, **kwargs):
    if tzinfo is None:
        tzinfo = timezone.utc
    elif isinstance(tzinfo, int):
        tzinfo = timezone(timedelta(hours=tzinfo))
    return datetime(*args, **kwargs, tzinfo=tzinfo)
