import pandas as pd
import numpy as np

# Match to check
match_id = 3930158

# ============================================================
# ORIGINAL APPROACH
# ============================================================
print("="*60)
print("ORIGINAL APPROACH (what original predictor sees)")
print("="*60)

orig = pd.read_csv('models/preprocessing/data/targets/momentum_targets_streamlined.csv')
orig['minute'] = orig['minute_range'].apply(lambda x: int(x.split('-')[0]))

orig_match = orig[orig['match_id'] == match_id].sort_values('minute')
orig_train = orig_match[orig_match['minute'] < 75]

print(f"Training records: {len(orig_train)}")
print(f"Minutes: {sorted(orig_train['minute'].unique())[:10]}...{sorted(orig_train['minute'].unique())[-5:]}")
print(f"\nOverlap zone (min 45-48):")
overlap = orig_train[(orig_train['minute'] >= 45) & (orig_train['minute'] <= 48)]
for _, row in overlap.iterrows():
    print(f"  Min {row['minute']}: home_change={row['team_home_momentum_change']:.3f}")

# ============================================================
# NEW APPROACH  
# ============================================================
print("\n" + "="*60)
print("NEW APPROACH (what new predictor sees)")
print("="*60)

new = pd.read_csv('models/period_separated_momentum/outputs/momentum_by_period.csv')
match_data = new[new['match_id'] == match_id].copy()

# Combine periods WITHOUT duplicates (as in predictor)
p1_data = match_data[(match_data['period'] == 1) & (match_data['minute'] < 45)]
p2_data = match_data[(match_data['period'] == 2) & (match_data['minute'] >= 45)]
combined = pd.concat([p1_data, p2_data]).sort_values('minute').reset_index(drop=True)

new_train = combined[combined['minute'] < 75]

print(f"Training records: {len(new_train)}")
print(f"Minutes: {sorted(new_train['minute'].unique())[:10]}...{sorted(new_train['minute'].unique())[-5:]}")
print(f"\nOverlap zone (min 45-48):")
overlap = new_train[(new_train['minute'] >= 45) & (new_train['minute'] <= 48)]
for _, row in overlap.iterrows():
    print(f"  Min {row['minute']}: home_change={row['team_home_momentum_change']:.3f}")

# ============================================================
# KEY DIFFERENCE
# ============================================================
print("\n" + "="*60)
print("KEY DIFFERENCE")
print("="*60)

# Merge and compare training data
orig_train_sub = orig_train[['minute', 'team_home_momentum_change']].copy()
orig_train_sub.columns = ['minute', 'orig_change']
new_train_sub = new_train[['minute', 'team_home_momentum_change']].copy()
new_train_sub.columns = ['minute', 'new_change']

merged = pd.merge(orig_train_sub, new_train_sub, on='minute', how='outer')
merged['diff'] = abs(merged['orig_change'] - merged['new_change'])

diff_count = (merged['diff'] > 0.001).sum()
print(f"\nDifferent training values: {diff_count}/{len(merged)} ({100*diff_count/len(merged):.1f}%)")
print(f"\nWhere differences occur (by minute):")
for m in sorted(merged[merged['diff'] > 0.001]['minute'].unique()):
    row = merged[merged['minute'] == m].iloc[0]
    print(f"  Min {m}: orig={row['orig_change']:.3f}, new={row['new_change']:.3f}")

