from ..utils import declare_component

_component_func = declare_component("pop_confirm")


def pop_confirm(
    title=None,
    description=None,
    on_confirm=None,
    on_cancel=None,
    ok_text="OK",
    cancel_text="Cancel",
    placement="top",
    children=None,
    class_name=None,
    ok_button_props=None,
    cancel_button_props=None,
    name=None,
    key=None,
):
    """
    Create a pop confirmation dialog that appears as a popover near the trigger element.

    Args:
        title (str|ReactNode, optional): Title text displayed in the pop confirm dialog
        description (str|ReactNode, optional): Description text displayed in the pop confirm dialog
        on_confirm (callable, optional): Callback function when the confirm button is clicked
        on_cancel (callable, optional): Callback function when the cancel button is clicked
        ok_text (str): Text for the confirm button (default: "OK")
        cancel_text (str): Text for the cancel button (default: "Cancel")
        placement (str): Position of the popover relative to trigger element (default: "top")
                       Options: "top", "left", "right", "bottom", "topLeft", "topRight",
                       "bottomLeft", "bottomRight", "leftTop", "leftBottom", "rightTop", "rightBottom"
        children (str|ReactNode, optional): The trigger element that shows the pop confirm when clicked
        class_name (str, optional): Custom CSS class name for styling the pop confirm
        ok_button_props (dict, optional): Additional props for the OK button
        cancel_button_props (dict, optional): Additional props for the cancel button
        name (str, optional): Name identifier for the pop confirm component
        key (str, optional): Streamlit component key

    Returns:
        dict: Dictionary with 'event' (confirm/cancel), 'name', and 'action' when interactions occur
    """
    component_value = _component_func(
        comp="pop_confirm",
        title=title,
        description=description,
        onConfirm=on_confirm,
        onCancel=on_cancel,
        okText=ok_text,
        cancelText=cancel_text,
        placement=placement,
        children=children,
        className=class_name,
        okButtonProps=ok_button_props,
        cancelButtonProps=cancel_button_props,
        name=name,
        key=key,
        default={"event": None, "name": name or "pop_confirm", "action": None},
    )

    # We could modify the value returned from the component if we wanted.
    # There's no need to do this in our simple example - but it's an option.
    return component_value
