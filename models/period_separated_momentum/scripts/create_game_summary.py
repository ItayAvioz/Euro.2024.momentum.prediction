#!/usr/bin/env python3
"""
Create game-by-game summary showing momentum differences between original and new data.
"""

import pandas as pd
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

# Create game summary
game_summaries = []

for match_id in original_df['match_id'].unique():
    orig_match = original_df[original_df['match_id'] == match_id]
    new_match = new_df[new_df['match_id'] == match_id]
    
    home_team = orig_match['team_home'].iloc[0]
    away_team = orig_match['team_away'].iloc[0]
    
    # Find differences for each minute
    diff_minutes_home = []
    diff_minutes_away = []
    
    for _, orig_row in orig_match.iterrows():
        minute_range = orig_row['minute_range']
        minute = orig_row['minute']
        
        # Get period 1 data
        new_row = new_match[(new_match['minute_range'] == minute_range) & (new_match['period'] == 1)]
        
        if len(new_row) == 0:
            continue
        
        new_row = new_row.iloc[0]
        
        home_diff = abs(orig_row['team_home_momentum'] - new_row['team_home_momentum'])
        away_diff = abs(orig_row['team_away_momentum'] - new_row['team_away_momentum'])
        
        if home_diff >= 0.1:
            diff_minutes_home.append(minute)
        if away_diff >= 0.1:
            diff_minutes_away.append(minute)
    
    game_summaries.append({
        'match_id': match_id,
        'home_team': home_team,
        'away_team': away_team,
        'total_minutes': len(orig_match),
        'home_diff_count': len(diff_minutes_home),
        'away_diff_count': len(diff_minutes_away),
        'home_diff_minutes': str(diff_minutes_home) if diff_minutes_home else 'None',
        'away_diff_minutes': str(diff_minutes_away) if diff_minutes_away else 'None',
        'home_diff_pct': round(100 * len(diff_minutes_home) / max(1, len(orig_match)), 1),
        'away_diff_pct': round(100 * len(diff_minutes_away) / max(1, len(orig_match)), 1)
    })

# Create DataFrame and save
summary_df = pd.DataFrame(game_summaries)
summary_df = summary_df.sort_values('home_diff_count', ascending=False)

output_file = output_path / "game_momentum_diff_summary.csv"
summary_df.to_csv(output_file, index=False)

print(f"\n✅ Saved to {output_file}")
print(f"\nTotal games: {len(summary_df)}")
print(f"Games with no home differences: {len(summary_df[summary_df['home_diff_count'] == 0])}")
print(f"Games with no away differences: {len(summary_df[summary_df['away_diff_count'] == 0])}")

# Print summary table
print("\n" + "="*80)
print("GAME SUMMARY - Momentum Differences (>0.1)")
print("="*80)
print(summary_df[['home_team', 'away_team', 'total_minutes', 'home_diff_count', 
                  'away_diff_count', 'home_diff_pct', 'away_diff_pct']].to_string())

