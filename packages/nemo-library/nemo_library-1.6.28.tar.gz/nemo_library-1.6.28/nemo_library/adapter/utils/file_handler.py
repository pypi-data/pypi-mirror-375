from datetime import date, datetime
from enum import Enum
import io
import json
import logging
import gzip
from pathlib import Path
from contextlib import contextmanager
from typing import Iterable, Iterator, Any, Optional

try:
    from prefect import get_run_logger  # type: ignore
    _PREFECT_AVAILABLE = True
except Exception:
    _PREFECT_AVAILABLE = False

from nemo_library.adapter.utils.structures import ETLAdapter, ETLBaseObjectType, ETLStep
from nemo_library.core import NemoLibrary
import pandas as pd


class ETLFileHandler:
    """
    Base class for handling ETL file operations, including JSON and streaming JSON.
    """

    def __init__(self):
        nl = NemoLibrary()
        self.config = nl.config
        self.logger = self._init_logger()
        super().__init__()

    def _init_logger(self) -> logging.Logger:
        if _PREFECT_AVAILABLE:
            try:
                plogger = get_run_logger()
                plogger.info("Using Prefect run logger.")
                return plogger  # type: ignore[return-value]
            except Exception:
                pass

        logger_name = "nemo.etl"
        logger = logging.getLogger(logger_name)
        if not logger.handlers:
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s %(levelname)s %(name)s: %(message)s",
            )
        logger.info("Using standard Python logger (no active Prefect context detected).")
        return logger

    # ---------- path helpers ----------

    def _output_path(
        self,
        adapter: ETLAdapter,
        step: ETLStep,
        entity: Optional[ETLBaseObjectType],
        filename: Optional[str],
        suffix: str,
    ) -> Path:
        """
        Build the path in the ETL directory structure and ensure parent exists.
        """
        etl_dir = self.config.get_etl_directory()
        name = filename if filename else (entity.filename if entity else "result")
        p = Path(etl_dir) / f"{adapter.value}" / f"{step.value}" / f"{name}{suffix}"
        p.parent.mkdir(parents=True, exist_ok=True)
        return p

    # ---------- (de)serialization helpers ----------

    def _json_default(self, o):
        if hasattr(o, "to_dict") and callable(o.to_dict):
            return o.to_dict()
        if isinstance(o, (datetime, date)):
            return o.isoformat()
        if isinstance(o, Enum):
            return o.value
        return str(o)

    # ---------- classic read/write ----------

    def readJSON(
        self,
        adapter: ETLAdapter,
        step: ETLStep,
        entity: ETLBaseObjectType | None,
        filename: str | None = None,
        label: str | None = None,
        ignore_nonexistent: bool = False,
    ) -> dict:
        file_path = self._output_path(adapter, step, entity, filename, ".json")
        if not file_path.exists():
            if ignore_nonexistent:
                self.logger.warning(
                    f"File {file_path} does not exist. Returning empty data for entity {entity.label if entity else label}."
                )
                return {}
            else:
                raise FileNotFoundError(f"File {file_path} does not exist.")
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        if not data:
            self.logger.warning(
                f"No data found in file {file_path} for entity {entity.label if entity else label}."
            )
            return {}
        return data

    def writeJSON(
        self,
        adapter: ETLAdapter,
        step: ETLStep,
        data: dict | list[dict],
        entity: ETLBaseObjectType | None,
        filename: str | None = None,
        label: str | None = None,
    ) -> None:
        """
        Write a dictionary or list of dictionaries as a single JSON document.
        """
        if not data:
            self.logger.warning(
                f"No data to write for entity {entity.label if entity else label}. Skipping file write."
            )
            return

        file_path = self._output_path(adapter, step, entity, filename, ".json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False, default=self._json_default)

        length_info = ""
        try:
            length_info = f"{format(len(data), ',')} records" if hasattr(data, "__len__") else "Data"
        except Exception:
            length_info = "Data"

        self.logger.info(
            f"{length_info} written to {file_path} for entity {entity.label if entity else label}."
        )

    # ---------- streaming (JSON Lines) ----------

    def writeJSONLines(
        self,
        adapter: ETLAdapter,
        step: ETLStep,
        records: Iterable[dict],
        entity: ETLBaseObjectType | None,
        filename: str | None = None,
        label: str | None = None,
        append: bool = False,
        gzip_enabled: bool = False,
    ) -> Path:
        """
        Write records as JSON Lines (NDJSON). Each record is one JSON object per line.
        Good fit for streaming large result sets.

        If gzip_enabled=True, file will be written as .jsonl.gz
        """
        suffix = ".jsonl.gz" if gzip_enabled else ".jsonl"
        path = self._output_path(adapter, step, entity, filename, suffix)

        if gzip_enabled:
            opener = lambda: gzip.open(path, "ab" if append else "wb")
        else:
            opener = lambda: open(path, "a" if append else "w", encoding="utf-8")

        count = 0
        with opener() as f:
            for rec in records:
                line = json.dumps(rec, ensure_ascii=False, default=self._json_default)
                if gzip_enabled:
                    f.write((line + "\n").encode("utf-8"))
                else:
                    f.write(line + "\n")
                count += 1

        self.logger.info(
            f"{format(count, ',')} records written to {path} (JSON Lines){' [append]' if append else ''}."
        )
        return path

    # ---------- streaming (valid JSON array) ----------

    @contextmanager
    def streamJSONList(
        self,
        adapter: ETLAdapter,
        step: ETLStep,
        entity: ETLBaseObjectType | None,
        filename: str | None = None,
        label: str | None = None,
        gzip_enabled: bool = False,
    ):
        """
        Context manager that writes a *valid JSON array* incrementally:
        opens '[', streams items separated by ',', then closes ']'.
        If gzip_enabled=True, file will be .json.gz.
        Usage:
            with fh.streamJSONList(adapter, step, entity, filename) as writer:
                writer.write_many([{"a":1}, {"a":2}])
                writer.write_one({"a":3})
        """
        suffix = ".json.gz" if gzip_enabled else ".json"
        path = self._output_path(adapter, step, entity, filename, suffix)

        if gzip_enabled:
            f = gzip.open(path, "wb")
            write_raw = lambda s: f.write(s.encode("utf-8"))
        else:
            f = open(path, "w", encoding="utf-8")
            write_raw = lambda s: f.write(s)

        first = True

        class _Writer:
            def write_one(self_inner, rec: dict):
                nonlocal first
                if first:
                    write_raw("[")
                    first = False
                else:
                    write_raw(",\n")
                write_raw(json.dumps(rec, ensure_ascii=False, default=self._json_default))

            def write_many(self_inner, recs: Iterable[dict]):
                for rec in recs:
                    self_inner.write_one(rec)

            @property
            def path(self_inner) -> Path:
                return path

        try:
            yield _Writer()
        finally:
            if first:
                # no items were written; still produce valid '[]'
                write_raw("[]")
            else:
                write_raw("]")
            f.close()
            self.logger.info(f"Streaming JSON list written to {path}.")