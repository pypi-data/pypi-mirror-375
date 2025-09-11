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

    # Query & output
    parser.add_argument(
        "--query", type=str, required=True, help="SQL query to execute."
    )
    parser.add_argument(
        "--filename",
        type=str,
        required=True,
        help="Output file name (without extension).",
    )
    parser.add_argument(
        "--chunksize",
        type=int,
        default=None,
        help="Optional chunk size for large result sets (streaming).",
    )

    # Optional output-format flags (falls du sie nutzen willst; sonst gerne entfernen)
    parser.add_argument(
        "--jsonl",
        action="store_true",
        help="Write as JSON Lines (.jsonl / .jsonl.gz) instead of a JSON array.",
    )
    parser.add_argument("--gzip", action="store_true", help="Compress output as .gz.")

    args = parser.parse_args()

    # Decide mode
    using_connection_string = bool(args.connection_string)
    using_discrete = not using_connection_string

    # If both sets are given, prefer connection_string and ignore discrete
    if using_connection_string and any(
        [args.host, args.database, args.user, args.password, args.port]
    ):
        print(
            "Warning: --connection_string provided. Discrete connection parameters will be ignored."
        )

    # Validate discrete params
    effective_password = None
    if using_discrete:
        missing = [k for k in ("host", "database", "user") if not getattr(args, k)]
        if missing:
            raise SystemExit(
                "Missing required parameter(s) for discrete connection: "
                + ", ".join(missing)
                + ". Either provide --connection_string OR --host --database --user (and a password)."
            )
        effective_password = args.password
        if not effective_password:
            # secure prompt (keine Shell-History)
            effective_password = getpass.getpass("Database password: ")

    # Run flow
    generic_sql_extract_flow(
        connection_string=args.connection_string if using_connection_string else None,
        engine=args.engine if using_discrete else None,
        host=args.host if using_discrete else None,
        port=args.port if using_discrete else None,
        database=args.database if using_discrete else None,
        user=args.user if using_discrete else None,
        password=effective_password if using_discrete else None,
        odbc_driver=args.odbc_driver if using_discrete else None,
        encrypt=args.encrypt if using_discrete else None,
        trust_server_certificate=(
            args.trust_server_certificate if using_discrete else None
        ),
        query=args.query,
        filename=args.filename,
        chunksize=args.chunksize,
        jsonl=args.jsonl,
        gzip_enabled=args.gzip,
    )


if __name__ == "__main__":
    main()
