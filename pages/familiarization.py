"""
Familiarization trials page - Practice rating interface.
Displays familiarization videos with rating scales but doesn't save data.
Always shows the same 3 videos for all users.
"""
import streamlit as st
import streamlit.components.v1 as components
import os
import pandas as pd
import base64
import html

from utils.config_loader import load_rating_scales
from utils.video_rating_display import display_video_rating_interface
from utils.r2_manager import list_video_filenames, get_video_url, download_file_to_temp
from utils.metadata_loader import load_metadata

def display_video_with_mode(video_src, playback_mode='loop'):
    """
    Display video with specified playback mode.

    Parameters:
    - video_src: Local file path or URL (presigned R2 URL) of the video
    - playback_mode: 'loop' or 'once'
        - 'loop': Autoplay, loop enabled, controls visible
        - 'once': Autoplay, no loop, no controls (plays once only)
    """
    is_url = video_src.startswith(('http://', 'https://'))
    if not is_url and not os.path.exists(video_src):
        st.error(f"Video file not found: {video_src}")
        return

    if playback_mode == 'loop':
        # Loop mode: autoplay with controls and looping
        st.video(video_src, autoplay=True, loop=True)

    elif playback_mode == 'once':
        # Once mode: autoplay without controls, no loop, plays once only
        # URLs are streamed directly; local files are embedded as base64
        if is_url:
            source_src = html.escape(video_src)
        else:
            with open(video_src, 'rb') as f:
                video_bytes = f.read()
            source_src = f"data:video/mp4;base64,{base64.b64encode(video_bytes).decode()}"

        # Create HTML5 video player without controls
        # Use object-fit: contain to ensure video is never cropped
        video_html = f"""
        <div style="width: 100%; height: 100vh; display: flex; align-items: center; justify-content: center;">
            <video
                autoplay
                muted
                style="max-width: 100%; max-height: 100%; width: auto; height: auto; object-fit: contain;"
                onended="this.pause();"
            >
                <source src="{source_src}" type="video/mp4">
                Your browser does not support the video tag.
            </video>
        </div>
        <style>
            video::-webkit-media-controls {{
                display: none !important;
            }}
            video::-webkit-media-controls-enclosure {{
                display: none !important;
            }}
        </style>
        """
        config = st.session_state.get('config', {}) or {}
        height = config.get('settings', {}).get('video_player_height', 600)
        components.html(video_html, height=height)

    else:
        # Fallback to default
        st.video(video_src)

def _validate_familiarization_ratings(scale_values):
    """
    Validate that all required ratings are provided for familiarization trials.
    Checks both individual required scales and group requirements.

    Returns:
        List of error messages (empty if validation passes)
    """
    errors = []

    # If action not recognized, skip validation
    action_not_recognized = scale_values.get('_action_not_recognized', False)
    if action_not_recognized:
        return errors

    # Check individually required scales (not in groups)
    required_scales = st.session_state.get('required_scales', [])
    missing_scales = [
        title for title in required_scales
        if scale_values.get(title) is None or scale_values.get(title) == ''
    ]

    if missing_scales:
        errors.append(f"Required fields: {', '.join(missing_scales)}")

    # Check group requirements
    group_requirements = st.session_state.get('group_requirements', {})
    rating_scales = st.session_state.get('rating_scales', [])

    for group_id, group_info in group_requirements.items():
        required_count = group_info['number_of_ratings']
        error_msg = group_info.get('error_msg', '')
        group_title = group_info.get('title', group_id)

        # Find all scales in this group
        group_scales = [
            scale for scale in rating_scales
            if scale.get('group') == group_id
        ]

        # Count how many scales in this group have been changed
        changed_count = 0
        for scale in group_scales:
            title = scale.get('title')
            value = scale_values.get(title)

            # Check if value exists and is not empty
            if value is None or value == '':
                continue

            # For sliders, check if value has been changed from initial position
            if scale.get('type') == 'slider':
                initial_state = scale.get('initial_state', 'low')
                slider_min = scale.get('slider_min', 0)
                slider_max = scale.get('slider_max', 100)

                # Calculate initial value based on initial_state
                if initial_state == 'low':
                    initial_value = slider_min
                elif initial_state == 'high':
                    initial_value = slider_max
                else:  # center
                    initial_value = (slider_min + slider_max) / 2

                # Count as changed if value is different from initial
                if value != initial_value:
                    changed_count += 1
            else:
                # For discrete and text types, any non-empty value counts as changed
                changed_count += 1

        if changed_count < required_count:
            # Use custom error message if provided, otherwise use default
            if error_msg:
                errors.append(error_msg)
            else:
                errors.append(
                    f"Group '{group_title}': Please rate at least {required_count} emotions "
                    f"(currently {changed_count}/{required_count})"
                )

    return errors

