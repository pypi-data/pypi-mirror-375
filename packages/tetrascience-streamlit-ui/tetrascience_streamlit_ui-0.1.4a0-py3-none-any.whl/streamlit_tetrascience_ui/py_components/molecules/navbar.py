from ..utils import declare_component

_component_func = declare_component("navbar")


def navbar(organization, key=None, class_name=None, **navbar_props):
    """
    Create a Navbar component for displaying organization and project info.

    Args:
        organization (dict): Organization info with keys 'name', optional 'subtext', and optional 'logo'.
        key (str, optional): Streamlit component key
        class_name (str, optional): Additional CSS class for the container
        **navbar_props: Additional Navbar properties

    Returns:
        dict: Dictionary with event details when the Navbar is rendered:
              - 'render': when the Navbar is displayed
              Contains: event, organization
    """
    component_value = _component_func(
        comp="navbar",
        organization=organization,
        className=class_name,
        key=key,
        **navbar_props,
        default={
            "event": "render",
            "organization": organization,
        },
    )

    return component_value
