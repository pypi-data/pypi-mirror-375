from ..utils import declare_component

_component_func = declare_component("modal")


def modal(
    is_open=False,
    on_close=None,
    on_close_label="Cancel",
    on_confirm=None,
    on_confirm_label="Confirm",
    children="This is modal content.",
    width="400px",
    class_name=None,
    hide_actions=False,
    title="Modal Title",
    name=None,
    key=None,
):
    """
    Create a modal dialog component for displaying overlay content with actions.

    Args:
        is_open (bool): Whether the modal is open/visible (default: False)
        on_close (callable, optional): Callback function when the modal is closed
        on_close_label (str): Label for the close/cancel button (default: "Cancel")
        on_confirm (callable, optional): Callback function when the confirm button is clicked
        on_confirm_label (str): Label for the confirm button (default: "Confirm")
        children (str|ReactNode): The main content to display inside the modal (default: "This is modal content.")
        width (str): Width of the modal (CSS value, e.g., "400px", "50%") (default: "400px")
        class_name (str, optional): Custom CSS class name for styling the modal
        hide_actions (bool): Whether to hide the action buttons (default: False)
        title (str, optional): Title to display in the modal header (default: "Modal Title")
        name (str, optional): Name identifier for the modal component
        key (str, optional): Streamlit component key

    Returns:
        dict: Dictionary with 'event' (close/confirm), 'name', and 'action' when interactions occur
    """
    component_value = _component_func(
        comp="modal",
        isOpen=is_open,
        onClose=on_close,
        onCloseLabel=on_close_label,
        onConfirm=on_confirm,
        onConfirmLabel=on_confirm_label,
        children=children,
        width=width,
        className=class_name,
        hideActions=hide_actions,
        title=title,
        name=name,
        key=key,
        default={"event": None, "name": name or "modal", "action": None},
    )

    # We could modify the value returned from the component if we wanted.
    # There's no need to do this in our simple example - but it's an option.
    return component_value
