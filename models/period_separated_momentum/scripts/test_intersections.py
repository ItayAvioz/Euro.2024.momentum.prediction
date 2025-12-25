import pandas as pd
import numpy as np

print("="*70)
print("TESTING INTERSECTION POINTS DETECTION")
print("="*70)

# Load data
momentum_df = pd.read_csv('../outputs/momentum_by_period.csv')
llm_df = pd.read_csv('../../../NLP - Commentator/research/10_llm_commentary/data/llm_commentary/all_matches_V3_20251209_193514.csv')

# Test with Germany vs Scotland
match_id = 3930158
game = momentum_df[momentum_df['match_id'] == match_id].copy()
game = game.sort_values(['period', 'minute'])

print(f"\nGame: Germany vs Scotland")
print(f"Total minutes: {len(game)}")

# Find intersection points for Absolute Momentum
print("\n" + "="*70)
print("ABSOLUTE MOMENTUM INTERSECTIONS")
print("="*70)

abs_intersections = []
for period in game['period'].unique():
    period_data = game[game['period'] == period].sort_values('minute')
    
    for i in range(len(period_data) - 1):
        curr = period_data.iloc[i]
        next_row = period_data.iloc[i + 1]
        
        # Check if lines cross (one team ahead, then other team ahead)
        curr_diff = curr['team_home_momentum'] - curr['team_away_momentum']
        next_diff = next_row['team_home_momentum'] - next_row['team_away_momentum']
        
        # Intersection occurs when signs are different
        if (curr_diff > 0 and next_diff < 0) or (curr_diff < 0 and next_diff > 0):
            # Intersection is between these two minutes
            intersection_minute = next_row['minute']
            display_minute = intersection_minute + 3
            
            abs_intersections.append({
                'period': period,
                'minute': intersection_minute,
                'display_minute': display_minute,
                'home_before': curr['team_home_momentum'],
                'away_before': curr['team_away_momentum'],
                'home_after': next_row['team_home_momentum'],
                'away_after': next_row['team_away_momentum'],
                'who_takes_lead': 'Home' if next_diff > 0 else 'Away'
            })

print(f"\nFound {len(abs_intersections)} intersections:")
print(f"\n{'Period':<8} {'Display Min':<12} {'Who Takes Lead':<15}")
print("-"*40)
for inter in abs_intersections:
    print(f"{inter['period']:<8} {inter['display_minute']:<12} {inter['who_takes_lead']:<15}")

# Get events at intersection minutes
print("\n\nEvents at intersection minutes:")
game_events = llm_df[llm_df['match_id'] == match_id]

for inter in abs_intersections[:5]:  # Show first 5
    # Events in the 3-minute window before intersection
    min_start = inter['minute']
    events = game_events[
        (game_events['period'] == inter['period']) &
        (game_events['minute'].isin([min_start, min_start+1, min_start+2]))
    ]['detected_type'].value_counts()
    
    print(f"\nDisplay Min {inter['display_minute']} (Period {inter['period']}):")
    print(f"  Events: {dict(events.head(3))}")

# Find intersection points for Momentum Change
print("\n" + "="*70)
print("MOMENTUM CHANGE INTERSECTIONS")
print("="*70)

change_intersections = []
for period in game['period'].unique():
    period_data = game[game['period'] == period].sort_values('minute')
    period_data = period_data.dropna(subset=['team_home_momentum_change', 'team_away_momentum_change'])
    
    for i in range(len(period_data) - 1):
        curr = period_data.iloc[i]
        next_row = period_data.iloc[i + 1]
        
        curr_diff = curr['team_home_momentum_change'] - curr['team_away_momentum_change']
        next_diff = next_row['team_home_momentum_change'] - next_row['team_away_momentum_change']
        
        if (curr_diff > 0 and next_diff < 0) or (curr_diff < 0 and next_diff > 0):
            intersection_minute = next_row['minute']
            display_minute = intersection_minute + 3
            
            change_intersections.append({
                'period': period,
                'minute': intersection_minute,
                'display_minute': display_minute,
                'who_takes_lead': 'Home' if next_diff > 0 else 'Away'
            })

print(f"\nFound {len(change_intersections)} change intersections")
print(f"\n{'Period':<8} {'Display Min':<12} {'Who Takes Lead':<15}")
print("-"*40)
for inter in change_intersections[:10]:
    print(f"{inter['period']:<8} {inter['display_minute']:<12} {inter['who_takes_lead']:<15}")

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print(f"\nAbsolute Momentum: {len(abs_intersections)} crossover points")
print(f"Momentum Change: {len(change_intersections)} crossover points")

