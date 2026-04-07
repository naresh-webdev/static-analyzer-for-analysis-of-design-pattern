# ==============================================================================
# TEST 6: THE HARDCODER (Should FAIL Rule 1)
# ==============================================================================
# Holds only one listener as a direct variable, not a collection. 
# This is a basic Callback/Wrapper, not a 1-to-Many Observer.
class HardcodedSubject:
    def __init__(self):
        self.only_listener = None

    def set_listener(self, lst):
        self.only_listener = lst

    def fire(self):
        if self.only_listener:
            self.only_listener.trigger() # ❌ Fails: No loop over a list/set

class HardcodedListener:
    def trigger(self): pass