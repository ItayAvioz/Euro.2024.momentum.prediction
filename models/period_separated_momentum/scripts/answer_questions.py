import pandas as pd

# Load data
original = pd.read_csv('models/preprocessing/data/targets/momentum_targets_streamlined.csv')
new = pd.read_csv('models/period_separated_momentum/outputs/momentum_by_period.csv')

original['minute'] = original['minute_range'].apply(lambda x: int(x.split('-')[0]))

print("="*70)
print("QUESTION 1: Period 3+4 (Overtime) Match Rate")
print("="*70)

# Filter overtime from original (minutes 90+)
orig_overtime = original[original['minute'] >= 90]
print(f"\nOriginal overtime records: {len(orig_overtime)}")

# Filter overtime from new (periods 3, 4)
new_overtime = new[new['period'].isin([3, 4])]
print(f"New overtime records: {len(new_overtime)}")

# Compare
same = 0
diff = 0
missing = 0

for _, orig_row in orig_overtime.iterrows():
    mr = orig_row['minute_range']
    match_id = orig_row['match_id']
    minute = orig_row['minute']
    
    # Find in new
    n = new[(new['match_id'] == match_id) & (new['minute_range'] == mr)]
    
    if len(n) == 0:
        missing += 1
        continue
    
    n_row = n.iloc[0]
    home_diff = abs(orig_row['team_home_momentum'] - n_row['team_home_momentum'])
    away_diff = abs(orig_row['team_away_momentum'] - n_row['team_away_momentum'])
    
    if home_diff < 0.001 and away_diff < 0.001:
        same += 1
    else:
        diff += 1

print(f"\nOvertime comparison:")
print(f"  Same (exact match): {same}")
print(f"  Different: {diff}")
print(f"  Missing in new: {missing}")

print("\n" + "="*70)
print("QUESTION 2: Where is the 0.1% close match (diff 0.001-0.01)?")
print("="*70)

close_matches = []

for _, orig_row in original.iterrows():
    mr = orig_row['minute_range']
    match_id = orig_row['match_id']
    minute = orig_row['minute']
    
    # Determine period
    if minute < 45:
        period = 1
    elif minute < 90:
        period = 2
    elif minute < 105:
        period = 3
    else:
        period = 4
    
    n = new[(new['match_id'] == match_id) & (new['minute_range'] == mr) & (new['period'] == period)]
    
    if len(n) == 0:
        continue
    
    n_row = n.iloc[0]
    home_diff = abs(orig_row['team_home_momentum'] - n_row['team_home_momentum'])
    away_diff = abs(orig_row['team_away_momentum'] - n_row['team_away_momentum'])
    
    # Close match: 0.001 <= diff < 0.01
    if (0.001 <= home_diff < 0.01) or (0.001 <= away_diff < 0.01):
        if home_diff < 0.01 and away_diff < 0.01:  # Both within close range
            close_matches.append({
                'match_id': match_id,
                'minute_range': mr,
                'minute': minute,
                'home_team': orig_row['team_home'],
                'away_team': orig_row['team_away'],
                'orig_home': orig_row['team_home_momentum'],
                'new_home': n_row['team_home_momentum'],
                'home_diff': round(home_diff, 4),
                'orig_away': orig_row['team_away_momentum'],
                'new_away': n_row['team_away_momentum'],
                'away_diff': round(away_diff, 4)
            })

print(f"\nTotal close matches (0.001-0.01 diff): {len(close_matches)}")
if len(close_matches) > 0:
    print("\nDetails:")
    for cm in close_matches:
        print(f"  {cm['home_team']} vs {cm['away_team']}, {cm['minute_range']}:")
        print(f"    Home: orig={cm['orig_home']}, new={cm['new_home']}, diff={cm['home_diff']}")
        print(f"    Away: orig={cm['orig_away']}, new={cm['new_away']}, diff={cm['away_diff']}")

print("\n" + "="*70)
print("QUESTION 3: Current prediction distribution")
print("="*70)

pred = pd.read_csv('models/period_separated_momentum/outputs/arimax_predictions_by_period.csv')
print("\nCurrent predictions by period:")
print(pred['period'].value_counts().sort_index())
print("\nNote: User wants predictions ONLY for period 2")
print("Training on period 1 (first 75 min), predicting period 2")

