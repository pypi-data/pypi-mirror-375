try:
    import pyodbc
except ImportError:
    pyodbc = None
    
from typing import List, Dict, Any, Optional
from .base_interface import DBInterface

class SQLServerInterface(DBInterface):
    def __init__(self, host: str, port: int, user: str, password: str, database: str, driver: str = "ODBC Driver 17 for SQL Server"):
        super().__init__()
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.driver = driver
        self.connect()

    def connect(self):
        """Establish SQL Server database connection."""
        try:
            connection_string = (
                f"DRIVER={{{self.driver}}};"
                f"SERVER={self.host},{self.port};"
                f"DATABASE={self.database};"
                f"UID={self.user};"
                f"PWD={self.password};"
                "Trusted_Connection=no;"
            )
            self.conn = pyodbc.connect(connection_string)
            self.conn.autocommit = False
        except Exception as e:
            raise RuntimeError(f"Failed to connect to SQL Server database: {e}") from e

    def get_columns(self, table_name: str) -> List[str]:
        """Get column names for a table."""
        query = """
        SELECT COLUMN_NAME 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_NAME = ? 
        ORDER BY ORDINAL_POSITION
        """
        cursor = self.conn.cursor()
        cursor.execute(query, (table_name,))
        return [row[0] for row in cursor.fetchall()]

    def get_table_names(self) -> List[str]:
        """Get all table names in the database."""
        query = """
        SELECT TABLE_NAME 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_NAME
        """
        cursor = self.conn.cursor()
        cursor.execute(query)
        return [row[0] for row in cursor.fetchall()]

    def table_exists(self, table_name: str) -> bool:
        """Check if table exists in database."""
        query = """
        SELECT TABLE_NAME 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_TYPE = 'BASE TABLE' AND TABLE_NAME = ?
        """
        cursor = self.conn.cursor()
        cursor.execute(query, (table_name,))
        return cursor.fetchone() is not None

    def create_table(self, table_name: str, schema: Dict[str, str], **kwargs) -> bool:
        """Create table with given schema."""
        try:
            columns = []
            for col_name, col_type in schema.items():
                columns.append(f"[{col_name}] {col_type}")
            
            columns_str = ", ".join(columns)
            
            # SQL Server doesn't have CREATE TABLE IF NOT EXISTS, so check first
            if not self.table_exists(table_name):
                query = f"CREATE TABLE [{table_name}] ({columns_str})"
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
            cursor = self.conn.cursor()
            
            if params:
                # Convert named parameters to positional for pyodbc
                # This is a simplified approach - more complex queries might need proper parsing
                param_values = []
                modified_query = query
                for key, value in params.items():
                    modified_query = modified_query.replace(f":{key}", "?")
                    param_values.append(value)
                cursor.execute(modified_query, param_values)
            else:
                cursor.execute(query)
            
            if fetch == "one":
                row = cursor.fetchone()
                if row:
                    columns = [desc[0] for desc in cursor.description]
                    return dict(zip(columns, row))
                return None
            elif fetch == "all":
                rows = cursor.fetchall()
                if rows:
                    columns = [desc[0] for desc in cursor.description]
                    return [dict(zip(columns, row)) for row in rows]
                return []
            else:
                return cursor.rowcount if cursor.rowcount > 0 else True
                
        except Exception as e:
            raise RuntimeError(f"Query execution failed: {e}") from e
