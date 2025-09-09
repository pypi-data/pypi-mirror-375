try:
    import teradatasql
except ImportError:
    teradatasql = None

from typing import List, Dict, Any, Optional
from .base_interface import DBInterface

class TeradataInterface(DBInterface):
    def __init__(self, host: str, user: str, password: str, database: Optional[str] = None):
        super().__init__()
        if teradatasql is None:
            raise ImportError("teradatasql is required for TeradataInterface")
            
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connect()

    def connect(self):
        """Establish Teradata database connection."""
        try:
            connection_params = {
                'host': self.host,
                'user': self.user,
                'password': self.password,
                'autocommit': False
            }
            
            if self.database:
                connection_params['database'] = self.database
                
            self.conn = teradatasql.connect(**connection_params)
        except Exception as e:
            raise RuntimeError(f"Failed to connect to Teradata: {e}") from e

    def get_columns(self, table_name: str) -> List[str]:
        """Get column names for a table."""
        query = """
        SELECT ColumnName 
        FROM DBC.ColumnsV 
        WHERE TableName = ? 
        ORDER BY ColumnId
        """
        cursor = self.conn.cursor()
        cursor.execute(query, (table_name.upper(),))
        return [row[0] for row in cursor.fetchall()]

    def get_table_names(self) -> List[str]:
        """Get all table names in the database."""
        query = """
        SELECT TableName 
        FROM DBC.TablesV 
        WHERE TableKind = 'T' 
        AND DatabaseName = DATABASE
        ORDER BY TableName
        """
        cursor = self.conn.cursor()
        cursor.execute(query)
        return [row[0] for row in cursor.fetchall()]

    def table_exists(self, table_name: str) -> bool:
        """Check if table exists in database."""
        query = """
        SELECT TableName 
        FROM DBC.TablesV 
        WHERE TableName = ? AND TableKind = 'T'
        """
        cursor = self.conn.cursor()
        cursor.execute(query, (table_name.upper(),))
        return cursor.fetchone() is not None

    def create_table(self, table_name: str, schema: Dict[str, str], **kwargs) -> bool:
        """Create table with given schema."""
        try:
            columns = []
            for col_name, col_type in schema.items():
                columns.append(f'"{col_name.upper()}" {col_type}')
            
            columns_str = ", ".join(columns)
            
            # Check if table exists first
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
                # Convert :param to ? format for Teradata
                modified_query = query
                param_values = []
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
