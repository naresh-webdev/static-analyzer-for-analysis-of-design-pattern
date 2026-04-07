# ==============================================================================
# TEST 3: THE ABANDONED SKELETON (Score: 50/100)
# ==============================================================================
from abc import ABC, abstractmethod


class AbandonedTemplate(ABC):
    def execute(self): # <- The Template Method
        self.do_the_thing() # Calls abstract step
        
    @abstractmethod
    def do_the_thing(self): pass

# NO subclasses exist! The detector flags this as an incomplete architecture.