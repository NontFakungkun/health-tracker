import streamlit as st
from streamlit_cookies_controller import CookieController

COOKIE_NAME = "ht_session"
COOKIE_EXPIRES_DAYS = 30


def _ctrl() -> CookieController:
    return CookieController(key="auth_ctrl")


def require_login():
    if st.session_state.get("authenticated"):
        return

    ctrl = _ctrl()
    if ctrl.get(COOKIE_NAME) == "ok":
        st.session_state.authenticated = True
        return

    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown("## 💪 Health Tracker")
        st.markdown("")
        pwd = st.text_input(
            "Password", type="password", key="login_pwd",
            label_visibility="collapsed", placeholder="Password",
        )
        if st.button("Login", type="primary", width='stretch'):
            correct = st.secrets.get("app_password", "")
            if pwd == correct:
                st.session_state.authenticated = True
                ctrl.set(COOKIE_NAME, "ok", expires=COOKIE_EXPIRES_DAYS)
                st.rerun()
            else:
                st.error("Wrong password.")

    st.stop()


def logout():
    ctrl = _ctrl()
    ctrl.remove(COOKIE_NAME)
    st.session_state.authenticated = False
    st.rerun()
