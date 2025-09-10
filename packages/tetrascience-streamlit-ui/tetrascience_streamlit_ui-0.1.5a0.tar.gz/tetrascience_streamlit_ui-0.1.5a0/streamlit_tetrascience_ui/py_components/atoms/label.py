from ..utils import declare_component

_component_func = declare_component("label")


def label(children="Label Text", info_text=None, class_name=None, name=None, key=None):
    """
    Create a label component to display text with optional info tooltip.

    Args:
        children (str|ReactNode): The main content/text to display in the label (default: "Label Text")
        info_text (str, optional): Additional information text that appears in a tooltip when hovering
                                  over the info icon next to the label
        class_name (str, optional): Custom CSS class name for styling the label container
        name (str, optional): Name identifier for the label component
        key (str, optional): Streamlit component key

    Returns:
        dict: Dictionary with label properties for tracking
    """
    component_value = _component_func(
        comp="label",
        children=children,
        infoText=info_text,
        className=class_name,
        name=name,
        key=key,
        default={"children": children, "name": name or "label"},
    )

    # We could modify the value returned from the component if we wanted.
    # There's no need to do this in our simple example - but it's an option.
    return component_value
