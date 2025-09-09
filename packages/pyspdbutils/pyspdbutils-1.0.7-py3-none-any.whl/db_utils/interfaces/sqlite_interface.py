try:
    import sqlite3
except ImportError:
    sqlite3 = None

from typing import List, Dict, Any, Optional
from .base_interface import DBInterface

class SQLiteInterface(DBInterface):
    def __init__(self, db_path: str):
        super().__init__()
        if sqlite3 is None:
            raise ImportError("sqlite3 is required for SQLiteInterface")
        self.db_path = db_path
        self.connect(db_path)

    def connect(self, db_path: str = None):
        """Establish SQLite database connection."""
        if db_path:
            self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # results as dict-like objects
        # Enable foreign key constraints
        self.conn.execute("PRAGMA foreign_keys = ON")

    def get_columns(self, table_name: str) -> List[str]:
        """Get column names for a table."""
        query = f"PRAGMA table_info({table_name})"
        cursor = self.conn.cursor()
        cursor.execute(query)
        return [row[1] for row in cursor.fetchall()]  # column name is at index 1

    def get_table_names(self) -> List[str]:
        """Get all table names in the database."""
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        cursor = self.conn.cursor()
        cursor.execute(query)
        return [row[0] for row in cursor.fetchall()]

    def table_exists(self, table_name: str) -> bool:
        """Check if table exists in database."""
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
        cursor = self.conn.cursor()
        cursor.execute(query, (table_name,))
        return cursor.fetchone() is not None

    def create_table(self, table_name: str, schema: Dict[str, str], **kwargs) -> bool:
        """Create table with given schema."""
        try:
            columns = []
            for col_name, col_type in schema.items():
                columns.append(f"{col_name} {col_type}")
            
            columns_str = ", ".join(columns)
            query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_str})"
            
            cursor = self.conn.cursor()
            cursor.execute(query)
            self.commit()
            return True
        except Exception as e:
            self.rollback()
            raise RuntimeError(f"Failed to create table {table_name}: {e}") from e

    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None, fetch: str = None):
        """Execute query with optional parameters and fetch mode."""
        try:
            # Reconnect if connection is None
            if self.conn is None:
                self.connect()
                
            cursor = self.conn.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if fetch == "one":
                result = cursor.fetchone()
                return dict(result) if result else None
            elif fetch == "all":
                results = cursor.fetchall()
                return [dict(row) for row in results]
            else:
                return cursor.rowcount if cursor.rowcount > 0 else True
                
        except Exception as e:
            raise RuntimeError(f"Query execution failed: {e}") from e

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Custom exit that doesn't close connection for SQLite."""
        if exc_type:
            self.rollback()
        else:
            self.commit()
        # Don't close connection for SQLite - just commit/rollback

