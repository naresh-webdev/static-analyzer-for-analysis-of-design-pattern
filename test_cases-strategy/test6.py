# ==============================================================================
# TEST 6: THE HOARDER (Should NOT be detected at all)
# ==============================================================================
class HoardedStrategy:
    def hoarded_execution(self): pass

class HoarderContext:
    # It takes the strategy and saves it...
    def __init__(self, strat):
        self._strat = strat

    def execute(self):
        # ❌ But it NEVER calls a method on it! No delegation = No Strategy.
        print("I do all the work myself.")