def show():
    """Display the familiarization trials screen."""
    user = st.session_state.user
    config = st.session_state.config

    if not config:
        st.error("Configuration not loaded. Please restart the application.")
        return

    # Initialize familiarization state
    if 'familiarization_initialized' not in st.session_state:
        initialize_familiarization(config)

    # Check if there are videos to show
    if not st.session_state.get('familiarization_videos'):
        st.title("⚠️ Familiarization Videos Not Found")
        st.error(f"""
        No familiarization videos found in the configured directory.

        **Current path in config:** `{config['paths'].get('familiarization_video_path', 'videos_familiarization')}`

        **Current working directory:** `{os.getcwd()}`

        Please check:
        1. The familiarization_video_path in config.yaml is correct
        2. The directory exists and contains .mp4 files
        3. The path is correct relative to the app's working directory
        """)

        if st.button("◀️ Back to Pre-Familiarization", use_container_width=True):
            st.session_state.page = 'pre_familiarization'
            st.session_state.familiarization_initialized = False
            st.rerun()
        return

    # Load current video
    current_video_index = st.session_state.get('familiarization_video_index', 0)
    videos = st.session_state.familiarization_videos

    if current_video_index >= len(videos):
        # All familiarization videos completed - navigate to post-familiarization screen
        st.session_state.page = 'post_familiarization'
        st.session_state.familiarization_initialized = False
        st.rerun()
        return

    current_video = videos[current_video_index]

    # Branch on display mode
    display_mode = config.get('settings', {}).get('display_mode', 'combined')

    if display_mode == 'separate':
        if 'current_famil_screen' not in st.session_state:
            st.session_state.current_famil_screen = 'video'

        if st.session_state.current_famil_screen == 'video':
            display_famil_video_screen(current_video, config)
        else:
            display_famil_rating_screen(current_video, config)
    else:
        display_familiarization_interface(current_video, config)

