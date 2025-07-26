#!/usr/bin/env python3
"""
Check data coverage - how many matches vs how many have events
"""

import pandas as pd

def check_data_coverage():
    """Check how many matches have events data"""
    print("🔍 Euro 2024 Data Coverage Check")
    print("=" * 50)
    
    # Load matches and events
    matches = pd.read_csv('euro_2024_data/matches.csv')
    events = pd.read_csv('euro_2024_data/events.csv')
    
    print(f"📊 Total matches in tournament: {len(matches)}")
    print(f"📊 Matches with events downloaded: {events['match_id'].nunique()}")
    print(f"📊 Coverage: {events['match_id'].nunique()}/{len(matches)} matches")
    print()
    
    # Show which matches have events
    matches_with_events = events['match_id'].unique()
    print("🏟️ Matches with events data:")
    
    for i, match_id in enumerate(matches_with_events, 1):
        match_info = matches[matches['match_id'] == match_id].iloc[0]
        print(f"   {i}. {match_info['home_team_name']} vs {match_info['away_team_name']} | {match_info['stage']}")
    
    print()
    
    # Show tournament structure
    print("🏆 Full Tournament Structure:")
    stage_counts = matches['stage'].value_counts()
    for stage, count in stage_counts.items():
        print(f"   {stage}: {count} matches")
    
    print()
    print("❓ Why only 5 matches?")
    print("   The download script was set to max_matches=5 for demonstration")
    print("   We can download events for ALL 51 matches if you want!")
    print()
    print("🚀 To get all tournament data:")
    print("   - Modify the download script to download all matches")
    print("   - This will give you the complete Euro 2024 dataset")

if __name__ == "__main__":
    check_data_coverage() 