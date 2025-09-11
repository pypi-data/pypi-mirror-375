from __future__ import annotations

import urllib.parse
from typing import Optional

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from prefect import get_run_logger
from nemo_library.adapter.genericsql.generic_sql_object_type import GenericSQLObjectType
from nemo_library.adapter.utils.file_handler import ETLFileHandler
from nemo_library.core import NemoLibrary
from nemo_library.adapter.utils.structures import ETLAdapter, ETLStep, ETLBaseObjectType


class GenericSQLExtract:
    """
    Generic extractor that supports either:
      - A full SQLAlchemy connection string, or
      - Discrete parameters (engine/host/port/db/user/password) to build one.

    Writes results using ETLFileHandler (JSON / streaming).
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
        self.config = nl.config
        self.logger = get_run_logger()
        self.file_handler = ETLFileHandler()

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

    # ---------- connection helpers ----------

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
        user_enc = urllib.parse.quote_plus(user)
        pwd_enc = urllib.parse.quote_plus(password)

        if engine.startswith("mssql+pyodbc"):
            params = {"driver": odbc_driver or "ODBC Driver 18 for SQL Server"}
            if encrypt in ("yes", "no"):
                params["Encrypt"] = "yes" if encrypt == "yes" else "no"
            if trust_server_certificate in ("yes", "no"):
                params["TrustServerCertificate"] = "yes" if trust_server_certificate == "yes" else "no"
            q = urllib.parse.urlencode(params, safe="+ ")
            hostport = f"{host}:{port}" if port else host
            return f"{engine}://{user_enc}:{pwd_enc}@{hostport}/{database}?{q}"

        hostport = f"{host}:{port}" if port else host
        return f"{engine}://{user_enc}:{pwd_enc}@{hostport}/{database}"

    def _get_engine(self) -> Engine:
        if self._engine is None:
            self._engine = create_engine(self.connection_string, pool_pre_ping=True, future=True)
        return self._engine

    # ---------- public API ----------

    def extract(
        self,
        query: str,
        *,
        # Where/How to write:
        adapter: ETLAdapter = ETLAdapter.GENERICSQL,
        step: ETLStep = ETLStep.EXTRACT,
        entity: ETLBaseObjectType = GenericSQLObjectType.GENERIC,
        filename: str | None = None,
        # Behavior:
        chunksize: Optional[int] = None,
        jsonl: bool = False,
        gzip_enabled: bool = False,
    ) -> None:
        """
        Execute the SQL query and write results via ETLFileHandler as JSON.

        Args:
            query: SQL query to execute.
            adapter, step, entity, filename: define the ETL file target.
                - If filename is None: uses entity.filename if provided, else 'result'.
            chunksize: stream results in chunks if provided.
            jsonl: if True, write JSON Lines (.jsonl or .jsonl.gz). If False:
                   write a valid JSON array (.json or .json.gz). For large data,
                   JSON Lines is generally recommended.
            gzip_enabled: compress the output (.gz).
        """
        log = self.logger
        fh = self.file_handler
        log.info("Starting extraction ...")

        try:
            engine = self._get_engine()
            log.info("Connected using provided connection configuration (details hidden).")

            if chunksize:
                log.info(f"Running query in streaming mode with chunksize={chunksize} ...")

                if jsonl:
                    # Stream as NDJSON
                    written = 0
                    with engine.connect() as conn:
                        for chunk in pd.read_sql_query(text(query), conn, chunksize=chunksize):
                            recs = chunk.to_dict(orient="records")
                            fh.writeJSONLines(
                                adapter=adapter,
                                step=step,
                                records=recs,
                                entity=entity,
                                filename=filename,
                                gzip_enabled=gzip_enabled,
                                append=True,  # append chunks
                            )
                            written += len(recs)
                    log.info(f"Query completed (streamed JSONL). Rows: {written}")
                else:
                    # Stream as valid JSON array
                    with fh.streamJSONList(
                        adapter=adapter,
                        step=step,
                        entity=entity,
                        filename=filename,
                        gzip_enabled=gzip_enabled,
                    ) as writer, engine.connect() as conn:
                        total = 0
                        for chunk in pd.read_sql_query(text(query), conn, chunksize=chunksize):
                            recs = chunk.to_dict(orient="records")
                            writer.write_many(recs)
                            total += len(recs)
                    log.info(f"Query completed (streamed JSON array). Rows: {total}")

            else:
                # Non-streaming: load to memory and write once
                log.info("Running query ...")
                with engine.connect() as conn:
                    df = pd.read_sql_query(text(query), conn)
                log.info(f"Query completed. Rows: {len(df)} Columns: {len(df.columns)}")

                data = df.to_dict(orient="records")
                if jsonl:
                    # write one-shot as NDJSON
                    fh.writeJSONLines(
                        adapter=adapter,
                        step=step,
                        records=data,
                        entity=entity,
                        filename=filename,
                        gzip_enabled=gzip_enabled,
                        append=False,
                    )
                else:
                    # classic pretty JSON array
                    fh.writeJSON(
                        adapter=adapter,
                        step=step,
                        data=data,
                        entity=entity,
                        filename=filename,
                    )

        except SQLAlchemyError as e:
            log.error(f"Database error: {e}")
            raise
        except Exception as e:
            log.error(f"Unexpected error: {e}")
            raise
        finally:
            if self._engine is not None:
                self._engine.dispose()
                log.info("Connection closed.")