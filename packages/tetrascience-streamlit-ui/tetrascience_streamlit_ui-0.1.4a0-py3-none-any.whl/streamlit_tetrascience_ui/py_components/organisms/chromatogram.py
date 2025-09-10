from ..utils import declare_component

_component_func = declare_component("chromatogram")


def chromatogram(
    data=None,
    width=900,
    height=600,
    position_interval=10,
    color_a="#2D9CDB",
    color_t="#A1C63C",
    color_g="#FF5C64",
    color_c="#FFA62E",
    name=None,
    key=None,
):
    """
    Create a chromatogram component for displaying DNA sequencing data with peak visualization.

    Args:
        data (list): List of peak data points, each containing:
                    - position (int): Position in the sequence
                    - base (str, optional): The base nucleotide (A, T, G, C)
                    - peakA (float): Peak intensity for Adenine
                    - peakT (float): Peak intensity for Thymine
                    - peakG (float): Peak intensity for Guanine
                    - peakC (float): Peak intensity for Cytosine
        width (int): Width of the chromatogram in pixels (default: 900)
        height (int): Height of the chromatogram in pixels (default: 600)
        position_interval (int): Interval between position markers on the chart (default: 10)
        color_a (str): Color for Adenine peaks (default: "#2D9CDB")
        color_t (str): Color for Thymine peaks (default: "#A1C63C")
        color_g (str): Color for Guanine peaks (default: "#FF5C64")
        color_c (str): Color for Cytosine peaks (default: "#FFA62E")
        name (str, optional): Name identifier for the chromatogram component
        key (str, optional): Streamlit component key

    Returns:
        dict: Dictionary with event details when the chromatogram is rendered:
              - 'render': when the chromatogram is displayed
              Contains: event, name, dataPoints, width, height, positionInterval
    """
    if data is None:
        data = []

    component_value = _component_func(
        comp="chromatogram",
        data=data,
        width=width,
        height=height,
        positionInterval=position_interval,
        colorA=color_a,
        colorT=color_t,
        colorG=color_g,
        colorC=color_c,
        name=name,
        key=key,
        default={
            "event": "render",
            "name": name or "chromatogram",
            "dataPoints": len(data),
            "width": width,
            "height": height,
            "positionInterval": position_interval,
        },
    )

    # We could modify the value returned from the component if we wanted.
    # There's no need to do this in our simple example - but it's an option.
    return component_value
