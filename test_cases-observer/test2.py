# ==============================================================================
# TEST 2: THE CLASSIC TEXTBOOK (Should PASS completely)
# ==============================================================================
# Proves we didn't break backward compatibility with textbook examples.
class ClassicSubject:
    def __init__(self):
        self.observers = []

    def attach(self, obs):
        self.observers.append(obs)

    def notify(self):
        for obs in self.observers:
            obs.update()

class MobileObserver:
    def update(self): pass

