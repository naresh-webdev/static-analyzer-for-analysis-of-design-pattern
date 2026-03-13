class Logger:
    _instance = None
    _logs = []
    _owner_name = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @classmethod
    def log(self, message):
        self._logs.append(message)
