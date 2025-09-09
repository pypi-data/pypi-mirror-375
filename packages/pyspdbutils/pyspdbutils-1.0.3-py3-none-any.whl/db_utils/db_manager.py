from typing import Dict, Any, List, Optional, Union
from .build_query import QueryBuilder
from .utils import generate_hash, check_duplicate_hash, validate_schema, sanitize_table_name
from .exception import DBOperationError, ValidationError

class DBManager:
    """
    Database manager that provides high-level database operations
    with built-in hash collision detection and validation.
    """
    
    def __init__(self, interface, hash_columns: Optional[List[str]] = None):
        """
        Initialize DB Manager.
        
        Args:
            interface: Database interface instance
            hash_columns: List of columns to use for hash generation
        """
        self.interface = interface
        self.query_builder = QueryBuilder(getattr(interface, 'db_type', 'sqlite'))
        self.hash_columns = hash_columns or []

    def create_table(self, table_name: str, schema: Dict[str, str], **kwargs) -> bool:
        """
        Create a table with the given schema.
        
        Args:
            table_name: Name of the table to create
            schema: Dictionary mapping column names to their data types
            **kwargs: Additional table creation options
            
        Returns:
            True if table created successfully
            
        Raises:
            ValidationError: If table name or schema is invalid
            DBOperationError: If table creation fails
        """
        try:
            table_name = sanitize_table_name(table_name)
            
            if not schema:
                raise ValidationError("Schema cannot be empty")
                
            # Create a copy of schema to avoid modifying the original
            table_schema = schema.copy()
            
            # Add hash column if hash_columns are specified
            if self.hash_columns and 'hash_value' not in table_schema:
                table_schema['hash_value'] = 'VARCHAR(64)'
                
            return self.interface.create_table(table_name, table_schema, **kwargs)
            
        except Exception as e:
            raise DBOperationError(f"Failed to create table {table_name}: {e}") from e

    def table_exists(self, table_name: str) -> bool:
        """Check if table exists in database."""
        try:
            table_name = sanitize_table_name(table_name)
            return self.interface.table_exists(table_name)
        except Exception as e:
            raise DBOperationError(f"Failed to check table existence: {e}") from e

    def insert(self, table_name: str, data: Dict[str, Any], 
               skip_duplicates: bool = True) -> Union[bool, str]:
        """
        Insert data into table with duplicate detection.
        
        Args:
            table_name: Name of the table
            data: Dictionary containing the data to insert
            skip_duplicates: Whether to skip duplicate records based on hash
            
        Returns:
            True if inserted successfully, "duplicate" if skipped due to duplicate
            
        Raises:
            ValidationError: If data validation fails
            DBOperationError: If insertion fails
        """
        try:
            table_name = sanitize_table_name(table_name)
            
            # Validate table exists
            if not self.table_exists(table_name):
                raise ValidationError(f"Table {table_name} does not exist")
            
            # Validate schema
            table_columns = self.interface.get_columns(table_name)
            data_columns = list(data.keys())
            
            # Add hash if configured and table supports it
            if self.hash_columns:
                hash_value = generate_hash(data, self.hash_columns)
                if hash_value:
                    # Check for duplicates using existing data (not hash column)
                    if skip_duplicates and self._check_duplicate_by_columns(table_name, data):
                        return "duplicate"
                    
                    # Only add hash_value if the column exists in the table
                    if 'hash_value' in table_columns:
                        data['hash_value'] = hash_value
                        data_columns.append('hash_value')
            
            # Validate all data columns exist in table
            invalid_columns = [col for col in data_columns if col not in table_columns]
            if invalid_columns:
                raise ValidationError(f"Invalid columns for table {table_name}: {invalid_columns}")
            
            query, params = self.query_builder.build_query_params("INSERT", table_name, data=data)
            self.interface.execute_query(str(query), params)
            return True
            
        except ValidationError:
            raise
        except Exception as e:
            raise DBOperationError(f"Failed to insert data into {table_name}: {e}") from e

    def update(self, table_name: str, data: Dict[str, Any], 
               conditions: Dict[str, Any]) -> bool:
        """
        Update data in table.
        
        Args:
            table_name: Name of the table
            data: Dictionary containing the data to update
            conditions: Dictionary containing the WHERE conditions
            
        Returns:
            True if updated successfully
            
        Raises:
            ValidationError: If validation fails
            DBOperationError: If update fails
        """
        try:
            table_name = sanitize_table_name(table_name)
            
            if not data:
                raise ValidationError("Update data cannot be empty")
            if not conditions:
                raise ValidationError("Update conditions cannot be empty")
            
            # Validate table exists
            if not self.table_exists(table_name):
                raise ValidationError(f"Table {table_name} does not exist")
            
            # Validate columns exist in table
            table_columns = self.interface.get_columns(table_name)
            all_columns = list(data.keys()) + list(conditions.keys())
            invalid_columns = [col for col in all_columns if col not in table_columns]
            if invalid_columns:
                raise ValidationError(f"Invalid columns for table {table_name}: {invalid_columns}")

            query, params = self.query_builder.build_query_params(
                "UPDATE", table_name, data=data, conditions=conditions
            )
            self.interface.execute_query(str(query), params)
            return True
            
        except ValidationError:
            raise
        except Exception as e:
            raise DBOperationError(f"Failed to update data in {table_name}: {e}") from e

    def select(self, table_name: str, columns: Union[List[str], str] = "*", 
               conditions: Optional[Dict[str, Any]] = None, 
               limit: Optional[int] = None, offset: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Select data from table.
        
        Args:
            table_name: Name of the table
            columns: List of columns to select or "*" for all
            conditions: Dictionary containing the WHERE conditions
            limit: Maximum number of rows to return
            offset: Number of rows to skip
            
        Returns:
            List of dictionaries containing the selected data
            
        Raises:
            ValidationError: If validation fails
            DBOperationError: If selection fails
        """
        try:
            table_name = sanitize_table_name(table_name)
            
            # Validate table exists
            if not self.table_exists(table_name):
                raise ValidationError(f"Table {table_name} does not exist")
            
            # Convert columns to list if string
            if isinstance(columns, str):
                columns = ["*"] if columns == "*" else [columns]
            
            # Validate columns exist in table (except for * and SQL expressions)
            if columns != ["*"]:
                table_columns = self.interface.get_columns(table_name)
                # Skip validation for SQL expressions (containing functions or operators)
                columns_to_validate = [
                    col for col in columns 
                    if not any(keyword in col.upper() for keyword in ['COUNT(', 'SUM(', 'AVG(', 'MAX(', 'MIN(', 'AS ', '*'])
                ]
                invalid_columns = [col for col in columns_to_validate if col not in table_columns]
                if invalid_columns:
                    raise ValidationError(f"Invalid columns for table {table_name}: {invalid_columns}")
            
            # Validate condition columns
            if conditions:
                table_columns = self.interface.get_columns(table_name)
                invalid_columns = [col for col in conditions.keys() if col not in table_columns]
                if invalid_columns:
                    raise ValidationError(f"Invalid condition columns for table {table_name}: {invalid_columns}")

            query, params = self.query_builder.build_query_params(
                "SELECT", table_name, columns=columns, conditions=conditions, 
                limit=limit, offset=offset
            )
            result = self.interface.execute_query(str(query), params, fetch="all")
            return result or []
            
        except ValidationError:
            raise
        except Exception as e:
            raise DBOperationError(f"Failed to select data from {table_name}: {e}") from e

    def fetch_all(self, table_name: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Fetch all records from table."""
        return self.select(table_name, "*", limit=limit)

    def count(self, table_name: str, conditions: Optional[Dict[str, Any]] = None) -> int:
        """
        Count records in table.
        
        Args:
            table_name: Name of the table
            conditions: Dictionary containing the WHERE conditions
            
        Returns:
            Number of records matching the conditions
        """
        try:
            table_name = sanitize_table_name(table_name)
            
            # Validate table exists
            if not self.table_exists(table_name):
                raise ValidationError(f"Table {table_name} does not exist")
            
            # Validate condition columns if provided
            if conditions:
                table_columns = self.interface.get_columns(table_name)
                invalid_columns = [col for col in conditions.keys() if col not in table_columns]
                if invalid_columns:
                    raise ValidationError(f"Invalid condition columns for table {table_name}: {invalid_columns}")

            # Build COUNT query directly to avoid column validation
            query, params = self.query_builder.build_query_params(
                "SELECT", table_name, columns=["COUNT(*) as count"], conditions=conditions, limit=1
            )
            
            # Execute query directly without column validation
            result = self.interface.execute_query(str(query), params, fetch="one")
            return result["count"] if result else 0
            
        except ValidationError:
            raise
        except Exception as e:
            raise DBOperationError(f"Failed to count records in {table_name}: {e}") from e

    def delete(self, table_name: str, conditions: Dict[str, Any]) -> bool:
        """
        Delete records from table.
        
        Args:
            table_name: Name of the table
            conditions: Dictionary containing the WHERE conditions
            
        Returns:
            True if deletion was successful
            
        Raises:
            ValidationError: If validation fails
            DBOperationError: If deletion fails
        """
        try:
            table_name = sanitize_table_name(table_name)
            
            if not conditions:
                raise ValidationError("Delete conditions cannot be empty")
            
            # Validate table exists
            if not self.table_exists(table_name):
                raise ValidationError(f"Table {table_name} does not exist")
            
            # Validate condition columns
            table_columns = self.interface.get_columns(table_name)
            invalid_columns = [col for col in conditions.keys() if col not in table_columns]
            if invalid_columns:
                raise ValidationError(f"Invalid condition columns for table {table_name}: {invalid_columns}")

            # Build DELETE query manually since QueryBuilder doesn't support DELETE
            where_clause = " AND ".join([f"{key} = :{key}" for key in conditions.keys()])
            query = f"DELETE FROM {table_name} WHERE {where_clause}"
            
            self.interface.execute_query(query, conditions)
            return True
            
        except ValidationError:
            raise
        except Exception as e:
            raise DBOperationError(f"Failed to delete data from {table_name}: {e}") from e

    def _check_duplicate_by_columns(self, table_name: str, data: Dict[str, Any]) -> bool:
        """Check for duplicates using hash columns without requiring hash_value column."""
        try:
            if not self.hash_columns:
                return False
            
            # Build conditions using hash columns
            conditions = {}
            for col in self.hash_columns:
                if col in data:
                    conditions[col] = data[col]
            
            if not conditions:
                return False
                
            # Check if record with same hash column values exists
            existing = self.select(table_name, conditions=conditions)
            return len(existing) > 0
            
        except Exception:
            # If check fails, allow insertion (better to allow than block incorrectly)
            return False

    def get_columns(self, table_name: str) -> List[str]:
        """Get column names for a table."""
        try:
            table_name = sanitize_table_name(table_name)
            return self.interface.get_columns(table_name)
        except Exception as e:
            raise DBOperationError(f"Failed to get columns for {table_name}: {e}") from e