from contextlib import contextmanager


class Scopes(object):
    def __init__(self):
        super(Scopes, self).__init__()
        self.scopes = [{}]

    def create(self):
        self.scopes.append({})

    def pop(self):
        return self.scopes.pop()

    @property
    def current(self):
        return self.scopes[-1]

    def get(self, name):
        for s in reversed(self.scopes):
            if name in s:
                return s[name]
        return None

    def __contains__(self, item):
        return item in self.current

    def __getitem__(self, key):
        return self.current[key]

    def __setitem__(self, key, value):
        self.current[key] = value

    @contextmanager
    def __call__(self):
        self.create()
        yield self
        self.pop()
