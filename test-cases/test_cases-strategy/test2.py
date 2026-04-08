# ==============================================================================
# TEST 2: THE DUCK-TYPED ROGUE (Should score 50/100)
# ==============================================================================
# No ABC interface here! Just two classes that happen to share a method name.
class RogueA:
    def rogue_execution(self): pass

class RogueB:
    def rogue_execution(self): pass

class RogueContext:
    # ✅ Has multiple concretes, ❌ No ABC, ❌ No Type Hints
    def __init__(self, rogue):
        self._rogue = rogue

    def execute(self):
        self._rogue.rogue_execution()