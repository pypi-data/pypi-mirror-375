from ..utils import declare_component

_component_func = declare_component("tab")


def tab(
    label="Tab Label",
    active=False,
    disabled=False,
    size="medium",
    on_click=None,
    name=None,
    key=None,
):
    """
    Create a tab component for tab navigation interfaces.

    Args:
        label (str): The text label displayed on the tab (default: "Tab Label")
        active (bool): Whether the tab is currently active/selected (default: False)
        disabled (bool): Whether the tab is disabled and cannot be clicked (default: False)
        size (str): Size of the tab - "small" or "medium" (default: "medium")
        on_click (callable, optional): Callback function when the tab is clicked
        name (str, optional): Name identifier for the tab component
        key (str, optional): Streamlit component key

    Returns:
        dict: Dictionary with 'event', 'name', 'label', and 'active' when clicked
    """
    component_value = _component_func(
        comp="tab",
        label=label,
        active=active,
        disabled=disabled,
        size=size,
        onClick=on_click,
        name=name,
        key=key,
        default={
            "event": None,
            "name": name or "tab",
            "label": label,
            "active": active,
        },
    )

    # We could modify the value returned from the component if we wanted.
    # There's no need to do this in our simple example - but it's an option.
    return component_value
