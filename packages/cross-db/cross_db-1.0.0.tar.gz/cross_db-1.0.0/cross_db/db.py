from typing import Any, Dict, List, Optional, Tuple, Union
from google.cloud.sql.connector import Connector
from contextlib import contextmanager
from aiohttp import (
    ServerDisconnectedError,
    ConnectionTimeoutError,
    ClientConnectorError,
    ClientResponseError,
    ClientOSError,
)

import pandas as pd
import logging
import random
import time
import os


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseDB:
    """
    Wrapper class for connecting to a PostgreSQL database using the pg8000 driver with
    automatic reconnection and exponential backoff.

    Args:
        config (dict): Configuration parameters for the database connection.
            Required keys: host, user, password, database
            Optional keys: app_name, max_retries, base_delay, max_delay, jitter
            If config is not provided, environment variables are used.

    Methods:
    --------
    - `select(query, params = None)` : Execute a SQL query and return the results as a pandas DataFrame
    - `execute(query, params = None)` : Execute a single non-SELECT query (INSERT, UPDATE, DELETE)
    - `execute_many(query, params = None)` : Execute a query with multiple parameter sets (bulk operations)
    """

    CONNECTION_ERRORS = [
        # Generic connection errors
        ConnectionError,
        OSError,
        TimeoutError,
        # Google Connector errors
        ServerDisconnectedError,
        ConnectionTimeoutError,
        ClientConnectorError,
        ClientResponseError,
        ClientOSError,
        RuntimeError,
    ]

    CONNECTION_ERROR_PATTERNS = [
        "connection",
        "network",
        "timeout",
        "broken pipe",
        "connection reset",
        "connection refused",
        "connection lost",
        "connection closed",
        "connection aborted",
        "host is down",
        "no route to host",
        "unreachable",
        "ssl connection has been closed unexpectedly",
        "server closed the connection unexpectedly",
        "connection to server",
        "could not connect",
        "connection failed",
        "server disconnected",
        "cannot schedule new futures",
        "connection timeout",
        "cannot connect to host",
    ]

    def __init__(self, config: dict = None):
        if config is None:
            config = {
                "host": os.environ["CLOUDSQL_HOST"],
                "driver": "pg8000",
                "user": os.environ["CLOUDSQL_USER"],
                "password": os.environ["CLOUDSQL_PASSWORD"],
                "database": os.environ["CLOUDSQL_DATABASE"],
                "app_name": None,
            }
            # Validate required environment variables
            missing_vars = [
                k
                for k, v in config.items()
                if k in ["host", "user", "password", "database"] and v is None
            ]
            if missing_vars:
                raise ValueError(
                    f"Missing required environment variables: {', '.join([f'CLOUDSQL_{var.upper()}' for var in missing_vars])}"
                )

        self.config = config

        # Exponential backoff configuration
        self.max_retries = config.get("max_retries", 5)
        self.base_delay = config.get("base_delay", 1.0)  # Base delay in seconds
        self.max_delay = config.get("max_delay", 60.0)  # Maximum delay in seconds
        self.jitter = config.get("jitter", True)

        self.connector = Connector()
        self.connection = None
        self.cursor = None

    def __enter__(self):
        """Context manager entry point."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit point."""
        self.close()

    def _is_connection_error(self, error: Exception) -> bool:
        """
        Determine if an error is a connection-related error that should trigger reconnection.

        Args:
            error: The exception to check

        Returns:
            bool: True if the error indicates a connection problem
        """
        error_message = str(error).lower()

        connection_error_pattern_match = any(
            pattern in error_message for pattern in self.CONNECTION_ERROR_PATTERNS
        )

        connection_error_instance_match = any(
            isinstance(error, error_type) for error_type in self.CONNECTION_ERRORS
        )

        return connection_error_instance_match or connection_error_pattern_match

    def _calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay for exponential backoff.

        Args:
            attempt: Current attempt number (0-based)

        Returns:
            float: Delay in seconds
        """
        # Exponential backoff: base_delay * (2 ^ attempt)
        delay = self.base_delay * (2**attempt)

        # Cap at max_delay
        delay = min(delay, self.max_delay)

        # Add jitter to prevent thundering herd problem
        if self.jitter:
            jitter_range = delay * 0.1  # 10% jitter
            delay += random.uniform(-jitter_range, jitter_range)

        return max(0, delay)

    def connect(self):
        """Establish a database connection with exponential backoff retry."""
        for attempt in range(self.max_retries + 1):
            try:
                logger.info(
                    f"Attempting to connect to database (attempt {attempt + 1}/{self.max_retries + 1})"
                )

                self.connection = self.connector.connect(
                    self.config.get("host"),
                    "pg8000",
                    user=self.config.get("user"),
                    password=self.config.get("password"),
                    db=self.config.get("database"),
                )
                self.cursor = self.connection.cursor()

                logger.info("Database connection established successfully")
                return

            except Exception as e:
                logger.error(f"Connection attempt {attempt + 1} failed: {e}")

                if attempt == self.max_retries:
                    logger.error(
                        f"All {self.max_retries + 1} connection attempts failed"
                    )
                    raise ConnectionError(
                        f"Failed to connect to database after {self.max_retries + 1} attempts: {e}"
                    )

                delay = self._calculate_delay(attempt)
                logger.info(f"Retrying connection in {delay:.2f} seconds...")
                time.sleep(delay)

    @contextmanager
    def _handle_connection_errors(self, operation_name: str):
        """
        Context manager to handle connection errors and retry operations.

        Args:
            operation_name: Name of the operation for logging purposes
        """
        for attempt in range(self.max_retries + 1):
            try:
                yield
                return  # Success, exit the retry loop

            except Exception as e:
                if self._is_connection_error(e):
                    logger.warning(
                        f"{operation_name} failed due to connection error (attempt {attempt + 1}/{self.max_retries + 1}): {e}"
                    )

                    if attempt == self.max_retries:
                        logger.error(
                            f"All {self.max_retries + 1} attempts for {operation_name} failed"
                        )
                        raise ConnectionError(
                            f"Operation '{operation_name}' failed after {self.max_retries + 1} attempts: {e}"
                        )

                    # Try to reconnect
                    try:
                        self.close()
                        delay = self._calculate_delay(attempt)
                        logger.info(f"Reconnecting in {delay:.2f} seconds...")
                        time.sleep(delay)
                        self.connect()
                    except Exception as reconnect_error:
                        logger.error(f"Reconnection failed: {reconnect_error}")
                        if attempt == self.max_retries:
                            raise ConnectionError(
                                f"Failed to reconnect: {reconnect_error}"
                            )
                else:
                    # Non-connection error, don't retry
                    logger.error(
                        f"{operation_name} failed with non-connection error: {e}"
                    )
                    raise

    def close(self):
        """Close the database connection and cursor."""
        try:
            if self.cursor:
                self.cursor.close()
                self.cursor = None
        except Exception as e:
            logger.warning(f"Error closing cursor: {e}")

        try:
            if self.connection:
                self.connection.close()
                self.connection = None
        except Exception as e:
            logger.warning(f"Error closing connection: {e}")

    def select(
        self,
        query: str,
        params: Optional[Union[Dict[str, Any], Tuple, List[Any]]] = None,
    ) -> pd.DataFrame:
        """Execute a SQL query and return the results as a pandas DataFrame.

        Args:
            query (str): SQL query to execute
            params: Parameters for the query

        Returns:
            pandas.DataFrame: Query results as a DataFrame

        Example:
        ```
        # Basic SELECT
        with BaseDB() as db:
            df = db.select("SELECT * FROM violations LIMIT 10")

        # SELECT with parameters
        with BaseDB() as db:
            df = db.select("SELECT * FROM violations WHERE severity > %s", (3,))
        ```
        """
        with self._handle_connection_errors("SELECT query"):
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)

            columns = [desc[0] for desc in self.cursor.description]
            results = self.cursor.fetchall()
            return pd.DataFrame(results, columns=columns)

    def execute(
        self,
        query: str,
        params: Optional[Union[Dict[str, Any], Tuple, List[Any]]] = None,
    ) -> int:
        """Execute a single non-SELECT query (INSERT, UPDATE, DELETE).

        Args:
            query: SQL query to execute
            params: Parameters for the query

        Returns:
            int: Number of affected rows

        Example:
        ```
        # INSERT single row
        with BaseDB() as db:
            db.execute(
                "INSERT INTO violations (id, name, severity) VALUES (%(id)s, %(name)s, %(severity)s)",
                {"id": 1, "name": "Test Violation", "severity": 3}
            )
        ```
        """
        with self._handle_connection_errors("EXECUTE query"):
            try:
                if params is None:
                    self.cursor.execute(query)
                else:
                    self.cursor.execute(query, params)

                affected_rows = self.cursor.rowcount
                self.connection.commit()
                return affected_rows

            except Exception as e:
                logger.error(f"Error executing query: {e}")
                if self.connection:
                    try:
                        self.connection.rollback()
                    except Exception as rollback_error:
                        logger.warning(f"Error during rollback: {rollback_error}")
                raise

    def execute_many(
        self,
        query: str,
        params_list: List[Dict[str, Any]],
    ) -> int:
        """Execute a query with multiple parameter sets (bulk operations).

        Args:
            query: SQL query to execute
            params_list: List of parameter dictionaries

        Returns:
            int: Number of affected rows

        Example:
        ```
        # Bulk INSERT
        violations = [
            {"id": i, "name": f"Violation {i}", "severity": i % 5}
            for i in range(1, 11)
        ]
        with BaseDB() as db:
            db.execute_many(
                "INSERT INTO violations (id, name, severity) VALUES (%(id)s, %(name)s, %(severity)s)",
                violations
            )
        """
        if not params_list:
            return 0

        with self._handle_connection_errors("EXECUTE_MANY query"):
            try:
                self.cursor.executemany(query, params_list)
                affected_rows = self.cursor.rowcount
                self.connection.commit()
                return affected_rows

            except Exception as e:
                logger.error(f"Error executing bulk query: {e}")
                if self.connection:
                    try:
                        self.connection.rollback()
                    except Exception as rollback_error:
                        logger.warning(f"Error during rollback: {rollback_error}")
                raise
