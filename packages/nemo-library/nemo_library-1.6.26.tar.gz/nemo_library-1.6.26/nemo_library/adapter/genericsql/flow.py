from prefect import flow, task
from nemo_library.adapter.genericsql.extract import GenericSQLExtract


@flow(name="Generic SQL Extract Flow", log_prints=True)
def generic_sql_extract_flow(
    connection_string: str | None,
    engine: str | None,
    host: str | None,
    port: str | None,
    database: str | None,
    user: str | None,
    password: str | None,
    odbc_driver: str | None,
    encrypt: str | None,
    trust_server_certificate: str | None,
    query: str,
    chunksize: int | None,
    filename: str | None,
) -> None:
    extract(
        connection_string=connection_string,
        engine=engine,
        host=host,
        port=port,
        database=database,
        user=user,
        password=password,
        odbc_driver=odbc_driver,
        encrypt=encrypt,
        trust_server_certificate=trust_server_certificate,
        query=query,
        chunksize=chunksize,
        filename=filename
    )


@task(name="Extract Data from Generic SQL Database")
def extract(
    connection_string: str | None,
    engine: str | None,
    host: str | None,
    port: str | None,
    database: str | None,
    user: str | None,
    password: str | None,
    odbc_driver: str | None,
    encrypt: str | None,
    trust_server_certificate: str | None,
    query: str,
    chunksize: int | None,
    filename: str = "generic_sql_data",
):
    extractor = GenericSQLExtract(
        connection_string=connection_string,
        engine=engine,
        host=host,
        port=port,
        database=database,
        user=user,
        password=password,
        odbc_driver=odbc_driver,
        encrypt=encrypt,
        trust_server_certificate=trust_server_certificate,
    )
    extractor.extract(query=query, chunksize=chunksize, filename=filename)
