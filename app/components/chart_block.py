import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from app.utils.data_source import load_data


def render(block):
    df = load_data(block)
    config = block.get("config", {})

    if df is None or df.empty:
        st.info("Нет данных для отображения")
        return

    chart_type = config.get("chart_type", "line")
    x_col = config.get("x_column", df.columns[0] if len(df.columns) > 0 else "")
    y_cols = config.get("y_columns", [df.columns[1] if len(df.columns) > 1 else ""])
    group_col = config.get("group_column", None)
    aggregation = config.get("aggregation", None)
    chart_title = config.get("title", block.get("title", ""))

    if not x_col or x_col not in df.columns:
        x_col = df.columns[0]
    valid_y = [c for c in y_cols if c in df.columns]
    if not valid_y:
        valid_y = [df.columns[1]] if len(df.columns) > 1 else [df.columns[0]]

    fig = None
    try:
        if chart_type == "line":
            if group_col and group_col in df.columns:
                fig = px.line(df, x=x_col, y=valid_y, color=group_col, title=chart_title)
            else:
                fig = px.line(df, x=x_col, y=valid_y, title=chart_title)
        elif chart_type == "bar":
            if group_col and group_col in df.columns:
                fig = px.bar(df, x=x_col, y=valid_y, color=group_col, title=chart_title, barmode="group")
            else:
                fig = px.bar(df, x=x_col, y=valid_y, title=chart_title)
        elif chart_type == "scatter":
            if group_col and group_col in df.columns:
                fig = px.scatter(df, x=x_col, y=valid_y, color=group_col, title=chart_title)
            else:
                fig = px.scatter(df, x=x_col, y=valid_y, title=chart_title)
        elif chart_type == "pie":
            if valid_y:
                fig = px.pie(df, names=x_col, values=valid_y[0], title=chart_title)
            else:
                fig = px.pie(df, names=x_col, title=chart_title)
        elif chart_type == "area":
            if group_col and group_col in df.columns:
                fig = px.area(df, x=x_col, y=valid_y, color=group_col, title=chart_title)
            else:
                fig = px.area(df, x=x_col, y=valid_y, title=chart_title)
        elif chart_type == "histogram":
            if group_col and group_col in df.columns:
                fig = px.histogram(df, x=x_col, color=group_col, title=chart_title)
            else:
                fig = px.histogram(df, x=x_col, title=chart_title)
    except Exception as e:
        st.error(f"Ошибка построения графика: {e}")
        return

    if fig:
        fig.update_layout(
            height=config.get("height", 400),
            margin=dict(l=20, r=20, t=40, b=20),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Не удалось построить график")


def render_config(block):
    df = load_data(block)
    config = block.get("config", {})

    if df is None or df.empty:
        st.warning("Загрузите данные, чтобы настроить график")
        return config

    columns = list(df.columns)
    numeric_cols = list(df.select_dtypes(include=["number"]).columns)

    chart_type = st.selectbox(
        "Тип графика",
        ["line", "bar", "scatter", "pie", "area", "histogram"],
        index=["line", "bar", "scatter", "pie", "area", "histogram"].index(
            config.get("chart_type", "line")
        ),
        key=f"chart_type_{block['id']}",
    )

    x_col = st.selectbox(
        "Ось X",
        columns,
        index=columns.index(config.get("x_column", columns[0]))
        if config.get("x_column") in columns
        else 0,
        key=f"x_col_{block['id']}",
    )

    available_y = numeric_cols if numeric_cols else columns
    y_cols = st.multiselect(
        "Ось Y (значения)",
        available_y,
        default=[c for c in config.get("y_columns", []) if c in available_y]
        or [available_y[0]] if available_y else [],
        key=f"y_cols_{block['id']}",
    )

    group_col = st.selectbox(
        "Группировка (цвет)",
        [None] + columns,
        index=0 if config.get("group_column") is None
        else (columns.index(config["group_column"]) + 1)
        if config.get("group_column") in columns
        else 0,
        key=f"group_col_{block['id']}",
    )

    title = st.text_input(
        "Заголовок графика",
        value=config.get("title", ""),
        key=f"chart_title_{block['id']}",
    )

    height = st.number_input(
        "Высота (px)", min_value=200, max_value=800, step=50,
        value=config.get("height", 400),
        key=f"chart_height_{block['id']}",
    )

    new_config = {
        "chart_type": chart_type,
        "x_column": x_col,
        "y_columns": y_cols,
        "group_column": group_col,
        "title": title,
        "height": height,
    }
    return new_config
