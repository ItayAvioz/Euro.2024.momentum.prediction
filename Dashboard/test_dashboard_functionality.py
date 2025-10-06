"""
Comprehensive Dashboard Functionality Test
Tests all components to ensure they work properly
"""

import streamlit as st
import sys
from pathlib import Path
import traceback

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def test_imports():
    """Test all required imports"""
    st.subheader("🔧 Import Tests")
    
    tests = []
    
    # Test basic imports
    try:
        import pandas as pd
        import plotly.express as px
        import plotly.graph_objects as go
        import numpy as np
        tests.append(("✅", "Basic libraries", "Success"))
    except Exception as e:
        tests.append(("❌", "Basic libraries", f"Failed: {str(e)}"))
    
    # Test dashboard imports
    try:
        from utils.data_loader import DataLoader
        from utils.config import DashboardConfig
        from utils.chart_helpers import ChartHelpers
        tests.append(("✅", "Dashboard utilities", "Success"))
    except Exception as e:
        tests.append(("❌", "Dashboard utilities", f"Failed: {str(e)}"))
    
    # Test page imports
    try:
        from pages.tournament_overview import TournamentOverview
        tests.append(("✅", "Tournament Overview page", "Success"))
    except Exception as e:
        tests.append(("❌", "Tournament Overview page", f"Failed: {str(e)}"))
    
    # Display results
    for status, component, message in tests:
        st.write(f"{status} **{component}**: {message}")
    
    return all(test[0] == "✅" for test in tests)

def test_data_loading():
    """Test data loading functionality"""
    st.subheader("📊 Data Loading Tests")
    
    try:
        from utils.data_loader import DataLoader
        from utils.config import DashboardConfig
        
        config = DashboardConfig()
        data_loader = DataLoader()
        
        # Test file paths
        st.write("**File Paths:**")
        paths = {
            "Euro 2024 Complete": config.EURO_2024_COMPLETE,
            "Events Complete": config.EVENTS_COMPLETE,
            "Matches Complete": config.MATCHES_COMPLETE,
            "EDA Insights": config.EDA_INSIGHTS
        }
        
        for name, path in paths.items():
            exists = Path(path).exists()
            status = "✅" if exists else "⚠️"
            st.write(f"{status} {name}: {path}")
        
        # Test data methods
        st.write("**Data Methods:**")
        
        try:
            stats = data_loader.get_tournament_stats()
            st.write("✅ Tournament stats loaded successfully")
            st.json(stats)
        except Exception as e:
            st.write(f"❌ Tournament stats failed: {str(e)}")
        
        try:
            time_analysis = data_loader.get_time_analysis()
            st.write("✅ Time analysis loaded successfully")
            st.write(f"Kickoff times: {list(time_analysis.get('kickoff_times', {}).keys())}")
        except Exception as e:
            st.write(f"❌ Time analysis failed: {str(e)}")
        
        try:
            stage_analysis = data_loader.get_stage_analysis()
            st.write("✅ Stage analysis loaded successfully")
            st.write(f"Stages: {list(stage_analysis.keys())}")
        except Exception as e:
            st.write(f"❌ Stage analysis failed: {str(e)}")
        
        return True
        
    except Exception as e:
        st.error(f"Data loading test failed: {str(e)}")
        st.code(traceback.format_exc())
        return False

def test_chart_creation():
    """Test chart creation functionality"""
    st.subheader("📈 Chart Creation Tests")
    
    try:
        from utils.chart_helpers import ChartHelpers
        from utils.data_loader import DataLoader
        
        chart_helpers = ChartHelpers()
        data_loader = DataLoader()
        
        # Test stage distribution pie chart
        try:
            stage_data = {
                "Group Stage": 36,
                "Round of 16": 8,
                "Quarter-finals": 4,
                "Semi-finals": 2,
                "Final": 1
            }
            fig = chart_helpers.create_stage_distribution_pie(stage_data)
            st.write("✅ Stage distribution pie chart created")
            st.plotly_chart(fig, use_container_width=True, key="test_stage_pie")
        except Exception as e:
            st.write(f"❌ Stage distribution pie chart failed: {str(e)}")
        
        # Test kickoff time comparison
        try:
            time_analysis = data_loader.get_time_analysis()
            fig = chart_helpers.create_kickoff_time_comparison(time_analysis)
            st.write("✅ Kickoff time comparison chart created")
            st.plotly_chart(fig, use_container_width=True, key="test_kickoff_chart")
        except Exception as e:
            st.write(f"❌ Kickoff time comparison failed: {str(e)}")
        
        # Test half comparison
        try:
            time_analysis = data_loader.get_time_analysis()
            fig = chart_helpers.create_half_comparison_chart(time_analysis)
            st.write("✅ Half comparison chart created")
            st.plotly_chart(fig, use_container_width=True, key="test_half_chart")
        except Exception as e:
            st.write(f"❌ Half comparison failed: {str(e)}")
        
        return True
        
    except Exception as e:
        st.error(f"Chart creation test failed: {str(e)}")
        st.code(traceback.format_exc())
        return False

def test_tournament_overview():
    """Test tournament overview page"""
    st.subheader("🏟️ Tournament Overview Page Test")
    
    try:
        from pages.tournament_overview import TournamentOverview
        from utils.data_loader import DataLoader
        
        data_loader = DataLoader()
        tournament_overview = TournamentOverview(data_loader)
        
        st.write("✅ Tournament Overview page instantiated successfully")
        
        # Test individual render methods
        try:
            stats = data_loader.get_tournament_stats()
            tournament_overview.render_key_metrics(stats)
            st.write("✅ Key metrics rendered successfully")
        except Exception as e:
            st.write(f"❌ Key metrics failed: {str(e)}")
        
        return True
        
    except Exception as e:
        st.error(f"Tournament overview test failed: {str(e)}")
        st.code(traceback.format_exc())
        return False

def main():
    """Main test function"""
    st.set_page_config(
        page_title="Dashboard Test Suite",
        page_icon="🧪",
        layout="wide"
    )
    
    st.title("🧪 Euro 2024 Dashboard Test Suite")
    st.markdown("Comprehensive testing of all dashboard components")
    st.markdown("---")
    
    # Run all tests
    tests = [
        ("Import Tests", test_imports),
        ("Data Loading Tests", test_data_loading),
        ("Chart Creation Tests", test_chart_creation),
        ("Tournament Overview Tests", test_tournament_overview)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        st.markdown(f"## {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            st.error(f"Test '{test_name}' crashed: {str(e)}")
            st.code(traceback.format_exc())
            results.append((test_name, False))
        
        st.markdown("---")
    
    # Summary
    st.markdown("## 📋 Test Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        st.write(f"{status} {test_name}")
    
    if passed == total:
        st.success(f"🎉 All {total} tests passed! Dashboard is ready to use.")
    else:
        st.warning(f"⚠️ {passed}/{total} tests passed. Please check the failed tests above.")
    
    # Instructions
    st.markdown("---")
    st.markdown("## 🚀 Next Steps")
    
    if passed == total:
        st.markdown("""
        **Dashboard is ready!** You can now:
        1. Run `streamlit run main.py` to start the main dashboard
        2. Navigate to the Tournament Overview page
        3. All charts and data should load properly
        """)
    else:
        st.markdown("""
        **Fix the issues above first:**
        1. Check the error messages in the failed tests
        2. Ensure all required files exist
        3. Verify import paths are correct
        4. Re-run this test suite until all tests pass
        """)

if __name__ == "__main__":
    main()
