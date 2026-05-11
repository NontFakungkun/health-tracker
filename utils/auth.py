import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime, timedelta

COOKIE_NAME = "ht_session"
COOKIE_DAYS = 30


# ── Write via raw JS (confirmed to persist to browser DevTools) ────────────

def _cookie_string(value: str, days: int) -> str:
    expires = (datetime.utcnow() + timedelta(days=days)).strftime("%a, %d %b %Y %H:%M:%S GMT")
    return f"{COOKIE_NAME}={value}; expires={expires}; path=/; SameSite=Lax"


def _set_cookie(value: str = "ok"):
    cookie = _cookie_string(value, COOKIE_DAYS)
    components.html(
        f"<script>try{{window.parent.document.cookie='{cookie}';}}catch(e){{document.cookie='{cookie}';}}</script>",
        height=0, width=0,
    )


def _clear_cookie():
    gone = f"{COOKIE_NAME}=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/"
    components.html(
        f"<script>try{{window.parent.document.cookie='{gone}';}}catch(e){{document.cookie='{gone}';}}</script>",
        height=0, width=0,
    )


# ── Read via st.context.cookies (Python-side, synchronous, no JS round-trip) ─

def _read_cookie() -> str | None:
    try:
        return st.context.cookies.get(COOKIE_NAME)
    except AttributeError:
        return None  # Streamlit < 1.37 — fall back gracefully


# ── Main entry ─────────────────────────────────────────────────────────────

def require_login():
    # PATH 1: already authenticated this session
    if st.session_state.get("authenticated"):
        if not st.session_state.get("_cookie_refreshed"):
            _set_cookie()  # rolling 30-day expiry on first render of each session
            st.session_state._cookie_refreshed = True
        return

    # PATH 2: check real browser cookie (synchronous — no async component needed)
    if _read_cookie() == "ok":
        st.session_state.authenticated = True
        st.session_state._cookie_refreshed = True
        return

    # PATH 3: no cookie — show login form
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
                st.session_state._cookie_refreshed = False  # trigger set on next render
                st.rerun()
            else:
                st.error("Wrong password.")

    st.stop()


def logout():
    st.session_state.authenticated = False
    st.session_state._cookie_refreshed = False
    _clear_cookie()
    st.rerun()


def debug_cookie_state():
    st.write("**Cookie debug**")
    st.write("authenticated:", st.session_state.get("authenticated"))
    st.write("cookie via st.context:", _read_cookie())
    components.html(
        """
        <div id='rc' style='font-family:monospace;font-size:11px;color:#aaa'></div>
        <script>
            try { document.getElementById('rc').innerText = "parent cookies: " + window.parent.document.cookie; }
            catch (e) { document.getElementById('rc').innerText = "iframe cookies: " + document.cookie; }
        </script>
        """,
        height=30,
    )
