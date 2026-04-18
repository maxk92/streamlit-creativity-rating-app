"""
Post-familiarization instructions page.
Displays reminder and creativity definition before the main rating task.
"""
import streamlit as st
import os

_DOCS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'docs')


@st.dialog("Creativity Definition (English)")
def _show_definition_en():
    path = os.path.join(_DOCS_DIR, 'creativity_definition_en.md')
    st.markdown(open(path).read())


@st.dialog("Kreativitätsdefinition (Deutsch)")
def _show_definition_de():
    path = os.path.join(_DOCS_DIR, 'creativity_definition_de.md')
    st.markdown(open(path).read())


def _definition_buttons():
    col1, col2, _ = st.columns([2, 2, 1])
    with col1:
        if st.button("📖 Show Creativity Definition (English)", use_container_width=True):
            _show_definition_en()
    with col2:
        if st.button("📖 Kreativitätsdefinition anzeigen (Deutsch)", use_container_width=True):
            _show_definition_de()


def show():
    """Display the post-familiarization instructions screen."""
    config = st.session_state.get('config', {}) or {}
    page_cfg = config.get('pages', {}).get('post_familiarization', {})

    success_message = page_cfg.get('success_message', '')
    text_before = page_cfg.get('text_before_definitions', '')
    text_after = page_cfg.get('text_after_definitions', '')

    if success_message:
        st.success(success_message)
    st.markdown("---")
    st.markdown(text_before)
    _definition_buttons()
    st.markdown(text_after)

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
