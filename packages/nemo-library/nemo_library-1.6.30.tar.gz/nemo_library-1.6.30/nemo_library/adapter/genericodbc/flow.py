from prefect import flow, task
from nemo_library.adapter.genericodbc.extract import GenericODBCExtract
from nemo_library.adapter.genericodbc.load import GenericODBCLoad


@flow(name="Generic ODBC Extract Flow", log_prints=True)
def generic_odbc_extract_flow(
    bextract: bool,
    bload: bool,
    odbc_connstr: str | None = None,
    query: str | None = None,
    filename: str | None = None,
    chunksize: int | None = None,
    gzip_enabled: bool = False,
    timeout: int = 300,
) -> None:
    if bextract:
        extract(
            odbc_connstr=odbc_connstr,
            query=query,
            filename=filename,
            chunksize=chunksize,
            gzip_enabled=gzip_enabled,
            timeout=timeout,
        )

    if bload:
        load(filename=filename)


@task(name="Extract Data from Generic ODBC Database")
def extract(
    odbc_connstr: str,
    query: str,
    filename: str,
    chunksize: int | None = None,
    gzip_enabled: bool = False,
    timeout: int = 300,
):
    extractor = GenericODBCExtract(odbc_connstr=odbc_connstr, timeout=timeout)
    extractor.extract(
        query=query,
        filename=filename,
        chunksize=chunksize,
        gzip_enabled=gzip_enabled,
    )


@task(name="Load Data into Nemo")
def load(
    filename: str,
):
    loader = GenericODBCLoad()
    loader.load(
        filename=filename,
    )
