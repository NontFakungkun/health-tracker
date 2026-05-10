import streamlit as st


def require_login():
    if st.session_state.get("authenticated"):
        return

    st.markdown("""
<style>
.login-box {
    max-width: 380px;
    margin: 80px auto 0 auto;
    text-align: center;
}
</style>
<div class="login-box"></div>
""", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("## 💪 Health Tracker")
        st.markdown("Enter your password to continue.")
        st.markdown("")

        pwd = st.text_input("Password", type="password", key="login_pwd", label_visibility="collapsed",
                            placeholder="Password")

        if st.button("Login", type="primary", use_container_width=True):
            correct = st.secrets.get("app_password", "")
            if pwd == correct:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Wrong password.")

    st.stop()
