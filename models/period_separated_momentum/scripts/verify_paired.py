import pandas as pd
import numpy as np

print("="*60)
print("PERIOD-SEPARATED DATA (after NaN fix)")
print("="*60)

df = pd.read_csv('../outputs/arimax_predictions_by_period.csv')
df_clean = df.dropna(subset=['prediction_value', 'actual_value'])

home = df_clean[df_clean['is_home'] == True][['match_id', 'minute_start', 'prediction_value', 'actual_value']].copy()
away = df_clean[df_clean['is_home'] == False][['match_id', 'minute_start', 'prediction_value', 'actual_value']].copy()

home.columns = ['match_id', 'minute_start', 'pred_home', 'actual_home']
away.columns = ['match_id', 'minute_start', 'pred_away', 'actual_away']

merged = pd.merge(home, away, on=['match_id', 'minute_start'])

print(f'Total paired windows: {len(merged)}')

home_correct = np.sign(merged['pred_home']) == np.sign(merged['actual_home'])
away_correct = np.sign(merged['pred_away']) == np.sign(merged['actual_away'])

both_correct = (home_correct & away_correct).sum()
only_home = (home_correct & ~away_correct).sum()
only_away = (~home_correct & away_correct).sum()
both_wrong = (~home_correct & ~away_correct).sum()

total = len(merged)
print(f'Both Correct: {both_correct} ({both_correct/total*100:.1f}%)')
print(f'Only Home Correct: {only_home} ({only_home/total*100:.1f}%)')
print(f'Only Away Correct: {only_away} ({only_away/total*100:.1f}%)')
print(f'One Team Correct: {only_home + only_away} ({(only_home+only_away)/total*100:.1f}%)')
print(f'Both Wrong: {both_wrong} ({both_wrong/total*100:.1f}%)')
print(f'Sum check: {both_correct + only_home + only_away + both_wrong}')

# Now check ORIGINAL
print("\n" + "="*60)
print("ORIGINAL DATA")
print("="*60)

orig = pd.read_csv('../../modeling/scripts/outputs/predictions/arimax_predictions.csv')
orig = orig[orig['model_type'] == 'momentum_to_change_arimax']
orig_clean = orig.dropna(subset=['prediction_value', 'actual_value'])

# Check home/away from team column
# Need match result data to determine which team is home/away
games = pd.read_csv('../../preprocessing/outputs/match_results.csv')

# Merge to get home/away info
orig_with_info = orig_clean.merge(
    games[['match_id', 'home_team', 'away_team']], 
    left_on='game_id', 
    right_on='match_id',
    how='left'
)

orig_with_info['is_home'] = orig_with_info['team'] == orig_with_info['home_team']

home_orig = orig_with_info[orig_with_info['is_home'] == True][['game_id', 'minute_start', 'prediction_value', 'actual_value']].copy()
away_orig = orig_with_info[orig_with_info['is_home'] == False][['game_id', 'minute_start', 'prediction_value', 'actual_value']].copy()

home_orig.columns = ['game_id', 'minute_start', 'pred_home', 'actual_home']
away_orig.columns = ['game_id', 'minute_start', 'pred_away', 'actual_away']

merged_orig = pd.merge(home_orig, away_orig, on=['game_id', 'minute_start'])

print(f'Total paired windows: {len(merged_orig)}')

home_correct_orig = np.sign(merged_orig['pred_home']) == np.sign(merged_orig['actual_home'])
away_correct_orig = np.sign(merged_orig['pred_away']) == np.sign(merged_orig['actual_away'])

both_correct_orig = (home_correct_orig & away_correct_orig).sum()
only_home_orig = (home_correct_orig & ~away_correct_orig).sum()
only_away_orig = (~home_correct_orig & away_correct_orig).sum()
both_wrong_orig = (~home_correct_orig & ~away_correct_orig).sum()

total_orig = len(merged_orig)
print(f'Both Correct: {both_correct_orig} ({both_correct_orig/total_orig*100:.1f}%)')
print(f'Only Home Correct: {only_home_orig} ({only_home_orig/total_orig*100:.1f}%)')
print(f'Only Away Correct: {only_away_orig} ({only_away_orig/total_orig*100:.1f}%)')
print(f'One Team Correct: {only_home_orig + only_away_orig} ({(only_home_orig+only_away_orig)/total_orig*100:.1f}%)')
print(f'Both Wrong: {both_wrong_orig} ({both_wrong_orig/total_orig*100:.1f}%)')
print(f'Sum check: {both_correct_orig + only_home_orig + only_away_orig + both_wrong_orig}')

