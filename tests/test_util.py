from googly.util import destring, make_date


def test_destringing():
    assert destring(True)
    assert destring('1') == 1
    assert destring('5.5') == 5.5
    assert destring('destring') == 'destring'
    assert destring('2045-08-12T12:09:00-04:00') == make_date(2045, 8, 12, 12, 9, tzinfo=-4)
    assert destring('2024-04-10T02:38:27.000Z') == make_date(2024, 4, 10, 2, 38, 27)
    assert destring('2024-04-09T17:29:05.648Z') == make_date(2024, 4, 9, 17, 29, 5, 648000)

    d = {
        'a': 1,
        'b': {
            'c': 5.5,
            'd': ['foo', 'bar', 1e5]
        }
    }
    ds = {
        'a': '1',
        'b': {
            'c': '5.5',
            'd': ['foo', 'bar', '1e5']
        }
    }

    assert destring(ds) == d
