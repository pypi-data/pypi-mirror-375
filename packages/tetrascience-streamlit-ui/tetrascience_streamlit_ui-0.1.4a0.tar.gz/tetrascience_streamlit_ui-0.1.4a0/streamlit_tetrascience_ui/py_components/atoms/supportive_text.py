from ..utils import declare_component

_component_func = declare_component("supportive_text")


def supportive_text(
    children="This is supportive text",
    show_check=False,
    class_name=None,
    name=None,
    key=None,
):
    """
    Create a supportive text component for displaying helpful text with optional check icon.

    Args:
        children (str|ReactNode): The text content to display (default: "This is supportive text")
        show_check (bool): Whether to show a check icon next to the text (default: False)
        class_name (str, optional): Custom CSS class name for styling the supportive text
        name (str, optional): Name identifier for the supportive text component
        key (str, optional): Streamlit component key

    Returns:
        dict: Dictionary with component name and default values
    """
    component_value = _component_func(
        comp="supportive_text",
        children=children,
        showCheck=show_check,
        className=class_name,
        name=name,
        key=key,
        default={"name": name or "supportive_text"},
    )

    # We could modify the value returned from the component if we wanted.
    # There's no need to do this in our simple example - but it's an option.
    return component_value
