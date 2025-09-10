from ..utils import declare_component

_component_func = declare_component("button_control")


def button_control(icon=None, selected=False, disabled=False, name=None, key=None):
    """
    Create a button control component.

    Args:
        icon (str, optional): Icon to display in the button control
        selected (bool): Whether the button is in selected state (default: False)
        disabled (bool): Whether the button is disabled (default: False)
        name (str, optional): Name identifier for the button control
        key (str, optional): Streamlit component key

    Returns:
        str: The component value (name or "button_control_clicked" when clicked)
    """
    component_value = _component_func(
        comp="button_control",
        icon=icon,
        selected=selected,
        disabled=disabled,
        name=name,
        key=key,
        default=0,
    )

    # We could modify the value returned from the component if we wanted.
    # There's no need to do this in our simple example - but it's an option.
    return component_value
