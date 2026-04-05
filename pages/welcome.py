"""
Welcome page - Initial instructions screen.
"""
import streamlit as st

def show():
    """Display the welcome screen."""
    config = st.session_state.get('config', {}) or {}
    body = config.get('pages', {}).get('welcome', {}).get('body', '')
    st.markdown(body)

    st.markdown("")  # Spacing

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("▶️ Next", use_container_width=True, type="primary"):
            st.session_state.page = 'login'
            st.rerun()
