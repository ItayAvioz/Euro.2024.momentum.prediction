"""
ARIMAX Differential Sign Analysis

Analyzes the differential sign between Team X and Team Y momentum changes:
- Differential = Team_X_momentum_change - Team_Y_momentum_change
- Compares ARIMAX predictions vs actual values for differential signs
- Focuses only on momentum_to_change_arimax model

Author: AI Assistant
Date: August 2024
"""

import pandas as pd
import numpy as np

# Load ARIMAX predictions
df = pd.read_csv('../outputs/predictions/arimax_predictions.csv')

# Filter for ARIMAX momentum-to-change model only
arimax_data = df[df['model_type'] == 'momentum_to_change_arimax'].copy()

print("🎯 ARIMAX DIFFERENTIAL SIGN ANALYSIS")
print("=" * 60)
print(f"Total ARIMAX predictions: {len(arimax_data):,}")

# Parse the minute ranges to get window identifiers
arimax_data['window'] = arimax_data['minutes_prediction']
arimax_data['game_window'] = arimax_data['game_id'].astype(str) + '_' + arimax_data['window']

print(f"Unique game windows: {arimax_data['game_window'].nunique():,}")
print(f"Games analyzed: {arimax_data['game_id'].nunique()}")

# Group by game window to get both teams
differential_analysis = []

for game_window in arimax_data['game_window'].unique():
    window_data = arimax_data[arimax_data['game_window'] == game_window]
    
    if len(window_data) == 2:  # Should have exactly 2 teams per window
        # Sort to ensure consistent team ordering
        window_data = window_data.sort_values('team').reset_index(drop=True)
        
        teams = window_data['team'].values
        pred_values = window_data['prediction_value'].values
        actual_values = window_data['actual_value'].values
        
        # Extract game info
        game_id = window_data['game_id'].iloc[0]
        minute_window = window_data['window'].iloc[0]
        minute_start = window_data['minute_start'].iloc[0]
        
        # Calculate differentials (Team X - Team Y, alphabetically sorted)
        pred_differential = pred_values[0] - pred_values[1]
        actual_differential = actual_values[0] - actual_values[1]
        
        # Calculate differential signs
        pred_diff_sign = np.sign(pred_differential)
        actual_diff_sign = np.sign(actual_differential)
        
        # Check if signs match
        signs_match = pred_diff_sign == actual_diff_sign
        
        differential_analysis.append({
            'game_id': game_id,
            'window': minute_window,
            'minute_start': minute_start,
            'team_x': teams[0],
            'team_y': teams[1],
            'team_x_pred': pred_values[0],
            'team_x_actual': actual_values[0],
            'team_y_pred': pred_values[1],
            'team_y_actual': actual_values[1],
            'pred_differential': pred_differential,
            'actual_differential': actual_differential,
            'pred_diff_sign': pred_diff_sign,
            'actual_diff_sign': actual_diff_sign,
            'signs_match': signs_match,
            'pred_diff_positive': pred_diff_sign > 0,
            'actual_diff_positive': actual_diff_sign > 0,
            'pred_diff_negative': pred_diff_sign < 0,
            'actual_diff_negative': actual_diff_sign < 0,
            'pred_diff_zero': pred_diff_sign == 0,
            'actual_diff_zero': actual_diff_sign == 0
        })

# Convert to DataFrame
diff_df = pd.DataFrame(differential_analysis)

print(f"\nDifferential analysis for {len(diff_df):,} game windows")

print(f"\n📊 DIFFERENTIAL SIGN ACCURACY ANALYSIS")
print("=" * 50)

# Calculate overall differential sign accuracy
total_windows = len(diff_df)
signs_correct = diff_df['signs_match'].sum()
differential_accuracy = signs_correct / total_windows

print(f"Total game windows analyzed: {total_windows:,}")
print(f"Differential signs correct: {signs_correct:,}")
print(f"Differential Sign Accuracy: {differential_accuracy:.4f} ({differential_accuracy*100:.2f}%)")

print(f"\n🔍 DETAILED DIFFERENTIAL SIGN BREAKDOWN")
print("=" * 45)

# Count sign combinations
pred_pos_actual_pos = ((diff_df['pred_diff_sign'] > 0) & (diff_df['actual_diff_sign'] > 0)).sum()
pred_neg_actual_neg = ((diff_df['pred_diff_sign'] < 0) & (diff_df['actual_diff_sign'] < 0)).sum()
pred_zero_actual_zero = ((diff_df['pred_diff_sign'] == 0) & (diff_df['actual_diff_sign'] == 0)).sum()

