from ..utils import declare_component

_component_func = declare_component("pie_chart")


def pie_chart(
    data_series=None,
    width=400,
    height=400,
    title="Pie Chart",
    text_info="percent",
    hole=0,
    rotation=0,
    name=None,
    key=None,
):
    """
    Create a pie chart component for displaying data in pie chart format using Plotly.

    Args:
        data_series (dict): Dictionary containing:
                           - labels (list): Labels for the pie slices
                           - values (list): Values for each slice
                           - name (str): Name of the series
                           - colors (list, optional): Colors for the slices
        width (int): Width of the chart in pixels (default: 400)
        height (int): Height of the chart in pixels (default: 400)
        title (str): Main title of the chart (default: "Pie Chart")
        text_info (str): Text info to display on slices (default: "percent")
        hole (int): Fraction of the radius to cut out of the pie (default: 0)
        rotation (int): Starting angle of the pie chart (default: 0)
        name (str, optional): Name identifier for the pie chart component
        key (str, optional): Streamlit component key

    Returns:
        dict: Dictionary with event details when the chart is rendered:
              - 'render': when the chart is displayed
              Contains: event, name, title, labelCount
    """
    if data_series is None:
        data_series = {"labels": [], "values": [], "name": "", "colors": []}

    component_value = _component_func(
        comp="pie_chart",
        dataSeries=data_series,
        width=width,
        height=height,
        title=title,
        textInfo=text_info,
        hole=hole,
        rotation=rotation,
        name=name,
        key=key,
        default={
            "event": "render",
            "name": name or "pie_chart",
            "title": title,
            "labelCount": len(data_series.get("labels", [])),
        },
    )

    return component_value
