import streamlit as st
from app.models import (
    get_blocks_for_user, create_block, update_block,
    delete_block, get_max_position, get_all_connectors,
    get_connector_by_id,
)
from app.config import MAX_BLOCKS
from app.components import chart_block, table_block, pivot_block, value_card
from app.utils.data_source import save_uploaded_file


def render():
    st.markdown("# 📊 Дашборд")
    user_id = st.session_state.user_id
    username = st.session_state.username
    blocks = get_blocks_for_user(user_id)

    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"Добро пожаловать, **{username}**!")
    with col2:
        if st.button("🔄 Обновить всё", use_container_width=True):
            st.rerun()

    st.divider()

    if len(blocks) >= MAX_BLOCKS:
        st.info(f"Достигнут лимит в {MAX_BLOCKS} блока. Удалите один блок, чтобы добавить новый.")
    else:
        with st.expander("➕ Добавить новый блок", expanded=False):
            render_add_block_form(user_id)

    if not blocks:
        st.info("У вас пока нет блоков. Нажмите «Добавить новый блок», чтобы начать.")
        return

    num_blocks = len(blocks)
    if num_blocks == 1:
        cols = [st.container()]
    elif num_blocks == 2:
        cols = st.columns(2)
    else:
        cols = st.columns(2)

    for i, block in enumerate(blocks):
        if num_blocks >= 3 and i == 2:
            st.divider()
            cols = st.columns(2)

        col_idx = i % 2 if num_blocks > 1 else 0
        col = cols[col_idx] if isinstance(cols, list) else cols[0] if num_blocks == 1 else cols[col_idx]

        with col:
            render_block(block, user_id)


def render_add_block_form(user_id):
    connectors = get_all_connectors()
    connector_options = {c["name"]: c["id"] for c in connectors}

    with st.form("add_block_form", clear_on_submit=True):
        title = st.text_input("Название блока", placeholder="Мои продажи")
        block_type = st.selectbox(
            "Тип блока",
            ["chart", "table", "pivot", "value_card"],
            format_func=lambda x: {
                "chart": "📈 График",
                "table": "📋 Таблица",
                "pivot": "📊 Сводная таблица",
                "value_card": "💳 Карточка значения",
            }[x],
        )
        data_source_type = st.radio(
            "Источник данных",
            ["query", "file"],
            format_func=lambda x: {"query": "SQL-запрос к БД", "file": "Загрузка файла"}[x],
            horizontal=True,
        )

        connector_id = None
        query = ""
        uploaded_file_path = ""

        if data_source_type == "query":
            connector_name = st.selectbox(
                "Коннектор",
                list(connector_options.keys()),
                index=0,
            )
            connector_id = connector_options[connector_name]
            query = st.text_area("SQL-запрос", placeholder="SELECT * FROM table LIMIT 100", height=100)
        else:
            uploaded_file = st.file_uploader(
                "Загрузить файл (CSV, XLSX)",
                type=["csv", "xlsx"],
            )

        refresh_interval = st.number_input(
            "Интервал автообновления (сек, 0 = вручную)",
            min_value=0, max_value=3600, step=30, value=0,
        )

        submitted = st.form_submit_button("Создать блок", type="primary", use_container_width=True)

        if submitted:
            if not title:
                st.error("Введите название блока")
                return

            if data_source_type == "file":
                if uploaded_file is None:
                    st.error("Загрузите файл")
                    return
                uploaded_file_path = save_uploaded_file(uploaded_file, st.session_state.username)
                query = ""
                connector_id = None

            position = get_max_position(user_id) + 1
            default_config = {}
            create_block(
                user_id, title, block_type, data_source_type,
                connector_id, query, uploaded_file_path,
                default_config, position, refresh_interval,
            )
            st.success(f"Блок «{title}» создан!")
            st.rerun()


