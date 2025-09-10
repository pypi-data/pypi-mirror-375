from ..utils import declare_component

_component_func = declare_component("form_field")


def form_field(
    label,
    info_text=None,
    supportive_text=None,
    show_supportive_check=False,
    class_name=None,
    key=None,
    **input_props,
):
    """
    Create a form field component for displaying a labeled input with supportive text.

    Args:
        label (str): The label for the form field (required)
        info_text (str, optional): Additional info text for the label
        supportive_text (str, optional): Supportive/help text below the input
        show_supportive_check (bool): Whether to show a check icon with supportive text (default: False)
        class_name (str, optional): Additional CSS class for the container
        key (str, optional): Streamlit component key
        **input_props: Additional input properties (passed to the input element)

    Returns:
        dict: Dictionary with event details when the form field is rendered:
              - 'render': when the form field is displayed
              Contains: event, label
    """
    component_value = _component_func(
        comp="form_field",
        label=label,
        infoText=info_text,
        supportiveText=supportive_text,
        showSupportiveCheck=show_supportive_check,
        className=class_name,
        key=key,
        **input_props,
        default={
            "event": "render",
            "label": label,
        },
    )

    return component_value
