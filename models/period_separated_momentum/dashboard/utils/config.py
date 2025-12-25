"""
Dashboard Configuration Settings for Period-Separated Momentum
"""

from pathlib import Path

class DashboardConfig:
    """Configuration settings for the period-separated momentum dashboard"""
    
    # Paths - relative to this dashboard folder
    DASHBOARD_ROOT = Path(__file__).parent.parent
    PERIOD_MOMENTUM_ROOT = DASHBOARD_ROOT.parent
    PROJECT_ROOT = PERIOD_MOMENTUM_ROOT.parent.parent
    
    DATA_PATH = PROJECT_ROOT / "Data"
    EDA_PATH = PROJECT_ROOT / "EDA"
    
    # Period-separated momentum data files
    MOMENTUM_DATA = PERIOD_MOMENTUM_ROOT / "outputs" / "momentum_by_period.csv"
    ARIMAX_PREDICTIONS = PERIOD_MOMENTUM_ROOT / "outputs" / "arimax_predictions_by_period.csv"
    
    # Original data files (for comparison if needed)
    EURO_2024_COMPLETE = DATA_PATH / "euro_2024_complete_dataset.csv"
    EVENTS_COMPLETE = DATA_PATH / "events_complete.csv"
    MATCHES_COMPLETE = DATA_PATH / "matches_complete.csv"
    
    # Dashboard settings
    COLOR_SCHEME = {
        'primary': '#1f77b4',      # Tournament blue
        'secondary': '#ff7f0e',    # Goal orange
        'success': '#2ca02c',      # Win green
        'warning': '#d62728',      # Loss red
        'neutral': '#7f7f7f',      # Draw gray
        'background': '#f0f2f6'
    }
    
    # Chart settings
    CHART_HEIGHT = 400
    CHART_WIDTH = None  # Auto
    
    @classmethod
    def get_color(cls, color_name):
        """Get color from scheme"""
        return cls.COLOR_SCHEME.get(color_name, '#1f77b4')
    
    @classmethod
    def file_exists(cls, filepath):
        """Check if file exists"""
        return Path(filepath).exists()
