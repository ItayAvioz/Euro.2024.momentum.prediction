"""
Configuration for GPT Commentary Generation - V3

V3 Settings:
- Model: gpt-4o-mini (fast, cheap, good quality)
- Temperature: 0.7 (balanced creativity)
- Max Tokens: 40 (ESPN style: 5-15 words)
- Seed: 42 (reproducibility)

Author: AI Assistant
Date: December 9, 2025
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# =====================================
# API CONFIGURATION
# =====================================
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Model settings
MODEL_NAME = "gpt-4o-mini"  # Cheapest model, still good quality
TEMPERATURE = 0.7           # Balanced creativity and consistency
MAX_TOKENS = 40             # ESPN style: 5-15 words max
TOP_P = 0.9                 # Nucleus sampling
SEED = 42                   # For reproducibility

# =====================================
# PATHS
# =====================================
BASE_DIR = Path(__file__).parent.parent
SCRIPTS_DIR = BASE_DIR / "scripts"
DATA_DIR = BASE_DIR / "data"
PROMPTS_DIR = BASE_DIR / "prompts"
DOCS_DIR = BASE_DIR / "docs"

# Output directories
LLM_COMMENTARY_DIR = DATA_DIR / "llm_commentary"
COMPARISONS_DIR = DATA_DIR / "comparisons"

# Create directories if they don't exist
LLM_COMMENTARY_DIR.mkdir(parents=True, exist_ok=True)
COMPARISONS_DIR.mkdir(parents=True, exist_ok=True)

# =====================================
# DATA PATHS
# =====================================
# Source data from previous phases
EVENTS_DATA = Path("Data/events_complete.csv")
MATCHES_DATA = Path("Data/matches_complete.csv")

# Rule-based commentary (Phase 7)
RULE_BASED_COMMENTARY_DIR = BASE_DIR.parent / "07_all_games_commentary" / "data"

# Enhanced comparison data (Phase 8)
COMPARISON_DATA_DIR = BASE_DIR.parent / "08_enhanced_comparison" / "data"

# =====================================
# COMMENTARY STYLE SETTINGS
# =====================================
COMMENTARY_STYLE = {
    'formality': 'professional',  # professional, casual, dramatic
    'excitement_level': 7,         # 1-10
    'detail_level': 'standard',    # brief, standard, detailed
    'include_emojis': False,       # True/False
    'include_stats': True,         # Include player/team stats
}

# =====================================
# EVENT IMPORTANCE WEIGHTS
# =====================================
# Higher weight = more exciting/detailed commentary
EVENT_IMPORTANCE = {
    'Goal': 10,
    'Own Goal': 10,
    'Penalty': 9,
    'Red Card': 9,
    'Yellow Card': 5,
    'Shot': 6,
    'Save': 7,
    'Substitution': 4,
    'Corner': 3,
    'Free Kick': 4,
    'Foul Committed': 3,
    'Offside': 3,
    'Pass': 2,
    'Carry': 2,
    'Dribble': 4,
    'Clearance': 2,
    'Interception': 3,
    'Block': 3,
    'General': 2,
}

# =====================================
# RATE LIMITING
# =====================================
REQUESTS_PER_MINUTE = 60  # OpenAI rate limit
DELAY_BETWEEN_REQUESTS = 1.0  # seconds

# =====================================
# V3 SETTINGS
# =====================================
V3_SETTINGS = {
    # Domination detection
    'min_possession_pct': 55,        # Minimum % to be "in control"
    'min_domination_streak': 2,      # Minimum consecutive generals for domination
    
    # Multiple events thresholds
    'min_shots_for_multi': 2,        # Shots in same minute
    'min_corners_for_multi': 2,      # Corners in same minute
    'min_fouls_for_multi': 3,        # Fouls to report as "physical"
    'min_subs_for_double': 2,        # Subs for "double change"
    'min_offsides_for_multi': 2,     # Offsides in same minute
    
    # Shot danger scoring weights
    'xg_weight': 100,                # xG × 100
    'distance_weight': 1,            # 120 - distance
    'outcome_bonuses': {
        'Saved': 30,
        'Post': 25,
        'Blocked': 20,
        'Off T': 10,
        'Wayward': 5
    },
    
    # Most active player threshold
    'min_events_for_active': 5,      # Events to be "most active"
}

# =====================================
# VALIDATION
# =====================================
def validate_config():
    """Validate configuration settings."""
    errors = []
    
    if not OPENAI_API_KEY:
        errors.append("OPENAI_API_KEY not set. Create a .env file with your API key.")
    
    if MODEL_NAME not in ['gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo', 'gpt-4o', 'gpt-4o-mini']:
        errors.append(f"Invalid model: {MODEL_NAME}")
    
    if not 0 <= TEMPERATURE <= 2:
        errors.append(f"Temperature must be 0-2, got: {TEMPERATURE}")
    
    if MAX_TOKENS < 20 or MAX_TOKENS > 2000:
        errors.append(f"Max tokens should be 20-2000, got: {MAX_TOKENS}")
    
    return errors

if __name__ == "__main__":
    # Test configuration
    errors = validate_config()
    if errors:
        print("Configuration errors:")
        for e in errors:
            print(f"  - {e}")
    else:
        print("✅ Configuration valid!")
        print(f"  Model: {MODEL_NAME}")
        print(f"  Temperature: {TEMPERATURE}")
        print(f"  Max Tokens: {MAX_TOKENS}")
        print(f"  API Key: {'Set' if OPENAI_API_KEY else 'Not Set'}")

