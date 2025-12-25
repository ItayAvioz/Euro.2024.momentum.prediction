"""
ARIMAX Sign Analysis - Detailed Breakdown
"""
import pandas as pd
import numpy as np

# Load predictions
df = pd.read_csv('outputs/predictions/arimax_predictions.csv')

# Filter for ARIMAX model only
arimax = df[df['model_type'] == 'momentum_to_change_arimax'].copy()

print('=' * 70)
print('ARIMAX MOMENTUM CHANGE SIGN ANALYSIS')
print('=' * 70)
print(f'Total ARIMAX predictions: {len(arimax):,}')
print(f'Games: {arimax["game_id"].nunique()}')
print(f'Teams: {arimax["team"].nunique()}')

# Extract values
pred = arimax['prediction_value'].values
actual = arimax['actual_value'].values

# Calculate signs
pred_sign = np.sign(pred)
actual_sign = np.sign(actual)

print()
print('=' * 70)
print('1. SIGN DISTRIBUTION (Prediction vs Real)')
print('=' * 70)

# Prediction distribution
pred_pos = (pred_sign > 0).sum()
pred_neg = (pred_sign < 0).sum()
pred_zero = (pred_sign == 0).sum()
total = len(pred)

print()
print('PREDICTION Distribution:')
print(f'  Positive (+): {pred_pos:>6} ({pred_pos/total*100:>6.2f}%)')
print(f'  Negative (-): {pred_neg:>6} ({pred_neg/total*100:>6.2f}%)')
print(f'  Zero (0):     {pred_zero:>6} ({pred_zero/total*100:>6.2f}%)')
print(f'  TOTAL:        {total:>6}')

# Actual distribution
actual_pos = (actual_sign > 0).sum()
actual_neg = (actual_sign < 0).sum()
actual_zero = (actual_sign == 0).sum()

print()
print('REAL (Actual) Distribution:')
print(f'  Positive (+): {actual_pos:>6} ({actual_pos/total*100:>6.2f}%)')
print(f'  Negative (-): {actual_neg:>6} ({actual_neg/total*100:>6.2f}%)')
print(f'  Zero (0):     {actual_zero:>6} ({actual_zero/total*100:>6.2f}%)')
print(f'  TOTAL:        {total:>6}')

print()
print('=' * 70)
print('2. SIGN AGREEMENT MATRIX (2x2 Contingency Table)')
print('=' * 70)

# Calculate all combinations
pp = ((pred_sign > 0) & (actual_sign > 0)).sum()
nn = ((pred_sign < 0) & (actual_sign < 0)).sum()
pn = ((pred_sign > 0) & (actual_sign < 0)).sum()
np_ = ((pred_sign < 0) & (actual_sign > 0)).sum()

# Handle zeros
pz = ((pred_sign > 0) & (actual_sign == 0)).sum()
nz = ((pred_sign < 0) & (actual_sign == 0)).sum()
zp = ((pred_sign == 0) & (actual_sign > 0)).sum()
zn = ((pred_sign == 0) & (actual_sign < 0)).sum()
zz = ((pred_sign == 0) & (actual_sign == 0)).sum()

print()
print('                          ACTUAL')
print('                    Positive    Negative    Zero')
print('            +----------------------------------------')
print(f'PREDICTED   Positive | {pp:>6} ({pp/total*100:>5.2f}%) | {pn:>6} ({pn/total*100:>5.2f}%) | {pz:>4}')
print(f'            Negative | {np_:>6} ({np_/total*100:>5.2f}%) | {nn:>6} ({nn/total*100:>5.2f}%) | {nz:>4}')
print(f'            Zero     | {zp:>6}        | {zn:>6}        | {zz:>4}')

print()
print('=' * 70)
print('3. SIGN AGREEMENT ACCURACY')
print('=' * 70)

# Correct predictions (same sign)
correct = pp + nn + zz
wrong = pn + np_ + pz + nz + zp + zn

sign_accuracy = correct / total

print()
print('SIGN AGREEMENT RESULTS:')
print(f'  [OK] Positive-Positive (correct): {pp:>6} ({pp/total*100:>6.2f}%)')
print(f'  [OK] Negative-Negative (correct): {nn:>6} ({nn/total*100:>6.2f}%)')
print(f'  [OK] Zero-Zero (correct):         {zz:>6} ({zz/total*100:>6.2f}%)')
print(f'  -----------------------------------------')
print(f'  [OK] TOTAL CORRECT:               {correct:>6} ({correct/total*100:>6.2f}%)')
print()
print(f'  [X] Positive-Negative (wrong):   {pn:>6} ({pn/total*100:>6.2f}%)')
print(f'  [X] Negative-Positive (wrong):   {np_:>6} ({np_/total*100:>6.2f}%)')
print(f'  [X] Other mismatches:            {pz+nz+zp+zn:>6} ({(pz+nz+zp+zn)/total*100:>6.2f}%)')
print(f'  -----------------------------------------')
print(f'  [X] TOTAL WRONG:                 {wrong:>6} ({wrong/total*100:>6.2f}%)')

print()
print('=' * 70)
print('4. METRIC DEFINITIONS')
print('=' * 70)
print()
print('DIRECTIONAL ACCURACY (81.61%):')
print('  What it measures: Whether CONSECUTIVE predictions move in the')
print('                    same direction as CONSECUTIVE actual values.')
print('  Formula: sign(pred[t+1] - pred[t]) == sign(actual[t+1] - actual[t])')
print('  Question: "Did the model predict if momentum goes UP or DOWN?"')
print()
print('SIGN ACCURACY (calculated above):')
print('  What it measures: Whether each individual prediction has the')
print('                    same SIGN (+/-) as the actual value.')
print('  Formula: sign(prediction) == sign(actual)')
print('  Question: "Did model correctly predict POSITIVE vs NEGATIVE change?"')
print()
print('DIFFERENTIAL SIGN ACCURACY (71.11%):')
print('  What it measures: Whether the model correctly predicts WHICH TEAM')
print('                    will gain more momentum in a time window.')
print('  Formula: sign(Team_X_pred - Team_Y_pred) == sign(Team_X_actual - Team_Y_actual)')
print('  Question: "Which team will gain the momentum advantage?"')

print()
print('=' * 70)
print('SUMMARY')
print('=' * 70)
print()
print(f'Sign Agreement Accuracy:        {sign_accuracy*100:.2f}%')
print(f'Directional Accuracy:           81.61% (trend direction)')
print(f'Differential Sign Accuracy:     71.11% (team comparison)')
print()
print(f'Random Chance Baseline:         50%')
print(f'Improvement over Random:        +{(sign_accuracy-0.5)*100:.2f}% (sign)')

