# ==============================================================================
# TEST 7: THE HARDCODER (Should NOT be detected at all)
# ==============================================================================
class HardcodedStrategy:
    def hardcoded_execution(self): pass

class HardcodedContext:
    def __init__(self):
        # ❌ Fails Composition. Does not inject state from the outside.
        self.internal_data = True

    def execute(self):
        # ❌ It instantiates the strategy directly. It is tightly coupled!
        strat = HardcodedStrategy()
        strat.hardcoded_execution()