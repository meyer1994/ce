
class Scopes(object):
    def __init__(self):
        super(Scopes, self).__init__()
        self.scopes = []

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

    def add(self, decl):
        self.current[decl.name] = decl


functions = {}
variables = Scopes()
