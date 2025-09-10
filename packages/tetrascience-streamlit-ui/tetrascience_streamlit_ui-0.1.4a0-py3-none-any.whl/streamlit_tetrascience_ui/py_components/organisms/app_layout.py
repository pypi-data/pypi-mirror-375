from ..utils import declare_component

_component_func = declare_component("app_layout")


def app_layout(
    user_profile=None,
    hostname=None,
    organization=None,
    line_graph_config=None,
    key=None,
):
    """
    Create an app layout component that provides a consistent application shell
    with navigation, sidebar, and header components.

    Args:
        user_profile (dict): User profile information containing:
                            - name (str): User's name
                            - avatar (str, optional): URL to user's avatar image
        hostname (str): The hostname to display in the header
        organization (dict): Organization information containing:
                            - name (str): Organization name
                            - subtext (str, optional): Additional organization text
                            - logo (React.ReactNode, optional): Organization logo
        line_graph_config (dict, optional): LineGraph configuration containing:
                                           - data_series (list): Data series for the graph
                                           - width (int): Width of the graph
                                           - height (int): Height of the graph
                                           - x_title (str): X-axis title
                                           - y_title (str): Y-axis title
                                           - title (str): Graph title
                                           - variant (str): Graph variant
        key (str, optional): Streamlit component key

    Returns:
        dict: Dictionary with event details when the layout is rendered:
              - 'render': when the layout is displayed
              Contains: event, user_profile, hostname, organization
    """
    if user_profile is None:
        user_profile = {"name": "User"}
    if hostname is None:
        hostname = "localhost"
    if organization is None:
        organization = {"name": "Organization"}

    component_value = _component_func(
        comp="app_layout",
        userProfile=user_profile,
        hostname=hostname,
        organization=organization,
        lineGraphConfig=line_graph_config,
        key=key,
        default={
            "event": "render",
            "userProfile": user_profile,
            "hostname": hostname,
            "organization": organization,
        },
    )

    return component_value
