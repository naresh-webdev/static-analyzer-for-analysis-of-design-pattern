# ==============================================================================
# TEST 3: THE LONER / MISSING FAMILY (Should score 30/100)
# ==============================================================================
from abc import ABC, abstractmethod


class LonerStrategy(ABC):
    @abstractmethod
    def loner_execution(self): pass

# Only ONE concrete implementation exists in the ecosystem!
class ConcreteLoner(LonerStrategy):
    def loner_execution(self): pass

class LonerContext:
    # ❌ Fails interchangeability check (only 1 concrete class exists)
    def __init__(self, strat: LonerStrategy):
        self._strat = strat

    def execute(self):
        self._strat.loner_execution()