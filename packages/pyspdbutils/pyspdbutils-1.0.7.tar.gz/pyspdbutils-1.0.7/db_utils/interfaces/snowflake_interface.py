try:
    import snowflake.connector as snowflake_connector
    from snowflake.connector import DictCursor
except ImportError:
    snowflake_connector = None
    DictCursor = None

from typing import List, Dict, Any, Optional
from .base_interface import DBInterface

class SnowflakeInterface(DBInterface):
    def __init__(self, account: str, user: str, password: str, warehouse: str, 
                 database: str, schema: str = "PUBLIC", role: Optional[str] = None):
        super().__init__()
        if snowflake_connector is None:
            raise ImportError("snowflake-connector-python is required for SnowflakeInterface")
            
        self.account = account
        self.user = user
        self.password = password
        self.warehouse = warehouse
        self.database = database
        self.schema = schema
        self.role = role
        self.connect()

    def connect(self):
        """Establish Snowflake database connection."""
        try:
            connection_params = {
                'account': self.account,
                'user': self.user,
                'password': self.password,
                'warehouse': self.warehouse,
                'database': self.database,
                'schema': self.schema,
            }
            
            if self.role:
                connection_params['role'] = self.role
                
            self.conn =snowflake_connector.connect(**connection_params)
        except Exception as e:
            raise RuntimeError(f"Failed to connect to Snowflake: {e}") from e

    def get_columns(self, table_name: str) -> List[str]:
        """Get column names for a table."""
        query = """
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_schema = CURRENT_SCHEMA() 
        AND table_name = UPPER(%(table_name)s)
        ORDER BY ordinal_position
        """
        cursor = self.conn.cursor(DictCursor)
        cursor.execute(query, {"table_name": table_name})
        return [row["COLUMN_NAME"] for row in cursor.fetchall()]

    def get_table_names(self) -> List[str]:
        """Get all table names in the database."""
        query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = CURRENT_SCHEMA() AND table_type = 'BASE TABLE'
        ORDER BY table_name
        """
        cursor = self.conn.cursor(DictCursor)
        cursor.execute(query)
        return [row["TABLE_NAME"] for row in cursor.fetchall()]

    def table_exists(self, table_name: str) -> bool:
        """Check if table exists in database."""
        query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = CURRENT_SCHEMA() 
        AND table_name = UPPER(%(table_name)s)
        """
        cursor = self.conn.cursor(DictCursor)
        cursor.execute(query, {"table_name": table_name})
        return cursor.fetchone() is not None

    def create_table(self, table_name: str, schema: Dict[str, str], **kwargs) -> bool:
        """Create table with given schema."""
        try:
            columns = []
            for col_name, col_type in schema.items():
                columns.append(f'"{col_name.upper()}" {col_type}')
            
            columns_str = ", ".join(columns)
            query = f'CREATE TABLE IF NOT EXISTS "{table_name.upper()}" ({columns_str})'
            
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
            cursor = self.conn.cursor(DictCursor)
            
            if params:
                # Convert :param to %(param)s format for Snowflake
                modified_query = query
                snowflake_params = {}
                for key, value in params.items():
                    modified_query = modified_query.replace(f":{key}", f"%({key})s")
                    snowflake_params[key] = value
                cursor.execute(modified_query, snowflake_params)
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
