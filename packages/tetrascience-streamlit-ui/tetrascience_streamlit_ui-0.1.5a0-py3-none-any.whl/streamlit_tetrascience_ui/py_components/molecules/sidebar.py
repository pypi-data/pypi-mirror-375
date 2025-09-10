from ..utils import declare_component

_component_func = declare_component("sidebar")


def sidebar(items=None, active_item=None, key=None):
    """
    Create a sidebar component with navigation items.

    Args:
        items (list): List of sidebar items, each containing:
                     - icon (str): Icon name for the item
                     - label (str): Display label for the item
                     - active (bool, optional): Whether the item is active
        active_item (str, optional): Label of the currently active item
        key (str, optional): Streamlit component key

    Returns:
        dict: Dictionary with event details when sidebar items are interacted with:
              - 'item_click': when a sidebar item is clicked
              Contains: event, label, timestamp
    """
    if items is None:
        items = []

    component_value = _component_func(
        comp="sidebar",
        items=items,
        activeItem=active_item,
        key=key,
        default={
            "event": "render",
            "items": items,
            "activeItem": active_item,
        },
    )

    return component_value
