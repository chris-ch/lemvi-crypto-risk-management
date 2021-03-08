from google.cloud.datastore.key import Key


class Entity(object):
    def __init__(self, key):
        pass

    def update(self, content):
        pass


class Client(object):
    def __init__(self, name):
        pass

    def key(self, *args):
        return Key()

    def put(self, entity):
        pass
