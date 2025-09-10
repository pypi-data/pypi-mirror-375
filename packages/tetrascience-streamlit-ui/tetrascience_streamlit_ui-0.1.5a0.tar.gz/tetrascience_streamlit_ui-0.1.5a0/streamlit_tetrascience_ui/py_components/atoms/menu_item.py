from ..utils import declare_component

_component_func = declare_component("menu_item")


def menu_item(
    label="Menu Item",
    checked=False,
    show_checkbox=False,
    on_click=None,
    on_check_change=None,
    active=False,
    class_name=None,
    name=None,
    key=None,
):
    """
    Create a menu item component for navigation menus with optional checkbox functionality.

    Args:
        label (str): The text label to display in the menu item (default: "Menu Item")
        checked (bool): Whether the checkbox is checked (only applies when show_checkbox=True) (default: False)
        show_checkbox (bool): Whether to display a checkbox with the menu item (default: False)
        on_click (callable, optional): Callback function when the menu item is clicked
        on_check_change (callable, optional): Callback function when checkbox state changes (receives bool)
        active (bool): Whether the menu item is in active/selected state (default: False)
        class_name (str, optional): Custom CSS class name for styling the menu item
        name (str, optional): Name identifier for the menu item component
        key (str, optional): Streamlit component key

    Returns:
        dict: Dictionary with 'event' (click/check_change), 'name', 'label', and 'checked' state when interactions occur
    """
    component_value = _component_func(
        comp="menu_item",
        label=label,
        checked=checked,
        showCheckbox=show_checkbox,
        onClick=on_click,
        onCheckChange=on_check_change,
        active=active,
        className=class_name,
        name=name,
        key=key,
        default={
            "event": None,
            "name": name or "menu_item",
            "label": label,
            "checked": checked,
        },
    )

    # We could modify the value returned from the component if we wanted.
    # There's no need to do this in our simple example - but it's an option.
    return component_value
