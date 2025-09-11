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

        data = filehandler.readJSON(
            adapter=ETLAdapter.ZENTIS,
            step=ETLStep.TRANSFORM,
            entity=InforComObjectType.JOINED_DATA,
        )
        self._load_data(InforComObjectType.JOINED_DATA, data)

    def _load_data(self, entity: InforComObjectType, data: list) -> None:
        """
        Loads the data into Nemo.
        """
        if not data:
            return

        self.logger.info(f"Loading {entity.label} data into Nemo")
        df = pd.DataFrame(data)
        
        ReUploadDataFrame(
            config=self.config,
            projectname=f"inforcom_{entity.label}",
            df=df,
            update_project_settings=False,
        )
