import googly


class SingleScope(googly.Scope):
    SINGULAR = 1


class FullerScope(googly.Scope):
    MEMBER_A = 1
    MEMBER_B = 2
    MEMBER_C_BONUS = 4


def test_length():
    assert len(SingleScope) == 1
    assert len(SingleScope.all()) == 1
    assert len(list(SingleScope.SINGULAR)) == 1

    assert len(FullerScope) == 3
    assert len(FullerScope.all()) == 3
    assert len(list(FullerScope.MEMBER_A)) == 1
    assert len(list(FullerScope.MEMBER_A | FullerScope.MEMBER_B)) == 2


def test_string_values():
    values = SingleScope.all()
    assert all(isinstance(a, str) for a in values)
    assert values == ['https://www.googleapis.com/auth/singular']

    values = list(SingleScope.SINGULAR)
    assert all(isinstance(a, str) for a in values)
    assert values == ['https://www.googleapis.com/auth/singular']

    values = FullerScope.all()
    assert all(isinstance(a, str) for a in values)
    assert values == ['https://www.googleapis.com/auth/member.a',
                      'https://www.googleapis.com/auth/member.b',
                      'https://www.googleapis.com/auth/member.c.bonus']

    values = list(FullerScope.MEMBER_A)
    assert all(isinstance(a, str) for a in values)
    assert values == ['https://www.googleapis.com/auth/member.a']

    values = list(FullerScope.MEMBER_A | FullerScope.MEMBER_C_BONUS)
    assert all(isinstance(a, str) for a in values)
    assert values == ['https://www.googleapis.com/auth/member.a',
                      'https://www.googleapis.com/auth/member.c.bonus']
