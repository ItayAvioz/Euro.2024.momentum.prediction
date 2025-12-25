import pandas as pd

# Load original momentum data
orig_momentum = pd.read_csv('models/preprocessing/data/targets/momentum_targets_streamlined.csv')

# Load new momentum data  
new_momentum = pd.read_csv('models/period_separated_momentum/outputs/momentum_by_period.csv')

# Check Germany vs Scotland at minute 75
match_id = 3930158

print("="*70)
print("COMPARING MOMENTUM CHANGE VALUES")
print("="*70)

# Original
orig_match = orig_momentum[orig_momentum['match_id'] == match_id].copy()
orig_match['minute'] = orig_match['minute_range'].apply(lambda x: int(x.split('-')[0]))
orig_match = orig_match.sort_values('minute')

print("\nOriginal data (minutes 73-80):")
print(orig_match[orig_match['minute'].between(73, 80)][['minute_range', 'team_home_momentum', 'team_home_momentum_change']].to_string())

# New
new_match = new_momentum[new_momentum['match_id'] == match_id].copy()
new_match = new_match.sort_values('minute')

print("\nNew data Period 2 (minutes 73-80):")
new_p2 = new_match[new_match['period'] == 2]
print(new_p2[new_p2['minute'].between(73, 80)][['minute_range', 'team_home_momentum', 'team_home_momentum_change']].to_string())

# What's the momentum_change formula?
print("\n" + "="*70)
print("MOMENTUM CHANGE FORMULA CHECK")
print("="*70)

# Check if momentum_change is calculated differently
print("\nOriginal minute 75:")
m75_orig = orig_match[orig_match['minute'] == 75].iloc[0]
m78_orig = orig_match[orig_match['minute'] == 78].iloc[0] if 78 in orig_match['minute'].values else None
print(f"  Momentum at 75: {m75_orig['team_home_momentum']:.3f}")
print(f"  Momentum change at 75: {m75_orig['team_home_momentum_change']:.3f}")
if m78_orig is not None:
    print(f"  Momentum at 78: {m78_orig['team_home_momentum']:.3f}")
    print(f"  Expected change (78-75): {m78_orig['team_home_momentum'] - m75_orig['team_home_momentum']:.3f}")

print("\nNew minute 75 (Period 2):")
m75_new = new_p2[new_p2['minute'] == 75].iloc[0] if 75 in new_p2['minute'].values else None
m78_new = new_p2[new_p2['minute'] == 78].iloc[0] if 78 in new_p2['minute'].values else None
if m75_new is not None:
    print(f"  Momentum at 75: {m75_new['team_home_momentum']:.3f}")
    print(f"  Momentum change at 75: {m75_new['team_home_momentum_change']:.3f}")
if m78_new is not None:
    print(f"  Momentum at 78: {m78_new['team_home_momentum']:.3f}")
    if m75_new is not None:
        print(f"  Expected change (78-75): {m78_new['team_home_momentum'] - m75_new['team_home_momentum']:.3f}")

