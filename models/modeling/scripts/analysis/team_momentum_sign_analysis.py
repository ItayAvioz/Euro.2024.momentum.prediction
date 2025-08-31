"""
Analysis: Team X vs Team Y Momentum Sign Accuracy in Same Game Windows
Check how often ARIMAX correctly predicts momentum signs for both teams simultaneously
"""

import pandas as pd
import numpy as np

# Load the ARIMAX predictions
df = pd.read_csv('../outputs/predictions/arimax_predictions.csv')

# Filter for ARIMAX momentum-to-change model only
arimax_data = df[df['model_type'] == 'momentum_to_change_arimax'].copy()

print("🎯 TEAM X vs TEAM Y MOMENTUM SIGN ANALYSIS")
print("=" * 60)
print(f"Total ARIMAX predictions: {len(arimax_data):,}")

# Parse the minute ranges to get window identifiers
arimax_data['window'] = arimax_data['minutes_prediction']
arimax_data['game_window'] = arimax_data['game_id'].astype(str) + '_' + arimax_data['window']

print(f"Unique game windows: {arimax_data['game_window'].nunique():,}")
print(f"Games analyzed: {arimax_data['game_id'].nunique()}")

# Calculate prediction and actual signs
arimax_data['pred_sign'] = np.sign(arimax_data['prediction_value'])
arimax_data['actual_sign'] = np.sign(arimax_data['actual_value'])
arimax_data['sign_correct'] = (arimax_data['pred_sign'] == arimax_data['actual_sign']).astype(int)

# Group by game window to get both teams
window_analysis = []

for game_window in arimax_data['game_window'].unique():
    window_data = arimax_data[arimax_data['game_window'] == game_window]
    
    if len(window_data) == 2:  # Should have exactly 2 teams per window
        teams = window_data['team'].values
        pred_signs = window_data['pred_sign'].values
        actual_signs = window_data['actual_sign'].values
        sign_correct = window_data['sign_correct'].values
        pred_values = window_data['prediction_value'].values
        actual_values = window_data['actual_value'].values
        
        # Extract game info
        game_id = window_data['game_id'].iloc[0]
        minute_window = window_data['window'].iloc[0]
        
        window_analysis.append({
            'game_id': game_id,
            'window': minute_window,
            'team_1': teams[0],
            'team_2': teams[1],
            'team_1_pred_sign': pred_signs[0],
            'team_1_actual_sign': actual_signs[0],
            'team_1_correct': sign_correct[0],
            'team_1_pred_value': pred_values[0],
            'team_1_actual_value': actual_values[0],
            'team_2_pred_sign': pred_signs[1],
            'team_2_actual_sign': actual_signs[1],
            'team_2_correct': sign_correct[1],
            'team_2_pred_value': pred_values[1],
            'team_2_actual_value': actual_values[1],
            'both_correct': sign_correct[0] & sign_correct[1],
            'both_wrong': (1 - sign_correct[0]) & (1 - sign_correct[1]),
            'one_correct': (sign_correct[0] + sign_correct[1]) == 1
        })

# Convert to DataFrame
window_df = pd.DataFrame(window_analysis)

print(f"\nWindows with both teams: {len(window_df):,}")

print(f"\n📊 OVERALL TEAM SIGN ACCURACY ANALYSIS")
print("=" * 50)

# Calculate overall statistics
total_windows = len(window_df)
both_correct = window_df['both_correct'].sum()
both_wrong = window_df['both_wrong'].sum()
one_correct = window_df['one_correct'].sum()

both_correct_pct = both_correct / total_windows * 100
both_wrong_pct = both_wrong / total_windows * 100
one_correct_pct = one_correct / total_windows * 100

print(f"Total game windows analyzed: {total_windows:,}")
print(f"\n🎯 SIMULTANEOUS TEAM PREDICTION ACCURACY:")
print(f"Both teams correct:     {both_correct:,} ({both_correct_pct:.2f}%)")
print(f"One team correct:       {one_correct:,} ({one_correct_pct:.2f}%)")
print(f"Both teams wrong:       {both_wrong:,} ({both_wrong_pct:.2f}%)")

# Individual team accuracy
team_1_correct = window_df['team_1_correct'].sum()
team_2_correct = window_df['team_2_correct'].sum()
total_team_predictions = total_windows * 2

