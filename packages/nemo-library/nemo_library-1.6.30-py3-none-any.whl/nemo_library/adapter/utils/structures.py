from enum import Enum


class ETLAdapter(Enum):
    GEDYS = "gedys"
    HUBSPOT = "hubspot"
    ZENTIS = "zentis"
    GENERICODBC = "genericodbc"


class ETLStep(Enum):
    EXTRACT = "extract"
    TRANSFORM = "transform"
    LOAD = "load"


class ETLBaseObjectType(Enum):
    def __init__(
        self,
        label: str,
        guid: str,
        sentiment_analysis_fields: list[str] | None = None,
        big_data: bool = False,
    ):
        """
        Initializes the ETLBaseObjectType with label, guid, and optional sentiment analysis fields.
        """
        self._label = label
        self._guid = guid
        self._sentiment_analysis_fields = sentiment_analysis_fields
        self._big_data = big_data

    @property
    def label(self) -> str:
        return self._label

    @property
    def guid(self) -> str:
        return self._guid

    @property
    def sentiment_analysis(self) -> bool:
        return self._sentiment_analysis_fields is not None

    @property
    def sentiment_analysis_fields(self) -> list[str] | None:
        return self._sentiment_analysis_fields

    @property
    def big_data(self) -> bool:
        return self._big_data
    
    @property
    def filename(self) -> str:
        return (
            self.label.lower()
            .replace(" ", "_")
            .replace("-", "_")
            .replace("(", "")
            .replace(")", "")
        )
