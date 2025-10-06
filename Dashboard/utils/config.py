"""
Dashboard Configuration Settings
"""

from pathlib import Path
import os

class DashboardConfig:
    """Configuration settings for the dashboard"""
    
    # Paths
    PROJECT_ROOT = Path(__file__).parent.parent.parent
    DATA_PATH = PROJECT_ROOT / "Data"
    EDA_PATH = PROJECT_ROOT / "EDA"
    MODELS_PATH = PROJECT_ROOT / "models"
    
    # Data files
    EURO_2024_COMPLETE = DATA_PATH / "euro_2024_complete_dataset.csv"
    EVENTS_COMPLETE = DATA_PATH / "events_complete.csv"
    MATCHES_COMPLETE = DATA_PATH / "matches_complete.csv"
    
    # EDA statistics files
    EDA_INSIGHTS = PROJECT_ROOT / "thoughts" / "eda_insights.csv"
    TOURNAMENT_STATS = EDA_PATH / "statistics"
    
    # Model results
    ARIMAX_PREDICTIONS = MODELS_PATH / "modeling" / "scripts" / "outputs" / "predictions" / "arimax_predictions.csv"
    MOMENTUM_WINDOWS = MODELS_PATH / "preprocessing" / "input_generation" / "momentum_windows_complete.csv"
    
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
    def get_data_path(cls, filename):
        """Get full path to data file"""
        return cls.DATA_PATH / filename
    
    @classmethod
    def file_exists(cls, filepath):
        """Check if file exists"""
        return Path(filepath).exists()
    
    @classmethod
    def get_color(cls, color_name):
        """Get color from scheme"""
        return cls.COLOR_SCHEME.get(color_name, '#1f77b4')
