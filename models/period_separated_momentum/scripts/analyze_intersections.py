import pandas as pd
import numpy as np

# Load data
momentum_df = pd.read_csv('../outputs/momentum_by_period.csv')

print("="*70)
print("ANALYSIS 2: Intersection Points in Momentum Graphs")
print("="*70)

# Analyze per game
all_abs_intersections = []
all_chg_intersections = []

for match_id in momentum_df['match_id'].unique():
    game = momentum_df[momentum_df['match_id'] == match_id].sort_values(['period', 'minute'])
    home_team = game['team_home'].iloc[0]
    away_team = game['team_away'].iloc[0]
    
    # Find intersection points for Absolute Momentum
    prev_home = None
    prev_away = None
    prev_minute = None
    prev_period = None
    
    for _, row in game.iterrows():
        home_mom = row['team_home_momentum']
        away_mom = row['team_away_momentum']
        minute = row['minute']
        period = row['period']
        
        if prev_home is not None:
            # Check if lines crossed (sign change in difference)
            prev_diff = prev_home - prev_away
            curr_diff = home_mom - away_mom
            
            if prev_diff * curr_diff < 0:  # Sign changed = intersection
                # Display minute (add 3 for display)
                display_min = minute + 3
                all_abs_intersections.append({
                    'match_id': match_id,
                    'home_team': home_team,
                    'away_team': away_team,
                    'period': period,
                    'minute': minute,
                    'display_minute': display_min,
                    'home_was_leading': prev_diff > 0,
                    'home_momentum': home_mom,
                    'away_momentum': away_mom
                })
        
        prev_home = home_mom
        prev_away = away_mom
        prev_minute = minute
        prev_period = period
    
    # Find intersection points for Momentum Change
    prev_home_chg = None
    prev_away_chg = None
    
    for _, row in game.iterrows():
        home_chg = row['team_home_momentum_change']
        away_chg = row['team_away_momentum_change']
        minute = row['minute']
        period = row['period']
        
        if pd.notna(home_chg) and pd.notna(away_chg) and prev_home_chg is not None:
            prev_diff = prev_home_chg - prev_away_chg
            curr_diff = home_chg - away_chg
            
            if prev_diff * curr_diff < 0:  # Sign changed
                display_min = minute + 3
                all_chg_intersections.append({
                    'match_id': match_id,
                    'home_team': home_team,
                    'away_team': away_team,
                    'period': period,
                    'minute': minute,
                    'display_minute': display_min,
                    'home_was_gaining': prev_diff > 0,
                    'home_change': home_chg,
                    'away_change': away_chg
                })
        
        if pd.notna(home_chg) and pd.notna(away_chg):
            prev_home_chg = home_chg
            prev_away_chg = away_chg

abs_df = pd.DataFrame(all_abs_intersections)
chg_df = pd.DataFrame(all_chg_intersections)

print(f"\n--- Absolute Momentum Intersections ---")
print(f"Total intersection points: {len(abs_df)}")
print(f"Average per game: {len(abs_df)/51:.1f}")

if len(abs_df) > 0:
    print(f"\nBy period:")
    print(abs_df['period'].value_counts().to_string())
    
    print(f"\nMost common display minutes:")
    print(abs_df['display_minute'].value_counts().head(10).to_string())

print(f"\n--- Momentum Change Intersections ---")
print(f"Total intersection points: {len(chg_df)}")
print(f"Average per game: {len(chg_df)/51:.1f}")

if len(chg_df) > 0:
    print(f"\nBy period:")
    print(chg_df['period'].value_counts().to_string())
    
    print(f"\nMost common display minutes:")
    print(chg_df['display_minute'].value_counts().head(10).to_string())

# Sample for one game
print("\n" + "="*70)
print("Sample: Germany vs Scotland (match_id=3930158)")
print("="*70)

sample_abs = abs_df[abs_df['match_id'] == 3930158]
sample_chg = chg_df[chg_df['match_id'] == 3930158]

print(f"\nAbs Momentum Intersections ({len(sample_abs)} total):")
if len(sample_abs) > 0:
    print(sample_abs[['period', 'display_minute', 'home_was_leading']].to_string(index=False))

print(f"\nMomentum Change Intersections ({len(sample_chg)} total):")
if len(sample_chg) > 0:
    print(sample_chg[['period', 'display_minute', 'home_was_gaining']].head(15).to_string(index=False))

