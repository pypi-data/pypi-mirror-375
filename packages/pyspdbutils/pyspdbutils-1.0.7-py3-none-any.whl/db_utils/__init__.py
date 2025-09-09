"""
Production-grade database utilities package for Python.

This package provides a unified interface for working with multiple database types
including SQLite, PostgreSQL, MySQL, SQL Server, Oracle, Snowflake, and more.

Key Features:
- Universal database interface
- Built-in hash collision detection
- Automatic schema validation
- Query building with parameter binding
- Production-ready error handling
- Support for 12+ database types

Example Usage:
    from db_utils import DBManager, DBConfig
    from db_utils.interfaces import SQLiteInterface
    
    # Initialize database interface
    interface = SQLiteInterface("example.db")
    
    # Create manager with hash collision detection
    manager = DBManager(interface, hash_columns=["id", "email"])
    
    # Create table
    schema = {
        "id": "INTEGER PRIMARY KEY",
        "name": "VARCHAR(100)",
        "email": "VARCHAR(255) UNIQUE"
    }
    manager.create_table("users", schema)
    
    # Insert data with automatic duplicate detection
    user_data = {"id": 1, "name": "John Doe", "email": "john@example.com"}
    result = manager.insert("users", user_data)
"""

from .db_manager import DBManager
from .db_config import DBConfig
from .build_query import QueryBuilder
from .utils import generate_hash, check_duplicate_hash, get_file_hash
from . import interfaces
from . import exception

# Version information
__version__ = "1.0.0"
__author__ = "Debi Prasad Rath"
__email__ = "debi.rath817@gmail.com"
__license__ = "MIT"

# Public API
__all__ = [
    # Core classes
    "DBManager",
    "DBConfig", 
    "QueryBuilder",
    
    # Utility functions
    "generate_hash",
    "check_duplicate_hash",
    "get_file_hash",
    
    # Modules
    "interfaces",
    "exception",
    
    # Version info
    "__version__",
]

# Convenience imports for commonly used interfaces
from .interfaces import SQLiteInterface, SQLAlchemyInterface

# Add to __all__
__all__.extend(["SQLiteInterface", "SQLAlchemyInterface"])

# Optional interface imports with graceful error handling
interface_imports = [
    ('MySQLInterface', 'MySQLInterface'),
    ('PostgreSQLInterface', 'PostgreSQLInterface'),
    ('OracleInterface', 'OracleInterface'),
    ('SQLServerInterface', 'SQLServerInterface'),
    ('SnowflakeInterface', 'SnowflakeInterface'),
    ('DatabricksInterface', 'DatabricksInterface'),
    ('RedshiftInterface', 'RedshiftInterface'),
    ('DB2Interface', 'DB2Interface'),
    ('TeradataInterface', 'TeradataInterface'),
]

for class_name, import_name in interface_imports:
    try:
        interface_class = getattr(__import__('db_utils.interfaces', fromlist=[class_name]), class_name)
        if interface_class is not None:
            globals()[class_name] = interface_class
            __all__.append(class_name)
    except (ImportError, AttributeError):
        pass

# Utility functions for checking available interfaces
def get_available_interfaces():
    """Get a dictionary of available database interfaces."""
    from .interfaces import get_available_interfaces as _get_available_interfaces
    return _get_available_interfaces()

def get_missing_dependencies():
    """Get a dictionary of missing dependencies for database interfaces."""
    from .interfaces import get_missing_dependencies as _get_missing_dependencies
    return _get_missing_dependencies()

# Add utility functions to __all__
__all__.extend(['get_available_interfaces', 'get_missing_dependencies'])