# ==============================================================================
# TEST 5: THE HOARDER (Should FAIL Rule 3)
# ==============================================================================
# It correctly creates a list and appends to it, but it never loops over 
# it to notify them. It just hoards objects in memory.
class HoarderSubject:
    def __init__(self):
        self.collection = list()

    def store(self, item):
        self.collection.append(item)
        
    def do_work(self):
        print("I am working, but I will never tell my collection about it.")
        # ❌ Fails Rule 3: No loop broadcasting a method call.

