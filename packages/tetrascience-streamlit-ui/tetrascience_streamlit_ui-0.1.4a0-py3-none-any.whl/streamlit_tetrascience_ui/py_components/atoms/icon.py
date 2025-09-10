from ..utils import declare_component

_component_func = declare_component("icon")


def icon(name, fill=None, width=None, height=None, key=None):
    """
    Create an icon component to display SVG icons from the TetraScience icon library.

    Args:
        name (str): Icon name from the available icon set (e.g., "check", "close", "search", etc.)
                   Available names include: bars-3-bottom-left, building, bulk-check, check,
                   check-circle, check-square, chevron-down, close, code, computer, copy, cube,
                   database, exclamation-circle, exclamation-triangle, gear, globe, hashtag,
                   home, inbox, information-circle, information-circle-micro, lamp, lock-open,
                   minus, paper-plane, pencil, pie-chart, pipeline, plus, profile, question-circle,
                   rocket-launch, search, search-document, search-sql, sitemap, tetrascience-icon,
                   text, trash, viewfinder-circle
        fill (str, optional): Fill color for the icon (CSS color value)
        width (str, optional): Width of the icon (CSS size value, e.g., "24px", "1rem")
        height (str, optional): Height of the icon (CSS size value, e.g., "24px", "1rem")
        key (str, optional): Streamlit component key

    Returns:
        dict: Dictionary with icon properties for tracking
    """
    component_value = _component_func(
        comp="icon",
        name=name,
        fill=fill,
        width=width,
        height=height,
        key=key,
        default={"name": name},
    )

    # We could modify the value returned from the component if we wanted.
    # There's no need to do this in our simple example - but it's an option.
    return component_value
