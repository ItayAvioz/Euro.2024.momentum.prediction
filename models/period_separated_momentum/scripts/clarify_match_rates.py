import pandas as pd
import numpy as np

# Load data
orig = pd.read_csv('models/preprocessing/data/targets/momentum_targets_streamlined.csv')
orig['minute'] = orig['minute_range'].apply(lambda x: int(x.split('-')[0]))

new = pd.read_csv('models/period_separated_momentum/outputs/momentum_by_period.csv')
p1 = new[(new['period'] == 1) & (new['minute'] < 45)]
p2 = new[(new['period'] == 2) & (new['minute'] >= 45)]
new_combined = pd.concat([p1, p2])

# Merge ALL data
merged = pd.merge(
    orig[['match_id', 'minute', 'team_home_momentum', 'team_away_momentum', 
          'team_home_momentum_change', 'team_away_momentum_change']],
    new_combined[['match_id', 'minute', 'team_home_momentum', 'team_away_momentum',
                   'team_home_momentum_change', 'team_away_momentum_change']],
    on=['match_id', 'minute'],
    suffixes=('_orig', '_new')
)

print("="*60)
print("CLARIFYING MATCH RATES")
print("="*60)

# 1. MOMENTUM values
merged['mom_home_diff'] = abs(merged['team_home_momentum_orig'] - merged['team_home_momentum_new'])
merged['mom_away_diff'] = abs(merged['team_away_momentum_orig'] - merged['team_away_momentum_new'])
merged['mom_max_diff'] = merged[['mom_home_diff', 'mom_away_diff']].max(axis=1)

mom_same = (merged['mom_max_diff'] < 0.001).sum()
print(f"\n1. MOMENTUM VALUES (all data):")
print(f"   Total: {len(merged)}")
print(f"   Identical: {mom_same} ({100*mom_same/len(merged):.1f}%)")

# 2. MOMENTUM_CHANGE values
merged_valid = merged.dropna(subset=['team_home_momentum_change_orig', 'team_home_momentum_change_new'])
merged_valid['change_home_diff'] = abs(merged_valid['team_home_momentum_change_orig'] - merged_valid['team_home_momentum_change_new'])
merged_valid['change_away_diff'] = abs(merged_valid['team_away_momentum_change_orig'] - merged_valid['team_away_momentum_change_new'])
merged_valid['change_max_diff'] = merged_valid[['change_home_diff', 'change_away_diff']].max(axis=1)

change_same = (merged_valid['change_max_diff'] < 0.001).sum()
print(f"\n2. MOMENTUM_CHANGE VALUES (all data with valid change):")
print(f"   Total: {len(merged_valid)}")
print(f"   Identical: {change_same} ({100*change_same/len(merged_valid):.1f}%)")

# 3. TRAINING DATA (minutes 0-74)
train = merged[merged['minute'] < 75]
train_valid = train.dropna(subset=['team_home_momentum_change_orig', 'team_home_momentum_change_new'])

train_mom_same = (train['mom_max_diff'] < 0.001).sum()
print(f"\n3. TRAINING DATA MOMENTUM (minutes 0-74):")
print(f"   Total: {len(train)}")
print(f"   Identical: {train_mom_same} ({100*train_mom_same/len(train):.1f}%)")

train_valid['change_max_diff'] = abs(train_valid['team_home_momentum_change_orig'] - train_valid['team_home_momentum_change_new']).combine(
    abs(train_valid['team_away_momentum_change_orig'] - train_valid['team_away_momentum_change_new']), max)
train_change_same = (train_valid['change_max_diff'] < 0.001).sum()
print(f"\n4. TRAINING DATA MOMENTUM_CHANGE (minutes 0-74):")
print(f"   Total: {len(train_valid)}")
print(f"   Identical: {train_change_same} ({100*train_change_same/len(train_valid):.1f}%)")

