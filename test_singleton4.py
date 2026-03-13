class Parser:
    _cache = None
    
    @classmethod
    def parse(cls, data):
        if cls._cache is None:
            cls._cache = {}
        return cls._cache  # returns dict not self instance