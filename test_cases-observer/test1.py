# ==============================================================================
# TEST 1: THE MODERN ENTERPRISE (Should PASS completely)
# ==============================================================================
# Uses set() instead of [], and completely custom method names.
# This proves our detector is immune to the "Hardcoding Trap".

class ModernSubject:
    def __init__(self):
        self._listeners = set()

    def subscribe(self, listener):
        self._listeners.add(listener)

    def broadcast(self):
        for lst in self._listeners:
            lst.on_event()

class EmailListener:
    def on_event(self): pass







