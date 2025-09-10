from ..utils import declare_component

_component_func = declare_component("app_header")


def app_header(hostname, user_profile, key=None, class_name=None, **app_header_props):
    """
    Create an AppHeader component for displaying the app header with user profile and hostname.

    Args:
        hostname (str): The hostname to display.
        user_profile (dict): User profile info with keys 'name' and optional 'avatar'.
        key (str, optional): Streamlit component key
        class_name (str, optional): Additional CSS class for the container
        **app_header_props: Additional AppHeader properties

    Returns:
        dict: Dictionary with event details when the AppHeader is rendered:
              - 'render': when the AppHeader is displayed
              Contains: event, hostname, user_profile
    """
    component_value = _component_func(
        comp="app_header",
        hostname=hostname,
        userProfile=user_profile,
        className=class_name,
        key=key,
        **app_header_props,
        default={
            "event": "render",
            "hostname": hostname,
            "user_profile": user_profile,
        },
    )

    return component_value
