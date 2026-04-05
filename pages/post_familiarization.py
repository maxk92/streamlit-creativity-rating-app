"""
Post-familiarization instructions page.
Displays instructions for the final rating procedure.
"""
import streamlit as st

def show():
    """Display the post-familiarization instructions screen."""
    config = st.session_state.get('config', {}) or {}
    page_cfg = config.get('pages', {}).get('post_familiarization', {})
    success_message = page_cfg.get('success_message', '')
    body = page_cfg.get('body', '')

    if success_message:
        st.success(success_message)
    st.markdown("---")
    st.markdown(body)

    st.markdown("---")

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("◀️ Back to Questionnaire", use_container_width=True):
            if st.session_state.get('confirm_back_post_famil', False):
                st.session_state.page = 'questionnaire'
                st.session_state.user_id_confirmed = False
                st.rerun()
            else:
                st.session_state.confirm_back_post_famil = True
                st.warning("⚠️ Click again to confirm.")

    with col3:
        if st.button("Begin Main Rating Task ▶️", use_container_width=True, type="primary"):
            st.session_state.page = 'videoplayer'
            st.session_state.confirm_back_post_famil = False
            st.rerun()
