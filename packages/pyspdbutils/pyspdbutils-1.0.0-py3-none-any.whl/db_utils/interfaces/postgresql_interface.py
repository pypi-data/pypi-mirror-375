try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:
    psycopg2 = None

from typing import List, Dict, Any, Optional
from .base_interface import DBInterface

class PostgreSQLInterface(DBInterface):
    def __init__(self, host: str, port: int, user: str, password: str, database: str):
        super().__init__()
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.connect()

    def connect(self):
        """Establish PostgreSQL database connection."""
        self.conn = psycopg2.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database,
            cursor_factory=RealDictCursor
        )
        self.conn.autocommit = False

    def get_columns(self, table_name: str) -> List[str]:
        """Get column names for a table."""
        query = """
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = %s 
        ORDER BY ordinal_position
        """
        cursor = self.conn.cursor()
        cursor.execute(query, (table_name,))
        return [row[0] for row in cursor.fetchall()]

    def get_table_names(self) -> List[str]:
        """Get all table names in the database."""
        query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
        ORDER BY table_name
        """
        cursor = self.conn.cursor()
        cursor.execute(query)
        return [row[0] for row in cursor.fetchall()]

    def table_exists(self, table_name: str) -> bool:
        """Check if table exists in database."""
        query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_type = 'BASE TABLE' AND table_name = %s
        """
        cursor = self.conn.cursor()
        cursor.execute(query, (table_name,))
        return cursor.fetchone() is not None

    def create_table(self, table_name: str, schema: Dict[str, str], **kwargs) -> bool:
        """Create table with given schema."""
        try:
            columns = []
            for col_name, col_type in schema.items():
                columns.append(f'"{col_name}" {col_type}')
            
            columns_str = ", ".join(columns)
            query = f'CREATE TABLE IF NOT EXISTS "{table_name}" ({columns_str})'
            
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
                result = cursor.fetchone()
                return dict(result) if result else None
            elif fetch == "all":
                results = cursor.fetchall()
                return [dict(row) for row in results]
            else:
                return cursor.rowcount if cursor.rowcount > 0 else True
                
        except Exception as e:
            raise RuntimeError(f"Query execution failed: {e}") from e
