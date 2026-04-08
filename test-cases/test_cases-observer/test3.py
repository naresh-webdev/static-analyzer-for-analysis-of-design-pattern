# ==============================================================================
# TEST 3: THE DELEGATION FAKE-OUT (Should FAIL Rule 3)
# ==============================================================================
# It loops over a list, but it calls a method on ITSELF, not the observer.
# This is a standard batch-processing class, NOT an Observer pattern.
class BatchProcessor:
    def __init__(self):
        self.items = []

    def add_item(self, item):
        self.items.append(item)

    def process_all(self):
        for item in self.items:
            self.process_single(item)  # ❌ Fails: self.process_single, not item.process_single

    def process_single(self, item):
        pass

