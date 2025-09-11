import argparse
import getpass
from nemo_library.adapter.genericodbc.flow import generic_odbc_extract_flow


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the generic ODBC adapter extract flow (ODBC-only)"
    )

    # Choose exactly one: full ODBC connection string OR DSN (+ optional credentials)
    parser.add_argument(
        "--odbc_connstr",
        type=str,
        help='Full ODBC connection string, e.g. "DRIVER={Oracle in OraClient11g_home1};DBQ=PROD71.db-infor71;UID=read;PWD=read"',
    )
    parser.add_argument("--odbc_dsn", type=str, help='ODBC DSN name, e.g. "Infor Prod"')
    parser.add_argument(
        "--user",
        type=str,
        help="Username for DSN-based connection (optional if DSN stores it)",
    )
    parser.add_argument(
        "--password",
        type=str,
        help="Password for DSN-based connection (if omitted, will prompt)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="ODBC connection/query timeout in seconds",
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
        help="Fetch size for streaming (e.g., 5000).",
    )
    parser.add_argument(
        "--jsonl",
        action="store_true",
        help="Write JSON Lines (.jsonl / .jsonl.gz) instead of JSON array.",
    )
    parser.add_argument("--gzip", action="store_true", help="Compress output as .gz.")

    args = parser.parse_args()

    # Validation: exactly one of odbc_connstr or odbc_dsn must be given
    if bool(args.odbc_connstr) == bool(args.odbc_dsn):
        raise SystemExit("Provide exactly one of --odbc_connstr OR --odbc_dsn.")

    effective_connstr = args.odbc_connstr
    effective_password = args.password

    # Build connection string from DSN if needed
    if args.odbc_dsn:
        # Prompt for password if user is given but no password provided
        if args.user and not effective_password:
            effective_password = getpass.getpass("Database password: ")

        parts = [f"DSN={args.odbc_dsn}"]
        if args.user:
            parts.append(f"UID={args.user}")
        if effective_password:
            parts.append(f"PWD={effective_password}")
        effective_connstr = ";".join(parts)

    generic_odbc_extract_flow(
        odbc_connstr=effective_connstr,
        query=args.query,
        filename=args.filename,
        chunksize=args.chunksize,
        jsonl=args.jsonl,
        gzip_enabled=args.gzip,
        timeout=args.timeout,
    )


if __name__ == "__main__":
    main()
