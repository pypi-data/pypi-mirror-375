from ..utils import declare_component

_component_func = declare_component("input")


def input(
    value="",
    placeholder="",
    size="small",
    icon_left=None,
    icon_right=None,
    error=False,
    disabled=False,
    type="text",
    name=None,
    on_change=None,
    on_focus=None,
    on_blur=None,
    key=None,
):
    """
    Create an input component for text input with optional icons and styling.

    Args:
        value (str): Current value of the input field (default: "")
        placeholder (str): Placeholder text when input is empty (default: "")
        size (str): Input size - "xsmall" or "small" (default: "small")
        icon_left (ReactNode, optional): Icon to display on the left side of the input
        icon_right (ReactNode, optional): Icon to display on the right side of the input
        error (bool): Whether the input has an error state (default: False)
        disabled (bool): Whether the input is disabled (default: False)
        type (str): HTML input type (e.g., "text", "email", "password", "number") (default: "text")
        name (str, optional): Name identifier for the input field
        on_change (callable, optional): Callback function when input value changes
        on_focus (callable, optional): Callback function when input gains focus
        on_blur (callable, optional): Callback function when input loses focus
        key (str, optional): Streamlit component key

    Returns:
        dict: Dictionary with 'value', 'name', and 'event' when input changes or events occur
    """
    component_value = _component_func(
        comp="input",
        value=value,
        placeholder=placeholder,
        size=size,
        iconLeft=icon_left,
        iconRight=icon_right,
        error=error,
        disabled=disabled,
        type=type,
        name=name,
        onChange=on_change,
        onFocus=on_focus,
        onBlur=on_blur,
        key=key,
        default={"value": value, "name": name or "input", "event": None},
    )

    # We could modify the value returned from the component if we wanted.
    # There's no need to do this in our simple example - but it's an option.
    return component_value
