from ..utils import declare_component

_component_func = declare_component("badge")


def badge(
    label,
    variant="default",
    size="medium",
    disabled=False,
    icon_left=None,
    icon_right=None,
    class_name=None,
    key=None,
):
    """
    Create a badge component.

    Args:
        label (str): The text content to display in the badge
        variant (str): Badge variant - "default" or "primary" (default: "default")
        size (str): Badge size - "small" or "medium" (default: "medium")
        disabled (bool): Whether the badge is disabled (default: False)
        icon_left (str, optional): Left icon element
        icon_right (str, optional): Right icon element
        class_name (str, optional): Additional CSS class name
        key (str, optional): Streamlit component key

    Returns:
        Component value
    """
    component_value = _component_func(
        comp="badge",
        label=label,
        variant=variant,
        size=size,
        disabled=disabled,
        iconLeft=icon_left,
        iconRight=icon_right,
        className=class_name,
        key=key,
        default=0,
    )

    # We could modify the value returned from the component if we wanted.
    # There's no need to do this in our simple example - but it's an option.
    return component_value
