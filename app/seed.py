from app.database import get_connection
from app.config import DEFAULT_CONNECTOR_NAME
from app.auth import hash_password


def seed_database():
    conn = get_connection()

    admin_exists = conn.execute(
        "SELECT id FROM users WHERE username = ?", ("adm",)
    ).fetchone()

    if not admin_exists:
        conn.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            ("adm", hash_password("adm"), "admin"),
        )

    main_connector = conn.execute(
        "SELECT id FROM connectors WHERE name = ?", (DEFAULT_CONNECTOR_NAME,)
    ).fetchone()

    if not main_connector:
        conn.execute(
            "INSERT INTO connectors (name, engine, connection_string) VALUES (?, ?, ?)",
            (DEFAULT_CONNECTOR_NAME, "sqlite", ""),
        )

    conn.commit()
    conn.close()
