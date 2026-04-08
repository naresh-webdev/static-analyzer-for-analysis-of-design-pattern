from abc import ABC, abstractmethod

# ==============================================================================
# TEST 1: THE ENTERPRISE GOLD STANDARD (Should score 100/100)
# ==============================================================================
class PerfectStrategy(ABC):
    @abstractmethod
    def perfect_execution(self): pass

class ConcretePerfectA(PerfectStrategy):
    def perfect_execution(self): pass

class ConcretePerfectB(PerfectStrategy):
    def perfect_execution(self): pass

class PerfectContext:
    # ✅ Has ABC, ✅ Has multiple concretes, ✅ Correctly Type-Hinted
    def __init__(self, strat: PerfectStrategy):
        self._strat = strat

    def execute(self):
        self._strat.perfect_execution()