from google.cloud.datastore.key import Key


class Entity(object):
    def __init__(self, key):
        pass

    def update(self, content):
        pass


class Client(object):
    def __init__(self, *args, **kwargs):
        pass

    def key(self, *args, **kwargs):
        return Key()

    def put(self, entity):
        pass

    def transaction(self):
        pass

    def query(self, kind):
        pass
