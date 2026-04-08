# ==============================================================================
# TEST 2: FUNCTIONAL BUT OVER-ENGINEERED (Score: 80/100)
# ==============================================================================
from abc import ABC, abstractmethod


class SingleWorkflow(ABC):
    def run_process(self): # <- The Template Method
        self.step_one()
        self.step_two()    # Calls abstract step
        
    def step_one(self): pass
    
    @abstractmethod
    def step_two(self): pass

# Only ONE subclass exists. The detector will suggest this might be over-engineered.
class OnlyImplementation(SingleWorkflow):
    def step_two(self): pass