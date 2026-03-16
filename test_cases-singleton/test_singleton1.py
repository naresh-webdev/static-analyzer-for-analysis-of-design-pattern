class Logger:
    _instance = None
    _logs = []
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()  
        return cls._logs  # ← returns _logs not _instance!
    
    @classmethod
    def log(cls, message):
        cls._logs.append(message)