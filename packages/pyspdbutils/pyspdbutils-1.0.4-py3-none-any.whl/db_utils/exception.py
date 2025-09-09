"""
Custom exceptions for the db_utils package.
"""

class DBUtilsError(Exception):
    """Base exception class for db_utils package."""
    pass

class ConnectionError(DBUtilsError):
    """Exception raised when database connection fails."""
    pass

class ValidationError(DBUtilsError):
    """Exception raised when data validation fails."""
    pass

class DBOperationError(DBUtilsError):
    """Exception raised when database operation fails."""
    pass

class ConfigurationError(DBUtilsError):
    """Exception raised when configuration is invalid."""
    pass

class UnsupportedDatabaseError(DBUtilsError):
    """Exception raised when database type is not supported."""
    pass

class QueryBuildError(DBUtilsError):
    """Exception raised when query building fails."""
    pass

class SchemaError(DBUtilsError):
    """Exception raised when table schema is invalid."""
    pass