import pandas as pd
import numpy as np

# Load original ARIMAX predictions (filtered)
orig = pd.read_csv('models/modeling/scripts/outputs/predictions/arimax_predictions.csv')
orig = orig[orig['model_type'] == 'momentum_to_change_arimax'].copy()
orig = orig.rename(columns={'game_id': 'match_id'})

# Load new predictions
new = pd.read_csv('models/period_separated_momentum/outputs/arimax_predictions_by_period.csv')

print(f"Original ARIMAX predictions: {len(orig)}")
print(f"New predictions: {len(new)}")

# Merge
merged = pd.merge(
    orig[['match_id', 'team', 'minute_start', 'prediction_value', 'actual_value']],
    new[['match_id', 'team', 'minute_start', 'prediction_value', 'actual_value']],
    on=['match_id', 'team', 'minute_start'],
    suffixes=('_orig', '_new')
)

print(f"Matched: {len(merged)}")

# Prediction comparison
merged['pred_diff'] = abs(merged['prediction_value_orig'] - merged['prediction_value_new'])

exact = (merged['pred_diff'] < 0.001).sum()
print(f"\nPredictions identical (<0.001): {exact} ({100*exact/len(merged):.1f}%)")

# Actual values comparison  
merged['actual_diff'] = abs(merged['actual_value_orig'] - merged['actual_value_new'])
exact_actual = (merged['actual_diff'] < 0.001).sum()
print(f"Actual values identical (<0.001): {exact_actual} ({100*exact_actual/len(merged):.1f}%)")

# The issue: training data (min 0-74) has differences in overlap zone (40-50)
# This affects ALL predictions even though test data (75-89) might be same
print("\n" + "="*50)
print("Training data affects ALL predictions!")
print("Differences in minutes 40-50 propagate to predictions.")
print("="*50)

