from sqlalchemy import text
from typing import Tuple, Dict, Any, List, Optional

class QueryBuilder:
    def __init__(self, db_type: str):
        """Initialize query builder with database type."""
        self.db_type = db_type.lower() if db_type else "sqlite"
        self.query = None
        self.params = None

    def build_query_params(self, query_type: str, table_name: str, **kwargs) -> Tuple:
        """
        Generic query builder using **kwargs.
        
        Args:
            query_type: Type of query (INSERT, UPDATE, SELECT, CREATE)
            table_name: Name of the table
            **kwargs: Additional parameters like data, conditions, columns, etc.
        
        Returns:
            Tuple of (query, params)
        """
        query_type = query_type.upper()
        data = kwargs.get("data", {})
        limit = kwargs.get("limit", None)
        offset = kwargs.get("offset", None)
        conditions = kwargs.get("conditions", {})
        columns = kwargs.get("columns", ["*"])
        schema = kwargs.get("schema", {})

        if query_type == "INSERT":
            return self._build_insert_query(table_name, data)
            
        elif query_type == "UPDATE":
            return self._build_update_query(table_name, data, conditions)
            
        elif query_type == "SELECT":
            return self._build_select_query(table_name, columns, conditions, limit, offset)
            
        elif query_type == "CREATE":
            return self._build_create_query(table_name, schema, **kwargs)
            
        else:
            raise ValueError(f"Invalid query type: {query_type}. Supported types: INSERT, UPDATE, SELECT, CREATE")

    def _build_insert_query(self, table_name: str, data: Dict[str, Any]) -> Tuple:
        """Build INSERT query."""
        if not data:
            raise ValueError("Data cannot be empty for INSERT query")
            
        insert_columns = ", ".join(data.keys())
        placeholders = ", ".join(["?" for _ in data.keys()])
        query = text(f"INSERT INTO {table_name} ({insert_columns}) VALUES ({placeholders})")
        return query, tuple(data.values())

    def _build_update_query(self, table_name: str, data: Dict[str, Any], conditions: Dict[str, Any]) -> Tuple:
        """Build UPDATE query."""
        if not data:
            raise ValueError("Data cannot be empty for UPDATE query")
        if not conditions:
            raise ValueError("Conditions cannot be empty for UPDATE query")
            
        set_clause = ", ".join([f"{key} = ?" for key in data.keys()])
        where_clause = " AND ".join([f"{key} = ?" for key in conditions.keys()])
        
        # Combine parameters in the correct order
        params = tuple(data.values()) + tuple(conditions.values())
            
        query = text(f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}")
        return query, params

    def _build_select_query(self, table_name: str, columns: List[str], conditions: Dict[str, Any], 
                          limit: Optional[int], offset: Optional[int]) -> Tuple:
        """Build SELECT query."""
        select_columns = ", ".join(columns) if columns != ["*"] else "*"
        
        query_str = f"SELECT {select_columns} FROM {table_name}"
        params = ()
        
        if conditions:
            where_clause = " AND ".join([f"{key} = ?" for key in conditions.keys()])
            query_str += f" WHERE {where_clause}"
            params = tuple(conditions.values())
            
        # Apply limit and offset based on database type
        query_str = self._apply_limit_offset(query_str, limit, offset)
        
        query = text(query_str)
        return query, params

    def _build_create_query(self, table_name: str, schema: Dict[str, str], **kwargs) -> Tuple:
        """Build CREATE TABLE query."""
        if not schema:
            raise ValueError("Schema cannot be empty for CREATE query")
            
        columns = []
        for col_name, col_type in schema.items():
            columns.append(f"{col_name} {col_type}")
            
        columns_str = ", ".join(columns)
        
        # Handle IF NOT EXISTS based on database type
        if self.db_type in ("sqlite", "postgresql", "mysql"):
            query_str = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_str})"
        else:
            query_str = f"CREATE TABLE {table_name} ({columns_str})"
            
        query = text(query_str)
        return query, {}
    
    def _apply_limit_offset(self, query_str: str, limit: Optional[int], offset: Optional[int]) -> str:
        """Apply LIMIT and OFFSET based on database type."""
        if limit is None:
            return query_str
            
        if self.db_type in ("mysql", "postgresql", "sqlite"):
            if offset is not None:
                query_str += f" LIMIT {limit} OFFSET {offset}"
            else:
                query_str += f" LIMIT {limit}"
                
        elif self.db_type in ("mssql", "sqlserver", "azure_sql"):
            if offset is not None:
                query_str += f" ORDER BY (SELECT NULL) OFFSET {offset} ROWS FETCH NEXT {limit} ROWS ONLY"
            else:
                query_str += f" ORDER BY (SELECT NULL) OFFSET 0 ROWS FETCH NEXT {limit} ROWS ONLY"
                
        elif self.db_type == "db2":
            if offset is not None:
                query_str += f" OFFSET {offset} ROWS FETCH NEXT {limit} ROWS ONLY"
            else:
                query_str += f" FETCH FIRST {limit} ROWS ONLY"
                
        elif self.db_type == "oracle":
            if offset is not None:
                query_str = f"SELECT * FROM ({query_str}) WHERE ROWNUM <= {limit + offset} AND ROWNUM > {offset}"
            else:
                query_str = f"SELECT * FROM ({query_str}) WHERE ROWNUM <= {limit}"
                
        else:
            # Fallback to LIMIT for unknown databases
            if offset is not None:
                query_str += f" LIMIT {limit} OFFSET {offset}"
            else:
                query_str += f" LIMIT {limit}"

        return query_str


    



