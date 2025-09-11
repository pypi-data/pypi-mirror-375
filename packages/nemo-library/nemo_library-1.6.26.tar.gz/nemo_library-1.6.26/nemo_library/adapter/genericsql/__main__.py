import argparse
import getpass
from nemo_library.adapter.genericsql.flow import generic_sql_extract_flow


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the generic SQL adapter extract flow"
    )

    # Variant A: full connection string
    parser.add_argument(
        "--connection_string",
        type=str,
        required=False,
        help="Full SQLAlchemy connection string (e.g. "
        "'mssql+pyodbc://user:pass@host:1433/db?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=yes')",
    )

    # Variant B: discrete params (to build a connection string)
    parser.add_argument(
        "--engine",
        type=str,
        default="mssql+pyodbc",
        help="SQLAlchemy engine, e.g. 'mssql+pyodbc', 'postgresql+psycopg2'.",
    )
    parser.add_argument("--host", type=str, help="Database host / server.")
    parser.add_argument("--port", type=str, help="Database port (e.g. 1433 for MSSQL).")
    parser.add_argument("--database", type=str, help="Database name.")
    parser.add_argument("--user", type=str, help="Username.")
    parser.add_argument(
        "--password",
        type=str,
        help="Password. If omitted with discrete params, you will be prompted securely.",
    )
    parser.add_argument(
        "--odbc_driver",
        type=str,
        default="ODBC Driver 18 for SQL Server",
        help="ODBC driver name (for pyodbc-based engines).",
    )
    parser.add_argument(
        "--encrypt",
        type=str,
        choices=["yes", "no"],
        default="yes",
        help="Enable encryption parameter in connection string when applicable.",
    )
    parser.add_argument(
        "--trust_server_certificate",
        type=str,
        choices=["yes", "no"],
        default="no",
        help="TrustServerCertificate parameter when applicable.",
    )
    parser.add_argument(
        "--query", type=str, required=True, help="SQL query to execute."
    )
    parser.add_argument("--filename", type=str, required=True, help="Output file name")
    parser.add_argument(
        "--chunksize",
        type=int,
        default=None,
        help="Optional chunk size for large result sets (streaming).",
    )

    args = parser.parse_args()

    # Validate: either connection_string OR (host & database & user ...)
    if not args.connection_string:
        # If using discrete params, ensure minimum set
        missing = []
        for key in ["host", "database", "user"]:
            if getattr(args, key) in (None, ""):
                missing.append(key)
        # Prompt password if not provided
        password = args.password
        if not password:
            # Ask interactively to avoid leaking in shell history/logs
            password = getpass.getpass("Database password: ")
        if missing:
            raise SystemExit(
                f"Missing required parameter(s) for discrete connection: {', '.join(missing)}. "
                f"Either provide --connection_string OR all of --host --database --user (and password)."
            )

    generic_sql_extract_flow(
        connection_string=args.connection_string,
        engine=args.engine,
        host=args.host,
        port=args.port,
        database=args.database,
        user=args.user,
        password=(args.password or password if not args.connection_string else None),
        odbc_driver=args.odbc_driver,
        encrypt=args.encrypt,
        trust_server_certificate=args.trust_server_certificate,
        query=args.query,
        filename=args.filename,
        chunksize=args.chunksize,
    )


if __name__ == "__main__":
    main()
