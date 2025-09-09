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

    def insert(self, table_name: str, data: Union[Dict[str, Any], List[Dict[str, Any]]], 
               skip_duplicates: bool = True) -> Union[bool, str, Dict[str, Any]]:
        """
        Insert data into table with duplicate detection. Supports both single and bulk inserts.
        
        Args:
            table_name: Name of the table
            data: Dictionary for single insert or List of dictionaries for bulk insert
            skip_duplicates: Whether to skip duplicate records based on hash
            
        Returns:
            Single insert: True if inserted successfully, "duplicate" if skipped
            Bulk insert: Dict with statistics {"inserted": int, "duplicates": int, "errors": List[str]}
            
        Raises:
            ValidationError: If data validation fails
            DBOperationError: If insertion fails
        """
        try:
            table_name = sanitize_table_name(table_name)
            
            # Check if this is a bulk insert (list of dictionaries)
            if isinstance(data, list):
                return self._bulk_insert(table_name, data, skip_duplicates)
            
            # Single insert (backward compatible)
            return self._single_insert(table_name, data, skip_duplicates)
            
        except ValidationError:
            raise
        except Exception as e:
            raise DBOperationError(f"Failed to insert data into {table_name}: {e}") from e

    def _single_insert(self, table_name: str, data: Dict[str, Any], skip_duplicates: bool) -> Union[bool, str]:
        """Handle single record insert (original functionality)."""
        if not isinstance(data, dict):
            raise ValidationError("Data must be a dictionary")
            
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

    def _bulk_insert(self, table_name: str, data_list: List[Dict[str, Any]], skip_duplicates: bool) -> Dict[str, Any]:
        """Handle bulk insert with list of dictionaries."""
        results = {"inserted": 0, "duplicates": 0, "errors": []}
        
        if not data_list:
            raise ValidationError("Data list cannot be empty")
        
        # Validate table exists once
        if not self.table_exists(table_name):
            raise ValidationError(f"Table {table_name} does not exist")
            
        table_columns = self.interface.get_columns(table_name)
        
        for i, data_item in enumerate(data_list, 1):
            try:
                # Validate data type
                if not isinstance(data_item, dict):
                    results["errors"].append(f"Row {i}: Data must be a dictionary")
                    continue
                
                data_copy = data_item.copy()
                data_columns = list(data_copy.keys())
                
                # Add hash if configured
                if self.hash_columns:
                    hash_value = generate_hash(data_copy, self.hash_columns)
                    if hash_value:
                        # Check for duplicates
                        if skip_duplicates and self._check_duplicate_by_columns(table_name, data_copy):
                            results["duplicates"] += 1
                            continue
                        
                        # Only add hash_value if the column exists in the table
                        if 'hash_value' in table_columns:
                            data_copy['hash_value'] = hash_value
                            data_columns.append('hash_value')
                
                # Validate all data columns exist in table
                invalid_columns = [col for col in data_columns if col not in table_columns]
                if invalid_columns:
                    results["errors"].append(f"Row {i}: Invalid columns {invalid_columns}")
                    continue
                
                # Insert the row
                query, params = self.query_builder.build_query_params("INSERT", table_name, data=data_copy)
                self.interface.execute_query(str(query), params)
                results["inserted"] += 1
                
            except Exception as e:
                results["errors"].append(f"Row {i}: {str(e)}")
                continue
        
        return results

    def update(self, table_name: str, data, 
               conditions: Optional[Dict[str, Any]] = None) -> Union[bool, Dict[str, Any]]:
        """
        Update data in table. Supports both single and bulk updates.
        
        Args:
            table_name: Name of the table
            data: For single update: Dict with update data
                  For bulk update: List of dicts with 'data' and 'conditions' keys
            conditions: For single update: Dict with WHERE conditions
                       For bulk update: Not used (conditions in each list item)
            
        Returns:
            Single update: True if updated successfully
            Bulk update: Dict with statistics {"updated": int, "errors": List[str]}
            
        Raises:
            ValidationError: If validation fails
            DBOperationError: If update fails
        """
        try:
            table_name = sanitize_table_name(table_name)
            
            # Check if this is a bulk update (list of update objects)
            if isinstance(data, list):
                return self._bulk_update(table_name, data)
            
            # Single update (backward compatible)
            return self._single_update(table_name, data, conditions)
            
        except ValidationError:
            raise
        except Exception as e:
            raise DBOperationError(f"Failed to update data in {table_name}: {e}") from e

    def _single_update(self, table_name: str, data: Dict[str, Any], 
                      conditions: Dict[str, Any]) -> bool:
        """Handle single record update (original functionality)."""
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

    def _bulk_update(self, table_name: str, updates_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Handle bulk updates with list of update objects."""
        results = {"updated": 0, "errors": []}
        
        if not updates_list:
            raise ValidationError("Updates list cannot be empty")
        
        # Validate table exists once
        if not self.table_exists(table_name):
            raise ValidationError(f"Table {table_name} does not exist")
            
        table_columns = self.interface.get_columns(table_name)
        
        for i, update_obj in enumerate(updates_list, 1):
            try:
                # Validate update object structure
                if not isinstance(update_obj, dict):
                    results["errors"].append(f"Update {i}: Must be a dictionary with 'data' and 'conditions' keys")
                    continue
                
                if 'data' not in update_obj or 'conditions' not in update_obj:
                    results["errors"].append(f"Update {i}: Must contain 'data' and 'conditions' keys")
                    continue
                
                data = update_obj['data']
                conditions = update_obj['conditions']
                
                if not data:
                    results["errors"].append(f"Update {i}: Update data cannot be empty")
                    continue
                    
                if not conditions:
                    results["errors"].append(f"Update {i}: Update conditions cannot be empty")
                    continue
                
                # Validate columns exist in table
                all_columns = list(data.keys()) + list(conditions.keys())
                invalid_columns = [col for col in all_columns if col not in table_columns]
                if invalid_columns:
                    results["errors"].append(f"Update {i}: Invalid columns {invalid_columns}")
                    continue
                
                # Execute the update
                query, params = self.query_builder.build_query_params(
                    "UPDATE", table_name, data=data, conditions=conditions
                )
                self.interface.execute_query(str(query), params)
                results["updated"] += 1
                
            except Exception as e:
                results["errors"].append(f"Update {i}: {str(e)}")
                continue
        
        return results

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
    
    def execute_query(self, query: str, params: Optional[Union[Dict[str, Any], List]] = None, fetch: Optional[str] = None):
        """
        Execute a raw SQL query.
        
        Args:
            query: SQL query string
            params: Query parameters (optional)
            fetch: Fetch mode - "all", "one", or None (for non-SELECT queries)
            
        Returns:
            Query results based on fetch mode
            
        Raises:
            DBOperationError: If query execution fails
        """
        try:
            return self.interface.execute_query(query, params, fetch)
        except Exception as e:
            raise DBOperationError(f"Failed to execute query: {e}") from e
    
    def close(self):
        """Close the database connection."""
        try:
            if hasattr(self.interface, 'close'):
                self.interface.close()
        except Exception as e:
            raise DBOperationError(f"Failed to close connection: {e}") from e