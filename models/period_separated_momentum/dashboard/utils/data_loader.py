"""
Data Loading Utilities for Period-Separated Momentum Dashboard
"""

import pandas as pd
import numpy as np
from pathlib import Path
import streamlit as st
try:
    from .config import DashboardConfig
except ImportError:
    from config import DashboardConfig


class DataLoader:
    """Handles loading and caching of period-separated momentum data"""
    
    def __init__(self):
        self.config = DashboardConfig()
        self._data_cache = {}
    
    @st.cache_data(ttl=3600)
    def load_momentum_data(_self):
        """Load period-separated momentum data"""
        try:
            if _self.config.MOMENTUM_DATA.exists():
                df = pd.read_csv(_self.config.MOMENTUM_DATA)
                return df
            else:
                st.warning(f"Momentum data not found at {_self.config.MOMENTUM_DATA}")
                return None
        except Exception as e:
            st.warning(f"Error loading momentum data: {str(e)}")
            return None
    
    @st.cache_data(ttl=3600)
    def load_arimax_predictions(_self):
        """Load period-separated ARIMAX predictions"""
        try:
            if _self.config.ARIMAX_PREDICTIONS.exists():
                df = pd.read_csv(_self.config.ARIMAX_PREDICTIONS)
                return df
            else:
                st.warning(f"ARIMAX predictions not found at {_self.config.ARIMAX_PREDICTIONS}")
                return None
        except Exception as e:
            st.warning(f"Error loading ARIMAX predictions: {str(e)}")
            return None
    
    @st.cache_data(ttl=3600)
    def load_events_data(_self):
        """Load events data for game comparison graphs"""
        try:
            if _self.config.EURO_2024_COMPLETE.exists():
                df = pd.read_csv(_self.config.EURO_2024_COMPLETE, low_memory=False)
                return df
            return None
        except Exception as e:
            st.warning(f"Error loading events data: {str(e)}")
            return None
    
    def load_all_data(self):
        """Load all available data"""
        self._data_cache['momentum'] = self.load_momentum_data()
        self._data_cache['arimax'] = self.load_arimax_predictions()
        self._data_cache['events'] = self.load_events_data()
    
    def get_data(self, data_type):
        """Get cached data"""
        return self._data_cache.get(data_type)
    
    def is_data_loaded(self):
        """Check if data is loaded"""
        return len(self._data_cache) > 0
    
    def get_tournament_stats(self):
        """Calculate tournament-level statistics from period-separated data"""
        momentum_df = self.get_data('momentum')
        
        fallback_stats = {
            'total_matches': 51,
            'total_momentum_windows': 0,
            'periods_covered': [1, 2]
        }
        
        if momentum_df is None:
            return fallback_stats
        
        try:
            stats = {
                'total_matches': momentum_df['match_id'].nunique(),
                'total_momentum_windows': len(momentum_df),
                'periods_covered': sorted(momentum_df['period'].unique().tolist())
            }
            return stats
        except Exception as e:
            st.warning(f"Error calculating stats: {str(e)}")
            return fallback_stats
