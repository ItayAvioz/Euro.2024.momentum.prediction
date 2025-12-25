#!/usr/bin/env python3
"""
Debug: Find exactly why there are differences in non-overlapping minutes.
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Paths
base_path = Path(__file__).parent.parent.parent
original_path = base_path / "preprocessing" / "data" / "targets" / "momentum_targets_streamlined.csv"
new_path = base_path / "period_separated_momentum" / "outputs" / "momentum_by_period.csv"

# Load data
print("Loading data...")
original_df = pd.read_csv(original_path)
new_df = pd.read_csv(new_path)

# Extract minute
original_df['minute'] = original_df['minute_range'].apply(lambda x: int(x.split('-')[0]))

# Define overlapping zones (where differences ARE expected)
# First half: 43-48 (45+3 max stoppage)
# Second half: 88-99 (90+9 max stoppage)
OVERLAP_1H = list(range(43, 52))  # 43-51
OVERLAP_2H = list(range(88, 100))  # 88-99

print(f"\nExpected overlap zones:")
print(f"  First half: minutes {min(OVERLAP_1H)}-{max(OVERLAP_1H)}")
print(f"  Second half: minutes {min(OVERLAP_2H)}-{max(OVERLAP_2H)}")

# Find ALL differences
differences = []

for match_id in original_df['match_id'].unique():
    orig_match = original_df[original_df['match_id'] == match_id]
    new_match = new_df[new_df['match_id'] == match_id]
    
    home_team = orig_match['team_home'].iloc[0]
    away_team = orig_match['team_away'].iloc[0]
    
    for _, orig_row in orig_match.iterrows():
        minute_range = orig_row['minute_range']
        minute = orig_row['minute']
        
        # Get period 1 data for comparison
        new_row = new_match[(new_match['minute_range'] == minute_range) & (new_match['period'] == 1)]
        
        if len(new_row) == 0:
            # Try period 2 if period 1 not found
            new_row = new_match[new_match['minute_range'] == minute_range]
            if len(new_row) == 0:
                differences.append({
                    'match_id': match_id,
                    'home_team': home_team,
                    'away_team': away_team,
                    'minute': minute,
                    'minute_range': minute_range,
                    'issue': 'MISSING',
                    'in_overlap': minute in OVERLAP_1H or minute in OVERLAP_2H
                })
                continue
        
        new_row = new_row.iloc[0]
        
        home_diff = abs(orig_row['team_home_momentum'] - new_row['team_home_momentum'])
        away_diff = abs(orig_row['team_away_momentum'] - new_row['team_away_momentum'])
        
        if home_diff > 0.001 or away_diff > 0.001:
            differences.append({
                'match_id': match_id,
                'home_team': home_team,
                'away_team': away_team,
                'minute': minute,
                'minute_range': minute_range,
                'orig_home': orig_row['team_home_momentum'],
                'new_home': new_row['team_home_momentum'],
                'home_diff': round(home_diff, 4),
                'orig_away': orig_row['team_away_momentum'],
                'new_away': new_row['team_away_momentum'],
                'away_diff': round(away_diff, 4),
                'issue': 'VALUE_DIFF',
                'in_overlap': minute in OVERLAP_1H or minute in OVERLAP_2H
            })

diff_df = pd.DataFrame(differences)

print(f"\n{'='*60}")
print("ANALYSIS OF ALL DIFFERENCES")
print(f"{'='*60}")

if len(diff_df) == 0:
    print("\n✅ NO DIFFERENCES FOUND - Perfect match!")
else:
    print(f"\nTotal differences: {len(diff_df)}")
    
    # Split by overlap zone
    in_overlap = diff_df[diff_df['in_overlap'] == True]
    outside_overlap = diff_df[diff_df['in_overlap'] == False]
    
    print(f"\n📊 Differences IN expected overlap zones: {len(in_overlap)}")
    print(f"📊 Differences OUTSIDE overlap zones: {len(outside_overlap)}")
    
    if len(outside_overlap) > 0:
        print(f"\n⚠️ UNEXPECTED DIFFERENCES (outside overlap):")
        print(f"\nMinutes with unexpected differences:")
        unexpected_minutes = sorted(outside_overlap['minute'].unique())
        print(f"  {unexpected_minutes}")
        
        print(f"\n🔍 Sample of unexpected differences:")
        sample = outside_overlap.head(20)
        for _, row in sample.iterrows():
            print(f"  {row['home_team']} vs {row['away_team']}, min {row['minute']}: "
                  f"home_diff={row.get('home_diff', 'N/A')}, away_diff={row.get('away_diff', 'N/A')}, "
                  f"issue={row['issue']}")
        
        # Check pattern
        print(f"\n📈 Distribution of unexpected differences by minute:")
        minute_counts = outside_overlap['minute'].value_counts().sort_index()
        print(minute_counts.to_string())
        
        # Save for analysis
        outside_overlap.to_csv(base_path / "period_separated_momentum" / "outputs" / "unexpected_differences.csv", index=False)
        print(f"\n✅ Saved unexpected differences to unexpected_differences.csv")