def initialize_familiarization(config):
    """Initialize familiarization state - load videos and rating scales."""
    # Load rating scales (now returns dict with scales, groups, and requirements)
    rating_data = load_rating_scales(config)
    st.session_state.rating_scales = rating_data['scales']
    st.session_state.rating_groups = rating_data['groups']
    st.session_state.group_requirements = rating_data['group_requirements']

    # Track which scales are required individually (not in a group)
    st.session_state.required_scales = [
        scale.get('title') for scale in st.session_state.rating_scales
        if scale.get('required_to_proceed', True) and not scale.get('group')
    ]

    # Get video source from config
    video_source = config['paths'].get('video_source', 'local')

    # Get all video files based on source
    if video_source == 'r2':
        # Get videos from Cloudflare R2
        try:
            prefix = config['paths'].get('r2_familiarization_prefix', '')
            all_videos = list_video_filenames(prefix)
            # Sort to ensure consistent order for all users
            all_videos = sorted(all_videos)
            print(f"[INFO] Found {len(all_videos)} familiarization videos from R2")
            # Store prefix for later use
            st.session_state.familiarization_r2_prefix = prefix
            st.session_state.familiarization_video_source = 'r2'
        except Exception as e:
            st.error(f"Failed to load familiarization videos from R2: {e}")
            print(f"[ERROR] R2 error: {e}")
            all_videos = []
    else:
        # Get videos from local filesystem
        familiarization_path = config['paths'].get('familiarization_video_path', 'videos_familiarization')
        try:
            all_videos = [f for f in os.listdir(familiarization_path) if f.lower().endswith('.mp4')]
            # Sort to ensure consistent order for all users
            all_videos.sort()
            print(f"[INFO] Found {len(all_videos)} familiarization videos in {familiarization_path}")
            st.session_state.familiarization_path = familiarization_path
            st.session_state.familiarization_video_source = 'local'
        except FileNotFoundError:
            st.error(f"Familiarization video directory not found: {familiarization_path}")
            print(f"[ERROR] Directory not found: {familiarization_path}")
            print(f"[INFO] Current working directory: {os.getcwd()}")
            all_videos = []
        except Exception as e:
            st.error(f"Error loading familiarization videos: {e}")
            print(f"[ERROR] Error loading videos from {familiarization_path}: {e}")
            all_videos = []

    # Load metadata (same logic as initialize_video_player)
    metadata_path = config['paths'].get('metadata_path', '')
    metadata_source = config['paths'].get('metadata_source', 'local')
    if metadata_source == 'r2':
        metadata_path = download_file_to_temp(config['paths'].get('r2_metadata_key', ''))
        if not metadata_path:
            print("[WARNING] Failed to download metadata for familiarization from R2")
    df_metadata = load_metadata(metadata_path, [os.path.splitext(v)[0] for v in all_videos])

    # Store in session state
    st.session_state.familiarization_videos = all_videos
    st.session_state.familiarization_video_index = 0
    st.session_state.familiarization_metadata = df_metadata
    st.session_state.familiarization_initialized = True

def _resolve_famil_video_src(video_filename):
    """
    Resolve the playable familiarization video source (local path or presigned URL).

    Returns:
        Local file path or URL, or None if the video cannot be loaded.
    """
    video_source = st.session_state.get('familiarization_video_source', 'local')

    if video_source == 'r2':
        video_url = get_video_url(st.session_state.familiarization_r2_prefix, video_filename)

        if not video_url:
            st.error(f"⚠️ Failed to load familiarization video from R2: {video_filename}")
            st.warning("This video could not be loaded due to a network error. You can skip this video and continue.")
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("Skip to Next Video", use_container_width=True, type="primary"):
                    st.session_state.familiarization_video_index = st.session_state.get('familiarization_video_index', 0) + 1
                    st.session_state.current_famil_screen = 'video'
                    st.rerun()
            return None

        return video_url

    else:
        return os.path.join(st.session_state.familiarization_path, video_filename)


def display_famil_video_screen(video_filename, config):
    """Show the video-only screen for a familiarization trial (separate mode)."""
    current_index = st.session_state.familiarization_video_index
    total_videos = len(st.session_state.familiarization_videos)
    action_id = os.path.splitext(video_filename)[0]
    metadata = st.session_state.get('familiarization_metadata', pd.DataFrame())

    st.info(f"🎯 **Familiarization Trial — Video {current_index + 1} of {total_videos}**. These ratings will not be saved.")

    video_src = _resolve_famil_video_src(video_filename)
    if video_src is None:
        return

    display_video_rating_interface(
        video_filename=video_filename,
        video_src=video_src,
        config=config,
        rating_scales=[],
        key_prefix="famil_scale_",
        action_id=action_id,
        metadata=metadata,
        display_video_func=display_video_with_mode,
        display_mode='video_only'
    )

    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col3:
        if st.button("Continue to Rating ▶️", use_container_width=True, type="primary"):
            st.session_state.current_famil_screen = 'rating'
            st.rerun()


