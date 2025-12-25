import pandas as pd
import numpy as np

# Load original predictions
orig = pd.read_csv('models/modeling/scripts/outputs/predictions/arimax_predictions.csv')
new = pd.read_csv('models/period_separated_momentum/outputs/arimax_predictions_by_period.csv')

print("="*70)
print("PREDICTION COMPARISON")
print("="*70)

print(f"\nOriginal predictions: {len(orig)}")
print(f"New predictions: {len(new)}")

# Check original structure
print("\nOriginal sample:")
print(orig[['game_id', 'team', 'minute_start', 'prediction_value', 'actual_value', 'n_train_observations']].head(10))

print("\nNew sample:")
print(new[['match_id', 'team', 'minute_start', 'prediction_value', 'actual_value', 'n_train']].head(10))

# Merge and compare
print("\n" + "="*70)
print("MATCHING PREDICTIONS")
print("="*70)

# Rename columns for merge
orig_renamed = orig.rename(columns={'game_id': 'match_id'})

# Merge on match_id, team, and minute_start
merged = pd.merge(
    orig_renamed[['match_id', 'team', 'minute_start', 'prediction_value', 'actual_value']],
    new[['match_id', 'team', 'minute_start', 'prediction_value', 'actual_value']],
    on=['match_id', 'team', 'minute_start'],
    suffixes=('_orig', '_new')
)

print(f"\nMatched records: {len(merged)}")

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
    
    print(f"\n📊 Actual Value Comparison:")
    print(f"  Exact match (<0.001): {exact_actual} ({100*exact_actual/len(merged):.1f}%)")
    print(f"  Close match (0.001-0.1): {close_actual} ({100*close_actual/len(merged):.1f}%)")
    print(f"  Different (>0.1): {diff_actual} ({100*diff_actual/len(merged):.1f}%)")
    
    # Show sample of different predictions
    if diff_pred > 0:
        print(f"\n📋 Sample of different predictions:")
        sample = merged[merged['pred_diff'] >= 0.1].head(10)
        for _, row in sample.iterrows():
            print(f"  Match {row['match_id']}, {row['team']}, min {row['minute_start']}: "
                  f"orig={row['prediction_value_orig']:.3f}, new={row['prediction_value_new']:.3f}, "
                  f"diff={row['pred_diff']:.3f}")

# Check why different counts
print("\n" + "="*70)
print("WHY DIFFERENT COUNTS?")
print("="*70)

print(f"\nOriginal unique matches: {orig['game_id'].nunique()}")
print(f"New unique matches: {new['match_id'].nunique()}")

print(f"\nOriginal predictions per match (avg): {len(orig) / orig['game_id'].nunique():.1f}")
print(f"New predictions per match (avg): {len(new) / new['match_id'].nunique():.1f}")

# Check minute ranges
print(f"\nOriginal minute_start range: {orig['minute_start'].min()} - {orig['minute_start'].max()}")
print(f"New minute_start range: {new['minute_start'].min()} - {new['minute_start'].max()}")

# Check n_train
print(f"\nOriginal n_train: {orig['n_train_observations'].unique()}")
print(f"New n_train range: {new['n_train'].min()} - {new['n_train'].max()}")

