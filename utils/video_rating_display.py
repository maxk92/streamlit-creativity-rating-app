"""
Shared display logic for video rating interface.
Used by both main videoplayer and familiarization screens.
"""
import streamlit as st
import os
import matplotlib.pyplot as plt


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _render_scale_widget(scale_config, unique_key):
    """Render a single rating scale widget and return the selected value."""
    scale_type = scale_config.get('type', 'discrete')
    title = scale_config.get('title', 'Scale')

    if scale_type == 'discrete':
        values = scale_config.get('values', [1, 2, 3, 4, 5, 6, 7])
        return st.pills(
            label=title,
            options=values,
            key=unique_key,
            label_visibility="collapsed",
            width="stretch"
        )

    elif scale_type == 'slider':
        slider_min = scale_config.get('slider_min', 0)
        slider_max = scale_config.get('slider_max', 100)
        initial_state = scale_config.get('initial_state', 'low')

        if initial_state == 'low':
            initial_value = float(slider_min)
        elif initial_state == 'high':
            initial_value = float(slider_max)
        else:  # 'center'
            initial_value = float(slider_min + slider_max) / 2

        return st.slider(
            label=title,
            min_value=float(slider_min),
            max_value=float(slider_max),
            value=initial_value,
            key=unique_key,
            label_visibility="collapsed"
        )

    elif scale_type == 'text':
        result = st.text_input(
            label=title,
            key=unique_key,
            placeholder="Enter your response...",
            label_visibility="collapsed"
        )
        return result if result else None

    return None


def _show_metadata_bar(config, action_id, metadata):
    """Display the metadata bar above the video if configured."""
    display_metadata = config['settings'].get('display_metadata', True)
    if not (display_metadata and metadata is not None and not metadata.empty and action_id):
        return

    row = metadata[metadata['id'] == action_id]
    if row.empty:
        return

    metadata_to_show = config['settings'].get('metadata_to_show', [])
    if metadata_to_show:
        cols = st.columns(len(metadata_to_show))
        for idx, field_config in enumerate(metadata_to_show):
            label = field_config.get('label', '')
            column = field_config.get('column', '')
            if column and column in row.columns:
                with cols[idx]:
                    st.metric(label, row[column].values[0])

    st.markdown("---")


# ---------------------------------------------------------------------------
# Public functions for separate display mode
# ---------------------------------------------------------------------------

def display_video_only(video_filename, video_path, config, display_video_func, action_id, metadata):
    """
    Show the metadata bar and video only — no pitch, no scales.
    Used by the video screen in 'separate' display mode.
    """
    settings = config.get('settings', {})
    video_playback_mode = settings.get('video_playback_mode', 'loop')

    _show_metadata_bar(config, action_id, metadata)

    video_file = os.path.join(video_path, video_filename)
    if display_video_func:
        display_video_func(video_file, video_playback_mode)
    else:
        st.video(video_file, autoplay=True, loop=(video_playback_mode == 'loop'))


