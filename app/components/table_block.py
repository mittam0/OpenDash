import streamlit as st
import pandas as pd
from app.utils.data_source import load_data


def render(block):
    df = load_data(block)
    config = block.get("config", {})

    if df is None or df.empty:
        st.info("Нет данных для отображения")
        return

    page_size = config.get("page_size", 20)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        height=min(400, 35 * min(len(df), page_size) + 40),
    )

    if len(df) > page_size:
        total_pages = (len(df) + page_size - 1) // page_size
        st.caption(f"Всего строк: {len(df)} | "
                   f"Показано первых {page_size} из {len(df)}")


def render_config(block):
    config = block.get("config", {})

    page_size = st.number_input(
        "Размер страницы",
        min_value=5, max_value=100, step=5,
        value=config.get("page_size", 20),
        key=f"page_size_{block['id']}",
    )

    show_search = st.checkbox(
        "Показать поиск",
        value=config.get("show_search", True),
        key=f"show_search_{block['id']}",
    )

    return {
        "page_size": page_size,
        "show_search": show_search,
    }
