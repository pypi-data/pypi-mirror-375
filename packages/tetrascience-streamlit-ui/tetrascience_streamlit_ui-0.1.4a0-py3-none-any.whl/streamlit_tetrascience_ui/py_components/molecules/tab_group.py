from ..utils import declare_component

_component_func = declare_component("tab_group")


def tab_group(tabs=None, active_tab=None, size="medium", key=None, **other_props):
    """
    Create a tab group component for displaying a group of tabs.

    Args:
        tabs (list): List of tab items (each a dict with id, label, etc.)
        active_tab (str, optional): The currently active tab id
        size (str): Size of the tabs (default: "medium")
        key (str, optional): Streamlit component key
        **other_props: Additional props for TabGroup

    Returns:
        dict: Dictionary with event details when the tab group is rendered:
              - 'render': when the tab group is displayed
              Contains: event, activeTab
    """
    if tabs is None:
        tabs = []

    component_value = _component_func(
        comp="tab_group",
        tabs=tabs,
        activeTab=active_tab,
        size=size,
        key=key,
        **other_props,
        default={
            "event": "render",
            "activeTab": active_tab,
        },
    )

    return component_value
