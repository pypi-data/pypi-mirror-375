from prefect import get_run_logger
from nemo_library.adapter.utils.file_handler import ETLFileHandler
from nemo_library.adapter.utils.structures import ETLAdapter, ETLStep
from nemo_library.adapter.inforcom.inforcom_object_type import InforComObjectType
from nemo_library.core import NemoLibrary
from nemo_library.features.fileingestion import ReUploadDataFrame
import pandas as pd


class InforComLoad:
    """
    Class to handle load of data for the InforCom adapter.
    """

    def __init__(self):

        nl = NemoLibrary()
        self.config = nl.config
        self.logger = get_run_logger()

        super().__init__()

    def load(self) -> None:
        """
        Load the extracted and transformed data into Nemo.
        """
        filehandler = ETLFileHandler()
