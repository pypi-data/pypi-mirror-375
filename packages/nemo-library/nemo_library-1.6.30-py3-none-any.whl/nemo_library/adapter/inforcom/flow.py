from prefect import flow, task, get_run_logger

from nemo_library.adapter.inforcom.extract import InforComExtract
from nemo_library.adapter.inforcom.load import InforComLoad
from nemo_library.adapter.inforcom.transform import InforComTransform


@flow(name="InforCom ETL Flow", log_prints=True)
def inforcom_flow(
    bextract: bool = True,
    btransform: bool = True,
    bload: bool = True,
    odbc_connstr: str | None = None,
    timeout: int = 300,
):
    logger = get_run_logger()
    logger.info("Starting InforCom ETL Flow")

    if bextract:
        logger.info("Extracting objects from InforCom")
        extract(
            odbc_connstr=odbc_connstr,
            timeout=timeout,
        )

    if btransform:
        logger.info("Transforming InforCom objects")
        transform()

    if bload:
        logger.info("Loading InforCom objects")
        load()

    logger.info("InforCom ETL Flow finished")


@task(name="Extract All Objects from InforCom")
def extract(
    odbc_connstr: str | None = None,
    timeout: int = 300,
):
    logger = get_run_logger()
    logger.info("Extracting all InforCom objects")

    extractor = InforComExtract()
    extractor.extract(
        odbc_connstr=odbc_connstr,
        timeout=timeout,
    )


@task(name="Transform Objects")
def transform():
    logger = get_run_logger()
    logger.info("Transforming InforCom objects")

    transformer = InforComTransform()
    transformer.transform()
    transformer.join()


@task(name="Load Objects into Nemo")
def load():
    logger = get_run_logger()
    logger.info("Loading InforCom objects into Nemo")

    loader = InforComLoad()
    loader.load()
