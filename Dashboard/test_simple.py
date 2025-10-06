"""
Simple test Streamlit app to verify everything works
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from pathlib import Path

def main():
    st.set_page_config(
        page_title="Euro 2024 Test",
        page_icon="⚽",
        layout="wide"
    )
    
    st.title("🏆 Euro 2024 Dashboard Test")
    st.write("Testing basic functionality...")
    
    # Test basic metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Matches", "51")
    with col2:
        st.metric("Total Events", "187,858")
    with col3:
        st.metric("Total Goals", "126")
    with col4:
        st.metric("Avg Goals/Match", "2.47")
    
    # Test basic chart
    st.subheader("Sample Chart")
    
    # Sample data for testing
    data = {
        'Stage': ['Group Stage', 'Round of 16', 'Quarter-finals', 'Semi-finals', 'Final'],
        'Matches': [36, 8, 4, 2, 1],
        'Avg Goals': [2.25, 2.0, 1.6, 1.0, 1.0]
    }
    
    fig = px.bar(
        x=data['Stage'],
        y=data['Avg Goals'],
        title="Goals by Tournament Stage",
        labels={'x': 'Stage', 'y': 'Average Goals'}
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Test data loading
    st.subheader("Data Loading Test")
    
    try:
        # Try to load the main dataset
        data_path = Path("../Data/euro_2024_complete_dataset.csv")
        if data_path.exists():
            st.success(f"✅ Found main dataset: {data_path}")
            df = pd.read_csv(data_path, nrows=100)  # Load only first 100 rows for testing
            st.write(f"Dataset shape (first 100 rows): {df.shape}")
            st.write("Sample data:")
            st.dataframe(df.head())
        else:
            st.warning(f"⚠️ Main dataset not found at: {data_path}")
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
    
    # Test other data files
    data_files = [
        "../Data/events_complete.csv",
        "../thoughts/eda_insights.csv",
        "../models/preprocessing/input_generation/momentum_windows_complete.csv"
    ]
    
    st.subheader("Data Files Status")
    for file_path in data_files:
        path = Path(file_path)
        if path.exists():
            st.success(f"✅ {path.name}")
        else:
            st.error(f"❌ {path.name} - Not found")
    
    st.success("🎉 Basic dashboard functionality is working!")

if __name__ == "__main__":
    main()
