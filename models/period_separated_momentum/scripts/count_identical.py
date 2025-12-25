import pandas as pd
import numpy as np

orig = pd.read_csv('models/modeling/scripts/outputs/predictions/arimax_predictions.csv')
orig_arimax = orig[orig['model_type'] == 'momentum_to_change_arimax'].copy()
orig_arimax = orig_arimax.rename(columns={'game_id': 'match_id'})

new = pd.read_csv('models/period_separated_momentum/outputs/arimax_predictions_by_period.csv')

merged = pd.merge(
    orig_arimax[['match_id', 'team', 'minute_start', 'prediction_value']],
    new[['match_id', 'team', 'minute_start', 'prediction_value']],
    on=['match_id', 'team', 'minute_start'],
    suffixes=('_orig', '_new')
)

merged['diff'] = abs(merged['prediction_value_orig'] - merged['prediction_value_new'])

print('MOMENTUM CHANGE PREDICTION COMPARISON')
print('='*50)
print(f'Total matched predictions: {len(merged)}')
print()
print('How many are identical?')
print('-'*50)

thresholds = [0.001, 0.01, 0.05, 0.1, 0.2, 0.3, 0.5]
labels = ['Exact', 'Very close', 'Close', 'Similar', 'Near', 'Acceptable', 'Reasonable']

for thresh, label in zip(thresholds, labels):
    count = len(merged[merged['diff'] < thresh])
    pct = 100 * count / len(merged)
    print(f'  {label} (<{thresh}): {count:>5} ({pct:.1f}%)')

