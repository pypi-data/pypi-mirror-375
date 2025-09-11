from prefect import flow, task
from nemo_library.adapter.genericodbc.extract import GenericODBCExtract


@flow(name="Generic ODBC Extract Flow", log_prints=True)
def generic_odbc_extract_flow(
    odbc_connstr: str,
    query: str,
    filename: str,
    chunksize: int | None = None,
    jsonl: bool = False,
    gzip_enabled: bool = False,
    timeout: int = 300,
) -> None:
    extract(
        odbc_connstr=odbc_connstr,
        query=query,
        filename=filename,
        chunksize=chunksize,
        jsonl=jsonl,
        gzip_enabled=gzip_enabled,
        timeout=timeout,
    )


@task(name="Extract Data from Generic ODBC Database")
def extract(
    odbc_connstr: str,
    query: str,
    filename: str,
    chunksize: int | None = None,
    jsonl: bool = False,
    gzip_enabled: bool = False,
    timeout: int = 300,
):
    extractor = GenericODBCExtract(odbc_connstr=odbc_connstr, timeout=timeout)
    extractor.extract(
        query=query,
        filename=filename,
        chunksize=chunksize,
        jsonl=jsonl,
        gzip_enabled=gzip_enabled,
    )
