try:
    import oracledb
except ImportError:
    oracledb = None

from typing import List, Dict, Any, Optional
from .base_interface import DBInterface

class OracleInterface(DBInterface):
    def __init__(self, host: str, port: int, user: str, password: str, service_name: str):
        super().__init__()
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.service_name = service_name
        self.connect()

    def connect(self):
        """Establish Oracle database connection."""
        try:
            # Create DSN for Oracle connection
            dsn = oracledb.makedsn(self.host, self.port, service_name=self.service_name)
            self.conn = oracledb.connect(
                user=self.user,
                password=self.password,
                dsn=dsn
            )
            self.conn.autocommit = False
        except Exception as e:
            raise RuntimeError(f"Failed to connect to Oracle database: {e}") from e

    def get_columns(self, table_name: str) -> List[str]:
        """Get column names for a table."""
        query = """
        SELECT column_name 
        FROM user_tab_columns 
        WHERE table_name = UPPER(:table_name)
        ORDER BY column_id
        """
        cursor = self.conn.cursor()
        cursor.execute(query, {"table_name": table_name})
        return [row[0] for row in cursor.fetchall()]

    def get_table_names(self) -> List[str]:
        """Get all table names in the database."""
        query = """
        SELECT table_name 
        FROM user_tables 
        ORDER BY table_name
        """
        cursor = self.conn.cursor()
        cursor.execute(query)
        return [row[0] for row in cursor.fetchall()]

    def table_exists(self, table_name: str) -> bool:
        """Check if table exists in database."""
        query = """
        SELECT table_name 
        FROM user_tables 
        WHERE table_name = UPPER(:table_name)
        """
        cursor = self.conn.cursor()
        cursor.execute(query, {"table_name": table_name})
        return cursor.fetchone() is not None

    def create_table(self, table_name: str, schema: Dict[str, str], **kwargs) -> bool:
        """Create table with given schema."""
        try:
            columns = []
            for col_name, col_type in schema.items():
                columns.append(f'"{col_name.upper()}" {col_type}')
            
            columns_str = ", ".join(columns)
            
            # Check if table exists first (Oracle doesn't have CREATE TABLE IF NOT EXISTS)
            if not self.table_exists(table_name):
                query = f'CREATE TABLE "{table_name.upper()}" ({columns_str})'
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
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if fetch == "one":
                row = cursor.fetchone()
                if row:
                    # Get column names
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
