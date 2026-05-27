import json
from app.database import get_connection


def dict_from_row(row):
    return dict(row) if row else None


# --- Users ---

def get_user_by_username(username):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM users WHERE username = ?", (username,)
    ).fetchone()
    conn.close()
    return dict_from_row(row)


def get_user_by_id(user_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM users WHERE id = ?", (user_id,)
    ).fetchone()
    conn.close()
    return dict_from_row(row)


def get_all_users():
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, username, role, created_at FROM users ORDER BY id"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_user(username, password_hash, role="user"):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, password_hash, role),
        )
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()


def delete_user(user_id):
    conn = get_connection()
    conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()


# --- Connectors ---

def get_connector_by_id(connector_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM connectors WHERE id = ?", (connector_id,)
    ).fetchone()
    conn.close()
    return dict_from_row(row)


def get_connector_by_name(name):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM connectors WHERE name = ?", (name,)
    ).fetchone()
    conn.close()
    return dict_from_row(row)


def get_all_connectors():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM connectors ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_connector(name, engine, connection_string):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO connectors (name, engine, connection_string) VALUES (?, ?, ?)",
            (name, engine, connection_string),
        )
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()


def update_connector(connector_id, name, engine, connection_string):
    conn = get_connection()
    conn.execute(
        "UPDATE connectors SET name=?, engine=?, connection_string=? WHERE id=?",
        (name, engine, connection_string, connector_id),
    )
    conn.commit()
    conn.close()


def delete_connector(connector_id):
    conn = get_connection()
    conn.execute("DELETE FROM connectors WHERE id = ?", (connector_id,))
    conn.commit()
    conn.close()


# --- Blocks ---

def get_blocks_for_user(user_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM blocks WHERE user_id = ? AND is_active = 1 ORDER BY position",
        (user_id,),
    ).fetchall()
    conn.close()
    blocks = []
    for r in rows:
        b = dict(r)
        try:
            b["config"] = json.loads(b["config"])
        except (json.JSONDecodeError, TypeError):
            b["config"] = {}
        blocks.append(b)
    return blocks


def get_block_by_id(block_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM blocks WHERE id = ?", (block_id,)
    ).fetchone()
    conn.close()
    if row:
        b = dict(row)
        try:
            b["config"] = json.loads(b["config"])
        except (json.JSONDecodeError, TypeError):
            b["config"] = {}
        return b
    return None


def create_block(user_id, title, block_type, data_source_type,
                 connector_id, query, uploaded_file_path, config, position,
                 refresh_interval=0):
    conn = get_connection()
    conn.execute("""
        INSERT INTO blocks
            (user_id, title, block_type, data_source_type, connector_id,
             query, uploaded_file_path, config, position, refresh_interval)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, title, block_type, data_source_type,
          connector_id, query, uploaded_file_path,
          json.dumps(config), position, refresh_interval))
    conn.commit()
    block_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.close()
    return block_id


def update_block(block_id, title, block_type, data_source_type,
                 connector_id, query, uploaded_file_path, config, position,
                 refresh_interval):
    conn = get_connection()
    conn.execute("""
        UPDATE blocks SET title=?, block_type=?, data_source_type=?,
            connector_id=?, query=?, uploaded_file_path=?,
            config=?, position=?, refresh_interval=?,
            updated_at=CURRENT_TIMESTAMP
        WHERE id=?
    """, (title, block_type, data_source_type,
          connector_id, query, uploaded_file_path,
          json.dumps(config), position, refresh_interval,
          block_id))
    conn.commit()
    conn.close()


def delete_block(block_id):
    conn = get_connection()
    conn.execute("UPDATE blocks SET is_active = 0 WHERE id = ?", (block_id,))
    conn.commit()
    conn.close()


def get_max_position(user_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT COALESCE(MAX(position), -1) as max_pos FROM blocks WHERE user_id = ? AND is_active = 1",
        (user_id,),
    ).fetchone()
    conn.close()
    return row["max_pos"]
