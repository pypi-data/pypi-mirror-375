from ..utils import declare_component

_component_func = declare_component("protocol_yaml_card")


def protocol_yaml_card(
    title="Protocol Editor",
    new_version_mode=False,
    on_toggle_new_version_mode=None,
    version_options=None,
    selected_version="",
    on_version_change=None,
    on_deploy=None,
    yaml="",
    on_yaml_change=None,
    name=None,
    key=None,
):
    """
    Create a protocol YAML card component for editing and managing protocol configurations.

    Args:
        title (str): The title displayed in the card header (default: "Protocol Editor")
        new_version_mode (bool): Whether new version mode is enabled (default: False)
        on_toggle_new_version_mode (callable, optional): Callback when new version mode is toggled
        version_options (list, optional): List of version options with 'label' and 'value' keys
        selected_version (str): Currently selected version (default: "")
        on_version_change (callable, optional): Callback when version selection changes
        on_deploy (callable, optional): Callback when deploy button is clicked
        yaml (str): The YAML content to display/edit (default: "")
        on_yaml_change (callable, optional): Callback when YAML content changes
        name (str, optional): Name identifier for the protocol yaml card component
        key (str, optional): Streamlit component key

    Returns:
        dict: Dictionary with event details when interactions occur:
              - 'toggleNewVersionMode': when version mode is toggled
              - 'versionChange': when version selection changes
              - 'deploy': when deploy button is clicked
              - 'yamlChange': when YAML content is modified
    """
    if version_options is None:
        version_options = []

    component_value = _component_func(
        comp="protocol_yaml_card",
        title=title,
        newVersionMode=new_version_mode,
        onToggleNewVersionMode=on_toggle_new_version_mode,
        versionOptions=version_options,
        selectedVersion=selected_version,
        onVersionChange=on_version_change,
        onDeploy=on_deploy,
        yaml=yaml,
        onYamlChange=on_yaml_change,
        name=name,
        key=key,
        default={
            "event": None,
            "name": name or "protocol_yaml_card",
            "newVersionMode": new_version_mode,
            "selectedVersion": selected_version,
            "yaml": yaml,
        },
    )

    # We could modify the value returned from the component if we wanted.
    # There's no need to do this in our simple example - but it's an option.
    return component_value
