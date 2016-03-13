from datetime import datetime, timedelta

CACHE_RETENTION_DELAY = 30


class MessagesCache:
    def __init__(self):
        self.cache = {}

    def AddToCache(self, key):
        self.cache[key] = datetime.utcnow()

    def IsInCache(self, key):
        self.CleanCache()
        return key in self.cache

    def CleanCache(self):
        for key, value in list(self.cache.items()):
            delta = timedelta(seconds=CACHE_RETENTION_DELAY)
            if value + delta < datetime.utcnow():
                del self.cache[key]
