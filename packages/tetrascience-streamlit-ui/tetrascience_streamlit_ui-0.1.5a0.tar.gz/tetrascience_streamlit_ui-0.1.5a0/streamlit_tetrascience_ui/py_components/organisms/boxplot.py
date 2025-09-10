from ..utils import declare_component

_component_func = declare_component("boxplot")


def boxplot(
    data_series=None,
    width=1000,
    height=600,
    x_range=None,
    y_range=None,
    x_title="Columns",
    y_title="Rows",
    title="Boxplot",
    show_points=False,
    name=None,
    key=None,
):
    """
    Create a boxplot component for displaying statistical distribution data using Plotly.

    Args:
        data_series (list): List of data series, each containing:
                           - y (list): Y-axis values (numbers) for the box plot
                           - name (str): Name of the series for legend
                           - color (str): Color for the box (hex or color name)
                           - x (list, optional): X-axis category values (strings or numbers)
                           - boxpoints (str, optional): Point display - "all", "outliers", "suspectedoutliers", or False
                           - jitter (float, optional): Amount of jitter for points (default: 0.3)
                           - pointpos (float, optional): Position of points relative to box (default: -1.8)
        width (int): Width of the graph in pixels (default: 1000)
        height (int): Height of the graph in pixels (default: 600)
        x_range (tuple, optional): X-axis range as (min, max) tuple
        y_range (tuple, optional): Y-axis range as (min, max) tuple
        x_title (str): Title for the X-axis (default: "Columns")
        y_title (str): Title for the Y-axis (default: "Rows")
        title (str): Main title of the graph (default: "Boxplot")
        show_points (bool): Whether to show outlier points (default: False)
        name (str, optional): Name identifier for the boxplot component
        key (str, optional): Streamlit component key

    Returns:
        dict: Dictionary with event details when the graph is rendered:
              - 'render': when the graph is displayed
              Contains: event, name, title, seriesCount, showPoints
    """
    if data_series is None:
        data_series = []

    component_value = _component_func(
        comp="boxplot",
        dataSeries=data_series,
        width=width,
        height=height,
        xRange=x_range,
        yRange=y_range,
        xTitle=x_title,
        yTitle=y_title,
        title=title,
        showPoints=show_points,
        name=name,
        key=key,
        default={
            "event": "render",
            "name": name or "boxplot",
            "title": title,
            "seriesCount": len(data_series),
            "showPoints": show_points,
        },
    )

    # We could modify the value returned from the component if we wanted.
    # There's no need to do this in our simple example - but it's an option.
    return component_value
