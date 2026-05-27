import streamlit as st
from app.models import (
    get_all_users, create_user, delete_user,
    get_all_connectors, create_connector, update_connector,
    delete_connector,
)
from app.auth import hash_password


def render():
    st.markdown("# ⚙️ Администрирование")

    if st.session_state.get("role") != "admin":
        st.error("Доступ запрещён. Только администратор.")
        return

    tab1, tab2 = st.tabs(["👥 Пользователи", "🔌 Коннекторы"])

    with tab1:
        render_users_tab()
    with tab2:
        render_connectors_tab()


def render_users_tab():
    st.markdown("### Пользователи")

    users = get_all_users()

    if users:
        data = [
            {
                "ID": u["id"],
                "Логин": u["username"],
                "Роль": "Администратор" if u["role"] == "admin" else "Пользователь",
                "Создан": u.get("created_at", ""),
            }
            for u in users
        ]
        st.dataframe(data, use_container_width=True, hide_index=True)
    else:
        st.info("Нет пользователей")

    st.divider()
    st.markdown("#### Создать пользователя")

    with st.form("create_user_form", clear_on_submit=True):
        new_username = st.text_input("Логин", placeholder="newuser")
        new_password = st.text_input("Пароль", type="password", placeholder="••••••")
        new_role = st.selectbox("Роль", ["user", "admin"])
        submitted = st.form_submit_button("Создать пользователя", type="primary", use_container_width=True)

        if submitted:
            if not new_username or not new_password:
                st.error("Заполните логин и пароль")
            elif len(new_password) < 3:
                st.error("Пароль должен быть минимум 3 символа")
            else:
                pwd_hash = hash_password(new_password)
                if create_user(new_username, pwd_hash, new_role):
                    st.success(f"Пользователь «{new_username}» создан!")
                    st.rerun()
                else:
                    st.error(f"Пользователь «{new_username}» уже существует")

    st.divider()
    st.markdown("#### Удалить пользователя")

    admin_users = [u for u in users if u["role"] == "admin"]
    other_users = [u for u in users if u["role"] != "admin"]

    if other_users:
        user_to_delete = st.selectbox(
            "Выберите пользователя для удаления",
            other_users,
            format_func=lambda u: f"{u['username']} (ID: {u['id']})",
        )
        if st.button(f"🗑️ Удалить {user_to_delete['username']}", type="secondary"):
            if len(admin_users) == 1 and user_to_delete["id"] == admin_users[0]["id"]:
                st.error("Нельзя удалить единственного администратора")
            else:
                delete_user(user_to_delete["id"])
                st.success(f"Пользователь «{user_to_delete['username']}» удалён")
                st.rerun()
    else:
        st.info("Нет пользователей для удаления")


def render_connectors_tab():
    st.markdown("### Коннекторы к данным")

    connectors = get_all_connectors()

    if connectors:
        data = [
            {
                "ID": c["id"],
                "Имя": c["name"],
                "Движок": c["engine"],
                "Строка подключения": c["connection_string"][:60] + "..." if len(c.get("connection_string", "")) > 60 else c.get("connection_string", ""),
                "Создан": c.get("created_at", ""),
            }
            for c in connectors
        ]
        st.dataframe(data, use_container_width=True, hide_index=True)
    else:
        st.info("Нет коннекторов")

    st.divider()
    st.markdown("#### Создать коннектор")

    with st.form("create_connector_form", clear_on_submit=True):
        conn_name = st.text_input("Имя коннектора", placeholder="my_postgres")
        conn_engine = st.selectbox(
            "Тип БД (движок SQLAlchemy)",
            ["sqlite", "postgresql", "mysql", "mssql", "oracle"],
        )
        conn_string = st.text_input(
            "Строка подключения SQLAlchemy",
            placeholder="postgresql://user:pass@host:5432/dbname",
            help="Для SQLite: sqlite:///path/to/db.db или оставьте пустым для основной БД",
        )
        submitted = st.form_submit_button("Создать коннектор", type="primary", use_container_width=True)

        if submitted:
            if not conn_name:
                st.error("Введите имя коннектора")
            else:
                if create_connector(conn_name, conn_engine, conn_string):
                    st.success(f"Коннектор «{conn_name}» создан!")
                    st.rerun()
                else:
                    st.error(f"Коннектор «{conn_name}» уже существует")

    non_default_connectors = [c for c in connectors if c["name"] != "main"]
    if non_default_connectors:
        st.divider()
        st.markdown("#### Управление коннекторами")

        conn_to_edit = st.selectbox(
            "Выберите коннектор",
            non_default_connectors,
            format_func=lambda c: f"{c['name']} ({c['engine']})",
            key="edit_connector_select",
        )

        if conn_to_edit:
            with st.form("edit_connector_form"):
                new_name = st.text_input("Имя", value=conn_to_edit["name"])
                new_engine = st.selectbox(
                    "Тип БД",
                    ["sqlite", "postgresql", "mysql", "mssql", "oracle"],
                    index=["sqlite", "postgresql", "mysql", "mssql", "oracle"].index(
                        conn_to_edit["engine"]
                    ) if conn_to_edit["engine"] in ["sqlite", "postgresql", "mysql", "mssql", "oracle"] else 0,
                )
                new_string = st.text_input("Строка подключения", value=conn_to_edit.get("connection_string", ""))

                col1, col2 = st.columns(2)
                with col1:
                    save = st.form_submit_button("💾 Сохранить", use_container_width=True)
                with col2:
                    delete = st.form_submit_button("🗑️ Удалить", use_container_width=True)

                if save:
                    update_connector(conn_to_edit["id"], new_name, new_engine, new_string)
                    st.success("Коннектор обновлён!")
                    st.rerun()
                if delete:
                    delete_connector(conn_to_edit["id"])
                    st.success("Коннектор удалён!")
                    st.rerun()
