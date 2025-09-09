"""
Database interfaces for various database backends.
"""

from .base_interface import DBInterface
from .sqlite_interface import SQLiteInterface
from .sqlalchemy_interface import SQLAlchemyInterface

# Optional imports with error handling for database-specific interfaces
try:
    from .mysql_interface import MySQLInterface
except ImportError:
    MySQLInterface = None

try:
    from .postgresql_interface import PostgreSQLInterface
except ImportError:
    PostgreSQLInterface = None

try:
    from .oracle_interface import OracleInterface
except ImportError:
    OracleInterface = None

try:
    from .sqlserver_interface import SQLServerInterface
except ImportError:
    SQLServerInterface = None

try:
    from .snowflake_interface import SnowflakeInterface
except ImportError:
    SnowflakeInterface = None

try:
    from .databricks_interface import DatabricksInterface
except ImportError:
    DatabricksInterface = None

try:
    from .redshift_interface import RedshiftInterface
except ImportError:
    RedshiftInterface = None

try:
    from .db2_interface import DB2Interface
except ImportError:
    DB2Interface = None

try:
    from .teradata_interface import TeradataInterface
except ImportError:
    TeradataInterface = None

__all__ = [
    # Core interfaces (always available)
    'DBInterface',
    'SQLiteInterface', 
    'SQLAlchemyInterface',
    
    # Optional database-specific interfaces
    'MySQLInterface',
    'PostgreSQLInterface',
    'OracleInterface',
    'SQLServerInterface',
    'SnowflakeInterface',
    'DatabricksInterface',
    'RedshiftInterface',
    'DB2Interface',
    'TeradataInterface'
]

def get_available_interfaces():
    """
    Get a list of available database interfaces based on installed dependencies.
    
    Returns:
        Dict mapping interface names to their classes (None if not available)
    """
    return {
        'SQLiteInterface': SQLiteInterface,
        'SQLAlchemyInterface': SQLAlchemyInterface,
        'MySQLInterface': MySQLInterface,
        'PostgreSQLInterface': PostgreSQLInterface,
        'OracleInterface': OracleInterface,
        'SQLServerInterface': SQLServerInterface,
        'SnowflakeInterface': SnowflakeInterface,
        'DatabricksInterface': DatabricksInterface,
        'RedshiftInterface': RedshiftInterface,
        'DB2Interface': DB2Interface,
        'TeradataInterface': TeradataInterface,
    }

def get_missing_dependencies():
    """
    Get a list of missing dependencies for database interfaces.
    
    Returns:
        Dict mapping interface names to required packages for missing interfaces
    """
    missing = {}
    interfaces_requirements = {
        'MySQLInterface': ['mysql-connector-python'],
        'PostgreSQLInterface': ['psycopg2-binary'],
        'OracleInterface': ['oracledb'],
        'SQLServerInterface': ['pyodbc'],
        'SnowflakeInterface': ['snowflake-connector-python'],
        'DatabricksInterface': ['databricks-sql-connector'],
        'RedshiftInterface': ['redshift-connector', 'psycopg2-binary'],
        'DB2Interface': ['ibm-db'],
        'TeradataInterface': ['teradatasql'],
    }
    
    available = get_available_interfaces()
    for interface_name, requirements in interfaces_requirements.items():
        if available[interface_name] is None:
            missing[interface_name] = requirements
            
    return missing