# ==============================================================================
# TEST 7: THE DICTIONARY REGISTRY (Should FAIL Rule 1)
# ==============================================================================
# This is a highly advanced edge case. It uses a dict {} instead of a list/set.
# Our detector strictly looks for list() or set() because dictionaries usually 
# imply a Registry or Service Locator pattern rather than a pure Observer.
class DictSubject:
    def __init__(self):
        self.registry = {} # ❌ Fails Rule 1: Not a list or set.

    def register(self, key, obs):
        self.registry[key] = obs

    def ping(self):
        for key in self.registry:
            self.registry[key].ping()

class DictObserver:
    def ping(self): pass