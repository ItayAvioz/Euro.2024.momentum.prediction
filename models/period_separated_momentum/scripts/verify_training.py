import pandas as pd
import numpy as np

# Load original data
orig = pd.read_csv('models/preprocessing/data/targets/momentum_targets_streamlined.csv')
orig['minute'] = orig['minute_range'].apply(lambda x: int(x.split('-')[0]))

# Load new data and build combined (same as predictor does)
new = pd.read_csv('models/period_separated_momentum/outputs/momentum_by_period.csv')
p1 = new[(new['period'] == 1) & (new['minute'] < 45)]
p2 = new[(new['period'] == 2) & (new['minute'] >= 45)]
new_combined = pd.concat([p1, p2]).sort_values(['match_id', 'minute'])

# Check one game
match_id = 3930158
print(f"Checking Germany vs Scotland (match {match_id})")
print("="*60)

# Training data (minutes 0-74)
orig_train = orig[(orig['match_id'] == match_id) & (orig['minute'] < 75)]
new_train = new_combined[(new_combined['match_id'] == match_id) & (new_combined['minute'] < 75)]

print(f"\nTraining records: orig={len(orig_train)}, new={len(new_train)}")

# Compare momentum_change values
merged = pd.merge(
    orig_train[['minute', 'team_home_momentum_change']],
    new_train[['minute', 'team_home_momentum_change']],
    on='minute',
    suffixes=('_orig', '_new')
)

merged = merged.dropna()
merged['diff'] = abs(merged['team_home_momentum_change_orig'] - merged['team_home_momentum_change_new'])

same = (merged['diff'] < 0.001).sum()
print(f"Training momentum_change identical: {same}/{len(merged)} ({100*same/len(merged):.1f}%)")

# Show differences
diff_rows = merged[merged['diff'] >= 0.001]
if len(diff_rows) > 0:
    print(f"\nDifferent training values:")
    for _, row in diff_rows.iterrows():
        print(f"  Min {int(row['minute'])}: orig={row['team_home_momentum_change_orig']:.3f}, new={row['team_home_momentum_change_new']:.3f}")

