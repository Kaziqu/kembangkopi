# __init__.py - Connection Manager Singleton
from .connection_manager import ConnectionManager

# Create a single instance that will be shared across all modules
manager = ConnectionManager()