def display_rating_scales_only(video_filename, rating_scales, key_prefix, action_id, config):
    """
    Show the action-not-recognized button and all rating scales — no video.
    Used by the rating screen in 'separate' display mode.

    Layout logic:
    - Scale with no labels → title on left, widget on right (side-by-side)
    - Scale with labels   → title on top, then label_low | widget | label_high (stacked)

    Returns:
        scale_values dict including '_action_not_recognized'
    """
    settings = config.get('settings', {})

    # Action not recognized button
    show_not_recognized = settings.get('show_action_not_recognized', True)
    action_not_recognized = False
    if show_not_recognized:
        button_key = f"not_recognized_{action_id}" if action_id else f"not_recognized_{video_filename}"
        action_not_recognized = st.button(
            "⚠️ Action not recognized",
            type="primary",
            key=button_key,
            help="Check this if you cannot identify or rate this action",
            use_container_width=True
        )

    st.markdown("---")

    rating_heading = settings.get('rating_section_heading', 'Please rate the action on the following dimensions:')
    st.markdown(f"### {rating_heading}")

    scale_values = {}

    for scale_config in rating_scales:
        title = scale_config.get('title', 'Scale')
        label_low = scale_config.get('label_low', '')
        label_high = scale_config.get('label_high', '')
        required = scale_config.get('required_to_proceed', True)
        has_labels = bool(label_low or label_high)

        unique_key = (
            f"{key_prefix}{action_id}_{title}" if action_id
            else f"{key_prefix}{video_filename}_{title}"
        )

        req_marker = '*(required)*' if required and not action_not_recognized else ''

        if not has_labels:
            # Side-by-side: title left, widget right
            col_title, col_scale = st.columns([2, 3])
            with col_title:
                st.markdown(f"**{title}** {req_marker}")
            with col_scale:
                scale_values[title] = _render_scale_widget(scale_config, unique_key)
        else:
            # Stacked: title row, then labels flanking widget
            st.markdown(f"**{title}** {req_marker}")
            col_low, col_scale, col_high = st.columns([1, 3, 1])
            with col_low:
                st.markdown(f"*{label_low}*")
            with col_scale:
                scale_values[title] = _render_scale_widget(scale_config, unique_key)
            with col_high:
                st.markdown(f"*{label_high}*")

        st.markdown("")  # spacing

    scale_values['_action_not_recognized'] = action_not_recognized
    return scale_values


# ---------------------------------------------------------------------------
# Combined interface (original behaviour, unchanged)
# ---------------------------------------------------------------------------

