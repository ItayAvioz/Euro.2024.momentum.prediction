import pandas as pd
import numpy as np

# Load data
orig = pd.read_csv('models/preprocessing/data/targets/momentum_targets_streamlined.csv')
orig['minute'] = orig['minute_range'].apply(lambda x: int(x.split('-')[0]))

new = pd.read_csv('models/period_separated_momentum/outputs/momentum_by_period.csv')
p1 = new[(new['period'] == 1) & (new['minute'] < 45)]
p2 = new[(new['period'] == 2) & (new['minute'] >= 45)]
new_combined = pd.concat([p1, p2])

# Training data (minutes 0-74)
orig_train = orig[orig['minute'] < 75]
new_train = new_combined[new_combined['minute'] < 75]

# Merge ALL training data
merged = pd.merge(
    orig_train[['match_id', 'minute', 'team_home_momentum_change', 'team_away_momentum_change']],
    new_train[['match_id', 'minute', 'team_home_momentum_change', 'team_away_momentum_change']],
    on=['match_id', 'minute'],
    suffixes=('_orig', '_new')
)

merged = merged.dropna()

# Check home momentum_change
merged['home_diff'] = abs(merged['team_home_momentum_change_orig'] - merged['team_home_momentum_change_new'])
merged['away_diff'] = abs(merged['team_away_momentum_change_orig'] - merged['team_away_momentum_change_new'])
merged['max_diff'] = merged[['home_diff', 'away_diff']].max(axis=1)

same = (merged['max_diff'] < 0.001).sum()
print(f"TRAINING DATA (minutes 0-74) across ALL games:")
print(f"Total: {len(merged)}")
print(f"Identical (<0.001): {same} ({100*same/len(merged):.1f}%)")
print(f"Different: {len(merged)-same} ({100*(len(merged)-same)/len(merged):.1f}%)")

# By minute bucket
print(f"\nDifferences by minute:")
for m_start in range(0, 75, 15):
    m_end = min(m_start + 15, 75)
    bucket = merged[(merged['minute'] >= m_start) & (merged['minute'] < m_end)]
    diff_count = (bucket['max_diff'] >= 0.001).sum()
    print(f"  {m_start}-{m_end}: {diff_count}/{len(bucket)} different ({100*diff_count/len(bucket):.1f}%)")

