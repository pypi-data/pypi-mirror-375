from ..utils import declare_component

_component_func = declare_component("error_alert")


def error_alert(
    error,
    title="An Error Occurred",
    on_close=None,
    show_details_default=False,
    no_error_content=None,
    name=None,
    key=None,
):
    """
    Create an error alert component to display error messages and details.

    Args:
        error (str|dict|Exception): Error object to display. Can be a string message, exception object,
                                   or dictionary with error details
        title (str|ReactNode): Optional title for the error alert (default: "An Error Occurred")
        on_close (callable, optional): Callback function when the alert is closed
        show_details_default (bool): Set to true to show technical details expanded by default (default: False)
        no_error_content (str|ReactNode, optional): Custom message to show when error is null/undefined
        name (str, optional): Name identifier for the error alert
        key (str, optional): Streamlit component key

    Returns:
        dict: Dictionary with 'event' (close action) and 'name' when alert is closed
    """
    component_value = _component_func(
        comp="error_alert",
        error=error,
        title=title,
        onClose=on_close,
        showDetailsDefault=show_details_default,
        noErrorContent=no_error_content,
        name=name,
        key=key,
        default={"event": None, "name": name or "error_alert"},
    )

    # We could modify the value returned from the component if we wanted.
    # There's no need to do this in our simple example - but it's an option.
    return component_value
