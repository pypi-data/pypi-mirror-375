from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class DBInterface(ABC):
    """Abstract base interface for all database backends."""

    def __init__(self):
        self.conn = None

    @abstractmethod
    def connect(self, *args, **kwargs):
        """Establish database connection."""
        pass

    @abstractmethod
    def get_columns(self, table_name: str) -> List[str]:
        """Get column names for a table."""
        pass
    
    @abstractmethod
    def get_table_names(self) -> List[str]:
        """Get all table names in the database."""
        pass
    
    @abstractmethod
    def table_exists(self, table_name: str) -> bool:
        """Check if table exists in database."""
        pass

    @abstractmethod
    def create_table(self, table_name: str, schema: Dict[str, str], **kwargs) -> bool:
        """Create table with given schema."""
        pass

    @abstractmethod
    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None, fetch: str = None):
        """Execute query with optional parameters and fetch mode."""
        pass

    def commit(self):
        """Commit transaction."""
        if self.conn:
            self.conn.commit()

    def rollback(self):
        """Rollback transaction."""
        if self.conn:
            self.conn.rollback()

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.rollback()
        else:
            self.commit()
        self.close()