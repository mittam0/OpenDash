import hashlib
import streamlit as st
from app.config import PASSWORD_SALT
from app.models import get_user_by_username


def hash_password(password):
    return hashlib.sha256((PASSWORD_SALT + password).encode()).hexdigest()


def authenticate(username, password):
    user = get_user_by_username(username)
    if user and user["password_hash"] == hash_password(password):
        return user
    return None


def login_user(username, password):
    user = authenticate(username, password)
    if user:
        st.session_state.logged_in = True
        st.session_state.username = user["username"]
        st.session_state.user_id = user["id"]
        st.session_state.role = user["role"]
        return True
    return False


def logout_user():
    for key in ["logged_in", "username", "user_id", "role", "page"]:
        st.session_state.pop(key, None)


def check_authentication():
    return st.session_state.get("logged_in", False)
