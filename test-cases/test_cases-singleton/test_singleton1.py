class Logger:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = "active" # assigns string not instance!
        return cls._instance