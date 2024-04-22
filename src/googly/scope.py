from enum import IntFlag

BASE_URL = 'https://www.googleapis.com/auth/'


class Scope(IntFlag):
    @classmethod
    def all(cls):
        a = []
        for f in cls:
            a.append(repr(f))
        return a

    def __iter__(self):
        for f in self.__class__:
            if f in self:
                yield repr(f)

    def __repr__(self):
        suffix = self.name.lower().replace('_', '.')
        return BASE_URL + suffix
