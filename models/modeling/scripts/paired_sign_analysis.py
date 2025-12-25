"""
ARIMAX Paired Sign Analysis - Same Window Analysis for Both Teams
Checks sign accuracy for Team X and Team Y in the same 3-minute window
"""
import pandas as pd
import numpy as np

# Load predictions
df = pd.read_csv('outputs/predictions/arimax_predictions.csv')

# Filter for ARIMAX model only
arimax = df[df['model_type'] == 'momentum_to_change_arimax'].copy()

print('=' * 70)
print('ARIMAX PAIRED SIGN ANALYSIS - SAME WINDOW FOR BOTH TEAMS')
print('=' * 70)
print(f'Total ARIMAX predictions: {len(arimax):,}')
print(f'Games: {arimax["game_id"].nunique()}')

# Create window identifier
arimax['window_id'] = arimax['game_id'].astype(str) + '_' + arimax['minutes_prediction']

# Calculate sign correctness for each prediction
arimax['pred_sign'] = np.sign(arimax['prediction_value'])
arimax['actual_sign'] = np.sign(arimax['actual_value'])
arimax['sign_correct'] = arimax['pred_sign'] == arimax['actual_sign']

# Group by window to get pairs
paired_analysis = []

for window_id in arimax['window_id'].unique():
    window_data = arimax[arimax['window_id'] == window_id]
    
    if len(window_data) == 2:  # Should have exactly 2 teams per window
        # Sort by team name for consistent ordering
        window_data = window_data.sort_values('team').reset_index(drop=True)
        
        team_x = window_data.iloc[0]['team']
        team_y = window_data.iloc[1]['team']
        
        team_x_correct = window_data.iloc[0]['sign_correct']
        team_y_correct = window_data.iloc[1]['sign_correct']
        
        team_x_pred_sign = window_data.iloc[0]['pred_sign']
        team_y_pred_sign = window_data.iloc[1]['pred_sign']
        team_x_actual_sign = window_data.iloc[0]['actual_sign']
        team_y_actual_sign = window_data.iloc[1]['actual_sign']
        
        # Determine case
        if team_x_correct and team_y_correct:
            case = "BOTH_CORRECT"
        elif team_x_correct and not team_y_correct:
            case = "ONLY_X_CORRECT"
        elif not team_x_correct and team_y_correct:
            case = "ONLY_Y_CORRECT"
        else:
            case = "BOTH_WRONG"
        
        paired_analysis.append({
            'window_id': window_id,
            'game_id': window_data.iloc[0]['game_id'],
            'minutes': window_data.iloc[0]['minutes_prediction'],
            'team_x': team_x,
            'team_y': team_y,
            'team_x_pred_sign': team_x_pred_sign,
            'team_x_actual_sign': team_x_actual_sign,
            'team_x_correct': team_x_correct,
            'team_y_pred_sign': team_y_pred_sign,
            'team_y_actual_sign': team_y_actual_sign,
            'team_y_correct': team_y_correct,
            'case': case
        })

# Convert to DataFrame
paired_df = pd.DataFrame(paired_analysis)
total_windows = len(paired_df)

print(f'\nTotal game windows analyzed: {total_windows}')

print()
print('=' * 70)
print('PAIRED SIGN ACCURACY ANALYSIS')
print('=' * 70)

# Count cases
both_correct = (paired_df['case'] == 'BOTH_CORRECT').sum()
only_x_correct = (paired_df['case'] == 'ONLY_X_CORRECT').sum()
only_y_correct = (paired_df['case'] == 'ONLY_Y_CORRECT').sum()
one_correct = only_x_correct + only_y_correct
both_wrong = (paired_df['case'] == 'BOTH_WRONG').sum()

print()
print('RESULTS:')
print('-' * 50)
print(f'  [OK][OK] BOTH teams correct:     {both_correct:>5} ({both_correct/total_windows*100:>6.2f}%)')
print(f'  [OK][X]  Only ONE team correct:  {one_correct:>5} ({one_correct/total_windows*100:>6.2f}%)')
print(f'           - Only Team X correct:  {only_x_correct:>5} ({only_x_correct/total_windows*100:>6.2f}%)')
print(f'           - Only Team Y correct:  {only_y_correct:>5} ({only_y_correct/total_windows*100:>6.2f}%)')
print(f'  [X][X]   BOTH teams wrong:       {both_wrong:>5} ({both_wrong/total_windows*100:>6.2f}%)')
print('-' * 50)
print(f'  TOTAL windows:                   {total_windows:>5}')

print()
print('=' * 70)
print('VISUAL BREAKDOWN')
print('=' * 70)
print()
print(f'                    Team Y Correct     Team Y Wrong')
print(f'                  +----------------+----------------+')
print(f'  Team X Correct  | {both_correct:>5} ({both_correct/total_windows*100:>5.1f}%) | {only_x_correct:>5} ({only_x_correct/total_windows*100:>5.1f}%) |')
print(f'  Team X Wrong    | {only_y_correct:>5} ({only_y_correct/total_windows*100:>5.1f}%) | {both_wrong:>5} ({both_wrong/total_windows*100:>5.1f}%) |')
print(f'                  +----------------+----------------+')

print()
print('=' * 70)
print('INTERPRETATION')
print('=' * 70)
print()
print(f'1. In {both_correct/total_windows*100:.1f}% of windows, we correctly predict the sign')
print(f'   for BOTH teams simultaneously.')
print()
print(f'2. In {one_correct/total_windows*100:.1f}% of windows, we correctly predict the sign')
print(f'   for exactly ONE team (partial success).')
print()
print(f'3. In {both_wrong/total_windows*100:.1f}% of windows, we get BOTH teams wrong.')
print()
print('=' * 70)
print('AT LEAST ONE CORRECT vs COMPLETE FAILURE')
print('=' * 70)
at_least_one = both_correct + one_correct
print()
print(f'  At least one team correct: {at_least_one:>5} ({at_least_one/total_windows*100:.2f}%)')
print(f'  Complete failure (both wrong): {both_wrong:>5} ({both_wrong/total_windows*100:.2f}%)')

print()
print('=' * 70)
print('SAMPLE EXAMPLES FROM EACH CATEGORY')
print('=' * 70)

for case_type in ['BOTH_CORRECT', 'ONLY_X_CORRECT', 'ONLY_Y_CORRECT', 'BOTH_WRONG']:
    case_data = paired_df[paired_df['case'] == case_type]
    if len(case_data) > 0:
        print(f'\n{case_type} Example:')
        sample = case_data.iloc[0]
        print(f'  Window: {sample["minutes"]}')
        print(f'  {sample["team_x"]}: Pred={sample["team_x_pred_sign"]:+.0f}, Actual={sample["team_x_actual_sign"]:+.0f} {"[OK]" if sample["team_x_correct"] else "[X]"}')
        print(f'  {sample["team_y"]}: Pred={sample["team_y_pred_sign"]:+.0f}, Actual={sample["team_y_actual_sign"]:+.0f} {"[OK]" if sample["team_y_correct"] else "[X]"}')

