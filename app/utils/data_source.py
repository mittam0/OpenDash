import os
import pandas as pd
from app.utils.query_executor import execute_query
from app.config import UPLOAD_DIR


def load_data(block):
    data_source_type = block.get("data_source_type", "query")

    if data_source_type == "file":
        file_path = block.get("uploaded_file_path", "")
        if not file_path or not os.path.exists(file_path):
            return None
        return load_file(file_path)

    connector_id = block.get("connector_id")
    query = block.get("query", "")
    if not query:
        return None
    return execute_query(connector_id, query)


def load_file(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    try:
        if ext == ".csv":
            return pd.read_csv(file_path)
        elif ext in (".xls", ".xlsx"):
            return pd.read_excel(file_path, engine="openpyxl")
        else:
            return None
    except Exception:
        return None


def save_uploaded_file(uploaded_file, username):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    safe_name = f"{username}_{uploaded_file.name}"
    dest = os.path.join(UPLOAD_DIR, safe_name)
    with open(dest, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return dest
