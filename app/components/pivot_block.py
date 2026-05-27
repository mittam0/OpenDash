import streamlit as st
import pandas as pd
from app.utils.data_source import load_data


def render(block):
    df = load_data(block)
    config = block.get("config", {})

    if df is None or df.empty:
        st.info("Нет данных для отображения")
        return

    index_cols = config.get("index_columns", [])
    col_cols = config.get("columns_columns", [])
    val_cols = config.get("values_columns", [])
    agg_func = config.get("agg_function", "sum")
    fill_val = config.get("fill_value", 0)

    if not index_cols or not val_cols:
        st.info("Настройте измерения сводной таблицы")
        return

    valid_index = [c for c in index_cols if c in df.columns]
    valid_col = [c for c in col_cols if c in df.columns]
    valid_val = [c for c in val_cols if c in df.columns]

    if not valid_index or not valid_val:
        st.warning("Выбранные колонки не найдены в данных")
        return

    try:
        pivot = df.pivot_table(
            index=valid_index,
            columns=valid_col if valid_col else None,
            values=valid_val,
            aggfunc=agg_func,
            fill_value=fill_val,
        )
        st.dataframe(pivot, use_container_width=True)
    except Exception as e:
        st.error(f"Ошибка построения сводной таблицы: {e}")


def render_config(block):
    df = load_data(block)
    config = block.get("config", {})

    if df is None or df.empty:
        st.warning("Загрузите данные, чтобы настроить сводную таблицу")
        return config

    columns = list(df.columns)
    numeric_cols = list(df.select_dtypes(include=["number"]).columns)

    index_cols = st.multiselect(
        "Строки (index)",
        columns,
        default=[c for c in config.get("index_columns", []) if c in columns],
        key=f"pivot_index_{block['id']}",
    )

    col_cols = st.multiselect(
        "Колонки (columns)",
        columns,
        default=[c for c in config.get("columns_columns", []) if c in columns],
        key=f"pivot_cols_{block['id']}",
    )

    val_cols = st.multiselect(
        "Значения (values)",
        numeric_cols if numeric_cols else columns,
        default=[c for c in config.get("values_columns", []) if c in (numeric_cols if numeric_cols else columns)],
        key=f"pivot_vals_{block['id']}",
    )

    agg_func = st.selectbox(
        "Агрегация",
        ["sum", "mean", "count", "min", "max", "median", "std"],
        index=["sum", "mean", "count", "min", "max", "median", "std"].index(
            config.get("agg_function", "sum")
        ),
        key=f"pivot_agg_{block['id']}",
    )

    fill_val = st.number_input(
        "Заполнить пустые значением",
        value=config.get("fill_value", 0),
        key=f"pivot_fill_{block['id']}",
    )

    return {
        "index_columns": index_cols,
        "columns_columns": col_cols,
        "values_columns": val_cols,
        "agg_function": agg_func,
        "fill_value": fill_val,
    }
