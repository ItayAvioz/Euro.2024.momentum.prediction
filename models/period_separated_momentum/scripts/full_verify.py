import pandas as pd
import numpy as np
import json

print('='*70)
print('FULL VERIFICATION OF ALL REAL DATA ANALYSIS METRICS')
print('='*70)

# Load period-separated momentum data
df = pd.read_csv('../outputs/momentum_by_period.csv')

# Filter for period 1 and 2 only (no overtime)
df = df[df['period'].isin([1, 2])].copy()

# Calculate minute from minute_range
df['minute'] = df['minute_range'].str.split('-').str[0].astype(int)

# Filter from minute 3 onwards (when momentum change is valid)
df = df[df['minute'] >= 3].copy()

print(f'Total matches: {df["match_id"].nunique()}')
print(f'Total momentum windows: {len(df)}')
print(f'Avg windows per game: {len(df) / df["match_id"].nunique():.1f}')

# Load pre-calculated metrics analysis
results_df = pd.read_csv('../outputs/metrics_vs_result_analysis.csv')
print(f'\nMatch results loaded: {len(results_df)} games')

# ============================================================
# 1. INDIVIDUAL METRICS VS MATCH OUTCOME (from pre-calc file)
# ============================================================
print('\n' + '='*70)
print('1. INDIVIDUAL METRICS VS MATCH OUTCOME')
print('='*70)

# Absolute Momentum
abs_mom_valid = results_df[results_df['momentum_outcome'] != 'TIE']
print(f'\nAbsolute Momentum:')
print(f'  Games (with winner): {len(abs_mom_valid)}')
print(f'  WIN:  {(abs_mom_valid["momentum_outcome"] == "WIN").sum()} ({(abs_mom_valid["momentum_outcome"] == "WIN").sum() / len(abs_mom_valid) * 100:.1f}%)')
print(f'  LOSE: {(abs_mom_valid["momentum_outcome"] == "LOSE").sum()} ({(abs_mom_valid["momentum_outcome"] == "LOSE").sum() / len(abs_mom_valid) * 100:.1f}%)')
print(f'  DRAW: {(abs_mom_valid["momentum_outcome"] == "DRAW").sum()} ({(abs_mom_valid["momentum_outcome"] == "DRAW").sum() / len(abs_mom_valid) * 100:.1f}%)')

# Number of Sequences
seq_valid = results_df[results_df['num_seq_outcome'] != 'TIE']
print(f'\nNumber of Sequences:')
print(f'  Games (with winner): {len(seq_valid)}')
print(f'  WIN:  {(seq_valid["num_seq_outcome"] == "WIN").sum()} ({(seq_valid["num_seq_outcome"] == "WIN").sum() / len(seq_valid) * 100:.1f}%)')
print(f'  LOSE: {(seq_valid["num_seq_outcome"] == "LOSE").sum()} ({(seq_valid["num_seq_outcome"] == "LOSE").sum() / len(seq_valid) * 100:.1f}%)')
print(f'  DRAW: {(seq_valid["num_seq_outcome"] == "DRAW").sum()} ({(seq_valid["num_seq_outcome"] == "DRAW").sum() / len(seq_valid) * 100:.1f}%)')

# Positive Changes
change_valid = results_df[results_df['change_outcome'] != 'TIE']
print(f'\nPositive Changes:')
print(f'  Games (with winner): {len(change_valid)}')
print(f'  WIN:  {(change_valid["change_outcome"] == "WIN").sum()} ({(change_valid["change_outcome"] == "WIN").sum() / len(change_valid) * 100:.1f}%)')
print(f'  LOSE: {(change_valid["change_outcome"] == "LOSE").sum()} ({(change_valid["change_outcome"] == "LOSE").sum() / len(change_valid) * 100:.1f}%)')
print(f'  DRAW: {(change_valid["change_outcome"] == "DRAW").sum()} ({(change_valid["change_outcome"] == "DRAW").sum() / len(change_valid) * 100:.1f}%)')

# Longest Sequence
longest_valid = results_df[results_df['longest_outcome'] != 'TIE']
print(f'\nLongest Sequence:')
print(f'  Games (with winner): {len(longest_valid)}')
print(f'  WIN:  {(longest_valid["longest_outcome"] == "WIN").sum()} ({(longest_valid["longest_outcome"] == "WIN").sum() / len(longest_valid) * 100:.1f}%)')
print(f'  LOSE: {(longest_valid["longest_outcome"] == "LOSE").sum()} ({(longest_valid["longest_outcome"] == "LOSE").sum() / len(longest_valid) * 100:.1f}%)')
print(f'  DRAW: {(longest_valid["longest_outcome"] == "DRAW").sum()} ({(longest_valid["longest_outcome"] == "DRAW").sum() / len(longest_valid) * 100:.1f}%)')

# ============================================================
# 2. COMPARE WITH JSON FILE
# ============================================================
print('\n' + '='*70)
print('2. COMPARE WITH dashboard_metrics.json')
print('='*70)

with open('../outputs/dashboard_metrics.json', 'r') as f:
    json_metrics = json.load(f)

