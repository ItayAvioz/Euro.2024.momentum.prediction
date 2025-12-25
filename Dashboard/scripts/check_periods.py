"""Check periods in the data"""
import pandas as pd

df = pd.read_csv('../models/preprocessing/data/targets/momentum_targets_streamlined.csv')

# Get one game
game = df[df['match_id'] == df['match_id'].iloc[0]].copy()
game['minute'] = game['minute_range'].apply(lambda x: int(x.split('-')[0]))
game = game.sort_values('minute')

print(f"Game: {game['team_home'].iloc[0]} vs {game['team_away'].iloc[0]}")
print(f"\nMinute range: {game['minute'].min()} to {game['minute'].max()}")
print(f"Total windows: {len(game)}")

# Check minutes around halftime
print("\nMinutes around halftime (40-50):")
for m in game[game['minute'].between(40, 50)]['minute'].unique():
    print(f"  Minute {m}")

# Check the events data to find period info
events_df = pd.read_csv('../Data/euro_2024_complete_dataset.csv', low_memory=False)
match_id = game['match_id'].iloc[0]
match_events = events_df[events_df['match_id'] == match_id]

print(f"\nPeriod column exists: {'period' in match_events.columns}")
if 'period' in match_events.columns:
    print(f"Unique periods: {match_events['period'].unique()}")
    
    # Find minute ranges per period
    for period in sorted(match_events['period'].dropna().unique()):
        period_events = match_events[match_events['period'] == period]
        print(f"\nPeriod {int(period)}:")
        print(f"  Minute range: {period_events['minute'].min()} to {period_events['minute'].max()}")

