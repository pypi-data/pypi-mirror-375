from ..utils import declare_component

_component_func = declare_component("card")


def card(
    children="Card Content",
    title=None,
    variant="default",
    size="medium",
    class_name=None,
    full_width=False,
    key=None,
):
    """
    Create a card component.

    Args:
        children (str): The content to display in the card (default: "Card Content")
        title (str, optional): Optional title for the card
        variant (str): Card variant - "default", "outlined", or "elevated" (default: "default")
        size (str): Card size - "small", "medium", or "large" (default: "medium")
        class_name (str, optional): Additional CSS class name
        full_width (bool): Whether the card should take full width (default: False)
        key (str, optional): Streamlit component key

    Returns:
        Component value
    """
    component_value = _component_func(
        comp="card",
        children=children,
        title=title,
        variant=variant,
        size=size,
        className=class_name,
        fullWidth=full_width,
        key=key,
        default=0,
    )

    # We could modify the value returned from the component if we wanted.
    # There's no need to do this in our simple example - but it's an option.
    return component_value