pred_pos_actual_neg = ((diff_df['pred_diff_sign'] > 0) & (diff_df['actual_diff_sign'] < 0)).sum()
pred_neg_actual_pos = ((diff_df['pred_diff_sign'] < 0) & (diff_df['actual_diff_sign'] > 0)).sum()
pred_pos_actual_zero = ((diff_df['pred_diff_sign'] > 0) & (diff_df['actual_diff_sign'] == 0)).sum()
pred_neg_actual_zero = ((diff_df['pred_diff_sign'] < 0) & (diff_df['actual_diff_sign'] == 0)).sum()
pred_zero_actual_pos = ((diff_df['pred_diff_sign'] == 0) & (diff_df['actual_diff_sign'] > 0)).sum()
pred_zero_actual_neg = ((diff_df['pred_diff_sign'] == 0) & (diff_df['actual_diff_sign'] < 0)).sum()

print(f"{'Predicted':<12} {'Actual':<12} {'Count':<8} {'%':<8} {'Result'}")
print("-" * 50)
print(f"{'Positive':<12} {'Positive':<12} {pred_pos_actual_pos:<8} {pred_pos_actual_pos/total_windows*100:<8.2f} ✅ Correct")
print(f"{'Negative':<12} {'Negative':<12} {pred_neg_actual_neg:<8} {pred_neg_actual_neg/total_windows*100:<8.2f} ✅ Correct")
print(f"{'Zero':<12} {'Zero':<12} {pred_zero_actual_zero:<8} {pred_zero_actual_zero/total_windows*100:<8.2f} ✅ Correct")
print(f"{'Positive':<12} {'Negative':<12} {pred_pos_actual_neg:<8} {pred_pos_actual_neg/total_windows*100:<8.2f} ❌ Wrong")
print(f"{'Negative':<12} {'Positive':<12} {pred_neg_actual_pos:<8} {pred_neg_actual_pos/total_windows*100:<8.2f} ❌ Wrong")
print(f"{'Positive':<12} {'Zero':<12} {pred_pos_actual_zero:<8} {pred_pos_actual_zero/total_windows*100:<8.2f} ❌ Wrong")
print(f"{'Negative':<12} {'Zero':<12} {pred_neg_actual_zero:<8} {pred_neg_actual_zero/total_windows*100:<8.2f} ❌ Wrong")
print(f"{'Zero':<12} {'Positive':<12} {pred_zero_actual_pos:<8} {pred_zero_actual_pos/total_windows*100:<8.2f} ❌ Wrong")
print(f"{'Zero':<12} {'Negative':<12} {pred_zero_actual_neg:<8} {pred_zero_actual_neg/total_windows*100:<8.2f} ❌ Wrong")

print(f"\n📈 DIFFERENTIAL DISTRIBUTION ANALYSIS")
print("=" * 40)

# Analyze distribution of differential signs
pred_positive_count = (diff_df['pred_diff_sign'] > 0).sum()
pred_negative_count = (diff_df['pred_diff_sign'] < 0).sum()
pred_zero_count = (diff_df['pred_diff_sign'] == 0).sum()

actual_positive_count = (diff_df['actual_diff_sign'] > 0).sum()
actual_negative_count = (diff_df['actual_diff_sign'] < 0).sum()
actual_zero_count = (diff_df['actual_diff_sign'] == 0).sum()

print(f"{'Sign':<12} {'Predicted':<15} {'%':<8} {'Actual':<15} {'%':<8}")
print("-" * 60)
print(f"{'Positive':<12} {pred_positive_count:<15} {pred_positive_count/total_windows*100:<8.2f} {actual_positive_count:<15} {actual_positive_count/total_windows*100:<8.2f}")
print(f"{'Negative':<12} {pred_negative_count:<15} {pred_negative_count/total_windows*100:<8.2f} {actual_negative_count:<15} {actual_negative_count/total_windows*100:<8.2f}")
print(f"{'Zero':<12} {pred_zero_count:<15} {pred_zero_count/total_windows*100:<8.2f} {actual_zero_count:<15} {actual_zero_count/total_windows*100:<8.2f}")

print(f"\n🎯 CONDITIONAL ACCURACY ANALYSIS")
print("=" * 35)

