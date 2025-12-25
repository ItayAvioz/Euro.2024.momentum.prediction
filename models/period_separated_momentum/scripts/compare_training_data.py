"""
Compare training data between original and period-separated.
"""
import pandas as pd
import numpy as np

# Load ORIGINAL data
orig_data = pd.read_csv('models/preprocessing/data/targets/momentum_targets_streamlined.csv')
orig_data['minute'] = orig_data['minute_range'].apply(lambda x: int(x.split('-')[0]))

# Load PERIOD-SEPARATED data
new_data = pd.read_csv('models/period_separated_momentum/outputs/momentum_by_period.csv')

match_id = 3930158  # Germany vs Scotland

print("="*60)
print("TRAINING DATA COMPARISON (minutes 0-74)")
print("="*60)

# Original training data
orig_match = orig_data[orig_data['match_id'] == match_id].copy()
orig_match = orig_match.sort_values('minute')
orig_train = orig_match[orig_match['minute'] < 75]

# Period-separated training data (how my predictor builds it)
new_match = new_data[new_data['match_id'] == match_id].copy()
p1_data = new_match[(new_match['period'] == 1) & (new_match['minute'] < 45)]
p2_data = new_match[(new_match['period'] == 2) & (new_match['minute'] >= 45)]
new_combined = pd.concat([p1_data, p2_data]).sort_values('minute').reset_index(drop=True)
new_train = new_combined[new_combined['minute'] < 75]

print(f"\nOriginal training: {len(orig_train)} records")
print(f"New training: {len(new_train)} records")

# Compare row by row
print("\n" + "-"*60)
print("Comparing training data (momentum_change values):")
print("-"*60)

differences = []
for minute in range(75):
    orig_row = orig_train[orig_train['minute'] == minute]
    new_row = new_train[new_train['minute'] == minute]
    
    if len(orig_row) == 0 or len(new_row) == 0:
        continue
    
    orig_change = orig_row['team_home_momentum_change'].values[0]
    new_change = new_row['team_home_momentum_change'].values[0]
    diff = abs(orig_change - new_change)
    
    if diff > 0.001:
        differences.append({
            'minute': minute,
            'orig_change': orig_change,
            'new_change': new_change,
            'diff': diff
        })

print(f"\nDifferent momentum_change values: {len(differences)}")
if differences:
    print("\nDetails:")
    for d in differences[:20]:
        print(f"  Min {d['minute']}: orig={d['orig_change']:.3f}, new={d['new_change']:.3f}, diff={d['diff']:.3f}")

# Also check momentum values
print("\n" + "-"*60)
print("Comparing training data (momentum values):")
print("-"*60)

momentum_diffs = []
for minute in range(75):
    orig_row = orig_train[orig_train['minute'] == minute]
    new_row = new_train[new_train['minute'] == minute]
    
    if len(orig_row) == 0 or len(new_row) == 0:
        continue
    
    orig_mom = orig_row['team_home_momentum'].values[0]
    new_mom = new_row['team_home_momentum'].values[0]
    diff = abs(orig_mom - new_mom)
    
    if diff > 0.001:
        momentum_diffs.append({
            'minute': minute,
            'orig': orig_mom,
            'new': new_mom,
            'diff': diff
        })

print(f"\nDifferent momentum values: {len(momentum_diffs)}")
if momentum_diffs:
    print("\nDetails:")
    for d in momentum_diffs[:20]:
        print(f"  Min {d['minute']}: orig={d['orig']:.3f}, new={d['new']:.3f}, diff={d['diff']:.3f}")

