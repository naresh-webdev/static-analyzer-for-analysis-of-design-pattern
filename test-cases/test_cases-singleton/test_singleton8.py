import threading

class ThreadSafeSingleton:
    _instance = None
    _lock = threading.Lock()

    @classmethod
    def get_instance(cls):
        # Rule A passes: _instance is in the condition
        if cls._instance is None:
            
            # The immediate child of the if-body is a 'With' node, not an 'Assign' node.
            with cls._lock:
                # Your current loop stops searching and never sees this assignment.
                cls._instance = cls()
                
        return cls._instance
    
    def __new__(cls):
        pass

    @classmethod
    def dummy_method(self):
        pass