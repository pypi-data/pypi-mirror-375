from ..utils import declare_component

_component_func = declare_component("tooltip")


def tooltip(
    content="This is a tooltip",
    children=None,
    placement="top",
    class_name=None,
    delay=100,
    name=None,
    key=None,
):
    """
    Create a tooltip component that displays content on hover.

    Args:
        content (str|ReactNode): The content to display in the tooltip (default: "This is a tooltip")
        children (str|ReactNode, optional): The element that triggers the tooltip on hover
        placement (str): Position of the tooltip relative to the trigger element (default: "top")
                        Options: "top", "right", "bottom", "left"
        class_name (str, optional): Custom CSS class name for styling the tooltip
        delay (int): Delay in milliseconds before showing the tooltip (default: 100)
        name (str, optional): Name identifier for the tooltip component
        key (str, optional): Streamlit component key

    Returns:
        dict: Dictionary with 'event', 'name', 'content', and 'placement' when mounted
    """
    component_value = _component_func(
        comp="tooltip",
        content=content,
        children=children,
        placement=placement,
        className=class_name,
        delay=delay,
        name=name,
        key=key,
        default={
            "event": "mount",
            "name": name or "tooltip",
            "content": content,
            "placement": placement,
        },
    )

    # We could modify the value returned from the component if we wanted.
    # There's no need to do this in our simple example - but it's an option.
    return component_value
