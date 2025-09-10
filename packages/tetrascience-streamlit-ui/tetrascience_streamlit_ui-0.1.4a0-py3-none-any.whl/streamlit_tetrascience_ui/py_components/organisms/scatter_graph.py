from ..utils import declare_component

_component_func = declare_component("scatter_graph")


def scatter_graph(
    data_series=None,
    width=1000,
    height=600,
    x_range=None,
    y_range=None,
    x_title="Columns",
    y_title="Rows",
    title="Scatter Plot",
    name=None,
    key=None,
):
    """
    Create a scatter graph component for displaying data in scatter plot format using Plotly.

    Args:
        data_series (list): List of data series, each containing:
                           - x (list): X-axis values (numbers)
                           - y (list): Y-axis values (numbers)
                           - name (str): Name of the series for legend
                           - color (str): Color for the points (hex or color name)
        width (int): Width of the graph in pixels (default: 1000)
        height (int): Height of the graph in pixels (default: 600)
        x_range (tuple, optional): X-axis range as (min, max) tuple
        y_range (tuple, optional): Y-axis range as (min, max) tuple
        x_title (str): Title for the X-axis (default: "Columns")
        y_title (str): Title for the Y-axis (default: "Rows")
        title (str): Main title of the graph (default: "Scatter Plot")
        name (str, optional): Name identifier for the scatter graph component
        key (str, optional): Streamlit component key

    Returns:
        dict: Dictionary with event details when the graph is rendered:
              - 'render': when the graph is displayed
              Contains: event, name, title, seriesCount
    """
    if data_series is None:
        data_series = []

    component_value = _component_func(
        comp="scatter_graph",
        dataSeries=data_series,
        width=width,
        height=height,
        xRange=x_range,
        yRange=y_range,
        xTitle=x_title,
        yTitle=y_title,
        title=title,
        name=name,
        key=key,
        default={
            "event": "render",
            "name": name or "scatter_graph",
            "title": title,
            "seriesCount": len(data_series),
        },
    )

    return component_value
