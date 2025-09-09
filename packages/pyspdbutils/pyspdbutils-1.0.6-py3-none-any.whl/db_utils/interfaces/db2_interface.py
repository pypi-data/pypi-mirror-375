try:
    import ibm_db
    import ibm_db_dbi
except ImportError:
    ibm_db = None
    ibm_db_dbi = None

from typing import List, Dict, Any, Optional
from .base_interface import DBInterface

class DB2Interface(DBInterface):
    def __init__(self, host: str, port: int, user: str, password: str, database: str):
        super().__init__()
        if ibm_db is None:
            raise ImportError("ibm-db is required for DB2Interface")
            
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.connect()

    def connect(self):
        """Establish DB2 database connection."""
        try:
            connection_string = (
                f"DATABASE={self.database};"
                f"HOSTNAME={self.host};"
                f"PORT={self.port};"
                f"PROTOCOL=TCPIP;"
                f"UID={self.user};"
                f"PWD={self.password};"
            )
            
            self.ibm_conn = ibm_db.connect(connection_string, "", "")
            self.conn = ibm_db_dbi.Connection(self.ibm_conn)
        except Exception as e:
            raise RuntimeError(f"Failed to connect to DB2: {e}") from e

    def get_columns(self, table_name: str) -> List[str]:
        """Get column names for a table."""
        query = """
        SELECT colname 
        FROM syscat.columns 
        WHERE tabname = UPPER(?) 
        ORDER BY colno
        """
        cursor = self.conn.cursor()
        cursor.execute(query, (table_name,))
        return [row[0] for row in cursor.fetchall()]

    def get_table_names(self) -> List[str]:
        """Get all table names in the database."""
        query = """
        SELECT tabname 
        FROM syscat.tables 
        WHERE tabschema = CURRENT_SCHEMA 
        AND type = 'T'
        ORDER BY tabname
        """
        cursor = self.conn.cursor()
        cursor.execute(query)
        return [row[0] for row in cursor.fetchall()]

    def table_exists(self, table_name: str) -> bool:
        """Check if table exists in database."""
        query = """
        SELECT tabname 
        FROM syscat.tables 
        WHERE tabname = UPPER(?) AND type = 'T'
        """
        cursor = self.conn.cursor()
        cursor.execute(query, (table_name,))
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
                # Convert :param to ? format for DB2
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
        if hasattr(self, 'ibm_conn') and self.ibm_conn:
            ibm_db.close(self.ibm_conn)
            self.conn = None
