from ..utils import declare_component

_component_func = declare_component("histogram")


def histogram(
    data_series,
    width=480,
    height=480,
    title="Histogram",
    x_title="X Axis",
    y_title="Frequency",
    bargap=0.2,
    show_distribution_line=False,
    key=None,
    class_name=None,
    **histogram_props
):
    """
    Create a Histogram component for displaying histogram charts.

    Args:
        data_series (dict or list): Histogram data series. Can be a single series dict or list of series.
                                   Each series should contain:
                                   - x (list): Data values for the histogram
                                   - name (str): Name of the series
                                   - color (str, optional): Color for the series
                                   - autobinx (bool, optional): Whether to automatically determine bins
                                   - xbins (dict, optional): Custom bin configuration with start, end, size
                                   - opacity (float, optional): Opacity of the bars
                                   - showDistributionLine (bool, optional): Show distribution line for this series
                                   - lineWidth (int, optional): Width of the distribution line
        width (int, optional): Width of the histogram in pixels. Default: 480
        height (int, optional): Height of the histogram in pixels. Default: 480
        title (str, optional): Title of the histogram. Default: "Histogram"
        x_title (str, optional): X-axis title. Default: "X Axis"
        y_title (str, optional): Y-axis title. Default: "Frequency"
        bargap (float, optional): Gap between bars. Default: 0.2
        show_distribution_line (bool, optional): Whether to show distribution line. Default: False
        key (str, optional): Streamlit component key
        class_name (str, optional): Additional CSS class for the container
        **histogram_props: Additional Histogram properties

    Returns:
        dict: Dictionary with event details when the Histogram is rendered:
              - 'render': when the Histogram is displayed
              Contains: event, dataSeries, width, height, title
    """
    component_value = _component_func(
        comp="histogram",
        dataSeries=data_series,
        width=width,
        height=height,
        title=title,
        xTitle=x_title,
        yTitle=y_title,
        bargap=bargap,
        showDistributionLine=show_distribution_line,
        className=class_name,
        key=key,
        **histogram_props,
        default={
            "event": "render",
            "dataSeries": data_series,
            "width": width,
            "height": height,
            "title": title,
        },
    )

    return component_value
