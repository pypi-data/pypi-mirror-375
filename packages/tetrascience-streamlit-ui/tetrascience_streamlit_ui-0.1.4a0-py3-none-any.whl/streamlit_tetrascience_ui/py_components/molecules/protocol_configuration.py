from ..utils import declare_component

_component_func = declare_component("protocol_configuration")


def protocol_configuration(class_name=None, key=None, **other_props):
    """
    Create a protocol configuration component for displaying protocol configuration UI.

    Args:
        class_name (str, optional): Additional CSS class for the container
        key (str, optional): Streamlit component key
        **other_props: Additional props for ProtocolConfiguration

    Returns:
        dict: Dictionary with event details when the protocol configuration is rendered:
              - 'render': when the protocol configuration is displayed
              Contains: event
    """
    component_value = _component_func(
        comp="protocol_configuration",
        className=class_name,
        key=key,
        **other_props,
        default={
            "event": "render",
        },
    )

    return component_value
