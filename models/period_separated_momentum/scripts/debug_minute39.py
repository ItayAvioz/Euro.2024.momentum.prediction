"""
Debug: Why is momentum_change at minute 39 so different?
"""
import pandas as pd

# Load both datasets
orig = pd.read_csv('models/preprocessing/data/targets/momentum_targets_streamlined.csv')
new = pd.read_csv('models/period_separated_momentum/outputs/momentum_by_period.csv')

match_id = 3930158

# Original
orig_match = orig[orig['match_id'] == match_id].copy()
orig_match['minute'] = orig_match['minute_range'].apply(lambda x: int(x.split('-')[0]))
orig_match = orig_match.sort_values('minute')

# New (Period 1 only for minutes < 45)
new_match = new[(new['match_id'] == match_id) & (new['period'] == 1)].copy()
new_match = new_match.sort_values('minute')

print("="*70)
print("DEBUG: Minutes 38-48 comparison")
print("="*70)

print("\nORIGINAL DATA (minutes 38-48):")
print(orig_match[orig_match['minute'].between(38, 48)][
    ['minute', 'minute_range', 'team_home_momentum', 'team_home_momentum_change']
].to_string())

print("\nNEW DATA - Period 1 (minutes 38-48):")
print(new_match[new_match['minute'].between(38, 48)][
    ['minute', 'minute_range', 'team_home_momentum', 'team_home_momentum_change']
].to_string())

# Check momentum_change formula
print("\n" + "="*70)
print("MOMENTUM CHANGE FORMULA CHECK")
print("="*70)

print("\nOriginal minute 39:")
m39 = orig_match[orig_match['minute'] == 39].iloc[0]
m42 = orig_match[orig_match['minute'] == 42].iloc[0]
print(f"  Momentum at 39: {m39['team_home_momentum']:.3f}")
print(f"  Momentum at 42: {m42['team_home_momentum']:.3f}")
print(f"  Stored change at 39: {m39['team_home_momentum_change']:.3f}")
print(f"  Calculated (42-39): {m42['team_home_momentum'] - m39['team_home_momentum']:.3f}")

print("\nNew minute 39 (Period 1):")
n39 = new_match[new_match['minute'] == 39]
n42 = new_match[new_match['minute'] == 42]
if len(n39) > 0 and len(n42) > 0:
    n39 = n39.iloc[0]
    n42 = n42.iloc[0]
    print(f"  Momentum at 39: {n39['team_home_momentum']:.3f}")
    print(f"  Momentum at 42: {n42['team_home_momentum']:.3f}")
    print(f"  Stored change at 39: {n39['team_home_momentum_change']:.3f}")
    print(f"  Calculated (42-39): {n42['team_home_momentum'] - n39['team_home_momentum']:.3f}")
else:
    print("  Missing data at minute 39 or 42 in Period 1")
    print(f"  Available minutes in P1: {new_match['minute'].unique()}")

