"""
Euro 2024 Momentum Analytics Dashboard
Main Streamlit Application
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Import dashboard modules
try:
    from pages.tournament_overview import TournamentOverview
    from pages.arimax_momentum import ARIMAXMomentumPage
    from utils.data_loader import DataLoader
    from utils.config import DashboardConfig
except ImportError:
    # Fallback for direct execution
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent))
    from pages.tournament_overview import TournamentOverview
    from pages.arimax_momentum import ARIMAXMomentumPage
    from utils.data_loader import DataLoader
    from utils.config import DashboardConfig

def main():
    """Main dashboard application"""
    
    # Page configuration
    st.set_page_config(
        page_title="Euro 2024 Analytics",
        page_icon="⚽",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .insight-box {
        background-color: #e8f4fd;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #1f77b4;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("🏆 Euro 2024 Analytics")
    st.sidebar.markdown("---")
    
    # Restructured pages - ARIMAX/Momentum first, removed Game and Time Analysis
    pages = {
        "ARIMAX Momentum Analysis": "🎯",
        "Tournament Overview": "🏟️"
    }
    
    selected_page = st.sidebar.selectbox(
        "Select Page",
        list(pages.keys()),
        format_func=lambda x: f"{pages[x]} {x}"
    )
    
    # Load data
    try:
        with st.spinner("Loading Euro 2024 data..."):
            data_loader = DataLoader()
            data_loader.load_all_data()
        
        # Route to selected page
        if selected_page == "ARIMAX Momentum Analysis":
            arimax_page = ARIMAXMomentumPage(data_loader)
            arimax_page.render()
        elif selected_page == "Tournament Overview":
            tournament_overview = TournamentOverview(data_loader)
            tournament_overview.render()
        else:
            st.title(f"{pages[selected_page]} {selected_page}")
            st.info(f"{selected_page} page coming soon...")
            
    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.info("Using fallback data from EDA analysis. Some features may be limited.")
        
        # Try to show basic page anyway
        try:
            data_loader = DataLoader()
            if selected_page == "ARIMAX Momentum Analysis":
                arimax_page = ARIMAXMomentumPage(data_loader)
                arimax_page.render()
            elif selected_page == "Tournament Overview":
                tournament_overview = TournamentOverview(data_loader)
                tournament_overview.render()
        except Exception as e2:
            st.error(f"Critical error: {str(e2)}")
            st.info("Please check the console for detailed error information.")

if __name__ == "__main__":
    main()
