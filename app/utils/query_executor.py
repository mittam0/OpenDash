import re
import pandas as pd
from sqlalchemy import create_engine, text
from app.models import get_connector_by_id
from app.config import DB_PATH


BLOCKED_KEYWORDS = [
    "drop", "truncate", "delete", "insert", "update", "alter",
    "create", "replace", "grant", "revoke", "exec", "execute",
]


def is_query_safe(query):
    query_lower = query.lower().strip()
    for kw in BLOCKED_KEYWORDS:
        if re.search(rf'\b{kw}\b', query_lower):
            return False
    return True


def get_engine_for_connector(connector_id):
    if connector_id is None:
        return None

    connector = get_connector_by_id(connector_id)
    if not connector:
        return None

    engine_name = connector["engine"]
    conn_string = connector["connection_string"]

    if engine_name == "sqlite":
        if conn_string and conn_string.strip():
            return create_engine(conn_string)
        else:
            return create_engine(f"sqlite:///{DB_PATH}")

    if conn_string:
        return create_engine(conn_string)
    return None


def execute_query(connector_id, query):
    if not query or not query.strip():
        return None

    if not is_query_safe(query):
        raise ValueError("Query contains blocked operations")

    engine = get_engine_for_connector(connector_id)
    if engine is None:
        raise ValueError("No valid connector/engine configured")

    with engine.connect() as conn:
        result = pd.read_sql_query(text(query), conn)

    return result


def get_tables_for_connector(connector_id):
    engine = get_engine_for_connector(connector_id)
    if engine is None:
        return []

    try:
        from sqlalchemy import inspect as sa_inspect
        inspector = sa_inspect(engine)
        return inspector.get_table_names()
    except Exception:
        return []
