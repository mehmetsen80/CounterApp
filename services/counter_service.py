from models.counter_model import Counter
from datetime import datetime

class CounterService:
    """Service class to handle counter business logic"""
    
    def __init__(self):
        # Initialize with a Counter model instance
        self._counter = Counter.create(value=0, description="Main counter")
    
    def get_count(self) -> int:
        """Get the current count"""
        return self._counter.value
    
    def get_counter(self) -> Counter:
        """Get the full counter object"""
        return self._counter
    
    def increment_count(self) -> int:
        """Increment the counter and return new value"""
        self._counter.value += 1
        self._counter.last_updated = datetime.now()
        return self._counter.value
    
    def reset_count(self) -> int:
        """Reset the counter to 0 and return the value"""
        self._counter.value = 0
        self._counter.last_updated = datetime.now()
        return self._counter.value
    
    def set_count(self, value: int) -> int:
        """Set the counter to a specific value"""
        self._counter.value = value
        self._counter.last_updated = datetime.now()
        return self._counter.value
    
    def get_counter_dict(self) -> dict:
        """Get counter as dictionary with metadata"""
        return self._counter.to_dict() 