from ..utils import declare_component

_component_func = declare_component("python_editor_modal")


def python_editor_modal(open, initial_value=None, title=None, key=None, **other_props):
    """
    Create a Python editor modal component for editing Python code in a modal dialog.

    Args:
        open (bool): Whether the modal is open (required)
        initial_value (str, optional): Initial code value
        title (str, optional): Title of the modal
        key (str, optional): Streamlit component key
        **other_props: Additional props for PythonEditorModal

    Returns:
        dict: Dictionary with event details when the modal is rendered:
              - 'render': when the modal is displayed
              Contains: event, open, title
    """
    component_value = _component_func(
        comp="python_editor_modal",
        open=open,
        initialValue=initial_value,
        title=title,
        key=key,
        **other_props,
        default={
            "event": "render",
            "open": open,
            "title": title,
        },
    )

    return component_value
