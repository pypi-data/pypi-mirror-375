from ..utils import declare_component

_component_func = declare_component("dot_plot")


def dot_plot(
    data_series=None,
    width=1000,
    height=600,
    variant="default",
    x_title="Columns",
    y_title="Rows",
    title="Dot Plot",
    marker_size=8,
    name=None,
    key=None,
):
    """
    Create a dot plot component for displaying data in scatter plot format using Plotly.

    Args:
        data_series (list): List of data series, each containing:
                           - x (list): X-axis values (numbers)
                           - y (list): Y-axis values (numbers)
                           - name (str): Name of the series for legend
                           - color (str, optional): Color for the markers (hex or color name)
                           - symbol (str, optional): Marker symbol - "circle", "square", "diamond",
                                    "triangle-up", "triangle-down", "star"
                           - size (int, optional): Size of individual markers
        width (int): Width of the graph in pixels (default: 1000)
        height (int): Height of the graph in pixels (default: 600)
        variant (str): Dot plot variant - "default" (all circles, same color) or
                      "stacked" (different symbols and colors) (default: "default")
        x_title (str): Title for the X-axis (default: "Columns")
        y_title (str): Title for the Y-axis (default: "Rows")
        title (str): Main title of the graph (default: "Dot Plot")
        marker_size (int): Default size of markers (default: 8)
        name (str, optional): Name identifier for the dot plot component
        key (str, optional): Streamlit component key

    Returns:
        dict: Dictionary with event details when the graph is rendered:
              - 'render': when the graph is displayed
              Contains: event, name, title, seriesCount, variant
    """
    if data_series is None:
        data_series = []

    component_value = _component_func(
        comp="dot_plot",
        dataSeries=data_series,
        width=width,
        height=height,
        variant=variant,
        xTitle=x_title,
        yTitle=y_title,
        title=title,
        markerSize=marker_size,
        name=name,
        key=key,
        default={
            "event": "render",
            "name": name or "dot_plot",
            "title": title,
            "seriesCount": len(data_series),
            "variant": variant,
        },
    )

    # We could modify the value returned from the component if we wanted.
    # There's no need to do this in our simple example - but it's an option.
    return component_value
