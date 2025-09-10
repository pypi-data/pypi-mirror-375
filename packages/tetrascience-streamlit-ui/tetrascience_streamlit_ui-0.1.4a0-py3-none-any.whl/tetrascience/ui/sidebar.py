import streamlit as st

from streamlit_tetrascience_ui.py_components.molecules.sidebar import (
    sidebar as sidebar_component,
)

# Default CSS styling for the sidebar
DEFAULT_SIDEBAR_CSS = """section[data-testid="stSidebar"] {background: #04263f;min-width: 100px;max-width: 100px;width: 100px;}[data-testid="stSidebarContent"] {padding: 0 !important; scrollbar-gutter: auto;}[data-testid="stSidebarUserContent"] {padding: 0;}[data-testid="stSidebarHeader"] {height: 80px;}section[data-testid="stSidebar"][aria-expanded="false"] {
    transform: translateX(-100px) !important;
    max-width: 0 !important;
    min-width: 0 !important;
}
"""


def sidebar(items=None, active_item="Home", custom_css=None):
    """
    Render the main application sidebar with navigation items.

    Args:
        items (list, optional): List of sidebar items, each containing:
                               - icon (str): Icon name for the item
                               - label (str): Display label for the item
                               If None, uses default items.
        active_item (str): The currently active sidebar item
        custom_css (str, optional): Additional custom CSS to style the sidebar.
                                   Default styling is always applied.

    Returns:
        dict: Result from sidebar interaction events
    """
    # Apply default CSS styling
    st.markdown(f"<style>{DEFAULT_SIDEBAR_CSS}</style>", unsafe_allow_html=True)

    # Apply additional custom CSS if provided
    if custom_css:
        st.markdown(f"<style>{custom_css}</style>", unsafe_allow_html=True)

    # Default items if none provided
    if items is None:
        items = [
            {"icon": "search-document", "label": "Search"},
            {"icon": "search-sql", "label": "SQL Search"},
            {"icon": "lamp", "label": "Projects"},
            {"icon": "pipeline", "label": "Pipelines"},
            {"icon": "computer", "label": "Data & AI Workspace"},
            {"icon": "cube", "label": "Artifacts"},
            {"icon": "database", "label": "Data Sources"},
            {"icon": "pie-chart", "label": "Health Monitoring"},
            {"icon": "bulk-check", "label": "Bulk Actions"},
            {"icon": "code", "label": "Attribute Management"},
            {"icon": "gear", "label": "Administration"},
        ]

    with st.sidebar:
        result = sidebar_component(
            items=items, active_item=active_item, key="main_sidebar"
        )

    return result
