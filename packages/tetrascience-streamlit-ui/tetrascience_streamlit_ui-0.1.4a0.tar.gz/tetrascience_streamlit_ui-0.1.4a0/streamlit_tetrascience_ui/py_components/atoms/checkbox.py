from ..utils import declare_component

_component_func = declare_component("checkbox")


def checkbox(
    checked=False,
    label="Checkbox",
    disabled=False,
    class_name=None,
    no_padding=False,
    name=None,
    key=None,
):
    """
    Create a checkbox component.

    Args:
        checked (bool): Whether the checkbox is checked (default: False)
        label (str): Label text for the checkbox (default: "Checkbox")
        disabled (bool): Whether the checkbox is disabled (default: False)
        class_name (str, optional): Additional CSS class name
        no_padding (bool): Whether to remove padding (default: False)
        name (str, optional): Name identifier for the checkbox
        key (str, optional): Streamlit component key

    Returns:
        dict: Dictionary with 'checked' state and 'name' when checkbox is toggled
    """
    component_value = _component_func(
        comp="checkbox",
        checked=checked,
        label=label,
        disabled=disabled,
        className=class_name,
        noPadding=no_padding,
        name=name,
        key=key,
        default={"checked": False, "name": name or "checkbox"},
    )

    # We could modify the value returned from the component if we wanted.
    # There's no need to do this in our simple example - but it's an option.
    return component_value
