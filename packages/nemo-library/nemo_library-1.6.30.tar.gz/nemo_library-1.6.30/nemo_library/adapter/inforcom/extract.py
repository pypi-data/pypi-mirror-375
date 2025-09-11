from pathlib import Path
from typing import List
from prefect import get_run_logger
import pandas as pd
from nemo_library.adapter.genericodbc.flow import generic_odbc_extract_flow
from nemo_library.adapter.inforcom.inforcom_object_type import InforComObjectType
from nemo_library.adapter.utils.datatype_handler import (
    df_to_records_jsonsafe,
    normalize_na,
    read_csv_all_str,
    to_bool_nullable,
    to_datetime_safe,
    to_float64_mixed,
    to_int64_nullable,
)
from nemo_library.adapter.utils.file_handler import ETLFileHandler
from nemo_library.adapter.utils.structures import ETLAdapter, ETLStep
from nemo_library.core import NemoLibrary


class InforComExtract:
    """
    Adapter for InforCom API.
    """

    def __init__(self):

        nl = NemoLibrary()
        self.config = nl.config
        self.logger = get_run_logger()

        super().__init__()

    def extract(
        self,
        odbc_connstr: str | None = None,
        timeout: int = 300,
    ) -> None:
        """
        Extracts data from the InforCom API for all entities.
        """

        for entity in InforComObjectType:
            self.logger.info(f"Starting extraction for entity: {entity.name}")

            generic_odbc_extract_flow(
                bextract=True,
                bload=True,
                odbc_connstr=odbc_connstr,
                query=f"SELECT * FROM {entity.label}",
                filename=f"INFORCOM_{entity.label}",
                chunksize=10000 if entity.big_data else None,
                gzip_enabled=True,
                timeout=timeout,
            )
