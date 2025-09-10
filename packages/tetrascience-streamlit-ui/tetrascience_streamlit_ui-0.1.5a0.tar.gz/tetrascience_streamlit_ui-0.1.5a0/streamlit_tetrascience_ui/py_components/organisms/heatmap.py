from ..utils import declare_component

_component_func = declare_component("heatmap")


def heatmap(
    data=None,
    x_labels=None,
    y_labels=None,
    title="Heatmap",
    x_title="Columns",
    y_title="Rows",
    colorscale=None,
    width=1000,
    height=600,
    show_scale=True,
    precision=0,
    zmin=0,
    zmax=50000,
    value_unit="",
    name=None,
    key=None,
):
    """
    Create a heatmap component for displaying 2D data using Plotly.

    Args:
        data (list): 2D list of numbers for the heatmap values
        x_labels (list, optional): Labels for the X-axis (columns)
        y_labels (list, optional): Labels for the Y-axis (rows)
        title (str): Main title of the heatmap (default: "Heatmap")
        x_title (str): Title for the X-axis (default: "Columns")
        y_title (str): Title for the Y-axis (default: "Rows")
        colorscale (str or list, optional): Plotly colorscale name or custom scale
        width (int): Width of the heatmap in pixels (default: 1000)
        height (int): Height of the heatmap in pixels (default: 600)
        show_scale (bool): Whether to show the color scale bar (default: True)
        precision (int): Number of decimal places for values (default: 0)
        zmin (int): Minimum value for color scale (default: 0)
        zmax (int): Maximum value for color scale (default: 50000)
        value_unit (str): Suffix for value display (default: "")
        name (str, optional): Name identifier for the heatmap component
        key (str, optional): Streamlit component key

    Returns:
        dict: Dictionary with event details when the heatmap is rendered:
              - 'render': when the heatmap is displayed
              Contains: event, name, title, dataPoints
    """
    if data is None:
        data = []

    component_value = _component_func(
        comp="heatmap",
        data=data,
        xLabels=x_labels,
        yLabels=y_labels,
        title=title,
        xTitle=x_title,
        yTitle=y_title,
        colorscale=colorscale,
        width=width,
        height=height,
        showScale=show_scale,
        precision=precision,
        zmin=zmin,
        zmax=zmax,
        valueUnit=value_unit,
        name=name,
        key=key,
        default={
            "event": "render",
            "name": name or "heatmap",
            "title": title,
            "dataPoints": len(data),
        },
    )

    return component_value
