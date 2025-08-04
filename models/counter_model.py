from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Counter:
    """Data model for counter"""
    value: int
    last_updated: datetime
    description: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert counter to dictionary"""
        return {
            "value": self.value,
            "last_updated": self.last_updated.isoformat(),
            "description": self.description
        }
    
    @classmethod
    def create(cls, value: int = 0, description: Optional[str] = None) -> 'Counter':
        """Create a new counter instance"""
        return cls(
            value=value,
            last_updated=datetime.now(),
            description=description
        ) 