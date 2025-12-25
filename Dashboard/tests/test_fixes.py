"""
Simple test script to verify dashboard fixes
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def main():
    st.set_page_config(
        page_title="Dashboard Fixes Test",
        page_icon="🔧",
        layout="wide"
    )
    
    st.title("🔧 Dashboard Fixes Test")
    st.markdown("Testing the UTF-8 and empty chart fixes")
    st.markdown("---")
    
    # Test imports
    st.subheader("📦 Import Tests")
    try:
        from utils.data_loader import DataLoader
        from utils.chart_helpers import ChartHelpers
        st.success("✅ All imports successful")
    except Exception as e:
        st.error(f"❌ Import error: {str(e)}")
        return
    
    # Test data loading
    st.subheader("📊 Data Loading Tests")
    
    try:
        data_loader = DataLoader()
        
        # Test time analysis (should always work)
        time_analysis = data_loader.get_time_analysis()
        if time_analysis and 'kickoff_times' in time_analysis:
            st.success("✅ Time analysis loaded successfully")
            st.write(f"Kickoff times: {list(time_analysis['kickoff_times'].keys())}")
        else:
            st.error("❌ Time analysis failed")
        
        # Test stage analysis (should always work)
        stage_analysis = data_loader.get_stage_analysis()
        if stage_analysis:
            st.success("✅ Stage analysis loaded successfully")
            st.write(f"Stages: {list(stage_analysis.keys())}")
        else:
            st.error("❌ Stage analysis failed")
        
    except Exception as e:
        st.error(f"❌ Data loading error: {str(e)}")
        st.code(str(e))
    
    # Test chart creation
    st.subheader("📈 Chart Creation Tests")
    
    try:
        chart_helpers = ChartHelpers()
        data_loader = DataLoader()
        
        # Test kickoff time chart
        time_analysis = data_loader.get_time_analysis()
        fig = chart_helpers.create_kickoff_time_comparison(time_analysis)
        
        if fig and fig.data:  # Check if chart has data
            st.success("✅ Kickoff time chart created with data")
            st.plotly_chart(fig, use_container_width=True, key="test_kickoff")
        else:
            st.error("❌ Kickoff time chart has no data")
        
        # Test half comparison chart
        fig2 = chart_helpers.create_half_comparison_chart(time_analysis)
        
        if fig2 and fig2.data:  # Check if chart has data
            st.success("✅ Half comparison chart created with data")
            st.plotly_chart(fig2, use_container_width=True, key="test_half")
        else:
            st.error("❌ Half comparison chart has no data")
        
        # Test stage distribution
        stage_analysis = data_loader.get_stage_analysis()
        stage_data = {
            "Group Stage": stage_analysis['group_stage']['matches'],
            "Round of 16": stage_analysis['round_16']['matches'],
            "Quarter-finals": stage_analysis['quarter_finals']['matches'],
            "Semi-finals": stage_analysis['semi_finals']['matches'],
            "Final": stage_analysis['final']['matches']
        }
        
        fig3 = chart_helpers.create_stage_distribution_pie(stage_data)
        
        if fig3 and fig3.data:  # Check if chart has data
            st.success("✅ Stage distribution chart created with data")
            st.plotly_chart(fig3, use_container_width=True, key="test_stage")
        else:
            st.error("❌ Stage distribution chart has no data")
        
    except Exception as e:
        st.error(f"❌ Chart creation error: {str(e)}")
        st.code(str(e))
    
    # Summary
    st.markdown("---")
    st.subheader("🎯 Test Summary")
    st.success("🎉 If you see charts above with data, the fixes are working!")
    st.info("💡 Now restart your main dashboard and the issues should be resolved.")

if __name__ == "__main__":
    main()
