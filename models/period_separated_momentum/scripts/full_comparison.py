"""
Full comparison: momentum_change values and model performance metrics
"""
import pandas as pd
import numpy as np

print("="*70)
print("1. MOMENTUM CHANGE COMPARISON (Original vs Period-Separated)")
print("="*70)

# Load data
orig = pd.read_csv('models/preprocessing/data/targets/momentum_targets_streamlined.csv')
new = pd.read_csv('models/period_separated_momentum/outputs/momentum_by_period.csv')

orig['minute'] = orig['minute_range'].apply(lambda x: int(x.split('-')[0]))

# For comparison, use Period 2 for minutes >= 45, Period 1 for minutes < 45
new_p1 = new[(new['period'] == 1) & (new['minute'] < 45)]
new_p2 = new[(new['period'] == 2) & (new['minute'] >= 45)]
new_combined = pd.concat([new_p1, new_p2])

# Merge on match_id and minute
merged = pd.merge(
    orig[['match_id', 'minute', 'minute_range', 'team_home_momentum_change', 'team_away_momentum_change']],
    new_combined[['match_id', 'minute', 'team_home_momentum_change', 'team_away_momentum_change']],
    on=['match_id', 'minute'],
    suffixes=('_orig', '_new')
)

# Calculate differences
merged['home_diff'] = abs(merged['team_home_momentum_change_orig'] - merged['team_home_momentum_change_new'])
merged['away_diff'] = abs(merged['team_away_momentum_change_orig'] - merged['team_away_momentum_change_new'])
merged['max_diff'] = merged[['home_diff', 'away_diff']].max(axis=1)

# Drop NaN
merged = merged.dropna()

print(f"\nTotal compared records: {len(merged)}")

# Count same vs different
exact = len(merged[merged['max_diff'] < 0.001])
close = len(merged[(merged['max_diff'] >= 0.001) & (merged['max_diff'] < 0.1)])
different = len(merged[merged['max_diff'] >= 0.1])

print(f"\nMomentum Change Comparison:")
print(f"  Exact same (<0.001):  {exact:>5} ({100*exact/len(merged):.1f}%)")
print(f"  Close (0.001-0.1):    {close:>5} ({100*close/len(merged):.1f}%)")
print(f"  Different (>=0.1):    {different:>5} ({100*different/len(merged):.1f}%)")

# Which minutes are different?
diff_records = merged[merged['max_diff'] >= 0.1]
print(f"\n📍 MINUTES WITH DIFFERENT MOMENTUM CHANGE (>=0.1):")
diff_minutes = sorted(diff_records['minute'].unique())
print(f"  Minutes: {diff_minutes}")
print(f"  Count of different minutes: {len(diff_minutes)}")

# Distribution by minute range
print(f"\n📊 Distribution of differences by minute bucket:")
merged['minute_bucket'] = pd.cut(merged['minute'], bins=[0, 30, 45, 60, 75, 90, 150], 
                                  labels=['0-30', '31-45', '46-60', '61-75', '76-90', '90+'])
for bucket in ['0-30', '31-45', '46-60', '61-75', '76-90', '90+']:
    bucket_data = merged[merged['minute_bucket'] == bucket]
    if len(bucket_data) > 0:
        diff_count = len(bucket_data[bucket_data['max_diff'] >= 0.1])
        print(f"  {bucket}: {diff_count}/{len(bucket_data)} different ({100*diff_count/len(bucket_data):.1f}%)")

print("\n" + "="*70)
print("2. MODEL PERFORMANCE COMPARISON")
print("="*70)

# Run predictions with new data
print("\n⏳ Generating new predictions...")
import subprocess
result = subprocess.run(['python', 'models/period_separated_momentum/scripts/period_arimax_predictor.py'], 
                       capture_output=True, text=True)

# Load predictions
orig_pred = pd.read_csv('models/modeling/scripts/outputs/predictions/arimax_predictions.csv')
orig_arimax = orig_pred[orig_pred['model_type'] == 'momentum_to_change_arimax'].copy()

new_pred = pd.read_csv('models/period_separated_momentum/outputs/arimax_predictions_by_period.csv')

# Calculate metrics for original
print("\n📊 ORIGINAL MODEL METRICS:")
orig_mse = orig_arimax['mse'].mean()
orig_dir_acc = orig_arimax['directional_accuracy'].mean() * 100
orig_arimax['sign_match'] = (np.sign(orig_arimax['prediction_value']) == np.sign(orig_arimax['actual_value']))
orig_sign_acc = orig_arimax['sign_match'].mean() * 100

# Differential sign (paired analysis) - approximate
print(f"  MSE:                   {orig_mse:.4f}")
print(f"  Directional Accuracy:  {orig_dir_acc:.2f}%")
print(f"  Sign Agreement:        {orig_sign_acc:.2f}%")

# Calculate metrics for new
print("\n📊 NEW MODEL METRICS (Period-Separated):")
new_mse = new_pred['mse'].mean()
new_dir_acc = new_pred['directional_accuracy'].mean() * 100
new_pred['sign_match'] = (np.sign(new_pred['prediction_value']) == np.sign(new_pred['actual_value']))
new_sign_acc = new_pred['sign_match'].mean() * 100

print(f"  MSE:                   {new_mse:.4f}")
print(f"  Directional Accuracy:  {new_dir_acc:.2f}%")
print(f"  Sign Agreement:        {new_sign_acc:.2f}%")

print("\n" + "="*70)
print("3. COMPARISON TABLE")
print("="*70)
print(f"\n{'Metric':<25} {'Original':<15} {'New (Period-Sep)':<15} {'Difference':<15}")
print("-"*70)
print(f"{'MSE':<25} {orig_mse:<15.4f} {new_mse:<15.4f} {new_mse-orig_mse:+.4f}")
print(f"{'Directional Accuracy':<25} {orig_dir_acc:<15.2f}% {new_dir_acc:<15.2f}% {new_dir_acc-orig_dir_acc:+.2f}%")
print(f"{'Sign Agreement':<25} {orig_sign_acc:<15.2f}% {new_sign_acc:<15.2f}% {new_sign_acc-orig_sign_acc:+.2f}%")

# Note about Differential Sign
print(f"\n📝 Note: Differential Sign requires paired team analysis (same calculation method)")
print(f"   Original shows 71.11% - this metric compares Team A vs Team B predictions")

