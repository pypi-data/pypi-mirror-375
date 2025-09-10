from ..utils import declare_component

_component_func = declare_component("markdown_display")


def markdown_display(
    markdown="# Default Markdown\nThis is default markdown content.",
    code_renderer=None,
    name=None,
    key=None,
):
    """
    Create a markdown display component to render markdown content with syntax highlighting.

    Args:
        markdown (str): The markdown content to render (default: "# Default Markdown\nThis is default markdown content.")
        code_renderer (callable, optional): Custom code renderer function for syntax highlighting.
                                          If not provided, uses the default code renderer with copy functionality
        name (str, optional): Name identifier for the markdown display component
        key (str, optional): Streamlit component key

    Returns:
        dict: Dictionary with markdown display properties for tracking
    """
    component_value = _component_func(
        comp="markdown_display",
        markdown=markdown,
        codeRenderer=code_renderer,
        name=name,
        key=key,
        default={"markdown": markdown, "name": name or "markdown_display"},
    )

    # We could modify the value returned from the component if we wanted.
    # There's no need to do this in our simple example - but it's an option.
    return component_value
