# """
# Simplified Lock Management and Concurrency Utilities for DB Utils.

# This module provides utilities to handle database locks, timeouts,
# and concurrent access patterns.
# """

# import time
# import threading
# import sqlite3
# import random
# from typing import Optional, Any, Callable
# from contextlib import contextmanager
# from .exception import DBOperationError

# # Constants
# DATABASE_LOCKED_ERROR = "database is locked"
# MAX_RETRY_ATTEMPTS = 5
# BASE_RETRY_DELAY = 0.1

# class SQLiteConcurrentInterface:
#     """SQLite interface with proper concurrent access handling."""
    
#     def __init__(self, db_path):
#         self.db_path = db_path
#         self._lock = threading.RLock()
#         self._setup_wal_mode()
    
#     def _setup_wal_mode(self):
#         """Enable WAL mode for better concurrent access."""
#         try:
#             with sqlite3.connect(self.db_path) as conn:
#                 conn.execute("PRAGMA journal_mode=WAL")
#                 conn.execute("PRAGMA synchronous=NORMAL")
#                 conn.execute("PRAGMA cache_size=10000")
#                 conn.execute("PRAGMA temp_store=memory")
#                 conn.execute("PRAGMA busy_timeout=30000")  # 30 seconds
#                 conn.commit()
#         except Exception as e:
#             print(f"Warning: Could not set WAL mode: {e}")
    
#     def _execute_with_retry(self, operation_func, *args, **kwargs):
#         """Execute database operation with retry logic."""
#         last_exception = None
        
#         for attempt in range(MAX_RETRY_ATTEMPTS):
#             try:
#                 return operation_func(*args, **kwargs)
#             except Exception as e:
#                 last_exception = e
#                 error_msg = str(e).lower()
                
#                 if "database is locked" in error_msg or "busy" in error_msg:
#                     if attempt < MAX_RETRY_ATTEMPTS - 1:
#                         # Exponential backoff with jitter
#                         delay = BASE_RETRY_DELAY * (2 ** attempt) + random.uniform(0, 0.1)
#                         time.sleep(delay)
#                         continue
                
#                 # If it's not a lock error, or we've exhausted retries, re-raise
#                 raise e
        
#         # If we get here, all retries failed
#         raise last_exception
    
#     def execute_query(self, query, params=None, fetch=True):
#         """Execute query with lock handling."""
#         def _execute():
#             with self._lock:
#                 conn = sqlite3.connect(self.db_path, timeout=30.0)
#                 conn.row_factory = sqlite3.Row
#                 try:
#                     cursor = conn.execute(query, params or ())
#                     if query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP')):
#                         conn.commit()
#                         return cursor.rowcount
#                     else:
#                         # Handle different fetch options
#                         if fetch == "one":
#                             row = cursor.fetchone()
#                             return dict(row) if row else None
#                         elif fetch is True or fetch == "all":
#                             return [dict(row) for row in cursor.fetchall()]
#                         else:
#                             # For fetch=False or other values, return cursor info
#                             return cursor.rowcount
#                 finally:
#                     conn.close()
        
#         return self._execute_with_retry(_execute)
    
#     def table_exists(self, table_name):
#         """Check if table exists."""
#         query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
#         result = self.execute_query(query, (table_name,))
#         return len(result) > 0
    
#     def create_table(self, table_name, schema):
#         """Create table with schema."""
#         columns = []
#         for col_name, col_type in schema.items():
#             columns.append(f"{col_name} {col_type}")
        
#         query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})"
#         return self.execute_query(query)
    
#     def get_columns(self, table_name):
#         """Get table columns for SQLite."""
#         query = f"PRAGMA table_info({table_name})"
#         result = self.execute_query(query, fetch=True)
#         return [row['name'] for row in result] if result else []
    
#     def close(self):
#         """Close interface - no persistent connections to close."""
#         pass

# class ThreadSafeInterface:
#     """Thread-safe wrapper for database interfaces."""
    
#     def __init__(self, original_interface):
#         self.original_interface = original_interface
        
#         # For SQLite, use our concurrent interface
#         if hasattr(original_interface, 'db_path'):
#             self._interface = SQLiteConcurrentInterface(original_interface.db_path)
#         else:
#             # For other databases, just use the original interface with locks
#             self._interface = original_interface
#             self._lock = threading.RLock()
    
#     def _execute_with_lock(self, method_name, *args, **kwargs):
#         """Execute method with proper locking."""
#         if hasattr(self, '_lock'):
#             with self._lock:
#                 method = getattr(self._interface, method_name)
#                 return method(*args, **kwargs)
#         else:
#             method = getattr(self._interface, method_name)
#             return method(*args, **kwargs)
    
#     def execute_query(self, query, params=None, fetch=True):
#         """Execute query with fetch parameter support."""
#         if hasattr(self, '_lock'):
#             with self._lock:
#                 # Handle fetch parameter for compatibility
#                 if hasattr(self._interface, 'execute_query'):
#                     try:
#                         # Try with fetch parameter first
#                         return self._interface.execute_query(query, params, fetch=fetch)
#                     except TypeError:
#                         # Fallback to basic execute_query if fetch not supported
#                         return self._interface.execute_query(query, params)
#                 else:
#                     return self._interface.execute_query(query, params)
#         else:
#             # Same logic for non-locking case
#             if hasattr(self._interface, 'execute_query'):
#                 try:
#                     return self._interface.execute_query(query, params, fetch=fetch)
#                 except TypeError:
#                     return self._interface.execute_query(query, params)
#             else:
#                 return self._interface.execute_query(query, params)
    
