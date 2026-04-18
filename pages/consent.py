"""
Consent page - Participant information and consent form.
"""
import streamlit as st
import os
from utils.navigation import get_next_page, get_prev_page

_DOCS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'docs')


@st.dialog("Participant Information and Informed Consent (English)", width="large")
def _show_consent_en():
    md_path = os.path.join(_DOCS_DIR, 'consent_en.md')
    pdf_path = os.path.join(_DOCS_DIR, 'consent_en.pdf')
    st.markdown(open(md_path).read())
    if os.path.exists(pdf_path):
        st.download_button(
            label="⬇️ Download as PDF",
            data=open(pdf_path, 'rb').read(),
            file_name="participant_information_en.pdf",
            mime="application/pdf",
            use_container_width=True,
        )


@st.dialog("Probandeninformation und Einwilligungserklärung (Deutsch)", width="large")
def _show_consent_de():
    md_path = os.path.join(_DOCS_DIR, 'consent_de.md')
    pdf_path = os.path.join(_DOCS_DIR, 'consent_de.pdf')
    st.markdown(open(md_path).read())
    if os.path.exists(pdf_path):
        st.download_button(
            label="⬇️ Als PDF herunterladen",
            data=open(pdf_path, 'rb').read(),
            file_name="probandeninformation_de.pdf",
            mime="application/pdf",
            use_container_width=True,
        )


def show():
    """Display the consent screen."""
    st.title("📋 Participant Information and Consent")
    st.markdown("---")

    st.markdown(
        "Please read the participant information carefully before providing your consent. "
        "You can open the full document in English or German below."
    )
    st.markdown("")

    col1, col2, _ = st.columns([2, 2, 1])
    with col1:
        if st.button("📄 Read Participant Information (English)", use_container_width=True, type="primary"):
            _show_consent_en()
    with col2:
        if st.button("📄 Probandeninformation lesen (Deutsch)", use_container_width=True, type="primary"):
            _show_consent_de()

    st.markdown("---")
    st.markdown("## Consent Declaration")

    consent_given = st.checkbox("**I confirm that**", key="consent_checkbox")

    st.markdown("""
1. I have read and understood the participant information
2. I consent to participate in this research study voluntarily
3. I understand that my participation is voluntary and I may withdraw at any time without consequence
4. I consent to the anonymous processing of my data for research purposes
5. I understand that my data will not be shared with third parties
6. I am at least 18 years old
""")

    st.markdown("")
    st.markdown("")

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("◀️ Back", use_container_width=True):
            st.session_state.page = get_prev_page('consent', st.session_state.config)
            st.rerun()

    with col3:
        if st.button("Next ▶️", use_container_width=True, type="primary"):
            if not consent_given:
                st.error("⚠️ You must provide your consent to proceed with the study.")
                st.stop()
            else:
                from datetime import datetime
                st.session_state.consent_given = True
                st.session_state.consent_timestamp = datetime.now().isoformat(timespec='seconds')
                st.session_state.page = get_next_page('consent', st.session_state.config)
                st.rerun()
