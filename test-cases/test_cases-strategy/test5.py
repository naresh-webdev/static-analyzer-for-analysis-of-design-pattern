# ==============================================================================
# TEST 5: THE PROXY FAKE-OUT (Should score 30/100 & warn you)
# ==============================================================================
# This looks like a Strategy, but it's just a Database wrapper.
class DatabaseConnection:
    def insert_data(self): pass

class LoggerProxy:
    def __init__(self, db):
        self._db = db

    def log(self):
        # ❌ It delegates, but 'insert_data' only belongs to one class.
        # The detector will warn that this might not be a real Strategy.
        self._db.insert_data()