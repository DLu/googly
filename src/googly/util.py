from ast import literal_eval
from dateutil.parser import parse
from datetime import datetime, timezone, timedelta
import re

DATE_PATTERN = re.compile(r'^\d{4}\-\d{2}\-\d{2}.*')


def destring(o):
    if isinstance(o, str):
        try:
            m = DATE_PATTERN.match(o)
            if m:
                return parse(o)
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
