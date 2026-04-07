class Singleton:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

class Regular:
    def __init__(self):
        self.value = 42


sing = Singleton()
db = sing.get_instance(Database)
db = Database()
db2 = Database()