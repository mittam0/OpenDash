import argparse
import pandas as pd
from sqlalchemy import Engine, create_engine, inspect as sa_inspect
from app.utils.query_executor import get_engine_for_connector
from app.config import DB_PATH


def upsert_table(
    df: pd.DataFrame,
    table_name: str,
    engine: Engine | int | None = None,
    dup_columns: list[str] | None = None,
    keep: str = "last",
) -> int:
    df = df.copy()

    if dup_columns:
        valid_cols = [c for c in dup_columns if c in df.columns]
        if valid_cols:
            before = len(df)
            df = df.drop_duplicates(subset=valid_cols, keep=keep)
            after = len(df)
            removed = before - after
        else:
            removed = 0
    else:
        removed = 0

    resolved = resolve_engine(engine)

    has_table = sa_inspect(resolved).has_table(table_name)

    if has_table:
        df.to_sql(table_name, resolved, if_exists="replace", index=False)
    else:
        df.to_sql(table_name, resolved, if_exists="append", index=False)

    return len(df)


def resolve_engine(engine: Engine | int | None = None) -> Engine:
    if engine is None:
        return create_engine(f"sqlite:///{DB_PATH}")
    if isinstance(engine, int):
        result = get_engine_for_connector(engine)
        if result is None:
            raise ValueError(f"Connector with id={engine} not found or invalid")
        return result
    if isinstance(engine, Engine):
        return engine
    raise TypeError(f"Unsupported engine type: {type(engine)}")


def load_input_file(path: str) -> pd.DataFrame:
    ext = path.lower().rsplit(".", 1)[-1]
    if ext == "csv":
        return pd.read_csv(path)
    if ext in ("xls", "xlsx"):
        return pd.read_excel(path, engine="openpyxl")
    raise ValueError(f"Unsupported file format: .{ext}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Upsert DataFrame into a database table"
    )
    parser.add_argument("--table", required=True, help="Target table name")
    parser.add_argument("--file", required=True, help="Input file path (CSV or XLSX)")
    parser.add_argument(
        "--dup_columns",
        nargs="+",
        default=None,
        help="Columns to use for duplicate detection",
    )
    parser.add_argument(
        "--db",
        default=None,
        help="SQLAlchemy connection string (default: sqlite:///<app DB>)",
    )
    parser.add_argument(
        "--keep",
        choices=["first", "last"],
        default="last",
        help="Which duplicate to keep (default: last)",
    )

    args = parser.parse_args()

    df = load_input_file(args.file)
    engine = create_engine(args.db) if args.db else None

    count = upsert_table(
        df=df,
        table_name=args.table,
        engine=engine,
        dup_columns=args.dup_columns,
        keep=args.keep,
    )
    print(f"Upserted {count} rows into table '{args.table}'")
