# ==============================================================================
# TEST 4: THE GHOST LISTENER (Should FAIL Rule 4)
# ==============================================================================
# The Subject is perfectly written, but no other class in the file 
# actually implements the 'wake_up' method. It's broadcasting to a void.
class GhostSubject:
    def __init__(self):
        self.subs = []

    def add(self, sub):
        self.subs.append(sub)

    def alert(self):
        for sub in self.subs:
            sub.wake_up() 

# ❌ Fails Rule 4: There is no class GhostObserver with def wake_up(self): pass

