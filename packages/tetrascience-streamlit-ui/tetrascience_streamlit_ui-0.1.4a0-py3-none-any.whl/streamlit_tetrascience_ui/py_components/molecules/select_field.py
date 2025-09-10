from ..utils import declare_component

_component_func = declare_component("select_field")


def select_field(
    label,
    info_text=None,
    supportive_text=None,
    show_supportive_check=False,
    class_name=None,
    key=None,
    **dropdown_props,
):
    """
    Create a select field component for displaying a labeled dropdown with supportive text.

    Args:
        label (str): The label for the select field (required)
        info_text (str, optional): Additional info text for the label
        supportive_text (str, optional): Supportive/help text below the dropdown
        show_supportive_check (bool): Whether to show a check icon with supportive text (default: False)
        class_name (str, optional): Additional CSS class for the container
        key (str, optional): Streamlit component key
        **dropdown_props: Additional dropdown properties (passed to the dropdown element)

    Returns:
        dict: Dictionary with event details when the select field is rendered:
              - 'render': when the select field is displayed
              Contains: event, label
    """
    component_value = _component_func(
        comp="select_field",
        label=label,
        infoText=info_text,
        supportiveText=supportive_text,
        showSupportiveCheck=show_supportive_check,
        className=class_name,
        key=key,
        **dropdown_props,
        default={
            "event": "render",
            "label": label,
        },
    )

    return component_value
