import hashlib
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

def generate_hash(data: Dict[str, Any], hash_columns: List[str]) -> Optional[str]:
    """
    Generate a SHA-256 hash string for given data and columns.
    
    Args:
        data: Dictionary containing the data
        hash_columns: List of column names to include in hash
        
    Returns:
        SHA-256 hash string or None if no hash columns provided
    """
    if not hash_columns:
        return None
        
    # Sort columns to ensure consistent hash order
    sorted_columns = sorted(hash_columns)
    hash_values = []
    
    for col in sorted_columns:
        if col in data:
            value = data[col]
            # Handle different data types consistently
            if isinstance(value, dict) or isinstance(value, list):
                hash_values.append(json.dumps(value, sort_keys=True))
            elif isinstance(value, datetime):
                hash_values.append(value.isoformat())
            elif value is None:
                hash_values.append("NULL")
            else:
                hash_values.append(str(value))
    
    concat_values = "|".join(hash_values)  # Use separator to avoid collision
    return hashlib.sha256(concat_values.encode("utf-8")).hexdigest()

def check_duplicate_hash(interface, table_name: str, hash_value: str, 
                        hash_column: str = "hash_value") -> bool:
    """
    Check if a hash value already exists in the table.
    
    Args:
        interface: Database interface instance
        table_name: Name of the table to check
        hash_value: Hash value to check for
        hash_column: Name of the hash column (default: 'hash_value')
        
    Returns:
        True if hash exists, False otherwise
    """
    try:
        # Use the interface's execute_query method with proper parameterization
        query = f"SELECT 1 FROM {table_name} WHERE {hash_column} = ? LIMIT 1"
        params = (hash_value,)
        
        result = interface.execute_query(query, params, fetch="one")
        return result is not None
    except Exception:
        # If hash column doesn't exist or any other error, assume no duplicate
        return False

def get_file_hash(file_path: str) -> str:
    """
    Generate SHA-256 hash of a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        SHA-256 hash string of the file
    """
    hash_sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except Exception as e:
        raise RuntimeError(f"Error reading file {file_path}: {e}")

def validate_schema(data: Dict[str, Any], required_columns: List[str]) -> bool:
    """
    Validate that data contains all required columns.
    
    Args:
        data: Dictionary containing the data
        required_columns: List of required column names
        
    Returns:
        True if all required columns are present, False otherwise
    """
    return all(col in data for col in required_columns)

def sanitize_table_name(table_name: str) -> str:
    """
    Sanitize table name to prevent SQL injection.
    
    Args:
        table_name: Original table name
        
    Returns:
        Sanitized table name
    """
    # Allow only alphanumeric characters and underscores
    import re
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', table_name):
        raise ValueError(f"Invalid table name: {table_name}")
    return table_name




