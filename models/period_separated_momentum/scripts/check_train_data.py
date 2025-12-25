import pandas as pd

# Load both datasets
orig = pd.read_csv('models/preprocessing/data/targets/momentum_targets_streamlined.csv')
new = pd.read_csv('models/period_separated_momentum/outputs/momentum_by_period.csv')

match_id = 3930158  # Germany vs Scotland

print("="*70)
print("TRAINING DATA COMPARISON (minutes 0-74)")
print("="*70)

# Original
orig_match = orig[orig['match_id'] == match_id].copy()
orig_match['minute'] = orig_match['minute_range'].apply(lambda x: int(x.split('-')[0]))
orig_train = orig_match[orig_match['minute'] < 75]
print(f"\nOriginal training records: {len(orig_train)}")
print(f"Minute range: {orig_train['minute'].min()} - {orig_train['minute'].max()}")

# New - need to combine periods
new_match = new[new['match_id'] == match_id].copy()
new_train = new_match[new_match['minute'] < 75]
print(f"\nNew training records (all periods < min 75): {len(new_train)}")
print(f"By period:")
print(new_train.groupby('period').size())

# The issue: new data has DUPLICATE minutes for periods
print("\n" + "="*70)
print("DUPLICATE MINUTE CHECK")
print("="*70)
print(f"\nMinutes 45-50 in new data:")
overlap = new_train[new_train['minute'].between(45, 50)]
print(overlap[['period', 'minute', 'minute_range', 'team_home_momentum']].to_string())

print(f"\nMinutes 45-50 in original data:")
orig_overlap = orig_train[orig_train['minute'].between(45, 50)]
print(orig_overlap[['minute', 'minute_range', 'team_home_momentum']].to_string())

