from castoranalytics.core.singleton import singleton


@singleton
class Cache:
    def __init__(self):
        self._cache_items = {}

    def get(self, name, default=None):
        if name in self._cache_items.keys():
            return self._cache_items[name]
        return default
    
    def set(self, name, value):
        self._cache_items[name] = value

    def clear(self):
        del self._cache_items