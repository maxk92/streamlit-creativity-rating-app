"""
Pre-familiarization instructions page.
Displays introductory text before the familiarization trials begin.
"""
import streamlit as st
from utils.navigation import get_prev_page

def show():
    """Display the pre-familiarization instructions screen."""
    config = st.session_state.get('config', {}) or {}
    body = config.get('pages', {}).get('pre_familiarization', {}).get('body', '')
    st.markdown(body)

    st.markdown("---")

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("◀️ Back to Questionnaire", use_container_width=True):
            if st.session_state.get('confirm_back_pre_famil', False):
                st.session_state.page = get_prev_page('pre_familiarization', config)
                st.session_state.user_id_confirmed = False
                st.rerun()
            else:
                st.session_state.confirm_back_pre_famil = True
                st.warning("⚠️ Click again to confirm.")

    with col3:
        if st.button("Begin Practice Trials ▶️", use_container_width=True, type="primary"):
            st.session_state.page = 'familiarization'
            st.session_state.confirm_back_pre_famil = False
            st.rerun()
