from datetime import date, datetime
from enum import Enum
import json
import logging
import gzip
from pathlib import Path
from contextlib import contextmanager
from typing import Iterable, Optional

try:
    from prefect import get_run_logger  # type: ignore
    _PREFECT_AVAILABLE = True
except Exception:
    _PREFECT_AVAILABLE = False

from nemo_library.adapter.utils.structures import ETLAdapter, ETLBaseObjectType, ETLStep
from nemo_library.core import NemoLibrary


class ETLFileHandler:
    """
    Base class for handling ETL file operations with JSON only.
    - Pretty JSON write (single document)
    - Streaming write as a valid JSON array (with '[' ... ',' ... ']')
    - Auto-detect gzip (.json.gz) on read & write
    """

    def __init__(self):
        nl = NemoLibrary()
        self.config = nl.config
        self.logger = self._init_logger()
        super().__init__()

    # ---------- logger ----------

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
        """Default JSON serializer for datetimes, enums, and objects with to_dict()."""
        if hasattr(o, "to_dict") and callable(o.to_dict):
            return o.to_dict()
        if isinstance(o, (datetime, date)):
            return o.isoformat()
        if isinstance(o, Enum):
            return o.value
        return str(o)

    # ---------- utility methods ----------

    def _is_gz(self, path: Path) -> bool:
        return str(path).lower().endswith(".gz")

    def _is_json(self, path: Path) -> bool:
        s = str(path).lower()
        return s.endswith(".json") or s.endswith(".json.gz")

    def _open_text_auto(self, path: Path, mode: str):
        """
        Open text file; auto-detect gzip by file extension. Mode is 'r' or 'w' or 'a'.
        Always uses UTF-8 text encoding.
        """
        assert mode in ("r", "w", "a")
        if self._is_gz(path):
            return gzip.open(path, mode + "t", encoding="utf-8")
        else:
            return open(path, mode, encoding="utf-8")

    # ---------- read/write JSON (single document) ----------

    def readJSON(
        self,
        adapter: ETLAdapter,
        step: ETLStep,
        entity: ETLBaseObjectType | None,
        filename: str | None = None,
        label: str | None = None,
        ignore_nonexistent: bool = False,
    ) -> dict | list:
        """
        Read a JSON document from the ETL output location, auto-detecting gzip.

        Behavior:
          - Tries `<base>.json` first, then `<base>.json.gz`.
          - Returns the parsed JSON (dict or list).
          - If file does not exist:
              * if ignore_nonexistent=True -> returns {} (and warns)
              * else -> raises FileNotFoundError
          - If file exists but is empty/falsey:
              * returns {} if the document is an object, else [] for arrays.
        """
        base_path = self._output_path(adapter, step, entity, filename, "")
        candidates = [base_path.with_suffix(".json"), base_path.with_suffix(".json.gz")]

        file_path = None
        for cand in candidates:
            if cand.exists():
                file_path = cand
                break

        if file_path is None:
            if ignore_nonexistent:
                self.logger.warning(
                    f"No JSON file found for base {base_path}. "
                    f"Returning empty data for entity {entity.label if entity else label}."
                )
                return {}
            raise FileNotFoundError(
                f"No JSON file found. Tried: {', '.join(str(c) for c in candidates)}"
            )

        with self._open_text_auto(file_path, "r") as f:
            data = json.load(f)

        if not data:
            self.logger.warning(
                f"No data found in file {file_path} for entity {entity.label if entity else label}."
            )
            return {} if isinstance(data, dict) else []

        return data

    def writeJSON(
        self,
        adapter: ETLAdapter,
        step: ETLStep,
        data: dict | list[dict],
        entity: ETLBaseObjectType | None,
        filename: str | None = None,
        label: str | None = None,
        gzip_enabled: bool = False,
        indent: int = 4,
    ) -> Path:
        """
        Write a dictionary or list of dictionaries as a single JSON document.
        If gzip_enabled=True, writes <name>.json.gz, else <name>.json.
        """
        if not data:
            self.logger.warning(
                f"No data to write for entity {entity.label if entity else label}. Skipping file write."
            )
            # Still return the path we would have written to (helps callers compute destinations)
            suffix = ".json.gz" if gzip_enabled else ".json"
            return self._output_path(adapter, step, entity, filename, suffix)

        suffix = ".json.gz" if gzip_enabled else ".json"
        file_path = self._output_path(adapter, step, entity, filename, suffix)
        with self._open_text_auto(file_path, "w") as f:
            json.dump(data, f, indent=indent, ensure_ascii=False, default=self._json_default)

        length_info = ""
        try:
            length_info = f"{format(len(data), ',')} records" if hasattr(data, "__len__") else "Data"
        except Exception:
            length_info = "Data"

        self.logger.info(
            f"{length_info} written to {file_path} for entity {entity.label if entity else label}."
        )
        return file_path

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
        If gzip_enabled=True, file will be <name>.json.gz, else <name>.json.

        Usage:
            with fh.streamJSONList(adapter, step, entity, filename, gzip_enabled) as writer:
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