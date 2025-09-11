from prefect import get_run_logger
from nemo_library.adapter.genericodbc.generic_odbc_object_type import (
    GenericODBCObjectType,
)
from nemo_library.adapter.utils.file_handler import ETLFileHandler
from nemo_library.adapter.utils.structures import ETLAdapter, ETLStep
from nemo_library.core import NemoLibrary
import pandas as pd

from nemo_library.features.fileingestion import ReUploadDataFrame


class GenericODBCLoad:
    def __init__(self):

        nl = NemoLibrary()
        self.config = nl.config
        self.logger = get_run_logger()

        super().__init__()

    def load(
        self,
        filename: str,
    ) -> None:
        """
        Load the extracted and transformed data into Nemo.
        """
        filehandler = ETLFileHandler()

        data = filehandler.readJSON(
            adapter=ETLAdapter.GENERICODBC,
            step=ETLStep.EXTRACT,
            entity=GenericODBCObjectType.GENERIC,
            filename=filename,
        )
        self._load_data(filename=filename, data=data)

    def _load_data(
        self,
        filename: str,
        data: dict,
    ) -> None:
        """
        Loads the data into Nemo.
        """
        if not data:
            return

        self.logger.info(f"Loading {filename} data into Nemo")
        df = pd.DataFrame(data)

        ReUploadDataFrame(
            config=self.config,
            projectname=f"{filename}",
            df=df,
            update_project_settings=False,
        )