def display_famil_rating_screen(video_filename, config):
    """Show the rating-only screen for a familiarization trial (separate mode)."""
    rating_scales = st.session_state.rating_scales
    current_index = st.session_state.familiarization_video_index
    total_videos = len(st.session_state.familiarization_videos)
    action_id = os.path.splitext(video_filename)[0]
    metadata = st.session_state.get('familiarization_metadata', pd.DataFrame())

    st.info(f"🎯 **Familiarization Rating {current_index + 1} of {total_videos}**. These ratings will not be saved.")

    scale_values = display_video_rating_interface(
        video_filename=video_filename,
        video_src="",  # not used in rating_only mode
        config=config,
        rating_scales=rating_scales,
        key_prefix="famil_scale_",
        action_id=action_id,
        metadata=metadata,
        display_video_func=display_video_with_mode,
        display_mode='rating_only'
    )

    # "Action not recognized" advances immediately (no save for familiarization)
    if scale_values.get('_action_not_recognized', False):
        st.session_state.familiarization_video_index += 1
        st.session_state.current_famil_screen = 'video'
        st.session_state.confirm_back_famil = False
        st.rerun()

    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("◀️ Back to Video", use_container_width=True):
            st.session_state.current_famil_screen = 'video'
            st.rerun()

    with col3:
        if st.button("Continue ▶️", use_container_width=True, type="primary"):
            validation_errors = _validate_familiarization_ratings(scale_values)

            if validation_errors:
                st.error("⚠️ Please complete the required ratings:")
                for error in validation_errors:
                    st.warning(error)
                st.stop()

            st.session_state.familiarization_video_index += 1
            st.session_state.current_famil_screen = 'video'
            st.session_state.confirm_back_famil = False
            st.rerun()


def display_familiarization_interface(video_filename, config):
    """Display the familiarization rating interface (combined mode)."""
    rating_scales = st.session_state.rating_scales
    action_id = os.path.splitext(video_filename)[0]
    metadata = st.session_state.get('familiarization_metadata', pd.DataFrame())

    video_src = _resolve_famil_video_src(video_filename)
    if video_src is None:
        return {}

    # Define header content as a function
    def show_familiarization_header():
        current_index = st.session_state.familiarization_video_index
        total_videos = len(st.session_state.familiarization_videos)
        st.info(f"🎯 **Familiarization Trial** - **Video {current_index + 1} of {total_videos}**. These ratings will not be saved.")

    # Use shared display function
    scale_values = display_video_rating_interface(
        video_filename=video_filename,
        video_src=video_src,
        config=config,
        rating_scales=rating_scales,
        key_prefix="famil_scale_",
        action_id=action_id,
        metadata=metadata,
        header_content=show_familiarization_header,
        display_video_func=display_video_with_mode
    )

    # "Action not recognized" advances immediately (no save for familiarization)
    if scale_values.get('_action_not_recognized', False):
        st.session_state.familiarization_video_index += 1
        st.session_state.confirm_back_famil = False
        st.rerun()

    st.markdown("---")

    # Navigation and submission buttons
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("◀️ Back to Login Screen", use_container_width=True):
            if st.session_state.get('confirm_back_famil', False):
                st.session_state.page = 'login'
                st.session_state.user_id_confirmed = False
                st.session_state.familiarization_initialized = False
                st.rerun()
            else:
                st.session_state.confirm_back_famil = True
                st.warning("⚠️ Click again to confirm.")

    with col3:
        if st.button("Continue ▶️", use_container_width=True, type="primary"):
            validation_errors = _validate_familiarization_ratings(scale_values)

            if validation_errors:
                st.error("⚠️ Please complete the required ratings:")
                for error in validation_errors:
                    st.warning(error)
                st.stop()

            st.session_state.familiarization_video_index += 1
            st.session_state.confirm_back_famil = False
            st.rerun()
