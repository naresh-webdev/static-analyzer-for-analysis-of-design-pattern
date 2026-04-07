from abc import ABC, abstractmethod

# ==============================================================================
# TEST 1: ENTERPRISE GRADE (Score: 100/100)
# ==============================================================================
class DataMiner(ABC):
    def mine_data(self):  # <- The Template Method
        self.open_file()
        self.extract_data() # Calls abstract step
        
    def open_file(self): pass
    
    @abstractmethod
    def extract_data(self): pass

# Multiple subclasses using the template
class PDFMiner(DataMiner):
    def extract_data(self): pass

class CSVMiner(DataMiner):
    def extract_data(self): pass