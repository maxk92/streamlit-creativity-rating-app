"""
Page navigation helpers that respect skip/enable settings from config.

All "Next" and "Back" buttons should use these functions instead of
hardcoding page names, so that skipped pages are transparently bypassed.
"""


# Ordered main page sequence. Familiarization sub-pages (familiarization,
# post_familiarization) are managed internally by their own pages and are
# not part of the linear back/forward chain.
_SEQUENCE = [
    'welcome',
    'login',
    'consent',
    'questionnaire',
    'pre_familiarization',
    'videoplayer',
]


def _active_pages(config):
    """Return the subset of _SEQUENCE that is active given the current config."""
    s = (config or {}).get('settings', {})
    conditions = {
        'welcome':            not s.get('skip_welcome', False),
        'login':              not s.get('skip_login', False),
        'consent':            not s.get('skip_consent', False),
        'questionnaire':      not s.get('skip_questionnaire', False),
        'pre_familiarization': s.get('enable_familiarization', False),
        'videoplayer':        True,
    }
    return [p for p in _SEQUENCE if conditions.get(p, True)]


def get_next_page(current_page, config):
    """
    Return the next active page after *current_page*, skipping any pages
    whose skip_* setting is True (or whose enable_* setting is False).

    Falls back to 'videoplayer' if nothing is found.
    """
    active = _active_pages(config)
    try:
        idx = active.index(current_page)
    except ValueError:
        return 'videoplayer'
    return active[idx + 1] if idx + 1 < len(active) else 'videoplayer'


def get_prev_page(current_page, config):
    """
    Return the previous active page before *current_page*, skipping any
    pages whose skip_* / enable_* settings exclude them.

    Falls back to 'welcome' if nothing is found.
    """
    active = _active_pages(config)
    try:
        idx = active.index(current_page)
    except ValueError:
        return 'welcome'
    return active[idx - 1] if idx > 0 else 'welcome'
