from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from typing import List, Dict, Any, Optional
from .base_interface import DBInterface

class SQLAlchemyInterface(DBInterface):
    def __init__(self, connection_string: str):
        super().__init__()
        self.connection_string = connection_string
        self.engine = None
        self.session = None
        self.connect()

    def connect(self):
        """Establish database connection using SQLAlchemy."""
        self.engine = create_engine(self.connection_string)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        self.conn = self.engine.connect()

    def get_columns(self, table_name: str) -> List[str]:
        """Get column names for a table."""
        inspector = inspect(self.engine)
        columns = inspector.get_columns(table_name)
        return [col['name'] for col in columns]

    def table_exists(self, table_name: str) -> bool:
        """Check if table exists in database."""
        inspector = inspect(self.engine)
        return inspector.has_table(table_name)

    def create_table(self, table_name: str, schema: Dict[str, str], **kwargs) -> bool:
        """Create table with given schema using raw SQL."""
        try:
            columns = []
            for col_name, col_type in schema.items():
                columns.append(f"{col_name} {col_type}")
            
            columns_str = ", ".join(columns)
            
            # Handle different SQL dialects for CREATE TABLE IF NOT EXISTS
            dialect = self.engine.dialect.name.lower()
            if dialect in ['sqlite', 'postgresql', 'mysql']:
                query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_str})"
            elif dialect in ['mssql', 'oracle']:
                # Use more complex syntax for databases that don't support IF NOT EXISTS
                check_query = text(f"""
                    SELECT COUNT(*) as count FROM information_schema.tables 
                    WHERE table_name = '{table_name}'
                """)
                result = self.session.execute(check_query).fetchone()
                if result.count == 0:
                    query = f"CREATE TABLE {table_name} ({columns_str})"
                else:
                    return True  # Table already exists
            else:
                query = f"CREATE TABLE {table_name} ({columns_str})"
            
            self.session.execute(text(query))
            self.commit()
            return True
        except Exception as e:
            self.rollback()
            raise RuntimeError(f"Failed to create table {table_name}: {e}") from e

    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None, fetch: str = None):
        """Execute query with optional parameters and fetch mode."""
        try:
            if isinstance(query, str):
                query = text(query)
            
            result = self.session.execute(query, params or {})
            
            if fetch == "one":
                row = result.fetchone()
                return dict(row._mapping) if row else None
            elif fetch == "all":
                rows = result.fetchall()
                return [dict(row._mapping) for row in rows]
            else:
                return result.rowcount if result.rowcount > 0 else True
                
        except Exception as e:
            raise RuntimeError(f"Query execution failed: {e}") from e

    def commit(self):
        """Commit transaction."""
        if self.session:
            self.session.commit()

    def rollback(self):
        """Rollback transaction."""
        if self.session:
            self.session.rollback()

    def close(self):
        """Close database connection."""
        if self.session:
            self.session.close()
        if self.conn:
            self.conn.close()
        if self.engine:
            self.engine.dispose()
