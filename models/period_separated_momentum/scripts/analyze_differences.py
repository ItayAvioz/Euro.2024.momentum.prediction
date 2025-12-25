#!/usr/bin/env python3
"""
Analyze differences between original and period-separated momentum data.
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Paths
base_path = Path(__file__).parent.parent.parent
original_path = base_path / "preprocessing" / "data" / "targets" / "momentum_targets_streamlined.csv"
new_path = base_path / "period_separated_momentum" / "outputs" / "momentum_by_period.csv"
output_path = base_path / "period_separated_momentum" / "outputs"

# Load data
print("Loading data...")
original_df = pd.read_csv(original_path)
new_df = pd.read_csv(new_path)

# Extract minute
original_df['minute'] = original_df['minute_range'].apply(lambda x: int(x.split('-')[0]))
new_df['minute'] = new_df['minute_range'].apply(lambda x: int(x.split('-')[0]))

print(f"Original: {len(original_df)} records")
print(f"New: {len(new_df)} records")

# Analyze by minute ranges
print("\n" + "="*60)
print("MINUTE DISTRIBUTION ANALYSIS")
print("="*60)

# Original minute distribution
print("\nOriginal data minute ranges:")
print(f"  Min: {original_df['minute'].min()}")
print(f"  Max: {original_df['minute'].max()}")

# New data by period
print("\nNew data by period:")
for period in [1, 2]:
    p_data = new_df[new_df['period'] == period]
    print(f"  Period {period}: min={p_data['minute'].min()}, max={p_data['minute'].max()}, count={len(p_data)}")

# Find overlapping minutes in new data
p1_minutes = set(new_df[new_df['period'] == 1]['minute'].unique())
p2_minutes = set(new_df[new_df['period'] == 2]['minute'].unique())
overlap = p1_minutes.intersection(p2_minutes)
print(f"\nOverlapping minutes: {sorted(overlap)}")
print(f"Number of overlapping minutes: {len(overlap)}")

# Detailed comparison
print("\n" + "="*60)
print("DETAILED COMPARISON BY GAME")
print("="*60)

results = []

for match_id in original_df['match_id'].unique():
    orig_match = original_df[original_df['match_id'] == match_id]
    new_match = new_df[new_df['match_id'] == match_id]
    
    home_team = orig_match['team_home'].iloc[0]
    away_team = orig_match['team_away'].iloc[0]
    
    # Compare each minute_range
    for _, orig_row in orig_match.iterrows():
        minute_range = orig_row['minute_range']
        minute = orig_row['minute']
        
        # Find matching record in new data (period 1 for non-overlap, both for overlap)
        new_rows = new_match[new_match['minute_range'] == minute_range]
        
        if len(new_rows) == 0:
            results.append({
                'match_id': match_id,
                'home_team': home_team,
                'away_team': away_team,
                'minute_range': minute_range,
                'minute': minute,
                'status': 'MISSING_IN_NEW',
                'orig_home_momentum': orig_row['team_home_momentum'],
                'orig_away_momentum': orig_row['team_away_momentum'],
                'new_home_momentum': None,
                'new_away_momentum': None,
                'home_diff': None,
                'away_diff': None,
                'period_in_new': None
            })
        else:
            # Use period 1 if available, otherwise period 2
            if len(new_rows[new_rows['period'] == 1]) > 0:
                new_row = new_rows[new_rows['period'] == 1].iloc[0]
                period_used = 1
            else:
                new_row = new_rows.iloc[0]
                period_used = new_row['period']
            
            home_diff = abs(orig_row['team_home_momentum'] - new_row['team_home_momentum'])
            away_diff = abs(orig_row['team_away_momentum'] - new_row['team_away_momentum'])
            
            if home_diff < 0.001 and away_diff < 0.001:
                status = 'EXACT_MATCH'
            elif home_diff < 0.1 and away_diff < 0.1:
                status = 'CLOSE_MATCH'
            else:
                status = 'DIFFERENT'
            
            results.append({
                'match_id': match_id,
                'home_team': home_team,
                'away_team': away_team,
                'minute_range': minute_range,
                'minute': minute,
                'status': status,
                'orig_home_momentum': round(orig_row['team_home_momentum'], 3),
                'orig_away_momentum': round(orig_row['team_away_momentum'], 3),
                'new_home_momentum': round(new_row['team_home_momentum'], 3),
                'new_away_momentum': round(new_row['team_away_momentum'], 3),
                'home_diff': round(home_diff, 3),
                'away_diff': round(away_diff, 3),
                'period_in_new': period_used
            })

results_df = pd.DataFrame(results)

# Summary by status
print("\nStatus Distribution:")
print(results_df['status'].value_counts())

# Summary by minute range
print("\nStatus by Minute Range:")
results_df['minute_bucket'] = pd.cut(results_df['minute'], bins=[0, 20, 40, 50, 70, 90, 120], 
                                      labels=['0-20', '21-40', '41-50', '51-70', '71-90', '90+'])
status_by_minute = results_df.groupby('minute_bucket')['status'].value_counts().unstack(fill_value=0)
print(status_by_minute)

# Save detailed results
output_file = output_path / "comparison_details.csv"
results_df.to_csv(output_file, index=False)
print(f"\n✅ Detailed comparison saved to {output_file}")

# Summary by game
print("\n" + "="*60)
print("SUMMARY BY GAME")
print("="*60)

game_summary = []
for match_id in results_df['match_id'].unique():
    game_data = results_df[results_df['match_id'] == match_id]
    home = game_data['home_team'].iloc[0]
    away = game_data['away_team'].iloc[0]
    
    total = len(game_data)
    exact = len(game_data[game_data['status'] == 'EXACT_MATCH'])
    close = len(game_data[game_data['status'] == 'CLOSE_MATCH'])
    diff = len(game_data[game_data['status'] == 'DIFFERENT'])
    missing = len(game_data[game_data['status'] == 'MISSING_IN_NEW'])
    
    # Get different minutes
    diff_rows = game_data[game_data['status'] == 'DIFFERENT']
    diff_minutes = diff_rows['minute'].tolist() if len(diff_rows) > 0 else []
    
    game_summary.append({
        'match_id': match_id,
        'home_team': home,
        'away_team': away,
        'total_records': total,
        'exact_match': exact,
        'close_match': close,
        'different': diff,
        'missing': missing,
        'match_rate': round(100 * (exact + close) / total, 1) if total > 0 else 0,
        'different_minutes': str(diff_minutes[:10]) if diff_minutes else ''
    })

game_summary_df = pd.DataFrame(game_summary)

# Save game summary
summary_file = output_path / "game_comparison_summary.csv"
game_summary_df.to_csv(summary_file, index=False)
print(f"✅ Game summary saved to {summary_file}")

# Print summary
print("\nGame Summary (first 10):")
print(game_summary_df[['home_team', 'away_team', 'total_records', 'match_rate', 'different']].head(10).to_string())

# Analyze WHERE differences occur
print("\n" + "="*60)
print("WHERE DO DIFFERENCES OCCUR?")
print("="*60)

diff_data = results_df[results_df['status'] == 'DIFFERENT']
print(f"\nTotal different records: {len(diff_data)}")
print(f"\nMinute distribution of differences:")
print(diff_data['minute'].describe())

print(f"\nDifferences by minute range:")
diff_by_minute = diff_data.groupby('minute_bucket').size()
print(diff_by_minute)

# Check if differences are in overlapping zone
overlap_minutes = list(overlap)
diff_in_overlap = diff_data[diff_data['minute'].isin(overlap_minutes)]
diff_outside_overlap = diff_data[~diff_data['minute'].isin(overlap_minutes)]

print(f"\nDifferences IN overlapping zone (min {min(overlap_minutes)}-{max(overlap_minutes)}): {len(diff_in_overlap)}")
print(f"Differences OUTSIDE overlapping zone: {len(diff_outside_overlap)}")

if len(diff_outside_overlap) > 0:
    print(f"\nMinutes with differences OUTSIDE overlap:")
    print(sorted(diff_outside_overlap['minute'].unique())[:20])