# When actual differential is positive
if actual_positive_count > 0:
    pos_correct = pred_pos_actual_pos
    pos_accuracy = pos_correct / actual_positive_count
    print(f"When actual differential is POSITIVE:")
    print(f"  Correctly predicted positive: {pos_correct}/{actual_positive_count} ({pos_accuracy*100:.2f}%)")

# When actual differential is negative  
if actual_negative_count > 0:
    neg_correct = pred_neg_actual_neg
    neg_accuracy = neg_correct / actual_negative_count
    print(f"When actual differential is NEGATIVE:")
    print(f"  Correctly predicted negative: {neg_correct}/{actual_negative_count} ({neg_accuracy*100:.2f}%)")

# When actual differential is zero
if actual_zero_count > 0:
    zero_correct = pred_zero_actual_zero
    zero_accuracy = zero_correct / actual_zero_count
    print(f"When actual differential is ZERO:")
    print(f"  Correctly predicted zero: {zero_correct}/{actual_zero_count} ({zero_accuracy*100:.2f}%)")

print(f"\n📊 DIFFERENTIAL MAGNITUDE ANALYSIS")
print("=" * 40)

# Analyze differential magnitudes
print(f"Predicted Differential Statistics:")
print(f"  Mean: {diff_df['pred_differential'].mean():.4f}")
print(f"  Std:  {diff_df['pred_differential'].std():.4f}")
print(f"  Min:  {diff_df['pred_differential'].min():.4f}")
print(f"  Max:  {diff_df['pred_differential'].max():.4f}")

print(f"\nActual Differential Statistics:")
print(f"  Mean: {diff_df['actual_differential'].mean():.4f}")
print(f"  Std:  {diff_df['actual_differential'].std():.4f}")
print(f"  Min:  {diff_df['actual_differential'].min():.4f}")
print(f"  Max:  {diff_df['actual_differential'].max():.4f}")

# Correlation between predicted and actual differentials
correlation = np.corrcoef(diff_df['pred_differential'], diff_df['actual_differential'])[0, 1]
print(f"\nCorrelation between predicted and actual differentials: {correlation:.4f}")

print(f"\n🎲 PERFORMANCE vs RANDOM CHANCE")
print("=" * 35)

# For differential signs, random chance depends on distribution
# If balanced (33% each), random would be 33%
# If binary (50% each), random would be 50%

# Calculate theoretical random chance based on actual distribution
actual_pos_rate = actual_positive_count / total_windows
actual_neg_rate = actual_negative_count / total_windows
actual_zero_rate = actual_zero_count / total_windows

# Random chance = sum of squares of probabilities (if predicting based on base rates)
random_chance = actual_pos_rate**2 + actual_neg_rate**2 + actual_zero_rate**2

print(f"ARIMAX Differential Sign Accuracy: {differential_accuracy*100:.2f}%")
print(f"Random Chance (base rate): {random_chance*100:.2f}%")
if random_chance > 0:
    improvement = (differential_accuracy - random_chance) / random_chance * 100
    print(f"Improvement over random: {improvement:.1f}%")

print(f"\n📋 SAMPLE EXAMPLES")
print("=" * 20)

# Show sample examples
print(f"{'Game':<8} {'Window':<8} {'Team X':<12} {'Team Y':<12} {'Pred Diff':<10} {'Actual Diff':<11} {'Signs Match'}")
print("-" * 85)

sample_indices = np.random.choice(len(diff_df), min(15, len(diff_df)), replace=False)
for idx in sample_indices:
    row = diff_df.iloc[idx]
    match_symbol = "✅" if row['signs_match'] else "❌"
    print(f"{row['game_id']:<8} {row['window']:<8} {row['team_x']:<12} {row['team_y']:<12} {row['pred_differential']:<10.3f} {row['actual_differential']:<11.3f} {match_symbol}")

print(f"\n✅ ANALYSIS COMPLETE!")
print(f"ARIMAX differential sign accuracy: {differential_accuracy*100:.2f}%")
print(f"Analyzed {total_windows:,} game windows across {diff_df['game_id'].nunique()} games")

# Save detailed results to CSV
output_file = "arimax_differential_sign_analysis.csv"
diff_df.to_csv(output_file, index=False)
print(f"Detailed results saved to: {output_file}")

# Summary statistics
print(f"\n📈 SUMMARY STATISTICS")
print("=" * 25)
print(f"Total Windows: {total_windows:,}")
print(f"Correct Differential Signs: {signs_correct:,}")
print(f"Differential Sign Accuracy: {differential_accuracy:.4f}")
print(f"Strongest Relationship: Differential correlation r = {correlation:.3f}")
