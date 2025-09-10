"""Base model class for xwolfx"""

class Base:
    """Base class for all WOLF models"""
    
    def __init__(self, client):
        """Initialize base model with client reference"""
        self.client = client