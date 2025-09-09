import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from .exception import ConfigurationError, UnsupportedDatabaseError

load_dotenv()

class DBConfig:
    """
    Handles database connection configuration dynamically for various database types.
    
    Supported databases:
    - SQLite (file-based)
    - PostgreSQL
    - MySQL/MariaDB
    - SQL Server/Azure SQL
    - Oracle
    - Snowflake
    - Databricks
    - Redshift
    - DB2
    - Teradata
    """
    SUPPORTED_DATABASES = {
        "sqlite": {"default_port": None, "requires_server": False},
        "postgresql": {"default_port": "5432", "requires_server": True},
        "mysql": {"default_port": "3306", "requires_server": True},
        "mariadb": {"default_port": "3306", "requires_server": True},
        "sqlserver": {"default_port": "1433", "requires_server": True},
        "azure_sql": {"default_port": "1433", "requires_server": True},
        "oracle": {"default_port": "1521", "requires_server": True},
        "snowflake": {"default_port": "443", "requires_server": True},
        "databricks": {"default_port": "443", "requires_server": True},
        "redshift": {"default_port": "5439", "requires_server": True},
        "db2": {"default_port": "50000", "requires_server": True},
        "teradata": {"default_port": "1025", "requires_server": True},
    }

    def __init__(self, db_type: str, **kwargs):
        """
        Initialize database configuration.
        
        Args:
            db_type: Type of database (e.g., 'postgresql', 'mysql', 'sqlite')
            **kwargs: Additional configuration parameters
        """
        self.db_type = db_type.lower()
        
        if self.db_type not in self.SUPPORTED_DATABASES:
            raise UnsupportedDatabaseError(
                f"Database type '{db_type}' is not supported. "
                f"Supported types: {list(self.SUPPORTED_DATABASES.keys())}"
            )
        
        # Initialize configuration from environment or kwargs
        self._init_config(**kwargs)
        
        # Generate connection string
        self.conn_str = self._generate_conn_string()

    def _init_config(self, **kwargs):
        """Initialize configuration parameters."""
        # Database connection parameters
        self.database = self._get_config_value("DATABASE", **kwargs)
        self.user = self._get_config_value("USER", **kwargs)
        self.password = self._get_config_value("PASSWORD", **kwargs)
        self.host = self._get_config_value("HOST", "SERVER", **kwargs)
        self.port = self._get_config_value("PORT", **kwargs) or self._get_default_port()
        
        # Special parameters for specific databases
        if self.db_type == "snowflake":
            self.warehouse = self._get_config_value("WAREHOUSE", **kwargs)
            self.schema = self._get_config_value("SCHEMA", **kwargs)
            self.account = self._get_config_value("ACCOUNT", **kwargs)
            self.role = self._get_config_value("ROLE", **kwargs)
        
        # SQLite specific
        if self.db_type == "sqlite":
            self.db_path = kwargs.get("db_path") or self.database or "filetracker.db"
        
        # Validate required parameters
        self._validate_config()

    def _get_config_value(self, primary_key: str, secondary_key: str = None, **kwargs) -> Optional[str]:
        """Get configuration value from kwargs or environment variables."""
        # First check using kwargs
        if primary_key.lower() in kwargs:
            return kwargs[primary_key.lower()]
        if secondary_key and secondary_key.lower() in kwargs:
            return kwargs[secondary_key.lower()]
        
        # Then check using environment variables
        env_primary = f"{self.db_type.upper()}_{primary_key}"
    
        value = os.getenv(env_primary)
        if not value and secondary_key is not None:
            env_secondary = f"{self.db_type.upper()}_{secondary_key}"
            value = os.getenv(env_secondary)
            
        return value

    def _get_default_port(self) -> Optional[str]:
        """Get default port for the database type."""
        return self.SUPPORTED_DATABASES[self.db_type]["default_port"]

    def _validate_config(self):
        """Validate configuration parameters."""
        db_info = self.SUPPORTED_DATABASES[self.db_type]
        
        if self.db_type == "sqlite":
            if not self.db_path:
                raise ConfigurationError("SQLite database requires 'db_path' parameter")
        elif db_info["requires_server"]:
            if not self.host:
                raise ConfigurationError(f"{self.db_type} requires 'host' parameter")
            if not self.user:
                raise ConfigurationError(f"{self.db_type} requires 'user' parameter")
            if not self.password:
                raise ConfigurationError(f"{self.db_type} requires 'password' parameter")
            
            if self.db_type == "snowflake":
                if not self.account:
                    raise ConfigurationError("Snowflake requires 'account' parameter")

    def _generate_conn_string(self) -> str:
        """Generate connection string based on database type."""
        try:
            if self.db_type == "sqlite":
                return f"sqlite:///{self.db_path}"
                
            elif self.db_type in ["sqlserver", "azure_sql"]:
                driver = "ODBC+Driver+17+for+SQL+Server"
                return f"mssql+pyodbc://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}?driver={driver}"
                
            elif self.db_type == "oracle":
                return f"oracle+oracledb://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
                
            elif self.db_type == "postgresql":
                return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
                
            elif self.db_type in ["mysql", "mariadb"]:
                return f"mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
                
            elif self.db_type == "redshift":
                return f"postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
                
            elif self.db_type == "teradata":
                return f"teradatasql://{self.user}:{self.password}@{self.host}/DATABASE={self.database}"
                
            elif self.db_type == "db2":
                return f"ibm_db_sa://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
                
            elif self.db_type == "databricks":
                return f"databricks://token:{self.password}@{self.host}:443{self.database}"
                
            elif self.db_type == "snowflake":
                conn_str = f"snowflake://{self.user}:{self.password}@{self.account}"
                if self.database:
                    conn_str += f"/{self.database}"
                if self.schema:
                    conn_str += f"/{self.schema}"
                params = []
                if self.warehouse:
                    params.append(f"warehouse={self.warehouse}")
                if self.role:
                    params.append(f"role={self.role}")
                if params:
                    conn_str += "?" + "&".join(params)
                return conn_str
                
            else:
                raise UnsupportedDatabaseError(f"Connection string generation not implemented for {self.db_type}")
                
        except Exception as e:
            raise ConfigurationError(f"Failed to generate connection string: {e}") from e

    def get_db_config(self) -> Dict[str, Any]:
        """
        Get database configuration as a dictionary.
        
        Returns:
            Dictionary containing database configuration
        """
        config = {
            "db_type": self.db_type,
            "connection_string": self.conn_str,
        }
        
        # Add type-specific configuration
        if self.db_type == "sqlite":
            config["db_path"] = self.db_path
        else:
            config.update({
                "host": self.host,
                "port": self.port,
                "user": self.user,
                "database": self.database,
            })
            
            if self.db_type == "snowflake":
                config.update({
                    "account": self.account,
                    "warehouse": self.warehouse,
                    "schema": self.schema,
                    "role": self.role,
                })
        
        return config

    @classmethod
    def from_env(cls, db_type: str) -> 'DBConfig':
        """
        Create DBConfig instance from environment variables.
        
        Args:
            db_type: Type of database
            
        Returns:
            DBConfig instance
        """
        return cls(db_type)

    @classmethod
    def get_supported_databases(cls) -> Dict[str, Dict[str, Any]]:
        """Get information about supported databases."""
        return cls.SUPPORTED_DATABASES.copy()
