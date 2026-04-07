# ==============================================================================
# TEST 4: THE FAKE OUT (Should NOT be detected)
# ==============================================================================
from abc import ABC, abstractmethod


class StandardClass(ABC):
    @abstractmethod
    def abstract_thing(self): pass
    
    def normal_thing(self):
        # This is a concrete method, but it does NOT call the abstract method.
        # Therefore, this is not a Template orchestrating a workflow.
        print("I'm just a normal method.")

        