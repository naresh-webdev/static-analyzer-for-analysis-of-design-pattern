class Logger: 
    _instance = None


    def __init__(self): 
        if self._instance is None:
            self._instance = self
        return self._instance
    
