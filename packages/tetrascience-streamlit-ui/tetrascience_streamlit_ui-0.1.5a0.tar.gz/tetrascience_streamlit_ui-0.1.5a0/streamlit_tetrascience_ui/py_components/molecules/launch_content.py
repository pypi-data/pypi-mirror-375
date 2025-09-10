from ..utils import declare_component

_component_func = declare_component("launch_content")


def launch_content(
    initial_code=None, versions=None, current_version=None, key=None, **other_props
):
    """
    Create a launch content component for displaying protocol launch UI.

    Args:
        initial_code (str, optional): Initial code to display in the editor
        versions (list, optional): List of version strings
        current_version (str, optional): The currently selected version
        key (str, optional): Streamlit component key
        **other_props: Additional props for LaunchContent

    Returns:
        dict: Dictionary with event details when the launch content is rendered:
              - 'render': when the launch content is displayed
              Contains: event, currentVersion
    """
    component_value = _component_func(
        comp="launch_content",
        initialCode=initial_code,
        versions=versions,
        currentVersion=current_version,
        key=key,
        **other_props,
        default={
            "event": "render",
            "currentVersion": current_version,
        },
    )

    return component_value
