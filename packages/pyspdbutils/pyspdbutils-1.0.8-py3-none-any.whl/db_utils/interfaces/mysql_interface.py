try:
    import mysql.connector as mysql_connector
except ImportError:
    mysql_connector = None

from typing import List, Dict, Any, Optional
from .base_interface import DBInterface

class MySQLInterface(DBInterface):
    def __init__(self, host: str, port: int, user: str, password: str, database: str):
        super().__init__()
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.connect()

    def connect(self):
        """Establish MySQL database connection."""
        self.conn = mysql_connector.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database,
            autocommit=False
        )

    def get_columns(self, table_name: str) -> List[str]:
        """Get column names for a table."""
        query = """
        SELECT COLUMN_NAME 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
        ORDER BY ORDINAL_POSITION
        """
        cursor = self.conn.cursor()
        cursor.execute(query, (self.database, table_name))
        return [row[0] for row in cursor.fetchall()]

    def get_table_names(self) -> List[str]:
        """Get all table names in the database."""
        query = """
        SELECT TABLE_NAME 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_SCHEMA = %s AND TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_NAME
        """
        cursor = self.conn.cursor()
        cursor.execute(query, (self.database,))
        return [row[0] for row in cursor.fetchall()]

    def table_exists(self, table_name: str) -> bool:
        """Check if table exists in database."""
        query = """
        SELECT TABLE_NAME 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
        """
        cursor = self.conn.cursor()
        cursor.execute(query, (self.database, table_name))
        return cursor.fetchone() is not None

    def create_table(self, table_name: str, schema: Dict[str, str], **kwargs) -> bool:
        """Create table with given schema."""
        try:
            columns = []
            for col_name, col_type in schema.items():
                columns.append(f"`{col_name}` {col_type}")
            
            columns_str = ", ".join(columns)
            query = f"CREATE TABLE IF NOT EXISTS `{table_name}` ({columns_str})"
            
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
            cursor = self.conn.cursor(dictionary=True)
            
            if params:
                # Convert named parameters to format expected by MySQL connector
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if fetch == "one":
                return cursor.fetchone()
            elif fetch == "all":
                return cursor.fetchall()
            else:
                return cursor.rowcount if cursor.rowcount > 0 else True
                
        except Exception as e:
            raise RuntimeError(f"Query execution failed: {e}") from e
