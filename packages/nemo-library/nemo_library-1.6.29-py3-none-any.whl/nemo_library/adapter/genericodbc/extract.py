from __future__ import annotations

from typing import Optional, Iterable, List, Any

import pyodbc
from prefect import get_run_logger
from nemo_library.core import NemoLibrary
from nemo_library.adapter.utils.structures import ETLAdapter, ETLStep, ETLBaseObjectType
from nemo_library.adapter.utils.file_handler import ETLFileHandler

class GenericODBCExtract:
    """
    ODBC-only extractor using pyodbc.
    Supports:
      - Full ODBC connection string OR DSN-based connection string
      - Streaming fetch with fetchmany(chunksize)
      - Writing via ETLFileHandler as JSON array or JSON Lines (optionally gzip)
    """

    def __init__(self, odbc_connstr: str, timeout: int = 300):
        nl = NemoLibrary()
        self.config = nl.config
        self.logger = get_run_logger()
        self.file_handler = ETLFileHandler()

        self.odbc_connstr = odbc_connstr
        self.timeout = timeout
        super().__init__()

    # ---------- helpers ----------

    @staticmethod
    def _decode(value: Any) -> Any:
        """Convert values to JSON-serializable types; decode bytes if necessary."""
        if isinstance(value, (bytes, bytearray, memoryview)):
            b = bytes(value)
            try:
                return b.decode("utf-8")
            except UnicodeDecodeError:
                # fallback typical Windows codepage; keep lossy to avoid crashes
                return b.decode("cp1252", errors="ignore")
        return value

    @staticmethod
    def _rows_to_dicts(columns: List[str], rows: Iterable[tuple]) -> list[dict]:
        out: list[dict] = []
        for r in rows:
            # pyodbc.Row is tuple-like
            out.append(
                {col: GenericODBCExtract._decode(r[i]) for i, col in enumerate(columns)}
            )
        return out

    # ---------- public API ----------

    def extract(
        self,
        query: str,
        *,
        adapter: ETLAdapter = ETLAdapter.GENERICODBC,
        step: ETLStep = ETLStep.EXTRACT,
        entity: ETLBaseObjectType | None = None,
        filename: str | None = None,
        chunksize: Optional[int] = None,
        jsonl: bool = False,
        gzip_enabled: bool = False,
    ) -> None:
        log = self.logger
        fh = self.file_handler
        log.info("Starting extraction (ODBC) ...")

        conn: Optional[pyodbc.Connection] = None
        cur: Optional[pyodbc.Cursor] = None

        try:
            # Connect
            log.info("Connecting via ODBC ...")
            conn = pyodbc.connect(self.odbc_connstr, timeout=self.timeout)
            cur = conn.cursor()
            if chunksize:
                cur.arraysize = chunksize  # hint for fetchmany

            log.info("Executing query ...")
            cur.execute(query)

            # Column names
            columns = [desc[0] for desc in cur.description]

            if chunksize:
                log.info(f"Streaming rows with chunksize={chunksize} ...")
                total = 0
                if jsonl:
                    while True:
                        rows = cur.fetchmany(chunksize)
                        if not rows:
                            break
                        recs = self._rows_to_dicts(columns, rows)
                        fh.writeJSONLines(
                            adapter=adapter,
                            step=step,
                            records=recs,
                            entity=entity,
                            filename=filename,
                            gzip_enabled=gzip_enabled,
                            append=True,
                        )
                        total += len(recs)
                    log.info(f"Completed (JSONL). Rows: {total}")
                else:
                    # valid JSON array streaming
                    with fh.streamJSONList(
                        adapter=adapter,
                        step=step,
                        entity=entity,
                        filename=filename,
                        gzip_enabled=gzip_enabled,
                    ) as writer:
                        total = 0
                        while True:
                            rows = cur.fetchmany(chunksize)
                            if not rows:
                                break
                            recs = self._rows_to_dicts(columns, rows)
                            writer.write_many(recs)
                            total += len(recs)
                    log.info(f"Completed (JSON array). Rows: {total}")
            else:
                # No streaming: fetch all (only for small/medium result sets)
                rows = cur.fetchall()
                recs = self._rows_to_dicts(columns, rows)
                if jsonl:
                    fh.writeJSONLines(
                        adapter=adapter,
                        step=step,
                        records=recs,
                        entity=entity,
                        filename=filename,
                        gzip_enabled=gzip_enabled,
                        append=False,
                    )
                else:
                    fh.writeJSON(
                        adapter=adapter,
                        step=step,
                        data=recs,
                        entity=entity,
                        filename=filename,
                    )
                log.info(f"Completed (non-streamed). Rows: {len(recs)}")

        except Exception as e:
            log.error(f"Unexpected error during ODBC extraction: {e}")
            raise
        finally:
            try:
                if cur is not None:
                    cur.close()
                if conn is not None:
                    conn.close()
                log.info("ODBC connection closed.")
            except Exception:
                pass
