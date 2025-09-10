from ..utils import declare_component

_component_func = declare_component("area_graph")


def area_graph(
    data_series=None,
    width=1000,
    height=600,
    x_range=None,
    y_range=None,
    variant="normal",
    x_title="Columns",
    y_title="Rows",
    title="Area Graph",
    name=None,
    key=None,
):
    """
    Create an area graph component for displaying data in area chart format using Plotly.

    Args:
        data_series (list): List of data series, each containing:
                           - x (list): X-axis values (numbers)
                           - y (list): Y-axis values (numbers)
                           - name (str): Name of the series for legend
                           - color (str): Color for the area (hex or color name)
                           - fill (str, optional): Fill mode - "tozeroy", "tonexty", or "toself"
        width (int): Width of the graph in pixels (default: 1000)
        height (int): Height of the graph in pixels (default: 600)
        x_range (tuple, optional): X-axis range as (min, max) tuple
        y_range (tuple, optional): Y-axis range as (min, max) tuple
        variant (str): Area display variant - "normal" or "stacked" (default: "normal")
        x_title (str): Title for the X-axis (default: "Columns")
        y_title (str): Title for the Y-axis (default: "Rows")
        title (str): Main title of the graph (default: "Area Graph")
        name (str, optional): Name identifier for the area graph component
        key (str, optional): Streamlit component key

    Returns:
        dict: Dictionary with event details when the graph is rendered:
              - 'render': when the graph is displayed
              Contains: event, name, title, seriesCount, variant
    """
    if data_series is None:
        data_series = []

    component_value = _component_func(
        comp="area_graph",
        dataSeries=data_series,
        width=width,
        height=height,
        xRange=x_range,
        yRange=y_range,
        variant=variant,
        xTitle=x_title,
        yTitle=y_title,
        title=title,
        name=name,
        key=key,
        default={
            "event": "render",
            "name": name or "area_graph",
            "title": title,
            "seriesCount": len(data_series),
            "variant": variant,
        },
    )

    # We could modify the value returned from the component if we wanted.
    # There's no need to do this in our simple example - but it's an option.
    return component_value
