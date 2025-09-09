try:
    import redshift_connector
    psycopg2 = None             # Initialize in case redshift_connector is available
    RealDictCursor = None       # Initialize in case redshift_connector is available
except ImportError:
    redshift_connector = None
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
    except ImportError:
        psycopg2 = None
        RealDictCursor = None

from typing import List, Dict, Any, Optional
from .base_interface import DBInterface

class RedshiftInterface(DBInterface):
    def __init__(self, host: str, port: int, user: str, password: str, database: str):
        super().__init__()
        if redshift_connector is None and psycopg2 is None:
            raise ImportError("Either redshift-connector or psycopg2 is required for RedshiftInterface")
            
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.connect()

    def connect(self):
        """Establish Redshift database connection."""
        try:
            if redshift_connector:
                self.conn = redshift_connector.connect(
                    host=self.host,
                    port=self.port,
                    user=self.user,
                    password=self.password,
                    database=self.database
                )
            else:
                # Fallback to psycopg2
                self.conn = psycopg2.connect(
                    host=self.host,
                    port=self.port,
                    user=self.user,
                    password=self.password,
                    database=self.database,
                    cursor_factory=RealDictCursor
                )
            self.conn.autocommit = False
        except Exception as e:
            raise RuntimeError(f"Failed to connect to Redshift: {e}") from e

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
        
        if redshift_connector:
            return [row[0] for row in cursor.fetchall()]
        else:
            return [row["column_name"] for row in cursor.fetchall()]

    def get_table_names(self) -> List[str]:
        """Get all table names in the database."""
        query = """
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'public'
        ORDER BY tablename
        """
        cursor = self.conn.cursor()
        cursor.execute(query)
        
        if redshift_connector:
            return [row[0] for row in cursor.fetchall()]
        else:
            return [row["tablename"] for row in cursor.fetchall()]

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
            
            # Check if table exists first (Redshift doesn't have CREATE TABLE IF NOT EXISTS)
            if not self.table_exists(table_name):
                query = f'CREATE TABLE "{table_name}" ({columns_str})'
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
                # Convert :param to %s format for psycopg2/redshift
                modified_query = query
                param_values = []
                for key, value in params.items():
                    modified_query = modified_query.replace(f":{key}", "%s")
                    param_values.append(value)
                cursor.execute(modified_query, param_values)
            else:
                cursor.execute(query)
            
            if fetch == "one":
                row = cursor.fetchone()
                if row:
                    if redshift_connector:
                        columns = [desc[0] for desc in cursor.description]
                        return dict(zip(columns, row))
                    else:
                        return dict(row)
                return None
            elif fetch == "all":
                rows = cursor.fetchall()
                if rows:
                    if redshift_connector:
                        columns = [desc[0] for desc in cursor.description]
                        return [dict(zip(columns, row)) for row in rows]
                    else:
                        return [dict(row) for row in rows]
                return []
            else:
                return cursor.rowcount if cursor.rowcount > 0 else True
                
        except Exception as e:
            raise RuntimeError(f"Query execution failed: {e}") from e
