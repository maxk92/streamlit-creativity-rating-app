"""
Pre-familiarization instructions page — 3-step flow.
Step 0: Identifying the correct action
Step 1: Creativity definition (inline, EN/DE toggle)
Step 2: Additional rating dimensions + loading note
"""
import streamlit as st
import os

_DOCS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'docs')


def _nav_buttons(back_label, back_action, next_label, next_action, confirm_key=None, confirm_msg=None):
    """Render back / next button row."""
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button(f"◀️ {back_label}", use_container_width=True):
            if confirm_key:
                if st.session_state.get(confirm_key, False):
                    back_action()
                else:
                    st.session_state[confirm_key] = True
                    st.warning(confirm_msg or "⚠️ Click again to confirm.")
            else:
                back_action()
    with col3:
        if st.button(f"{next_label} ▶️", use_container_width=True, type="primary"):
            next_action()


def _go_to_step(n):
    st.session_state.pre_famil_step = n
    st.rerun()


def _go_to_login():
    st.session_state.pre_famil_step = 0
    st.session_state.user_id_confirmed = False
    st.session_state.page = 'login'
    st.rerun()


# ---------------------------------------------------------------------------
# Step 0 — Identifying the action
# ---------------------------------------------------------------------------

def _show_step_0():
    st.markdown("### Instructions — Step 1 of 3: Identifying the Action")
    st.markdown("---")

    st.markdown("""
Each video clip shows a short soccer action. Because soccer is fast-paced, a clip
may contain **more than one action** in quick succession. To help you identify the
**specific action** you are asked to rate, two pieces of information are displayed
alongside every video:

- **Metadata bar** (top) — shows the team, player name, jersey number, action type,
  and body part involved in the action.
- **Pitch drawing** (right) — shows the ball trajectory during the action, so you
  can see where on the pitch it took place and in which direction.

Please use both to make sure you are rating the **correct** action.

If you are **not certain** which action is meant, press the
**"⚠️ Action not recognized"** button rather than guessing.
It is essential that you are confident you are rating the intended action.

The screenshot below shows what the rating screen looks like:
""")

    screenshot = os.path.join(_DOCS_DIR, 'videoplayerscreen.png')
    if os.path.exists(screenshot):
        st.image(screenshot, width=500)
    else:
        st.warning("Screenshot not found.")

    st.markdown("---")
    _nav_buttons(
        back_label="Back to Login Screen",
        back_action=_go_to_login,
        next_label="Next",
        next_action=lambda: _go_to_step(1),
        confirm_key="confirm_back_pre_famil_0",
        confirm_msg="⚠️ Click again to confirm going back to the login screen.",
    )


# ---------------------------------------------------------------------------
# Step 1 — Creativity definition
# ---------------------------------------------------------------------------

def _show_step_1():
    st.markdown("### Instructions — Step 2 of 3: The Creativity Definition")
    st.markdown("---")

    st.markdown(
        "The foundation for your creativity ratings is the definition below. "
        "Please read it carefully — you can return to it at any time during the experiment."
    )
    st.markdown("")

    if 'pre_famil_lang' not in st.session_state:
        st.session_state.pre_famil_lang = 'en'

    lang = st.session_state.pre_famil_lang

    # Language toggle button (compact, secondary style)
    toggle_col, _ = st.columns([1, 3])
    with toggle_col:
        if lang == 'en':
            if st.button("🇩🇪 Deutsche Version", use_container_width=True):
                st.session_state.pre_famil_lang = 'de'
                st.rerun()
        else:
            if st.button("🇬🇧 English Version", use_container_width=True):
                st.session_state.pre_famil_lang = 'en'
                st.rerun()

    st.markdown("---")

    # Center-align text inside the success callout
    st.markdown(
        """<style>
        div[data-testid="stAlert"] h1,
        div[data-testid="stAlert"] h2,
        div[data-testid="stAlert"] h3,
        div[data-testid="stAlert"] h4 {
            text-align: center !important;
            font-size: calc(2rem - 3px) !important;
        }
        div[data-testid="stAlert"] p,
        div[data-testid="stAlert"] li {
            text-align: center !important;
            font-size: 22px !important;
        }
        </style>""",
        unsafe_allow_html=True,
    )
    path = os.path.join(_DOCS_DIR, f'creativity_definition_{lang}.md')
    st.success(open(path).read())

    st.markdown("---")
    _nav_buttons(
        back_label="Back",
        back_action=lambda: _go_to_step(0),
        next_label="Next",
        next_action=lambda: _go_to_step(2),
    )


# ---------------------------------------------------------------------------
# Step 2 — Additional dimensions + loading note
# ---------------------------------------------------------------------------

def _show_step_2():
    st.markdown("### Instructions — Step 3 of 3: Additional Rating Dimensions")
    st.markdown("---")

    st.markdown("""
In addition to creativity, you will rate each action on **two further dimensions**:

#### Technical Correctness
How technically well was the action executed? This refers to the **precision, control,
and skill** with which the action was performed — regardless of whether it was creative
or not. A technically perfect pass that is completely ordinary is rated high here;
a sloppy but original trick is rated low.

*(1 = very poor technique — 7 = perfect technique)*

#### Aesthetic Appeal
How **visually appealing or pleasing** was the action to watch? This is a subjective
impression of elegance, style, or beauty of movement — independent of effectiveness
or creativity.

*(1 = not appealing at all — 7 = extremely appealing)*
""")

    st.markdown("---")

    st.markdown(
        """<style>
        div[data-testid="stAlert"] p { font-size: 24px !important; }
        </style>""",
        unsafe_allow_html=True,
    )
    st.info(
        "⏳ **Please note:** Loading the videos might take a moment. "
        "Please do not refresh or close the app."
    )

    st.markdown("---")
    _nav_buttons(
        back_label="Back",
        back_action=lambda: _go_to_step(1),
        next_label="Begin Practice Trials",
        next_action=_start_famil,
    )


def _start_famil():
    st.session_state.pre_famil_step = 0
    st.session_state.page = 'familiarization'
    st.rerun()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def show():
    if 'pre_famil_step' not in st.session_state:
        st.session_state.pre_famil_step = 0

    step = st.session_state.pre_famil_step

    if step == 0:
        _show_step_0()
    elif step == 1:
        _show_step_1()
    else:
        _show_step_2()
