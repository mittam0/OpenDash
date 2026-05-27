import streamlit as st
from app.auth import login_user


def render():
    st.markdown("# OpenDash")
    st.markdown("### Вход в систему")

    with st.form("login_form"):
        username = st.text_input("Логин", placeholder="adm")
        password = st.text_input("Пароль", type="password", placeholder="adm")
        submitted = st.form_submit_button("Войти", type="primary", use_container_width=True)

        if submitted:
            if not username or not password:
                st.error("Введите логин и пароль")
            elif login_user(username, password):
                st.success("Успешный вход!")
                st.rerun()
            else:
                st.error("Неверный логин или пароль")
