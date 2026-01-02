"""
V3 Helper Functions Wrapper
===========================
Imports V3 functions without triggering dotenv encoding issues.

This module patches the dotenv loading before importing run_final_test_v3.
"""

import os
import sys

# Patch dotenv to avoid encoding issues
try:
    import dotenv
    # Override load_dotenv to do nothing
    original_load_dotenv = dotenv.load_dotenv
    dotenv.load_dotenv = lambda *args, **kwargs: None
except:
    pass

# Now import from run_final_test_v3 - dotenv.load_dotenv won't cause issues
from run_final_test_v3 import (
    get_location_description,
    get_distance_description,
    extract_xg_from_shot_column,
    get_foul_danger_context,
    extract_card_from_row,
    validate_player_team,
    calculate_shot_danger_score,
    analyze_multiple_shots,
    analyze_multiple_corners,
    analyze_multiple_fouls,
    analyze_multiple_substitutions,
    analyze_multiple_offsides,
    get_dominant_team_for_minute,
    check_domination_for_consecutive_generals,
    get_most_active_player,
    detect_all_important_events,
    detect_main_event,
    extract_event_specific_data,
    detect_event_chain,
    analyze_event_sequence,  # V6: Event sequence detection
)

# Restore original if needed
try:
    dotenv.load_dotenv = original_load_dotenv
except:
    pass

print("[OK] V3 helpers loaded successfully")

