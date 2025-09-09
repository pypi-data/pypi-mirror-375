try:
    from databricks import sql
except ImportError:
    sql = None

from typing import List, Dict, Any, Optional
from .base_interface import DBInterface

class DatabricksInterface(DBInterface):
    def __init__(self, server_hostname: str, http_path: str, access_token: str):
        super().__init__()
        if sql is None:
            raise ImportError("databricks-sql-connector is required for DatabricksInterface")
            
        self.server_hostname = server_hostname
        self.http_path = http_path
        self.access_token = access_token
        self.connect()

    def connect(self):
        """Establish Databricks database connection."""
        try:
            self.conn = sql.connect(
                server_hostname=self.server_hostname,
                http_path=self.http_path,
                access_token=self.access_token
            )
        except Exception as e:
            raise RuntimeError(f"Failed to connect to Databricks: {e}") from e

    def get_columns(self, table_name: str) -> List[str]:
        """Get column names for a table."""
        query = f"DESCRIBE {table_name}"
        cursor = self.conn.cursor()
        cursor.execute(query)
        
        columns = []
        for row in cursor.fetchall():
            # DESCRIBE returns (col_name, data_type, comment)
            if row[0] and not row[0].startswith('#'):  # Skip comment lines
                columns.append(row[0])
        return columns

    def get_table_names(self) -> List[str]:
        """Get all table names in the database."""
        query = "SHOW TABLES"
        cursor = self.conn.cursor()
        cursor.execute(query)
        
        tables = []
        for row in cursor.fetchall():
            # SHOW TABLES returns (database, tableName, isTemporary)
            if len(row) >= 2:
                tables.append(row[1])  # tableName is at index 1
            else:
                tables.append(row[0])  # fallback to first column
        return tables

    def table_exists(self, table_name: str) -> bool:
        """Check if table exists in database."""
        try:
            query = f"DESCRIBE {table_name}"
            cursor = self.conn.cursor()
            cursor.execute(query)
            return True
        except Exception:
            return False

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
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to create table {table_name}: {e}") from e

    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None, fetch: str = None):
        """Execute query with optional parameters and fetch mode."""
        try:
            cursor = self.conn.cursor()
            
            if params:
                # Databricks uses different parameter substitution
                modified_query = query
                for key, value in params.items():
                    # Simple string replacement for demo - production should use proper parameter binding
                    if isinstance(value, str):
                        modified_query = modified_query.replace(f":{key}", f"'{value}'")
                    else:
                        modified_query = modified_query.replace(f":{key}", str(value))
                cursor.execute(modified_query)
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
                return True  # Databricks doesn't provide rowcount easily
                
        except Exception as e:
            raise RuntimeError(f"Query execution failed: {e}") from e

    def commit(self):
        """Commit transaction - Databricks auto-commits."""
        pass  # Databricks typically auto-commits

    def rollback(self):
        """Rollback transaction - Not supported in Databricks."""
        pass  # Databricks doesn't support explicit rollback

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
