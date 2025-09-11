from __future__ import annotations

import urllib.parse
from typing import Optional

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from prefect import get_run_logger
from nemo_library.core import NemoLibrary


class GenericSQLExtract:
    """
    Generic extractor that supports either:
      - A full SQLAlchemy connection string, or
      - Discrete parameters (engine/host/port/db/user/password) to build one.
    """

    def __init__(
        self,
        connection_string: Optional[str] = None,
        engine: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[str] = None,
        database: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        odbc_driver: Optional[str] = None,
        encrypt: Optional[str] = None,
        trust_server_certificate: Optional[str] = None,
    ):
        nl = NemoLibrary()
        self.config = nl.config  # keep for future use (e.g., default output dir)
        self.logger = get_run_logger()

        # Build connection string if not provided
        if connection_string:
            self.connection_string = connection_string
        else:
            self.connection_string = self._build_connection_string(
                engine=engine or "mssql+pyodbc",
                host=host or "",
                port=port,
                database=database or "",
                user=user or "",
                password=password or "",
                odbc_driver=odbc_driver or "ODBC Driver 18 for SQL Server",
                encrypt=encrypt or "yes",
                trust_server_certificate=trust_server_certificate or "no",
            )

        self._engine: Optional[Engine] = None

        super().__init__()

    # ---------- helpers ----------

    def _build_connection_string(
        self,
        engine: str,
        host: str,
        port: Optional[str],
        database: str,
        user: str,
        password: str,
        odbc_driver: Optional[str],
        encrypt: str,
        trust_server_certificate: str,
    ) -> str:
        """
        Build a SQLAlchemy connection string.

        Notes:
        - For mssql+pyodbc we need a URL-encoded ODBC driver in the query string.
        - For other engines (e.g., postgresql+psycopg2) we omit driver-specific params.
        """
        # URL-encode user & password to be safe with special chars
        user_enc = urllib.parse.quote_plus(user)
        pwd_enc = urllib.parse.quote_plus(password)

        if engine.startswith("mssql+pyodbc"):
            # Build query params
            params = {
                "driver": odbc_driver or "ODBC Driver 18 for SQL Server",
            }
            # Optional security params
            if encrypt in ("yes", "no"):
                params["Encrypt"] = "yes" if encrypt == "yes" else "no"
            if trust_server_certificate in ("yes", "no"):
                params["TrustServerCertificate"] = "yes" if trust_server_certificate == "yes" else "no"

            q = urllib.parse.urlencode(params, safe="+ ")
            # host[:port]
            hostport = f"{host}:{port}" if port else host
            return f"{engine}://{user_enc}:{pwd_enc}@{hostport}/{database}?{q}"

        # Default generic pattern: engine://user:pass@host:port/db
        hostport = f"{host}:{port}" if port else host
        return f"{engine}://{user_enc}:{pwd_enc}@{hostport}/{database}"

    def _get_engine(self) -> Engine:
        """Create and cache the SQLAlchemy engine."""
        if self._engine is None:
            # echo=False avoids printing SQL; pool_pre_ping improves reliability on long-lived connections
            self._engine = create_engine(self.connection_string, pool_pre_ping=True, future=True)
        return self._engine

    # ---------- public API ----------

    def extract(self, query: str, output: Optional[str] = None, chunksize: Optional[int] = None) -> None:
        """
        Execute the SQL query and optionally write results to CSV or Parquet.

        Args:
            query: The SQL query to execute.
            output: Optional path to write results (.csv or .parquet). If None, nothing is written.
            chunksize: If provided, stream results in chunks (useful for large datasets).
        """
        logger = self.logger
        logger.info("Starting extraction ...")

        try:
            engine = self._get_engine()
            logger.info("Connected using provided connection configuration (details hidden).")

            # Streamed read if chunksize is specified
            if chunksize:
                logger.info(f"Running query in streaming mode with chunksize={chunksize} ...")
                if output:
                    self._write_streaming(engine, query, output, chunksize)
                else:
                    # Count only, to avoid loading everything into memory
                    total_rows = self._count_rows_streaming(engine, query, chunksize)
                    logger.info(f"Query completed (streamed). Approx. rows: {total_rows}")
            else:
                logger.info("Running query ...")
                with engine.connect() as conn:
                    df = pd.read_sql_query(text(query), conn)
                logger.info(f"Query completed. Rows: {len(df)} Columns: {len(df.columns)}")

                if output:
                    self._write_dataframe(df, output)
                    logger.info(f"Result written to: {output}")

        except SQLAlchemyError as e:
            logger.error(f"Database error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise
        finally:
            # Dispose engine cleanly
            if self._engine is not None:
                self._engine.dispose()
                logger.info("Connection closed.")

    # ---------- IO helpers ----------

    def _write_dataframe(self, df: pd.DataFrame, output: str) -> None:
        """Write a DataFrame to CSV or Parquet based on file extension."""
        if output.lower().endswith(".csv"):
            df.to_csv(output, index=False)
        elif output.lower().endswith(".parquet"):
            df.to_parquet(output, index=False)
        else:
            raise ValueError("Unsupported output format. Use a path ending with .csv or .parquet")

    def _write_streaming(self, engine: Engine, query: str, output: str, chunksize: int) -> None:
        """
        Stream results and append to CSV/Parquet. For Parquet we buffer in memory by chunks
        and write at the end; for CSV we append incrementally.
        """
        if output.lower().endswith(".csv"):
            first = True
            with engine.connect() as conn:
                for chunk in pd.read_sql_query(text(query), conn, chunksize=chunksize):
                    chunk.to_csv(output, index=False, mode="w" if first else "a", header=first)
                    first = False
        elif output.lower().endswith(".parquet"):
            # Buffer chunks in memory; alternatively, write to a temporary dataset (pyarrow.dataset)
            dfs = []
            with engine.connect() as conn:
                for chunk in pd.read_sql_query(text(query), conn, chunksize=chunksize):
                    dfs.append(chunk)
            if dfs:
                pd.concat(dfs, ignore_index=True).to_parquet(output, index=False)
        else:
            raise ValueError("Unsupported output format for streaming. Use .csv or .parquet")

    def _count_rows_streaming(self, engine: Engine, query: str, chunksize: int) -> int:
        """Consume the stream to count rows without holding everything in memory."""
        total = 0
        with engine.connect() as conn:
            for chunk in pd.read_sql_query(text(query), conn, chunksize=chunksize):
                total += len(chunk)
        return total