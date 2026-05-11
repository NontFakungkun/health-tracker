import streamlit as st
from datetime import datetime, timedelta

COOKIE_NAME = "ht_session"
COOKIE_DAYS = 30


def _cookie_manager():
    try:
        import extra_streamlit_components as stx
        return stx.CookieManager(key="ht_cookie_mgr")
    except Exception:
        return None


def require_login():
    # Must render the cookie component unconditionally (before any st.stop)
    cm = _cookie_manager()

    # Check cookie to restore session without re-entering password
    if not st.session_state.get("authenticated") and cm is not None:
        try:
            cookies = cm.get_all()
            if isinstance(cookies, dict) and cookies.get(COOKIE_NAME) == "ok":
                st.session_state.authenticated = True
        except Exception:
            pass

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
                if cm is not None:
                    try:
                        cm.set(COOKIE_NAME, "ok",
                               expires_at=datetime.now() + timedelta(days=COOKIE_DAYS))
                    except Exception:
                        pass
                st.rerun()
            else:
                st.error("Wrong password.")

    st.stop()


def logout():
    st.session_state.authenticated = False
    cm = _cookie_manager()
    if cm is not None:
        try:
            cm.delete(COOKIE_NAME)
        except Exception:
            pass
    st.rerun()