#     def get_columns(self, table_name):
#         """Get table columns - delegate to interface or provide fallback."""
#         if hasattr(self._interface, 'get_columns'):
#             return self._execute_with_lock('get_columns', table_name)
#         else:
#             # Fallback implementation for SQLite
#             query = f"PRAGMA table_info({table_name})"
#             result = self.execute_query(query, fetch=True)
#             return [row['name'] for row in result] if result else []
    
#     def table_exists(self, table_name):
#         return self._execute_with_lock('table_exists', table_name)
    
#     def create_table(self, table_name, schema):
#         return self._execute_with_lock('create_table', table_name, schema)
    
#     def close(self):
#         if hasattr(self._interface, 'close'):
#             self._interface.close()
    
#     def __getattr__(self, name):
#         """Delegate any other method calls to the wrapped interface."""
#         if hasattr(self._interface, name):
#             attr = getattr(self._interface, name)
#             if callable(attr):
#                 if hasattr(self, '_lock'):
#                     def wrapped_method(*args, **kwargs):
#                         with self._lock:
#                             return attr(*args, **kwargs)
#                     return wrapped_method
#                 else:
#                     return attr
#             else:
#                 return attr
#         else:
#             raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

# # Enhanced DB Manager with lock management
# class ConcurrentDBManager:
#     """Enhanced DB Manager with built-in concurrency and lock management."""
    
#     def __init__(self, interface, hash_columns=None, enable_wal_mode=True, thread_safe=True):
#         from .db_manager import DBManager
        
#         # Make interface thread-safe if needed
#         if thread_safe and hasattr(interface, 'db_path'):
#             # Create thread-safe wrapper using the original interface
#             self.interface = ThreadSafeInterface(interface)
#         else:
#             self.interface = interface
            
#         self.base_manager = DBManager(self.interface, hash_columns)
    
#     def __getattr__(self, name):
#         """Delegate to base manager for compatibility."""
#         return getattr(self.base_manager, name)
    
#     def concurrent_insert(self, table_name: str, data, skip_duplicates=True, 
#                          max_retries: int = 3):
#         """Insert with automatic retry on lock conflicts."""
#         import time
        
#         for attempt in range(max_retries):
#             try:
#                 result = self.base_manager.insert(table_name, data, skip_duplicates)
#                 return result  # Return immediately on success
#             except Exception as e:
#                 error_msg = str(e).lower()
#                 if ("database is locked" in error_msg or 
#                     "busy" in error_msg) and attempt < max_retries - 1:
#                     # Exponential backoff
#                     delay = BASE_RETRY_DELAY * (2 ** attempt)
#                     print(f"Retry {attempt + 1}/{max_retries} after {delay}s due to: {e}")
#                     time.sleep(delay)
#                     continue
#                 else:
#                     # Re-raise any other exception or if we've exhausted retries
#                     raise e
        
#         return False
    
#     def batch_insert(self, table_name: str, data_list: list, batch_size: int = 100,
#                     skip_duplicates: bool = True):
#         """Batch insert with optimized locking."""
#         results = []
        
#         # Process in batches to avoid long-running transactions
#         for i in range(0, len(data_list), batch_size):
#             batch = data_list[i:i + batch_size]
            
#             batch_results = []
#             for data in batch:
#                 try:
#                     result = self.concurrent_insert(table_name, data, skip_duplicates)
#                     batch_results.append(result)
#                 except Exception as e:
#                     if skip_duplicates and "unique constraint" in str(e).lower():
#                         batch_results.append("duplicate")
#                     else:
#                         batch_results.append(False)
            
#             results.extend(batch_results)
        
#         return results
    
#     def concurrent_select(self, table_name: str, **kwargs):
#         """Read-optimized select operation."""
#         max_retries = 3
#         for attempt in range(max_retries):
#             try:
#                 return self.base_manager.select(table_name, **kwargs)
#             except Exception as e:
#                 if ("database is locked" in str(e).lower() or 
#                     "busy" in str(e).lower()) and attempt < max_retries - 1:
#                     # Short delay for reads
#                     time.sleep(0.1 * (attempt + 1))
#                     continue
#                 raise
        
#         return []
    
#     def safe_create_table(self, table_name: str, schema: dict, **kwargs):
#         """Create table with extended timeout for schema operations."""
#         max_retries = 5
#         for attempt in range(max_retries):
#             try:
#                 return self.base_manager.create_table(table_name, schema, **kwargs)
#             except Exception as e:
#                 if ("database is locked" in str(e).lower() or 
#                     "busy" in str(e).lower()) and attempt < max_retries - 1:
#                     # Longer delay for schema operations
#                     time.sleep(0.5 * (attempt + 1))
#                     continue
#                 raise
        
#         return False