print(f"\n👥 INDIVIDUAL TEAM ACCURACY:")
print(f"Team 1 correct:         {team_1_correct:,} / {total_windows:,} ({team_1_correct/total_windows*100:.2f}%)")
print(f"Team 2 correct:         {team_2_correct:,} / {total_windows:,} ({team_2_correct/total_windows*100:.2f}%)")
print(f"Overall team accuracy:  {(team_1_correct + team_2_correct):,} / {total_team_predictions:,} ({(team_1_correct + team_2_correct)/total_team_predictions*100:.2f}%)")

print(f"\n🔍 DETAILED BREAKDOWN BY SIGN COMBINATIONS")
print("=" * 55)

# Analyze sign combinations
sign_combinations = {}

for _, row in window_df.iterrows():
    t1_pred = "+" if row['team_1_pred_sign'] > 0 else "-" if row['team_1_pred_sign'] < 0 else "0"
    t1_actual = "+" if row['team_1_actual_sign'] > 0 else "-" if row['team_1_actual_sign'] < 0 else "0"
    t2_pred = "+" if row['team_2_pred_sign'] > 0 else "-" if row['team_2_pred_sign'] < 0 else "0"
    t2_actual = "+" if row['team_2_actual_sign'] > 0 else "-" if row['team_2_actual_sign'] < 0 else "0"
    
    pred_combo = f"{t1_pred}{t2_pred}"
    actual_combo = f"{t1_actual}{t2_actual}"
    key = f"{pred_combo}→{actual_combo}"
    
    if key not in sign_combinations:
        sign_combinations[key] = 0
    sign_combinations[key] += 1

# Sort by frequency
sorted_combos = sorted(sign_combinations.items(), key=lambda x: x[1], reverse=True)

print(f"{'Predicted':<10} {'Actual':<10} {'Count':<8} {'%':<8} {'Result'}")
print("-" * 50)

for combo, count in sorted_combos[:15]:  # Show top 15
    pred_part, actual_part = combo.split('→')
    pct = count / total_windows * 100
    
    # Determine if correct
    t1_correct = pred_part[0] == actual_part[0]
    t2_correct = pred_part[1] == actual_part[1]
    
    if t1_correct and t2_correct:
        result = "✅✅ Both"
    elif t1_correct or t2_correct:
        result = "✅❌ One"
    else:
        result = "❌❌ None"
    
    print(f"{pred_part:<10} {actual_part:<10} {count:<8} {pct:<8.2f} {result}")

# Expected vs actual performance
expected_both_correct = (both_correct_pct / 100) ** 2 * 100  # If independent
print(f"\n🎲 PERFORMANCE vs RANDOM CHANCE:")
print(f"Actual both correct:    {both_correct_pct:.2f}%")
print(f"Random chance (25%):    25.00%")
print(f"If independent (~45%):  {(67.35/100)**2*100:.2f}%")
print(f"Improvement over random: {(both_correct_pct - 25)/25*100:.1f}%")

# Sample examples
print(f"\n📋 SAMPLE EXAMPLES (Both Teams Correct):")
print("-" * 70)
print(f"{'Game':<8} {'Window':<8} {'Team 1':<12} {'Pred':<6} {'Actual':<7} {'Team 2':<12} {'Pred':<6} {'Actual'}")

both_correct_examples = window_df[window_df['both_correct'] == 1].head(10)
for _, row in both_correct_examples.iterrows():
    t1_pred_sign = "+" if row['team_1_pred_sign'] > 0 else "-"
    t1_actual_sign = "+" if row['team_1_actual_sign'] > 0 else "-"
    t2_pred_sign = "+" if row['team_2_pred_sign'] > 0 else "-"
    t2_actual_sign = "+" if row['team_2_actual_sign'] > 0 else "-"
    
    print(f"{row['game_id']:<8} {row['window']:<8} {row['team_1']:<12} {t1_pred_sign:<6} {t1_actual_sign:<7} {row['team_2']:<12} {t2_pred_sign:<6} {t2_actual_sign}")

print(f"\n✅ ANALYSIS COMPLETE!")
print(f"ARIMAX correctly predicts momentum signs for BOTH teams in {both_correct_pct:.2f}% of game windows")
