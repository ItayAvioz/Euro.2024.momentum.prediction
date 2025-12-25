import pandas as pd
import numpy as np

# Load and merge
orig = pd.read_csv('models/modeling/scripts/outputs/predictions/arimax_predictions.csv')
orig_arimax = orig[orig['model_type'] == 'momentum_to_change_arimax'].copy()
orig_arimax = orig_arimax.rename(columns={'game_id': 'match_id'})

new = pd.read_csv('models/period_separated_momentum/outputs/arimax_predictions_by_period.csv')

merged = pd.merge(
    orig_arimax[['match_id', 'team', 'minute_start', 'prediction_value', 'actual_value']],
    new[['match_id', 'team', 'minute_start', 'prediction_value', 'actual_value']],
    on=['match_id', 'team', 'minute_start'],
    suffixes=('_orig', '_new')
)

merged['pred_diff'] = abs(merged['prediction_value_orig'] - merged['prediction_value_new'])

print("="*60)
print("PREDICTION DIFFERENCE DISTRIBUTION")
print("="*60)

# Distribution of differences
bins = [0, 0.001, 0.01, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 100]
labels = ['<0.001', '0.001-0.01', '0.01-0.05', '0.05-0.1', '0.1-0.2', '0.2-0.5', '0.5-1.0', '1.0-2.0', '>2.0']
merged['diff_bucket'] = pd.cut(merged['pred_diff'], bins=bins, labels=labels)

print("\nPrediction difference distribution:")
print(merged['diff_bucket'].value_counts().sort_index())

# Statistics
print(f"\nStatistics:")
print(f"  Mean difference: {merged['pred_diff'].mean():.4f}")
print(f"  Median difference: {merged['pred_diff'].median():.4f}")
print(f"  Max difference: {merged['pred_diff'].max():.4f}")
print(f"  Std: {merged['pred_diff'].std():.4f}")

# What % are within 0.3?
within_03 = len(merged[merged['pred_diff'] < 0.3])
print(f"\nWithin 0.3: {within_03} ({100*within_03/len(merged):.1f}%)")

# Check correlation
corr = merged['prediction_value_orig'].corr(merged['prediction_value_new'])
print(f"Correlation between predictions: {corr:.4f}")

