from ..utils import declare_component

_component_func = declare_component("code_editor")


def code_editor(
    value="",
    language="javascript",
    editor_theme="light",
    height="300px",
    width="100%",
    options=None,
    label=None,
    on_copy=None,
    on_launch=None,
    disabled=False,
    name=None,
    key=None,
):
    """
    Create a code editor component.

    Args:
        value (str): The code content to display in the editor (default: "")
        language (str): Programming language for syntax highlighting (default: "javascript")
        editor_theme (str): Editor theme - "light" or "dark" (default: "light")
        height (str): Editor height (default: "300px")
        width (str): Editor width (default: "100%")
        options (dict, optional): Monaco editor configuration options
        label (str, optional): Label for the editor
        on_copy (callable, optional): Callback function for copy action
        on_launch (callable, optional): Callback function for launch action
        disabled (bool): Whether the editor is disabled (default: False)
        name (str, optional): Name identifier for the editor
        key (str, optional): Streamlit component key

    Returns:
        dict: Dictionary with 'value' (current code) and 'name' when code changes
    """
    component_value = _component_func(
        comp="code_editor",
        value=value,
        language=language,
        editorTheme=editor_theme,
        height=height,
        width=width,
        options=options,
        label=label,
        onCopy=on_copy,
        onLaunch=on_launch,
        disabled=disabled,
        name=name,
        key=key,
        default={"value": "", "name": name or "code_editor"},
    )

    # We could modify the value returned from the component if we wanted.
    # There's no need to do this in our simple example - but it's an option.
    return component_value
