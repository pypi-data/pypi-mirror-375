from ..utils import declare_component

_component_func = declare_component("toggle")


def toggle(
    checked=False,
    on_change=None,
    disabled=False,
    label=None,
    class_name=None,
    name=None,
    key=None,
):
    """
    Create a toggle switch component for boolean input.

    Args:
        checked (bool): Whether the toggle is currently checked/on (default: False)
        on_change (callable, optional): Callback function when the toggle state changes
        disabled (bool): Whether the toggle is disabled and cannot be changed (default: False)
        label (str, optional): Optional label text displayed next to the toggle
        class_name (str, optional): Custom CSS class name for styling the toggle
        name (str, optional): Name identifier for the toggle component
        key (str, optional): Streamlit component key

    Returns:
        dict: Dictionary with 'event', 'name', 'checked', and 'label' when toggled
    """
    component_value = _component_func(
        comp="toggle",
        checked=checked,
        onChange=on_change,
        disabled=disabled,
        label=label,
        className=class_name,
        name=name,
        key=key,
        default={
            "event": None,
            "name": name or "toggle",
            "checked": checked,
            "label": label,
        },
    )

    # We could modify the value returned from the component if we wanted.
    # There's no need to do this in our simple example - but it's an option.
    return component_value
