import streamlit as st
import pandas as pd
from app.utils.data_source import load_data


def render(block):
    df = load_data(block)
    config = block.get("config", {})

    if df is None or df.empty:
        st.info("Нет данных для отображения")
        return

    value_col = config.get("value_column", df.columns[0] if len(df.columns) > 0 else "")
    value_label = config.get("value_label", value_col)
    fmt = config.get("format_string", "{:.2f}")
    prefix = config.get("prefix", "")
    suffix = config.get("suffix", "")
    delta_col = config.get("delta_column", None)

    if value_col not in df.columns:
        st.warning(f"Колонка '{value_col}' не найдена")
        return

    value = df[value_col].iloc[0] if len(df) > 0 else 0
    delta = None
    if delta_col and delta_col in df.columns:
        delta = df[delta_col].iloc[0] if len(df) > 0 else None

    try:
        if isinstance(value, (int, float)):
            display_value = f"{prefix}{fmt.format(value)}{suffix}"
            if delta is not None and isinstance(delta, (int, float)):
                st.metric(label=value_label, value=display_value, delta=f"{delta:+.2f}")
            else:
                st.metric(label=value_label, value=display_value)
        else:
            st.metric(label=value_label, value=str(value))
    except Exception:
        st.metric(label=value_label, value=str(value))


def render_config(block):
    df = load_data(block)
    config = block.get("config", {})

    if df is None or df.empty:
        st.warning("Загрузите данные, чтобы настроить карточку")
        return config

    columns = list(df.columns)

    value_col = st.selectbox(
        "Колонка со значением",
        columns,
        index=columns.index(config.get("value_column", columns[0]))
        if config.get("value_column") in columns
        else 0,
        key=f"vc_col_{block['id']}",
    )

    value_label = st.text_input(
        "Подпись значения",
        value=config.get("value_label", value_col),
        key=f"vc_label_{block['id']}",
    )

    prefix = st.text_input(
        "Префикс",
        value=config.get("prefix", ""),
        key=f"vc_prefix_{block['id']}",
    )

    suffix = st.text_input(
        "Суффикс",
        value=config.get("suffix", ""),
        key=f"vc_suffix_{block['id']}",
    )

    fmt = st.text_input(
        "Формат числа",
        value=config.get("format_string", "{:.2f}"),
        key=f"vc_fmt_{block['id']}",
    )

    delta_col = st.selectbox(
        "Колонка дельты (изменения)",
        [None] + columns,
        index=0 if config.get("delta_column") is None
        else (columns.index(config["delta_column"]) + 1)
        if config.get("delta_column") in columns
        else 0,
        key=f"vc_delta_{block['id']}",
    )

    return {
        "value_column": value_col,
        "value_label": value_label,
        "prefix": prefix,
        "suffix": suffix,
        "format_string": fmt,
        "delta_column": delta_col,
    }
