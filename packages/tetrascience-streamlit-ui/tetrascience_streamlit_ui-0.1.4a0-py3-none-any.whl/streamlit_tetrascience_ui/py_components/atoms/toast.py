from ..utils import declare_component

_component_func = declare_component("toast")


def toast(
    type="default",
    heading="Toast Notification",
    description=None,
    class_name=None,
    name=None,
    key=None,
):
    """
    Create a toast notification component for displaying temporary messages.

    Args:
        type (str): Type of toast notification - "info", "success", "warning", "danger", or "default" (default: "default")
        heading (str): The main heading text of the toast (default: "Toast Notification")
        description (str, optional): Optional description text for additional details
        class_name (str, optional): Custom CSS class name for styling the toast
        name (str, optional): Name identifier for the toast component
        key (str, optional): Streamlit component key

    Returns:
        dict: Dictionary with 'event', 'name', 'type', 'heading', and 'description' when displayed
    """
    component_value = _component_func(
        comp="toast",
        type=type,
        heading=heading,
        description=description,
        className=class_name,
        name=name,
        key=key,
        default={
            "event": "display",
            "name": name or "toast",
            "type": type,
            "heading": heading,
            "description": description,
        },
    )

    # We could modify the value returned from the component if we wanted.
    # There's no need to do this in our simple example - but it's an option.
    return component_value
