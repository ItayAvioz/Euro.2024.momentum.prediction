"""
Euro 2024 Momentum Analytics Dashboard - Period-Separated Version
Main Streamlit Application

This dashboard uses period-separated momentum data where first half and 
second half events are properly separated (no mixing at overlapping minutes).
"""

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add project paths
dashboard_root = Path(__file__).parent
project_root = dashboard_root.parent.parent.parent
sys.path.append(str(project_root))
sys.path.append(str(dashboard_root))

# Import dashboard modules
try:
    from pages.arimax_momentum import ARIMAXMomentumPage
    from utils.data_loader import DataLoader
    from utils.config import DashboardConfig
except ImportError:
    # Fallback for direct execution
    sys.path.append(str(Path(__file__).parent))
    from pages.arimax_momentum import ARIMAXMomentumPage
    from utils.data_loader import DataLoader
    from utils.config import DashboardConfig


def main():
    """Main dashboard application"""
    
    # Page configuration
    st.set_page_config(
        page_title="Euro 2024 ARIMAX Analytics (Period-Separated)",
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
    .period-separated-badge {
        background-color: #d4edda;
        color: #155724;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.9rem;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("🏆 Euro 2024 Analytics")
    st.sidebar.markdown('<span class="period-separated-badge">Period-Separated Data</span>', 
                       unsafe_allow_html=True)
    st.sidebar.markdown("---")
    
    # Single page - ARIMAX Momentum Analysis (focused dashboard)
    pages = {
        "ARIMAX Momentum Analysis": "🎯"
    }
    
    selected_page = st.sidebar.selectbox(
        "Select Page",
        list(pages.keys()),
        format_func=lambda x: f"{pages[x]} {x}"
    )
    
    # Data info in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Data Source")
    st.sidebar.info("""
    **Period-Separated Momentum**
    
    - First half (Period 1) and second half (Period 2) are calculated separately
    - No event mixing at overlapping minutes
    - Cleaner visualization for stoppage time
    """)
    
    # Load data
    try:
        with st.spinner("Loading period-separated momentum data..."):
            data_loader = DataLoader()
            data_loader.load_all_data()
        
        # Route to selected page
        if selected_page == "ARIMAX Momentum Analysis":
            arimax_page = ARIMAXMomentumPage(data_loader)
            arimax_page.render()
        else:
            st.title(f"{pages[selected_page]} {selected_page}")
            st.info(f"{selected_page} page coming soon...")
            
    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.info("Please check that the period-separated data files exist.")
        
        # Show expected file paths
        config = DashboardConfig()
        st.markdown("### Expected Data Files:")
        st.code(f"""
Momentum Data: {config.MOMENTUM_DATA}
  Exists: {config.MOMENTUM_DATA.exists()}

ARIMAX Predictions: {config.ARIMAX_PREDICTIONS}
  Exists: {config.ARIMAX_PREDICTIONS.exists()}
        """)
        
        # Try to show basic page anyway
        try:
            data_loader = DataLoader()
            if selected_page == "ARIMAX Momentum Analysis":
                arimax_page = ARIMAXMomentumPage(data_loader)
                arimax_page.render()
        except Exception as e2:
            st.error(f"Critical error: {str(e2)}")
            import traceback
            st.code(traceback.format_exc())


if __name__ == "__main__":
    main()

