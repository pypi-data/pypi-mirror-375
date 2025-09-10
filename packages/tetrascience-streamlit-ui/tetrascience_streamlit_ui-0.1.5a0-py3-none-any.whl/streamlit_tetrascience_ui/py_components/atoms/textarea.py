from ..utils import declare_component

_component_func = declare_component("textarea")


def textarea(
    value="",
    placeholder="Enter text here...",
    size="small",
    error=False,
    disabled=False,
    full_width=False,
    rows=None,
    on_change=None,
    on_focus=None,
    on_blur=None,
    name=None,
    key=None,
):
    """
    Create a textarea component for multi-line text input.

    Args:
        value (str): The current value of the textarea (default: "")
        placeholder (str): Placeholder text shown when textarea is empty (default: "Enter text here...")
        size (str): Size of the textarea - "xsmall" or "small" (default: "small")
        error (bool): Whether to display the textarea in error state (default: False)
        disabled (bool): Whether the textarea is disabled (default: False)
        full_width (bool): Whether the textarea should take full width of container (default: False)
        rows (int, optional): Number of visible text lines (height of textarea)
        on_change (callable, optional): Callback function when textarea value changes
        on_focus (callable, optional): Callback function when textarea receives focus
        on_blur (callable, optional): Callback function when textarea loses focus
        name (str, optional): Name identifier for the textarea component
        key (str, optional): Streamlit component key

    Returns:
        dict: Dictionary with 'event', 'name', 'value', and 'placeholder' for interactions
    """
    component_value = _component_func(
        comp="textarea",
        value=value,
        placeholder=placeholder,
        size=size,
        error=error,
        disabled=disabled,
        fullWidth=full_width,
        rows=rows,
        onChange=on_change,
        onFocus=on_focus,
        onBlur=on_blur,
        name=name,
        key=key,
        default={
            "event": None,
            "name": name or "textarea",
            "value": value,
            "placeholder": placeholder,
        },
    )

    # We could modify the value returned from the component if we wanted.
    # There's no need to do this in our simple example - but it's an option.
    return component_value
