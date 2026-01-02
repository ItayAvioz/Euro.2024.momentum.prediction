"""
Momentum Agent Configuration
============================
All configurable thresholds and settings for the momentum agent.

Author: Euro 2024 Momentum Project
Date: December 2024
"""

from pathlib import Path

# =====================================================
# PATHS
# =====================================================

# Base paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
MODELS_DIR = PROJECT_ROOT / "models"
MOMENTUM_DIR = MODELS_DIR / "period_separated_momentum" / "outputs"

# Data files
MOMENTUM_FILE = MOMENTUM_DIR / "momentum_by_period.csv"
PREDICTIONS_FILE = MOMENTUM_DIR / "arimax_predictions_by_period.csv"

# =====================================================
# DOMINANCE THRESHOLDS
# =====================================================

# Momentum differential thresholds
DOMINANCE_THRESHOLDS = {
    'balanced': 0.5,           # diff < 0.5 = balanced
    'slight_advantage': 1.5,   # 0.5 <= diff < 1.5 = slight advantage
    'dominant': 2.5,           # 1.5 <= diff < 2.5 = dominant
    # diff >= 2.5 = complete control
}

# =====================================================
# CHANGE THRESHOLDS
# =====================================================

# Momentum change thresholds
CHANGE_THRESHOLDS = {
    'significant': 0.3,        # Notable change
    'strong': 0.6,             # Strong change
    'swing': 1.0,              # Major swing
}

# =====================================================
# STREAK THRESHOLDS
# =====================================================

# Streak detection thresholds
STREAK_THRESHOLDS = {
    'minimum': 2,              # Minimum for streak detection
    'strong': 3,               # Strong streak
    'dominant': 4,             # Dominant streak
    'small_change': 0.1,       # Minimum change to count in streak
}

# =====================================================
# DIVERGENCE THRESHOLDS
# =====================================================

# Divergence detection (one rising, other falling)
DIVERGENCE_THRESHOLD = 0.4     # Each team must have at least this change

# =====================================================
# PREDICTION SETTINGS (75+ minutes)
# =====================================================

PREDICTION_SETTINGS = {
    'min_minute': 75,          # Start using predictions from this minute
    'surge_threshold': 0.6,    # Predicted change for "surge"
    'maintain_threshold': 0.3, # Predicted change for "maintain pressure"
    'diff_threshold': 0.3,     # Difference to determine expected dominant
}

# =====================================================
# PHRASE GENERATION PRIORITY
# =====================================================

# Priority order for phrase generation
PHRASE_PRIORITY = [
    'divergence',              # Most dramatic - one rising, other falling
    'strong_streak',           # Extended run of positive/negative
    'dominance_trend',         # Based on dominance level and trend
    'prediction',              # Add prediction note if available
]

# Minimum streak length to prioritize in phrase
MIN_STREAK_FOR_PRIORITY = 3

# =====================================================
# OUTPUT SETTINGS
# =====================================================

OUTPUT_SETTINGS = {
    'include_raw_data': True,  # Include raw momentum values in result
    'include_history': True,   # Include historical data for analysis
    'history_lookback': 5,     # How many minutes to look back
}

# =====================================================
# AGENT MODE
# =====================================================

# Agent operating mode
AGENT_MODE = 'rule_based'      # Options: 'rule_based', 'hybrid', 'llm_only'

# LLM settings (if using hybrid mode)
LLM_SETTINGS = {
    'model': 'gpt-4o-mini',
    'temperature': 0.3,        # Lower for more consistent decisions
    'max_tokens': 50,          # Short responses for decisions
}

