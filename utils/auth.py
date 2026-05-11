import streamlit as st
from datetime import datetime, timedelta

COOKIE_NAME = "ht_session"
COOKIE_DAYS = 30


@st.cache_resource
def _get_cookie_manager():
    try:
        import extra_streamlit_components as stx
        return stx.CookieManager(key="ht_cookie_mgr")
    except Exception:
        return None


def _read_auth_cookie() -> bool:
    cm = _get_cookie_manager()
    if cm is None:
        return False
    try:
        cookies = cm.get_all()
        return isinstance(cookies, dict) and cookies.get(COOKIE_NAME) == "ok"
    except Exception:
        return False


def _write_auth_cookie():
    cm = _get_cookie_manager()
    if cm is None:
        return
    try:
        cm.set(COOKIE_NAME, "ok", expires_at=datetime.now() + timedelta(days=COOKIE_DAYS))
    except Exception:
        pass


def _clear_auth_cookie():
    cm = _get_cookie_manager()
    if cm is None:
        return
    try:
        cm.delete(COOKIE_NAME)
    except Exception:
        pass


def require_login():
    # Render the invisible cookie component (must happen before st.stop)
    _get_cookie_manager()

    # Cookie check — sets session on first load after previous login
    if not st.session_state.get("authenticated") and _read_auth_cookie():
        st.session_state.authenticated = True

    if st.session_state.get("authenticated"):
        return

    # Login form
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown("## 💪 Health Tracker")
        st.markdown("")
        pwd = st.text_input(
            "Password", type="password", key="login_pwd",
            label_visibility="collapsed", placeholder="Password",
        )
        if st.button("Login", type="primary", use_container_width=True):
            correct = st.secrets.get("app_password", "")
            if pwd == correct:
                st.session_state.authenticated = True
                _write_auth_cookie()
                st.rerun()
            else:
                st.error("Wrong password.")

    st.stop()


def logout():
    st.session_state.authenticated = False
    _clear_auth_cookie()
    st.rerun()
