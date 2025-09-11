from sortedcontainers import SortedDict


class MultiMap:
    # A class that represents a dictionary with duplicate keys with support for
    # order based on keys
    def __init__(self, sorted: bool = False, reverse: bool = False):
        self._store = SortedDict() if sorted else {}
        self._sorted = sorted
        self._reverse = reverse

    def __setitem__(self, key, value):
        if key in self._store:
            self._store[key].append(value)
        else:
            self._store[key] = [value]

    def __getitem__(self, key):
        if key in self._store:
            return self._store[key]
        else:
            raise KeyError(f"{key} not found")

    def __delitem__(self, key):
        if key in self._store:
            del self._store[key]
        else:
            raise KeyError(f"{key} not found")

    def __len__(self):
        # Return the number of key-value pairs in the hashmap
        return len(self._store)

    def __str__(self):
        # Return a string representation of the dictionary
        return "{" + ", ".join(f"{k}: {v}" for k, v in self.items()) + "}"

    def keys(self):
        if self._sorted and self._reverse:
            return list(reversed(self._store.keys()))
        return list(self._store.keys())

    def values(self):
        if self._sorted and self._reverse:
            return list(reversed(self._store.values()))
        return list(self._store.values())

    def items(self):
        if self._sorted and self._reverse:
            return list(reversed(self._store.items()))
        return list(self._store.items())
