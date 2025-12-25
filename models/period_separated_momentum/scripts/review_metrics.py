"""
Review all key metrics for period-separated ARIMAX model
"""

import pandas as pd
import numpy as np

# Load period-separated predictions
pred_path = '../outputs/arimax_predictions_by_period.csv'
df = pd.read_csv(pred_path)

print('='*70)
print('PERIOD-SEPARATED ARIMAX METRICS REVIEW')
print('='*70)

print(f'\nTotal predictions: {len(df)}')
print(f'Games: {df["match_id"].nunique()}')

# Filter out NaN values
df_clean = df.dropna(subset=['prediction_value', 'actual_value'])
print(f'Clean predictions (no NaN): {len(df_clean)}')

pred = df_clean['prediction_value'].values
actual = df_clean['actual_value'].values

# 1. SIGN AGREEMENT
pred_sign = np.sign(pred)
actual_sign = np.sign(actual)
sign_agreement = (pred_sign == actual_sign).mean()

pred_pos = (pred_sign > 0).sum()
pred_neg = (pred_sign < 0).sum()
actual_pos = (actual_sign > 0).sum()
actual_neg = (actual_sign < 0).sum()

pp = ((pred_sign > 0) & (actual_sign > 0)).sum()
nn = ((pred_sign < 0) & (actual_sign < 0)).sum()
pn = ((pred_sign > 0) & (actual_sign < 0)).sum()
np_ = ((pred_sign < 0) & (actual_sign > 0)).sum()

print('\n' + '='*70)
print('1. SIGN AGREEMENT ACCURACY')
print('='*70)
print(f'\nOverall Sign Agreement: {sign_agreement*100:.2f}%')
print(f'Total: {len(df_clean)}')
print(f'Correct (PP + NN): {pp + nn} ({(pp+nn)/len(df_clean)*100:.2f}%)')
print(f'  - Positive->Positive (PP): {pp} ({pp/len(df_clean)*100:.2f}%)')
print(f'  - Negative->Negative (NN): {nn} ({nn/len(df_clean)*100:.2f}%)')
print(f'Wrong (PN + NP): {pn + np_} ({(pn+np_)/len(df_clean)*100:.2f}%)')
print(f'  - Positive->Negative (PN): {pn} ({pn/len(df_clean)*100:.2f}%)')
print(f'  - Negative->Positive (NP): {np_} ({np_/len(df_clean)*100:.2f}%)')

print(f'\nPrediction Distribution:')
print(f'  Positive: {pred_pos} ({pred_pos/len(df_clean)*100:.1f}%)')
print(f'  Negative: {pred_neg} ({pred_neg/len(df_clean)*100:.1f}%)')

print(f'\nActual Distribution:')
print(f'  Positive: {actual_pos} ({actual_pos/len(df_clean)*100:.1f}%)')
print(f'  Negative: {actual_neg} ({actual_neg/len(df_clean)*100:.1f}%)')

# 2. DIRECTIONAL ACCURACY
print('\n' + '='*70)
print('2. DIRECTIONAL ACCURACY')
print('='*70)

if len(pred) > 1:
    pred_dirs = np.sign(np.diff(pred))
    actual_dirs = np.sign(np.diff(actual))
    directional_acc = (pred_dirs == actual_dirs).mean()
    print(f'\nDirectional Accuracy: {directional_acc*100:.2f}%')
    print(f'(Measures if consecutive predictions move same direction as actual)')

# 3. DIFFERENTIAL SIGN ACCURACY
print('\n' + '='*70)
print('3. DIFFERENTIAL SIGN ACCURACY')
print('='*70)

# Get home and away predictions per window
home_preds = df_clean[df_clean['is_home'] == True][['match_id', 'minute_start', 'prediction_value', 'actual_value']].copy()
away_preds = df_clean[df_clean['is_home'] == False][['match_id', 'minute_start', 'prediction_value', 'actual_value']].copy()

home_preds.columns = ['match_id', 'minute_start', 'pred_home', 'actual_home']
away_preds.columns = ['match_id', 'minute_start', 'pred_away', 'actual_away']

merged = pd.merge(home_preds, away_preds, on=['match_id', 'minute_start'])
merged = merged.dropna()

# Calculate differentials
merged['pred_diff'] = merged['pred_home'] - merged['pred_away']
merged['actual_diff'] = merged['actual_home'] - merged['actual_away']

# Filter non-zero
non_zero = merged[(merged['pred_diff'] != 0) & (merged['actual_diff'] != 0)]

pred_diff_sign = np.sign(non_zero['pred_diff'].values)
actual_diff_sign = np.sign(non_zero['actual_diff'].values)

diff_accuracy = (pred_diff_sign == actual_diff_sign).mean()

diff_pp = int(((pred_diff_sign > 0) & (actual_diff_sign > 0)).sum())
diff_nn = int(((pred_diff_sign < 0) & (actual_diff_sign < 0)).sum())
diff_pn = int(((pred_diff_sign > 0) & (actual_diff_sign < 0)).sum())
diff_np = int(((pred_diff_sign < 0) & (actual_diff_sign > 0)).sum())

print(f'\nDifferential Sign Accuracy: {diff_accuracy*100:.2f}%')
print(f'Total windows (paired): {len(non_zero)}')
print(f'Correct (PP + NN): {diff_pp + diff_nn} ({(diff_pp+diff_nn)/len(non_zero)*100:.2f}%)')
print(f'  - Positive->Positive (PP): {diff_pp} ({diff_pp/len(non_zero)*100:.2f}%)')
print(f'  - Negative->Negative (NN): {diff_nn} ({diff_nn/len(non_zero)*100:.2f}%)')
print(f'Wrong (PN + NP): {diff_pn + diff_np} ({(diff_pn+diff_np)/len(non_zero)*100:.2f}%)')
print(f'  - Positive->Negative (PN): {diff_pn} ({diff_pn/len(non_zero)*100:.2f}%)')
print(f'  - Negative->Positive (NP): {diff_np} ({diff_np/len(non_zero)*100:.2f}%)')

# Conditional accuracy
actual_pos_count = diff_pp + diff_np
actual_neg_count = diff_nn + diff_pn
acc_when_pos = diff_pp / actual_pos_count * 100 if actual_pos_count > 0 else 0
acc_when_neg = diff_nn / actual_neg_count * 100 if actual_neg_count > 0 else 0

print(f'\nConditional Accuracy:')
print(f'  When Actual Positive (Home ahead): {acc_when_pos:.2f}% ({diff_pp}/{actual_pos_count})')
print(f'  When Actual Negative (Away ahead): {acc_when_neg:.2f}% ({diff_nn}/{actual_neg_count})')

print('\n' + '='*70)
print('SUMMARY - PERIOD SEPARATED DATA')
print('='*70)
print(f'\n1. Directional Accuracy:    {directional_acc*100:.2f}%')
print(f'2. Differential Sign:       {diff_accuracy*100:.2f}%')
print(f'3. Sign Agreement:          {sign_agreement*100:.2f}%')
print('='*70)

