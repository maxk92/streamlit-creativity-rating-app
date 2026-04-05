"""
Login page - Check if user has participated before.
"""
import streamlit as st
from utils.data_persistence import user_exists, get_all_existing_user_ids, save_user_data
from utils.navigation import get_next_page


def show():
    """Display the login screen."""
    config = st.session_state.config
    settings = config.get('settings', {})

    # If a new-user ID was just generated (skip_questionnaire path), show confirmation panel
    if st.session_state.get('login_id_generated', False):
        _show_id_confirmation(config)
        return

    st.title("🔐 Login")

    st.markdown("### Have you participated in this study before?")

    # Radio button for Yes/No
    participated = st.radio(
        "Select one:",
        options=["No, this is my first time", "Yes, I have participated before"],
        key="participated_radio",
        label_visibility="collapsed"
    )

    st.markdown("")  # Spacing

    # If user selected "Yes", show user ID input
    if participated == "Yes, I have participated before":
        st.markdown("### Please enter your User ID")

        user_id_input = st.text_input(
            "User ID:",
            key="user_id_input",
            placeholder="Enter your user ID (e.g., ABCD12 or giha3042)",
            help="Your user ID was shown to you after completing the questionnaire"
        ).strip()

        # Check if user ID exists
        if user_id_input:
            if user_exists(user_id_input):
                st.success(f"✓ User ID '{user_id_input}' found!")
                st.session_state.user_id_valid = True
                # Store the user ID as entered (preserve original case)
                st.session_state.validated_user_id = user_id_input
            else:
                st.error("⚠️ User ID not found. Please check your ID or select 'No' if this is your first time.")
                st.info("💡 If you cannot remember your user ID, please reach out to the study administration.")
                st.session_state.user_id_valid = False
        else:
            st.session_state.user_id_valid = False

    # Navigation buttons
    st.markdown("")
    st.markdown("")
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("◀️ Back", use_container_width=True):
            st.session_state.page = 'welcome'
            st.rerun()

    with col3:
        if st.button("Next ▶️", use_container_width=True, type="primary"):
            if participated == "Yes, I have participated before":
                if not user_id_input:
                    st.error("Please enter your user ID")
                    st.info("💡 If you cannot remember your user ID, please reach out to the study administration.")
                    st.stop()
                elif not st.session_state.get('user_id_valid', False):
                    st.error("User ID not found. Please check your ID.")
                    st.info("💡 If you cannot remember your user ID, please reach out to the study administration.")
                    st.stop()
                else:
                    # Valid returning user — jump directly past questionnaire
                    st.session_state.user.user_id = st.session_state.get('validated_user_id', user_id_input)
                    enable_familiarization = settings.get('enable_familiarization', True)
                    st.session_state.page = 'pre_familiarization' if enable_familiarization else 'videoplayer'
                    st.rerun()
            else:
                # New user
                skip_questionnaire = settings.get('skip_questionnaire', False)
                skip_consent = settings.get('skip_consent', False)

                if skip_questionnaire:
                    # Generate ID immediately; show confirmation before proceeding
                    user = st.session_state.user
                    try:
                        existing_ids = get_all_existing_user_ids()
                        user.generate_random_user_id(existing_ids)
                        st.session_state.login_id_generated = True
                        st.rerun()
                    except Exception as e:
                        st.error(f"⚠️ Failed to generate user ID: {e}")
                else:
                    # Must go through questionnaire; skip consent if configured
                    st.session_state.page = 'questionnaire' if skip_consent else 'consent'
                    st.rerun()


def _show_id_confirmation(config):
    """Confirmation panel shown to new users when questionnaire is skipped."""
    user = st.session_state.user

    st.title("✅ User ID Generated")
    st.markdown("### Your User ID has been generated:")
    st.markdown(f"# `{user.user_id}`")

    st.warning("""
    **⚠️ IMPORTANT: Please memorize or write down your User ID!**

    You will need this ID if you want to continue rating videos in a future session.
    This ID is the only way to link your ratings across sessions.
    """)

    st.markdown("---")

    col1, col2, col3 = st.columns([1, 1, 1])

    with col3:
        if st.button("Understood. Proceed ▶️", use_container_width=True, type="primary"):
            if save_user_data(user):
                st.session_state.login_id_generated = False
                st.session_state.page = get_next_page('questionnaire', config)
                st.rerun()
            else:
                st.error("Failed to save user data. Please try again.")
