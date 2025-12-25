import pandas as pd
import numpy as np

# Load predictions
orig = pd.read_csv('models/modeling/scripts/outputs/predictions/arimax_predictions.csv')
orig = orig[orig['model_type'] == 'momentum_to_change_arimax'].copy()
orig = orig.rename(columns={'game_id': 'match_id'})

new = pd.read_csv('models/period_separated_momentum/outputs/arimax_predictions_by_period.csv')

# Merge
merged = pd.merge(
    orig[['match_id', 'team', 'minute_start', 'prediction_value']],
    new[['match_id', 'team', 'minute_start', 'prediction_value']],
    on=['match_id', 'team', 'minute_start'],
    suffixes=('_orig', '_new')
)

print("="*60)
print("PREDICTION SIMILARITY ANALYSIS")
print("="*60)
print(f"Total matched predictions: {len(merged)}")

# 1. Same sign?
merged['same_sign'] = np.sign(merged['prediction_value_orig']) == np.sign(merged['prediction_value_new'])
same_sign_count = merged['same_sign'].sum()
print(f"\n1. SAME SIGN: {same_sign_count}/{len(merged)} ({100*same_sign_count/len(merged):.1f}%)")

# 2. Correlation
corr = merged['prediction_value_orig'].corr(merged['prediction_value_new'])
print(f"\n2. CORRELATION: {corr:.4f}")

# 3. Distribution of differences
merged['diff'] = merged['prediction_value_orig'] - merged['prediction_value_new']
print(f"\n3. DIFFERENCE DISTRIBUTION:")
print(f"   Mean diff: {merged['diff'].mean():.4f}")
print(f"   Std diff:  {merged['diff'].std():.4f}")
print(f"   Min diff:  {merged['diff'].min():.4f}")
print(f"   Max diff:  {merged['diff'].max():.4f}")

# 4. Close predictions
abs_diff = abs(merged['diff'])
print(f"\n4. CLOSE PREDICTIONS:")
print(f"   Within 0.1: {(abs_diff < 0.1).sum()} ({100*(abs_diff < 0.1).sum()/len(merged):.1f}%)")
print(f"   Within 0.2: {(abs_diff < 0.2).sum()} ({100*(abs_diff < 0.2).sum()/len(merged):.1f}%)")
print(f"   Within 0.3: {(abs_diff < 0.3).sum()} ({100*(abs_diff < 0.3).sum()/len(merged):.1f}%)")
print(f"   Within 0.5: {(abs_diff < 0.5).sum()} ({100*(abs_diff < 0.5).sum()/len(merged):.1f}%)")

# 5. Sample comparison
print(f"\n5. SAMPLE PREDICTIONS (first 10):")
print(f"{'Min':<5} {'Orig':<10} {'New':<10} {'Diff':<10} {'Same Sign':<10}")
print("-"*45)
for _, row in merged.head(10).iterrows():
    print(f"{row['minute_start']:<5} {row['prediction_value_orig']:<10.3f} {row['prediction_value_new']:<10.3f} {row['diff']:<10.3f} {row['same_sign']}")

