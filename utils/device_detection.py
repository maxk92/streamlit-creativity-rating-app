"""
Device detection utilities using HTTP User-Agent parsing.
Captures device type, OS, and browser once per session and attaches this
info to every saved rating.

Note: Screen/window dimensions are intentionally omitted — collecting them
requires a streamlit_js_eval iframe (150 px tall by Streamlit default) that
creates unwanted visual space at the top of the page.  The UA string covers
the most research-relevant fields (device class, OS, browser).
"""
import streamlit as st


def get_device_info():
    """
    Detect device information from the HTTP User-Agent header.

    Returns:
        dict with keys: device_type, os, os_version, browser, browser_version,
                        user_agent
    """
    import user_agents

    ua_string = ""
    device_type = "unknown"
    os_family = "unknown"
    os_version = "unknown"
    browser_family = "unknown"
    browser_version = "unknown"

    try:
        ua_string = st.context.headers.get("User-Agent", "")
        ua = user_agents.parse(ua_string)

        if ua.is_mobile:
            device_type = "mobile"
        elif ua.is_tablet:
            device_type = "tablet"
        else:
            device_type = "desktop"

        os_family = ua.os.family
        os_version = ua.os.version_string
        browser_family = ua.browser.family
        browser_version = ua.browser.version_string

    except Exception as e:
        print(f"[WARNING] Failed to parse user agent: {e}")

    return {
        'device_type': device_type,
        'os': os_family,
        'os_version': os_version,
        'browser': browser_family,
        'browser_version': browser_version,
        'user_agent': ua_string,
    }


def get_device_info_cached():
    """
    Get device info once per session, caching the result in session_state.

    Returns:
        dict with device info fields
    """
    if 'device_info' not in st.session_state:
        st.session_state.device_info = get_device_info()
    return st.session_state.device_info
