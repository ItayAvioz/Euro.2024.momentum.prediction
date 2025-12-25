import pandas as pd
import numpy as np

# Load original (filter to ARIMAX only)
orig = pd.read_csv('models/modeling/scripts/outputs/predictions/arimax_predictions.csv')
orig_arimax = orig[orig['model_type'] == 'momentum_to_change_arimax'].copy()
orig_arimax = orig_arimax.rename(columns={'game_id': 'match_id'})

# Load new
new = pd.read_csv('models/period_separated_momentum/outputs/arimax_predictions_by_period.csv')

print("="*70)
print("ARIMAX MODEL COMPARISON")
print("="*70)

print(f"\nOriginal ARIMAX predictions: {len(orig_arimax)}")
print(f"New predictions: {len(new)}")

# Merge on match_id, team, minute_start
merged = pd.merge(
    orig_arimax[['match_id', 'team', 'minute_start', 'prediction_value', 'actual_value']],
    new[['match_id', 'team', 'minute_start', 'prediction_value', 'actual_value']],
    on=['match_id', 'team', 'minute_start'],
    suffixes=('_orig', '_new')
)

print(f"Matched records: {len(merged)}")

if len(merged) > 0:
    # Calculate differences
    merged['pred_diff'] = abs(merged['prediction_value_orig'] - merged['prediction_value_new'])
    merged['actual_diff'] = abs(merged['actual_value_orig'] - merged['actual_value_new'])
    
    # Count matches
    exact_pred = len(merged[merged['pred_diff'] < 0.001])
    close_pred = len(merged[(merged['pred_diff'] >= 0.001) & (merged['pred_diff'] < 0.1)])
    diff_pred = len(merged[merged['pred_diff'] >= 0.1])
    
    exact_actual = len(merged[merged['actual_diff'] < 0.001])
    close_actual = len(merged[(merged['actual_diff'] >= 0.001) & (merged['actual_diff'] < 0.1)])
    diff_actual = len(merged[merged['actual_diff'] >= 0.1])
    
    print(f"\n📊 Prediction Value Comparison:")
    print(f"  Exact match (<0.001): {exact_pred} ({100*exact_pred/len(merged):.1f}%)")
    print(f"  Close match (0.001-0.1): {close_pred} ({100*close_pred/len(merged):.1f}%)")
    print(f"  Different (>0.1): {diff_pred} ({100*diff_pred/len(merged):.1f}%)")
    
    print(f"\n📊 Actual Value Comparison (should match ~95%):")
    print(f"  Exact match (<0.001): {exact_actual} ({100*exact_actual/len(merged):.1f}%)")
    print(f"  Close match (0.001-0.1): {close_actual} ({100*close_actual/len(merged):.1f}%)")
    print(f"  Different (>0.1): {diff_actual} ({100*diff_actual/len(merged):.1f}%)")
    
    # Sample comparison
    print("\n📋 Sample comparison (first 10):")
    sample = merged.head(10)
    for _, row in sample.iterrows():
        print(f"  Min {row['minute_start']}: orig_pred={row['prediction_value_orig']:.3f}, new_pred={row['prediction_value_new']:.3f}, "
              f"orig_actual={row['actual_value_orig']:.3f}, new_actual={row['actual_value_new']:.3f}")
    
    # Actual values should be very similar - check where they differ
    diff_actuals = merged[merged['actual_diff'] >= 0.1]
    if len(diff_actuals) > 0:
        print(f"\n⚠️ Different actual values found ({len(diff_actuals)} records):")
        print(f"   These are the minutes where momentum calculation changed:")
        print(f"   Minutes: {sorted(diff_actuals['minute_start'].unique())}")