def render_block(block, user_id):
    block_id = block["id"]
    title = block["title"]
    block_type = block["block_type"]
    refresh_interval = block.get("refresh_interval", 0)

    expander_label = f"{get_block_icon(block_type)} {title}"
    if refresh_interval > 0:
        expander_label += f" ⏱{refresh_interval}с"

    with st.expander(expander_label, expanded=True):
        refresh_col, edit_col, delete_col = st.columns([1, 1, 1])
        with refresh_col:
            if st.button("🔄 Обновить", key=f"refresh_{block_id}", use_container_width=True):
                pass
        with edit_col:
            edit_mode = st.session_state.get(f"edit_mode_{block_id}", False)
            if st.button(
                "⚙️ Настройки" if not edit_mode else "❌ Закрыть",
                key=f"edit_{block_id}",
                use_container_width=True,
            ):
                st.session_state[f"edit_mode_{block_id}"] = not edit_mode
                st.rerun()
        with delete_col:
            if st.button("🗑️ Удалить", key=f"delete_{block_id}", use_container_width=True):
                delete_block(block_id)
                st.rerun()

        if block_type == "chart":
            chart_block.render(block)
        elif block_type == "table":
            table_block.render(block)
        elif block_type == "pivot":
            pivot_block.render(block)
        elif block_type == "value_card":
            value_card.render(block)

        if st.session_state.get(f"edit_mode_{block_id}", False):
            st.divider()
            st.markdown("#### ✏️ Настройки блока")
            render_edit_block_form(block, user_id)


def render_edit_block_form(block, user_id):
    connectors = get_all_connectors()
    connector_options = {c["name"]: c["id"] for c in connectors}

    with st.form(key=f"edit_block_form_{block['id']}"):
        title = st.text_input("Название", value=block["title"])
        block_type = st.selectbox(
            "Тип блока",
            ["chart", "table", "pivot", "value_card"],
            index=["chart", "table", "pivot", "value_card"].index(block["block_type"]),
            format_func=lambda x: {
                "chart": "📈 График",
                "table": "📋 Таблица",
                "pivot": "📊 Сводная таблица",
                "value_card": "💳 Карточка значения",
            }[x],
        )
        data_source_type = st.radio(
            "Источник данных",
            ["query", "file"],
            index=0 if block["data_source_type"] == "query" else 1,
            format_func=lambda x: {"query": "SQL-запрос к БД", "file": "Загрузка файла"}[x],
            horizontal=True,
        )

        connector_id = block.get("connector_id")
        query = block.get("query", "")
        uploaded_file_path = block.get("uploaded_file_path", "")

        if data_source_type == "query":
            conn_names = list(connector_options.keys())
            current_connector = get_connector_by_id(connector_id) if connector_id else None
            default_idx = 0
            if current_connector and current_connector["name"] in conn_names:
                default_idx = conn_names.index(current_connector["name"])
            connector_name = st.selectbox("Коннектор", conn_names, index=default_idx)
            connector_id = connector_options[connector_name]
            query = st.text_area("SQL-запрос", value=query, height=100)
        else:
            uploaded_file = st.file_uploader(
                "Загрузить новый файл (оставьте пустым, чтобы не менять)",
                type=["csv", "xlsx"],
            )
            if uploaded_file:
                uploaded_file_path = save_uploaded_file(uploaded_file, st.session_state.username)
            if uploaded_file_path:
                st.caption(f"Текущий файл: {uploaded_file_path}")

        refresh_interval = st.number_input(
            "Интервал автообновления (сек, 0 = вручную)",
            min_value=0, max_value=3600, step=30, value=block.get("refresh_interval", 0),
        )

        st.divider()
        st.markdown("##### Настройки отображения")

        config = block.get("config", {})
        if block_type == "chart":
            new_config = chart_block.render_config({**block, "config": config})
        elif block_type == "table":
            new_config = table_block.render_config({**block, "config": config})
        elif block_type == "pivot":
            new_config = pivot_block.render_config({**block, "config": config})
        elif block_type == "value_card":
            new_config = value_card.render_config({**block, "config": config})
        else:
            new_config = config

        submitted = st.form_submit_button("💾 Сохранить изменения", type="primary", use_container_width=True)

        if submitted:
            if not title:
                st.error("Введите название блока")
                return
            if data_source_type == "query" and not query:
                st.error("Введите SQL-запрос")
                return

            update_block(
                block["id"], title, block_type, data_source_type,
                connector_id, query, uploaded_file_path,
                new_config, block["position"], refresh_interval,
            )
            st.session_state[f"edit_mode_{block['id']}"] = False
            st.success("Блок обновлён!")
            st.rerun()


def get_block_icon(block_type):
    icons = {
        "chart": "📈",
        "table": "📋",
        "pivot": "📊",
        "value_card": "💳",
    }
    return icons.get(block_type, "📦")
