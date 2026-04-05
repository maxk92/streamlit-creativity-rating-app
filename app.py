"""
Creativity Rating App - Streamlit Version

Main application file with navigation and session state management.
"""
import streamlit as st

import os
import sys

# Add utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from utils.user import User
from utils.config_loader import load_config

# Load config early so st.set_page_config() can use it
# (must be called before any other st.* calls)
_early_config = {}
try:
    _early_config = load_config() or {}
except Exception:
    pass
_app_cfg = _early_config.get('app', {})

st.set_page_config(
    page_title=_app_cfg.get('title', 'Rating App'),
    page_icon=_app_cfg.get('icon', ''),
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hide sidebar navigation button
st.markdown(
    """
    <style>
        [data-testid="collapsedControl"] {
            display: none;
        }
        section[data-testid="stSidebar"] {
            display: none;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize session state
def get_starting_page(config):
    """Determine the first page to show based on skip settings in config."""
    settings = (config or {}).get('settings', {})
    if not settings.get('skip_welcome', False):
        return 'welcome'
    if not settings.get('skip_login', False):
        return 'login'
    if not settings.get('skip_consent', False):
        return 'consent'
    if not settings.get('skip_questionnaire', False):
        return 'questionnaire'
    if settings.get('enable_familiarization', True):
        return 'pre_familiarization'
    return 'videoplayer'


def init_session_state():
    """Initialize session state variables if not already set."""
    if 'user' not in st.session_state:
        st.session_state.user = User()

    if 'config' not in st.session_state:
        st.session_state.config = _early_config if _early_config else None
        if not st.session_state.config:
            st.error("Failed to load configuration. Please check config/config.yaml.")

    if 'page' not in st.session_state:
        st.session_state.page = get_starting_page(st.session_state.config)

    # Pre-set consent when consent page is skipped
    if 'consent_given' not in st.session_state:
        settings = (st.session_state.config or {}).get('settings', {})
        if settings.get('skip_consent', False):
            st.session_state.consent_given = True

    if 'user_id_confirmed' not in st.session_state:
        st.session_state.user_id_confirmed = False

# Navigation function
def navigate_to(page_name):
    """Navigate to a specific page."""
    st.session_state.page = page_name
    st.rerun()

# Initialize
init_session_state()

# Trigger device detection once per session.
# Placed here (before any page content) so the single JS eval iframe renders
# at the top of the app on first load rather than inside a specific page.
from utils.device_detection import get_device_info_cached
get_device_info_cached()

# Display current page based on session state
current_page = st.session_state.page

if current_page == 'welcome':
    import pages.welcome as welcome
    welcome.show()

elif current_page == 'login':
    import pages.login as login
    login.show()

elif current_page == 'consent':
    import pages.consent as consent
    consent.show()

elif current_page == 'questionnaire':
    import pages.questionnaire as questionnaire
    questionnaire.show()

elif current_page == 'pre_familiarization':
    import pages.pre_familiarization as pre_familiarization
    pre_familiarization.show()

elif current_page == 'familiarization':
    import pages.familiarization as familiarization
    familiarization.show()

elif current_page == 'post_familiarization':
    import pages.post_familiarization as post_familiarization
    post_familiarization.show()

elif current_page == 'videoplayer':
    import pages.videoplayer as videoplayer
    videoplayer.show()

else:
    st.error(f"Unknown page: {current_page}")
    st.button("Go to Welcome", on_click=lambda: navigate_to('welcome'))