print('\nMetric             | CSV File | JSON File | Match?')
print('-' * 55)

print(f'Absolute Momentum  | {len(abs_mom_valid):8} | {json_metrics["absolute_momentum"]["games"]:9} | {"✅" if len(abs_mom_valid) == json_metrics["absolute_momentum"]["games"] else "❌"}')
print(f'Number of Sequences| {len(seq_valid):8} | {json_metrics["num_sequences"]["games"]:9} | {"✅" if len(seq_valid) == json_metrics["num_sequences"]["games"] else "❌"}')
print(f'Positive Changes   | {len(change_valid):8} | {json_metrics["positive_changes"]["games"]:9} | {"✅" if len(change_valid) == json_metrics["positive_changes"]["games"] else "❌"}')
print(f'Longest Sequence   | {len(longest_valid):8} | {json_metrics["longest_sequence"]["games"]:9} | {"✅" if len(longest_valid) == json_metrics["longest_sequence"]["games"] else "❌"}')

# ============================================================
# 3. TIE COUNTS
# ============================================================
print('\n' + '='*70)
print('3. TIE COUNTS (Why games < 51)')
print('='*70)

print('\nMetric             | With Winner | Ties')
print('-' * 45)
print(f'Absolute Momentum  | {len(abs_mom_valid):11} | {51 - len(abs_mom_valid)}')
print(f'Number of Sequences| {len(seq_valid):11} | {51 - len(seq_valid)}')
print(f'Positive Changes   | {len(change_valid):11} | {51 - len(change_valid)}')
print(f'Longest Sequence   | {len(longest_valid):11} | {51 - len(longest_valid)}')

# ============================================================
# 4. WIN/LOSE/DRAW PERCENTAGES COMPARISON
# ============================================================
print('\n' + '='*70)
print('4. WIN/LOSE/DRAW PERCENTAGES COMPARISON')
print('='*70)

def compare_pcts(name, csv_df, outcome_col, json_data):
    total = len(csv_df)
    if total == 0:
        return
    
    calc_win = (csv_df[outcome_col] == 'WIN').sum() / total * 100
    calc_lose = (csv_df[outcome_col] == 'LOSE').sum() / total * 100
    calc_draw = (csv_df[outcome_col] == 'DRAW').sum() / total * 100
    
    json_win = json_data['win_pct']
    json_lose = json_data['lose_pct']
    json_draw = json_data['draw_pct']
    
    print(f'\n{name}:')
    print(f'  WIN:  CSV={calc_win:.1f}% JSON={json_win}% {"✅" if abs(calc_win - json_win) < 0.5 else "❌"}')
    print(f'  LOSE: CSV={calc_lose:.1f}% JSON={json_lose}% {"✅" if abs(calc_lose - json_lose) < 0.5 else "❌"}')
    print(f'  DRAW: CSV={calc_draw:.1f}% JSON={json_draw}% {"✅" if abs(calc_draw - json_draw) < 0.5 else "❌"}')

compare_pcts('Absolute Momentum', abs_mom_valid, 'momentum_outcome', json_metrics['absolute_momentum'])
compare_pcts('Number of Sequences', seq_valid, 'num_seq_outcome', json_metrics['num_sequences'])
compare_pcts('Positive Changes', change_valid, 'change_outcome', json_metrics['positive_changes'])
compare_pcts('Longest Sequence', longest_valid, 'longest_outcome', json_metrics['longest_sequence'])

# ============================================================
# 5. SHOW TIE GAMES
# ============================================================
print('\n' + '='*70)
print('5. TIE GAMES BY METRIC')
print('='*70)

abs_ties = results_df[results_df['momentum_outcome'] == 'TIE']
if len(abs_ties) > 0:
    print(f'\nAbsolute Momentum Ties ({len(abs_ties)}):')
    for _, row in abs_ties.iterrows():
        print(f'  {row["home_team"]} vs {row["away_team"]}: {row["home_momentum_wins"]}-{row["away_momentum_wins"]}')

seq_ties = results_df[results_df['num_seq_outcome'] == 'TIE']
if len(seq_ties) > 0:
    print(f'\nNumber of Sequences Ties ({len(seq_ties)}):')
    for _, row in seq_ties.iterrows():
        print(f'  {row["home_team"]} vs {row["away_team"]}: {row["home_num_seq"]}-{row["away_num_seq"]}')

change_ties = results_df[results_df['change_outcome'] == 'TIE']
if len(change_ties) > 0:
    print(f'\nPositive Changes Ties ({len(change_ties)}):')
    for _, row in change_ties.iterrows():
        print(f'  {row["home_team"]} vs {row["away_team"]}: {row["home_positive_changes"]}-{row["away_positive_changes"]}')

longest_ties = results_df[results_df['longest_outcome'] == 'TIE']
if len(longest_ties) > 0:
    print(f'\nLongest Sequence Ties ({len(longest_ties)}):')
    for _, row in longest_ties.iterrows():
        print(f'  {row["home_team"]} vs {row["away_team"]}: {row["home_longest"]}-{row["away_longest"]}')
