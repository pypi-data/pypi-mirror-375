from ..utils import declare_component

_component_func = declare_component("dropdown")


def dropdown(
    options,
    value=None,
    placeholder="Select an option...",
    disabled=False,
    error=False,
    size="small",
    on_open=None,
    on_close=None,
    width=None,
    menu_width=None,
    name=None,
    key=None,
):
    """
    Create a dropdown component.

    Args:
        options (list): List of dictionaries with 'value', 'label', and optional 'disabled' keys
        value (str, optional): Currently selected value
        placeholder (str): Placeholder text when no option is selected (default: "Select an option...")
        disabled (bool): Whether the dropdown is disabled (default: False)
        error (bool): Whether the dropdown has an error state (default: False)
        size (str): Dropdown size - "xsmall" or "small" (default: "small")
        on_open (callable, optional): Callback function when dropdown opens
        on_close (callable, optional): Callback function when dropdown closes
        width (str, optional): Custom width for the dropdown
        menu_width (str, optional): Custom width for the dropdown menu
        name (str, optional): Name identifier for the dropdown
        key (str, optional): Streamlit component key

    Returns:
        dict: Dictionary with 'value' (selected option value) and 'name' when selection changes
    """
    component_value = _component_func(
        comp="dropdown",
        options=options,
        value=value,
        placeholder=placeholder,
        disabled=disabled,
        error=error,
        size=size,
        onOpen=on_open,
        onClose=on_close,
        width=width,
        menuWidth=menu_width,
        name=name,
        key=key,
        default={"value": None, "name": name or "dropdown"},
    )

    # We could modify the value returned from the component if we wanted.
    # There's no need to do this in our simple example - but it's an option.
    return component_value
