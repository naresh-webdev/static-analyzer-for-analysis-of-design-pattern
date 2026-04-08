from abc import ABC, abstractmethod

# ==========================================
# 1. TEMPLATE METHOD: The Pipeline Skeleton
# ==========================================
class DataPipeline(ABC):
    
    def run_pipeline(self):
        """The Skeleton Method orchestrating the workflow."""
        data = self.extract_data()
        cleaned = self.transform_data(data)
        self.load_data(cleaned)

    @abstractmethod
    def extract_data(self): pass

    @abstractmethod
    def transform_data(self, data): pass

    @abstractmethod
    def load_data(self, data): pass


# Concrete Implementations of the Template
class JSONtoPostgresPipeline(DataPipeline):
    def extract_data(self): return {"name": "test"}
    def transform_data(self, data): return data
    def load_data(self, data): pass

class CSVtoMongoPipeline(DataPipeline):
    def extract_data(self): return "name,age\ntest,20"
    def transform_data(self, data): return data
    def load_data(self, data): pass


# ==========================================
# 2. FACTORY: True Factory Method
# ==========================================
class PipelineCreator(ABC):
    @abstractmethod
    def build_pipeline(self):
        pass

class PostgresCreator(PipelineCreator):
    def build_pipeline(self):
        return JSONtoPostgresPipeline()

class MongoCreator(PipelineCreator):
    def build_pipeline(self):
        return CSVtoMongoPipeline()