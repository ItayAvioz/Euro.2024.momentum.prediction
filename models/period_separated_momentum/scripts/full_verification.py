import pandas as pd
import numpy as np

print("="*70)
print("FULL VERIFICATION")
print("="*70)

# ============================================================
# PART 1: DATA MATCH RATES
# ============================================================
print("\n" + "="*70)
print("PART 1: DATA MATCH RATES")
print("="*70)

orig = pd.read_csv('models/preprocessing/data/targets/momentum_targets_streamlined.csv')
orig['minute'] = orig['minute_range'].apply(lambda x: int(x.split('-')[0]))

new = pd.read_csv('models/period_separated_momentum/outputs/momentum_by_period.csv')
p1 = new[(new['period'] == 1) & (new['minute'] < 45)]
p2 = new[(new['period'] == 2) & (new['minute'] >= 45)]
new_combined = pd.concat([p1, p2])

merged = pd.merge(
    orig[['match_id', 'minute', 'team_home_momentum', 'team_away_momentum', 
          'team_home_momentum_change', 'team_away_momentum_change']],
    new_combined[['match_id', 'minute', 'team_home_momentum', 'team_away_momentum',
                   'team_home_momentum_change', 'team_away_momentum_change']],
    on=['match_id', 'minute'],
    suffixes=('_orig', '_new')
)

# Momentum values
merged['mom_diff'] = (abs(merged['team_home_momentum_orig'] - merged['team_home_momentum_new']) + 
                      abs(merged['team_away_momentum_orig'] - merged['team_away_momentum_new'])) / 2
mom_same = (merged['mom_diff'] < 0.001).sum()
print(f"\n1. Momentum values: {mom_same}/{len(merged)} identical ({100*mom_same/len(merged):.1f}%)")

# Momentum change values
mc = merged.dropna(subset=['team_home_momentum_change_orig', 'team_home_momentum_change_new']).copy()
mc['change_diff'] = (abs(mc['team_home_momentum_change_orig'] - mc['team_home_momentum_change_new']) + 
                     abs(mc['team_away_momentum_change_orig'] - mc['team_away_momentum_change_new'])) / 2
change_same = (mc['change_diff'] < 0.001).sum()
print(f"2. Momentum_change values: {change_same}/{len(mc)} identical ({100*change_same/len(mc):.1f}%)")

# Training data
train = mc[mc['minute'] < 75]
train_same = (train['change_diff'] < 0.001).sum()
print(f"3. Training data (min 0-74): {train_same}/{len(train)} identical ({100*train_same/len(train):.1f}%)")

# ============================================================
# PART 2: MODEL PARAMETERS VERIFICATION
# ============================================================
print("\n" + "="*70)
print("PART 2: MODEL PARAMETERS VERIFICATION")
print("="*70)

orig_pred = pd.read_csv('models/modeling/scripts/outputs/predictions/arimax_predictions.csv')
orig_pred = orig_pred[orig_pred['model_type'] == 'momentum_to_change_arimax'].copy()

new_pred = pd.read_csv('models/period_separated_momentum/outputs/arimax_predictions_by_period.csv')

print("\nOriginal predictions columns:", list(orig_pred.columns))
print("New predictions columns:", list(new_pred.columns))

# Check if model parameters exist
if 'arima_order' in orig_pred.columns:
    print(f"\nOriginal ARIMA order: {orig_pred['arima_order'].unique()}")
if 'arima_order' in new_pred.columns:
    print(f"New ARIMA order: {new_pred['arima_order'].unique()}")

if 'has_exog' in orig_pred.columns:
    print(f"\nOriginal has_exog: {orig_pred['has_exog'].unique()}")
if 'has_exog' in new_pred.columns:
    print(f"New has_exog: {new_pred['has_exog'].unique()}")

# ============================================================
# PART 3: PREDICTION PROCESS VERIFICATION
# ============================================================
print("\n" + "="*70)
print("PART 3: PREDICTION PROCESS VERIFICATION")
print("="*70)

# Check minute ranges
print(f"\nOriginal predictions minute range: {orig_pred['minute_start'].min()} - {orig_pred['minute_start'].max()}")
print(f"New predictions minute range: {new_pred['minute_start'].min()} - {new_pred['minute_start'].max()}")

# Check number of predictions per game
orig_pred_count = orig_pred.groupby('game_id').size().mean()
new_pred_count = new_pred.groupby('match_id').size().mean()
print(f"\nAvg predictions per game - Original: {orig_pred_count:.1f}, New: {new_pred_count:.1f}")

# ============================================================
# PART 4: PREDICTION COMPARISON
# ============================================================
print("\n" + "="*70)
print("PART 4: PREDICTION COMPARISON")
print("="*70)

orig_pred = orig_pred.rename(columns={'game_id': 'match_id'})
pred_merged = pd.merge(
    orig_pred[['match_id', 'team', 'minute_start', 'prediction_value', 'actual_value']],
    new_pred[['match_id', 'team', 'minute_start', 'prediction_value', 'actual_value']],
    on=['match_id', 'team', 'minute_start'],
    suffixes=('_orig', '_new')
)

print(f"\nMatched predictions: {len(pred_merged)}")

# Actual values comparison
actual_diff = abs(pred_merged['actual_value_orig'] - pred_merged['actual_value_new'])
actual_same = (actual_diff < 0.001).sum()
print(f"\nActual values identical: {actual_same}/{len(pred_merged)} ({100*actual_same/len(pred_merged):.1f}%)")

# Prediction comparison
pred_merged['same_sign'] = np.sign(pred_merged['prediction_value_orig']) == np.sign(pred_merged['prediction_value_new'])
same_sign = pred_merged['same_sign'].sum()
print(f"Same sign predictions: {same_sign}/{len(pred_merged)} ({100*same_sign/len(pred_merged):.1f}%)")

pred_diff = abs(pred_merged['prediction_value_orig'] - pred_merged['prediction_value_new'])
print(f"Within 0.3: {(pred_diff < 0.3).sum()}/{len(pred_merged)} ({100*(pred_diff < 0.3).sum()/len(pred_merged):.1f}%)")
print(f"Within 0.5: {(pred_diff < 0.5).sum()}/{len(pred_merged)} ({100*(pred_diff < 0.5).sum()/len(pred_merged):.1f}%)")

corr = pred_merged['prediction_value_orig'].corr(pred_merged['prediction_value_new'])
print(f"Correlation: {corr:.3f}")

