"""
PostgreSQL database handler for easy connection management and queries.

This module provides a simple interface for connecting to PostgreSQL databases
and executing queries using SQLAlchemy.

Required dependencies:
    pip install qufe[database]

This installs: sqlalchemy>=1.3.0, python-dotenv>=0.15.0
"""

import os
from typing import List, Dict, Optional


# Lazy imports for external dependencies
def _import_sqlalchemy():
    """Lazy import SQLAlchemy with helpful error message."""
    try:
        from sqlalchemy import create_engine, text
        from sqlalchemy.engine import Engine
        return create_engine, text, Engine
    except ImportError as e:
        raise ImportError(
            "Database functionality requires SQLAlchemy. "
            "Install with: pip install qufe[database]"
        ) from e


def _import_dotenv():
    """Lazy import python-dotenv with graceful fallback."""
    try:
        from dotenv import load_dotenv
        return load_dotenv
    except ImportError:
        # Graceful degradation: continue without dotenv support
        return None


def help():
    """
    Display help information for database handler functionality.

    Shows installation instructions, usage examples, and configuration options.
    """
    print("qufe.dbhandler - PostgreSQL Database Handler")
    print("=" * 45)
    print()

    try:
        _import_sqlalchemy()
        print("✓ Dependencies: INSTALLED")
    except ImportError:
        print("✗ Dependencies: MISSING")
        print("  Install with: pip install qufe[database]")
        print("  This installs: sqlalchemy>=1.3.0, python-dotenv>=0.15.0")
        print()
        return

    print()
    print("FEATURES:")
    print("  • PostgreSQL connection management with SQLAlchemy")
    print("  • Automatic environment variable loading (.env support)")
    print("  • Database and table exploration utilities")
    print("  • Connection pooling and cleanup")
    print()

    print("CONFIGURATION OPTIONS:")
    print("  1. .env file (recommended):")
    print("     POSTGRES_USER=username")
    print("     POSTGRES_PASSWORD=password")
    print("     POSTGRES_HOST=localhost")
    print("     POSTGRES_PORT=5432")
    print("     POSTGRES_DB=database_name")
    print()

    print("  2. Environment variables:")
    print("     export POSTGRES_USER=username")
    print("     # ... other variables")
    print()

    print("  3. Direct parameters:")
    print("     db = PostgreSQLHandler(user='...', password='...')")
    print()

    print("USAGE EXAMPLE:")
    print("  from qufe.dbhandler import PostgreSQLHandler")
    print("  db = PostgreSQLHandler()  # Uses .env or environment variables")
    print("  databases = db.get_database_list()")
    print("  tables = db.get_table_list()")
    print("  results = db.execute_query('SELECT * FROM users LIMIT 5')")


class PostgreSQLHandler:
    """
    PostgreSQL connection handler with automatic environment variable support.

    This class provides a convenient interface for connecting to PostgreSQL databases
    and executing queries. It supports environment variables for configuration
    and uses SQLAlchemy for connection management.

    Environment variables are loaded from a .env file if available, or from system
    environment variables as fallback.
    """

    def __init__(
            self,
            db_name: Optional[str] = None,
            user: Optional[str] = None,
            password: Optional[str] = None,
            host: Optional[str] = None,
            port: Optional[int] = None):
        """
        Initialize PostgreSQL connection handler.

        Args:
            db_name: Database name (defaults to POSTGRES_DB env var or 'postgres')
            user: Username (defaults to POSTGRES_USER env var)
            password: Password (defaults to POSTGRES_PASSWORD env var)
            host: Host address (defaults to POSTGRES_HOST env var or 'localhost')
            port: Port number (defaults to POSTGRES_PORT env var or 5432)

        Raises:
            ImportError: If required dependencies are not installed
            ValueError: If username or password is not provided
        """
        # Import required dependencies
        self._create_engine, self._text, self._Engine = _import_sqlalchemy()

        # Try to load .env file if dotenv is available
        load_dotenv = _import_dotenv()
        if load_dotenv:
            load_dotenv()

        # Set connection parameters with environment variable fallback
        self.user = user or os.getenv('POSTGRES_USER')
        self.password = password or os.getenv('POSTGRES_PASSWORD')
        self.host = host or os.getenv('POSTGRES_HOST', 'localhost')
        self.port = port or int(os.getenv('POSTGRES_PORT', '5432'))
        self.database = db_name or os.getenv('POSTGRES_DB', 'postgres')

        if not self.user or not self.password:
            raise ValueError(
                "Database username and password are required. "
                "Please set POSTGRES_USER and POSTGRES_PASSWORD environment variables "
                "in a .env file or provide them as parameters."
            )

        # Create database connection URL
        url = f"postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
        self.engine = self._create_engine(url, echo=False, future=True)

    def get_connection_url(self, db_name: Optional[str] = None) -> str:
        """
        Get the connection URL for the database.

        Args:
            db_name: Specific database name (optional)

        Returns:
            PostgreSQL connection URL string
        """
        database = db_name or self.database
        return f"postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{database}"

    def reset_connection(self) -> None:
        """
        Reset the database connection by disposing the connection pool.

        This method cleans up the connection pool, which can be useful
        when connections become stale or need to be refreshed.
        """
        self.engine.dispose()

    def execute_query(self, sql: str) -> List:
        """
        Execute a SQL query and return all results.

        Args:
            sql: SQL query string to execute

        Returns:
            List of query results

        Example:
            >>> handler = PostgreSQLHandler()
            >>> results = handler.execute_query("SELECT * FROM users LIMIT 5")
        """
        with self.engine.connect() as conn:
            return conn.execute(self._text(sql)).fetchall()

    def get_database_list(self, print_result: bool = False) -> List[str]:
        """
        Get list of all databases in the PostgreSQL server.

        Args:
            print_result: Whether to print the database list to console

        Returns:
            List of database names

        Example:
            >>> handler = PostgreSQLHandler()
            >>> databases = handler.get_database_list(print_result=True)
        """
        sql = """
            SELECT datname
            FROM pg_database
            WHERE datistemplate = false;
        """
        result = self.execute_query(sql)
        database_names = [row.datname for row in result]

        if print_result:
            print("Available databases on the server:")
            for db_name in database_names:
                print(f" - {db_name}")

        return database_names

    def get_table_list(self, print_result: bool = False) -> List[Dict[str, str]]:
        """
        Get list of all tables and views in the current database.

        Args:
            print_result: Whether to print the table list to console

        Returns:
            List of dictionaries containing table information with keys:
            - catalog: Table catalog name
            - schema: Schema name
            - name: Table/view name
            - type: Table type (BASE TABLE, VIEW, etc.)

        Example:
            >>> handler = PostgreSQLHandler()
            >>> tables = handler.get_table_list(print_result=True)
        """
        sql = """
            SELECT table_catalog,
                   table_schema,
                   table_name,
                   table_type
            FROM information_schema.tables
            ORDER BY table_schema, table_name;
        """
        result = self.execute_query(sql)

        tables = [
            {
                'catalog': row.table_catalog,
                'schema': row.table_schema,
                'name': row.table_name,
                'type': row.table_type
            } for row in result
        ]

        if print_result:
            print(f"\n=== Database: {self.database} - Tables and Views ===")
            for table in tables:
                print(f" - {table['schema']}.{table['name']} ({table['type']})")

        return tables