def display_video_rating_interface(
    video_filename,
    video_path,
    config,
    rating_scales,
    key_prefix,
    action_id=None,
    metadata=None,
    header_content=None,
    display_video_func=None,
    display_mode='combined'
):
    """
    Display the video rating interface with configurable options.

    Parameters:
    - video_filename: Name of the video file to display
    - video_path: Path to the directory containing the video
    - config: Configuration dictionary
    - rating_scales: List of rating scale configurations
    - key_prefix: Prefix for Streamlit widget keys (e.g., 'scale_' or 'famil_scale_')
    - action_id: Optional action ID for metadata lookup
    - metadata: Optional metadata DataFrame
    - header_content: Optional callable to display at the top
    - display_video_func: Function to display video (accepts file_path, playback_mode)
    - display_mode: 'combined' (default), 'video_only', or 'rating_only'

    Returns:
    - scale_values dict ({scale_title: value}); empty dict for 'video_only'
    """
    # Display optional header content (e.g., familiarization info)
    if header_content:
        header_content()

    # --- Delegate to sub-functions for separate mode ---
    if display_mode == 'video_only':
        display_video_only(video_filename, video_path, config, display_video_func, action_id, metadata)
        return {}

    if display_mode == 'rating_only':
        return display_rating_scales_only(video_filename, rating_scales, key_prefix, action_id, config)

    # --- Combined mode (original behaviour) ---
    display_metadata = config['settings'].get('display_metadata', True)
    display_pitch = config['settings'].get('display_pitch', True)
    video_playback_mode = config['settings'].get('video_playback_mode', 'loop')

    # Top metadata bar
    if display_metadata and metadata is not None and not metadata.empty and action_id:
        row = metadata[metadata['id'] == action_id]
        if not row.empty:
            metadata_to_show = config['settings'].get('metadata_to_show', [])

            if metadata_to_show:
                cols = st.columns(len(metadata_to_show))

                for idx, field_config in enumerate(metadata_to_show):
                    label = field_config.get('label', '')
                    column = field_config.get('column', '')

                    if column and column in row.columns:
                        with cols[idx]:
                            st.metric(label, row[column].values[0])

        st.markdown("---")

    # Video and pitch visualization area
    settings = config.get('settings', {})
    col_ratio = settings.get('video_pitch_column_ratio', [55, 45])
    pitch_type = settings.get('pitch_type', 'statsbomb')
    pitch_color = settings.get('pitch_color', 'grass')
    arrow_color = settings.get('pitch_arrow_color', 'blue')
    arrow_width = settings.get('pitch_arrow_width', 2)
    arrow_headwidth = settings.get('pitch_arrow_headwidth', 10)
    arrow_headlength = settings.get('pitch_arrow_headlength', 5)
    marker_color = settings.get('pitch_marker_color', 'blue')
    marker_size = settings.get('pitch_marker_size', 10)

    if display_pitch and metadata is not None and not metadata.empty and action_id:
        col_video, col_pitch = st.columns(col_ratio)

        with col_video:
            video_file = os.path.join(video_path, video_filename)
            if display_video_func:
                display_video_func(video_file, video_playback_mode)
            else:
                st.video(video_file, autoplay=True, loop=(video_playback_mode == 'loop'))

        with col_pitch:
            row = metadata[metadata['id'] == action_id]
            if not row.empty:
                try:
                    import mplsoccer
                    pitch = mplsoccer.Pitch(pitch_type=pitch_type, pitch_color=pitch_color)
                    fig, ax = pitch.draw(figsize=(6, 4))

                    fig.patch.set_facecolor('black')
                    fig.patch.set_alpha(1)

                    start_x = row.start_x.values[0]
                    start_y = row.start_y.values[0]
                    end_x = row.end_x.values[0]
                    end_y = row.end_y.values[0]

                    pitch.arrows(start_x, start_y, end_x, end_y,
                                ax=ax, color=arrow_color, width=arrow_width,
                                headwidth=arrow_headwidth, headlength=arrow_headlength)
                    ax.plot(start_x, start_y, 'o', color=marker_color, markersize=marker_size)

                    fig.tight_layout(pad=0)
                    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

                    st.pyplot(fig)
                    plt.close(fig)
                except Exception as e:
                    st.error(f"Failed to generate pitch visualization: {e}")
            else:
                st.info("No metadata available for this video")

    else:
        video_file = os.path.join(video_path, video_filename)
        if display_video_func:
            display_video_func(video_file, video_playback_mode)
        else:
            st.video(video_file, autoplay=True, loop=(video_playback_mode == 'loop'))

    # Action not recognized button
    show_not_recognized = settings.get('show_action_not_recognized', True)
    action_not_recognized = False
    if show_not_recognized:
        button_key = f"not_recognized_{action_id}" if action_id else f"not_recognized_{video_filename}"
        action_not_recognized = st.button(
            "⚠️ Action not recognized",
            type="primary",
            key=button_key,
            help="Check this if you cannot identify or rate this action",
            use_container_width=True
        )

    st.markdown("---")

    # Rating scales
    rating_heading = settings.get('rating_section_heading', 'Please rate the action on the following dimensions:')
    st.markdown(f"### {rating_heading}")

    scale_values = {}

    for scale_config in rating_scales:
        scale_type = scale_config.get('type', 'discrete')
        title = scale_config.get('title', 'Scale')
        label_low = scale_config.get('label_low', '')
        label_high = scale_config.get('label_high', '')
        required = scale_config.get('required_to_proceed', True)

        st.markdown(f"**{title}** {'*(required)*' if required and not action_not_recognized else ''}")

        col_low, col_scale, col_high = st.columns([1, 3, 1])

        with col_low:
            st.markdown(f"*{label_low}*")

        with col_scale:
            unique_key = (
                f"{key_prefix}{action_id}_{title}" if action_id
                else f"{key_prefix}{video_filename}_{title}"
            )
            scale_values[title] = _render_scale_widget(scale_config, unique_key)

        with col_high:
            st.markdown(f"*{label_high}*")

        st.markdown("")  # Spacing

    scale_values['_action_not_recognized'] = action_not_recognized

    return scale_values
