import streamlit as st

COOKIE_NAME = "ht_session"
COOKIE_MAX_AGE = 30 * 24 * 3600  # 30 days in seconds


def _controller():
    try:
        from streamlit_cookies_controller import CookieController
        return CookieController()
    except Exception:
        return None


def require_login():
    ctrl = _controller()

    # Already authenticated this session — nothing to do
    if st.session_state.get("authenticated"):
        return

    if ctrl is not None:
        try:
            val = ctrl.get(COOKIE_NAME)

            if val == "ok":
                st.session_state.authenticated = True
                # Rolling expiry: reset the cookie to 30 days from now on every visit
                ctrl.set(COOKIE_NAME, "ok", max_age=COOKIE_MAX_AGE)
                return

            # Cookie component needs one render cycle to initialise —
            # rerun once so it can hand back the cookie value before we
            # decide the user is logged out.
            if not st.session_state.get("_auth_init"):
                st.session_state._auth_init = True
                st.rerun()

        except Exception:
            pass

    if st.session_state.get("authenticated"):
        return

    # ── Login form ──────────────────────────────────────────────
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
                if ctrl is not None:
                    try:
                        ctrl.set(COOKIE_NAME, "ok", max_age=COOKIE_MAX_AGE)
                    except Exception:
                        pass
                st.rerun()
            else:
                st.error("Wrong password.")

    st.stop()


def logout():
    st.session_state.authenticated = False
    ctrl = _controller()
    if ctrl is not None:
        try:
            ctrl.remove(COOKIE_NAME)
        except Exception:
            pass
    st.rerun()
