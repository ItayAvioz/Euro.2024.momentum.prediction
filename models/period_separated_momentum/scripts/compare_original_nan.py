"""
Compare NaN and count differences: Original vs Period-Separated
"""

import pandas as pd
import numpy as np

print('='*70)
print('COMPARISON: ORIGINAL vs PERIOD-SEPARATED')
print('='*70)

# Load original predictions
orig_df = pd.read_csv('../../../models/modeling/scripts/outputs/predictions/arimax_predictions.csv')
orig_df = orig_df[orig_df['model_type'] == 'momentum_to_change_arimax']

# Load period-separated predictions
new_df = pd.read_csv('../outputs/arimax_predictions_by_period.csv')

print('\n--- ORIGINAL DATA ---')
print(f'Total rows: {len(orig_df)}')
print(f'NaN in prediction_value: {orig_df["prediction_value"].isna().sum()}')
print(f'NaN in actual_value: {orig_df["actual_value"].isna().sum()}')

orig_clean = orig_df.dropna(subset=['prediction_value', 'actual_value'])
print(f'Clean rows: {len(orig_clean)}')

# Check minutes
print(f'Minute range: {orig_df["minute_start"].min()} - {orig_df["minute_start"].max()}')

# Check for zeros
orig_pred_sign = np.sign(orig_clean['prediction_value'].values)
orig_actual_sign = np.sign(orig_clean['actual_value'].values)
print(f'Zero actuals: {(orig_actual_sign == 0).sum()}')

print('\n--- PERIOD-SEPARATED DATA ---')
print(f'Total rows: {len(new_df)}')
print(f'NaN in prediction_value: {new_df["prediction_value"].isna().sum()}')
print(f'NaN in actual_value: {new_df["actual_value"].isna().sum()}')

new_clean = new_df.dropna(subset=['prediction_value', 'actual_value'])
print(f'Clean rows: {len(new_clean)}')

# Check minutes
print(f'Minute range: {new_df["minute_start"].min()} - {new_df["minute_start"].max()}')

# Check for zeros
new_pred_sign = np.sign(new_clean['prediction_value'].values)
new_actual_sign = np.sign(new_clean['actual_value'].values)
print(f'Zero actuals: {(new_actual_sign == 0).sum()}')

# Where do NaN occur in original?
orig_nan = orig_df[orig_df['actual_value'].isna()]
if len(orig_nan) > 0:
    print(f'\nOriginal NaN at minutes: {sorted(orig_nan["minute_start"].unique())}')
else:
    print('\nOriginal has NO NaN in actual_value!')

# Where do NaN occur in new?
new_nan = new_df[new_df['actual_value'].isna()]
if len(new_nan) > 0:
    print(f'Period-separated NaN at minutes: {sorted(new_nan["minute_start"].unique())}')

print('\n' + '='*70)
print('KEY DIFFERENCE')
print('='*70)

print(f'''
ORIGINAL:
- Predictions: {len(orig_df)} rows
- NaN in actual: {orig_df["actual_value"].isna().sum()}
- Clean for analysis: {len(orig_clean)}

PERIOD-SEPARATED:
- Predictions: {len(new_df)} rows  
- NaN in actual: {new_df["actual_value"].isna().sum()} (at minutes 88-89)
- Clean for analysis: {len(new_clean)}

DIFFERENCE: {len(orig_clean) - len(new_clean)} fewer predictions in period-separated

REASON: 
- Original: minute 88-89 had actual values because it used "next" windows
  that mixed period 1 and period 2 data (incorrect)
- Period-separated: minute 88-89 have NaN because we properly separate
  periods, so there's no "next" window within period 2 (correct!)
''')

