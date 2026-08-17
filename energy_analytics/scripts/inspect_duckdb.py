import argparse
import sys

import duckdb


DB_PATH = "dev.duckdb"

ALLOWED_RELATIONS = {
    "customers",
    "meters",
    "meter_readings",
    "stg_customers",
    "stg_meters",
    "stg_meter_readings",
    "int_daily_consumption",
    "int_customer_daily_consumption",
    "dim_customers",
    "dim_meters",
    "dim_customer_history",
    "fct_energy_consumption",
    "fct_meter_readings",
    "main_snapshots.customer_snapshot",
}


def validate_relation(table_name):
    if table_name not in ALLOWED_RELATIONS:
        raise ValueError(
            f"Unsupported relation: {table_name}"
        )


def show_tables(con):
    """List all user tables and views."""

    con.sql("""
        select
            table_schema,
            table_name,
            table_type
        from information_schema.tables
        where table_schema not in ('information_schema', 'pg_catalog')
        order by table_schema, table_name
    """).show()


def show_count(con, table_name):
    validate_relation(table_name)

    con.sql(f"""
        select
            count(*) as row_count
        from {table_name}
    """).show()


def show_readings(con, limit):
    """Show the latest meter readings."""
    if limit <= 0:
        raise ValueError("Limit must be greater than 0.")

    con.sql(f"""
        select
            reading_id,
            meter_id,
            reading_timestamp,
            consumption_kwh,
            reading_type
        from fct_meter_readings
        order by reading_timestamp desc
        limit {limit}
    """).show()


def show_reading(con, reading_id):
    """Find one reading in both the raw source and incremental fact."""

    print(f"\n=== Raw source: {reading_id} ===")

    con.sql("""
        select
            reading_id,
            meter_id,
            reading_timestamp,
            consumption_kwh,
            reading_type
        from meter_readings
        where reading_id = $reading_id
    """, params={"reading_id": reading_id}).show()

    print(f"\n=== Incremental fact: {reading_id} ===")

    con.sql("""
        select
            reading_id,
            meter_id,
            reading_timestamp,
            consumption_kwh,
            reading_type
        from fct_meter_readings
        where reading_id = $reading_id
    """, params={"reading_id": reading_id}).show()


def show_max_timestamp(con):
    """Compare the latest timestamps in source and fact."""
    con.sql("""
        select
            'raw meter_readings' as relation,
            max(reading_timestamp) as max_reading_timestamp
        from meter_readings

        union all

        select
            'fct_meter_readings' as relation,
            max(reading_timestamp) as max_reading_timestamp
        from fct_meter_readings
    """).show()


def show_daily(con, limit):
    """Show daily meter consumption."""
    if limit <= 0:
        raise ValueError("Limit must be greater than 0.")

    con.sql(f"""
        select
            meter_id,
            reading_date,
            total_consumption_kwh,
            reading_count
        from int_daily_consumption
        order by reading_date desc, meter_id
        limit {limit}
    """).show()


def show_customer_snapshot(con):
    """Show customer history captured by dbt snapshot."""

    con.sql("""
        select
            customer_id,
            customer_name,
            city,
            customer_status,
            dbt_valid_from,
            dbt_valid_to
        from main_snapshots.customer_snapshot
        order by customer_id, dbt_valid_from
    """).show()


def show_relation_info(con, table_name):
    """Show basic metadata, row count, and schema for a relation."""
    validate_relation(table_name)

    print(f"\n=== Relation: {table_name} ===")

    con.sql(f"""
        select
            count(*) as row_count
        from {table_name}
    """).show()

    print("\n=== Columns ===")

    con.sql(f"""
        describe {table_name}
    """).show()


def preview_relation(con, table_name, limit):
    """Preview rows from a relation."""
    validate_relation(table_name)

    if limit <= 0:
        raise ValueError("Limit must be greater than 0.")

    con.sql(f"""
        select *
        from {table_name}
        limit {limit}
    """).show()


def build_parser():
    parser = argparse.ArgumentParser(
        description="Inspect the local energy analytics DuckDB database."
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True
    )

    subparsers.add_parser(
        "tables",
        help="List tables and views."
    )

    count_parser = subparsers.add_parser(
        "count",
        help="Count rows in a relation."
    )
    count_parser.add_argument("table")

    readings_parser = subparsers.add_parser(
        "readings",
        help="Show latest meter readings."
    )
    readings_parser.add_argument(
        "--limit",
        type=int,
        default=10
    )

    reading_parser = subparsers.add_parser(
        "reading",
        help="Find a reading in both raw source and incremental fact."
    )
    reading_parser.add_argument("reading_id")

    subparsers.add_parser(
        "max-timestamp",
        help="Compare latest source and fact timestamps."
    )

    subparsers.add_parser(
        "customer-history",
        help="Show customer snapshot history."
    )

    daily_parser = subparsers.add_parser(
        "daily",
        help="Show daily consumption."
    )
    daily_parser.add_argument(
        "--limit",
        type=int,
        default=20
    )

    duplicate_parser = subparsers.add_parser(
        "duplicates",
        help="Check a column for duplicate values."
    )
    duplicate_parser.add_argument("table")
    duplicate_parser.add_argument("column")

    info_parser = subparsers.add_parser(
        "info",
        help="Show row count and column information for a relation."
    )
    info_parser.add_argument("table")

    preview_parser = subparsers.add_parser(
        "preview",
        help="Preview rows from a table or view."
    )

    preview_parser.add_argument("table")

    preview_parser.add_argument(
        "--limit",
        type=int,
        default=10
    )

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    try:
        con = duckdb.connect(DB_PATH, read_only=True)

        if args.command == "tables":
            show_tables(con)

        elif args.command == "count":
            show_count(con, args.table)

        elif args.command == "readings":
            show_readings(con, args.limit)

        elif args.command == "reading":
            show_reading(con, args.reading_id)

        elif args.command == "max-timestamp":
            show_max_timestamp(con)

        elif args.command == "daily":
            show_daily(con, args.limit)

        elif args.command == "duplicates":
            show_duplicates(
                con,
                args.table,
                args.column
            )

        elif args.command == "customer-history":
            show_customer_snapshot(con)

        elif args.command == "info":
            show_relation_info(con, args.table)

        elif args.command == "preview":
            preview_relation(con, args.table, args.limit)

    except duckdb.Error as error:
        print(f"DuckDB error: {error}", file=sys.stderr)
        sys.exit(1)

    finally:
        if "con" in locals():
            con.close()


if __name__ == "__main__":
    main()
