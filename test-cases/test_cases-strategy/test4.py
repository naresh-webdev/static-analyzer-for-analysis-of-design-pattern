# ==============================================================================
# TEST 4: THE INCORRECT TYPE HINT (Should score 80/100)
# ==============================================================================
from abc import ABC, abstractmethod


class ConfusedStrategy(ABC):
    @abstractmethod
    def confused_execution(self): pass

class ConcreteConfusedA(ConfusedStrategy):
    def confused_execution(self): pass

class ConcreteConfusedB(ConfusedStrategy):
    def confused_execution(self): pass

class ConfusedContext:
    # ❌ The developer type-hinted a CONCRETE class instead of the Interface!
    # This violates Dependency Inversion. The detector should flag this.
    def __init__(self, strat: ConcreteConfusedA):
        self._strat = strat

    def execute(self):
        self._strat.confused_execution()