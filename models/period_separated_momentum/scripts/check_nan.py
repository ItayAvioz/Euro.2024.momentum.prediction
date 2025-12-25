"""
Investigate NaN values and count discrepancies
"""

import pandas as pd
import numpy as np

df = pd.read_csv('../outputs/arimax_predictions_by_period.csv')

print('='*70)
print('INVESTIGATING NaN VALUES')
print('='*70)

print(f'\nTotal rows: {len(df)}')
print(f'NaN in prediction_value: {df["prediction_value"].isna().sum()}')
print(f'NaN in actual_value: {df["actual_value"].isna().sum()}')

# Look at the NaN rows
nan_rows = df[df['actual_value'].isna()]
print(f'\nRows with NaN actual_value: {len(nan_rows)}')

if len(nan_rows) > 0:
    print('\nSample NaN rows:')
    print(nan_rows[['match_id', 'team', 'minute_start', 'minute_range', 'prediction_value', 'actual_value']].head(10))
    
    print('\nMinutes where NaN occurs:')
    print(nan_rows['minute_start'].value_counts().sort_index())
    
    print('\nGames with NaN:')
    print(f'{nan_rows["match_id"].nunique()} games')

# Check the clean data counts
df_clean = df.dropna(subset=['prediction_value', 'actual_value'])
print(f'\n\nClean rows (no NaN): {len(df_clean)}')

pred_sign = np.sign(df_clean['prediction_value'].values)
actual_sign = np.sign(df_clean['actual_value'].values)

pp = int(((pred_sign > 0) & (actual_sign > 0)).sum())
nn = int(((pred_sign < 0) & (actual_sign < 0)).sum())
pn = int(((pred_sign > 0) & (actual_sign < 0)).sum())
np_ = int(((pred_sign < 0) & (actual_sign > 0)).sum())

total = pp + nn + pn + np_
print(f'\nSign Agreement counts:')
print(f'PP: {pp}')
print(f'NN: {nn}')
print(f'PN: {pn}')
print(f'NP: {np_}')
print(f'Total: {total}')

# Check for zeros
zero_pred = (pred_sign == 0).sum()
zero_actual = (actual_sign == 0).sum()
print(f'\nZero predictions: {zero_pred}')
print(f'Zero actuals: {zero_actual}')

# Why NaN in actual_value?
print('\n' + '='*70)
print('WHY NaN IN ACTUAL_VALUE?')
print('='*70)

# Check momentum data
mom_df = pd.read_csv('../outputs/momentum_by_period.csv')
print(f'\nMomentum data rows: {len(mom_df)}')
print(f'NaN in team_home_momentum_change: {mom_df["team_home_momentum_change"].isna().sum()}')
print(f'NaN in team_away_momentum_change: {mom_df["team_away_momentum_change"].isna().sum()}')

# Check if these are the last minutes of games (no future to predict)
nan_minutes = nan_rows['minute_start'].unique()
print(f'\nNaN occurs at minutes: {sorted(nan_minutes)}')

# Check one example
print('\nExample NaN case (first one):')
example = nan_rows.iloc[0]
print(f'Match: {example["match_id"]}, Team: {example["team"]}, Minute: {example["minute_start"]}')

# Check momentum for this match
match_mom = mom_df[mom_df['match_id'] == example['match_id']]
print(f'Max minute in momentum data for this match: {match_mom["minute"].max()}')

