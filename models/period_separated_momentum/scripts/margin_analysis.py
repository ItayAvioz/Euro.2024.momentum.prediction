import pandas as pd
import numpy as np

# Load pre-calculated metrics analysis
df = pd.read_csv('../outputs/metrics_vs_result_analysis.csv')

print('='*80)
print('CUMULATIVE MARGIN ANALYSIS - ALL METRICS')
print('='*80)

# ============================================================
# 1. ABSOLUTE MOMENTUM MARGIN
# ============================================================
print('\n' + '='*80)
print('1. ABSOLUTE MOMENTUM MARGIN')
print('='*80)

# Calculate margin percentage for each game
df['abs_mom_margin_pct'] = df['momentum_margin_pct']

# Show distribution
print('\nMargin % Distribution:')
print(f'  Min: {df["abs_mom_margin_pct"].min():.1f}%')
print(f'  Max: {df["abs_mom_margin_pct"].max():.1f}%')
print(f'  Mean: {df["abs_mom_margin_pct"].mean():.1f}%')
print(f'  Median: {df["abs_mom_margin_pct"].median():.1f}%')
print(f'  Quantiles:')
print(f'    10th: {df["abs_mom_margin_pct"].quantile(0.10):.1f}%')
print(f'    25th: {df["abs_mom_margin_pct"].quantile(0.25):.1f}%')
print(f'    75th: {df["abs_mom_margin_pct"].quantile(0.75):.1f}%')

print('\nCumulative Margins:')
print(f'{"Min Margin":<12} | {"Games":>6} | {"WIN":>8} | {"LOSE":>8} | {"DRAW":>8}')
print('-'*55)

for threshold in [0, 5, 10, 15, 20, 25]:
    valid = df[(df['momentum_outcome'] != 'TIE') & (df['momentum_margin_pct'] >= threshold)]
    total = len(valid)
    if total > 0:
        wins = (valid['momentum_outcome'] == 'WIN').sum()
        loses = (valid['momentum_outcome'] == 'LOSE').sum()
        draws = (valid['momentum_outcome'] == 'DRAW').sum()
        print(f'{threshold}%+         | {total:>6} | {wins/total*100:>6.1f}% | {loses/total*100:>6.1f}% | {draws/total*100:>6.1f}%')
    else:
        print(f'{threshold}%+         | {total:>6} | {"N/A":>8} | {"N/A":>8} | {"N/A":>8}')

# ============================================================
# 2. NUMBER OF SEQUENCES MARGIN
# ============================================================
print('\n' + '='*80)
print('2. NUMBER OF SEQUENCES MARGIN')
print('='*80)

# Calculate margin for sequences
df['seq_margin'] = abs(df['home_num_seq'] - df['away_num_seq'])

print('\nMargin Distribution (absolute difference):')
print(f'  Min: {df["seq_margin"].min()}')
print(f'  Max: {df["seq_margin"].max()}')
print(f'  Mean: {df["seq_margin"].mean():.1f}')
print(f'  Median: {df["seq_margin"].median():.1f}')
print(f'  Quantiles:')
print(f'    10th: {df["seq_margin"].quantile(0.10):.1f}')
print(f'    25th: {df["seq_margin"].quantile(0.25):.1f}')
print(f'    75th: {df["seq_margin"].quantile(0.75):.1f}')

print('\nCumulative Margins:')
print(f'{"Min Margin":<12} | {"Games":>6} | {"WIN":>8} | {"LOSE":>8} | {"DRAW":>8}')
print('-'*55)

for threshold in [0, 1, 2, 3, 4, 5]:
    valid = df[(df['num_seq_outcome'] != 'TIE') & (df['seq_margin'] >= threshold)]
    total = len(valid)
    if total > 0:
        wins = (valid['num_seq_outcome'] == 'WIN').sum()
        loses = (valid['num_seq_outcome'] == 'LOSE').sum()
        draws = (valid['num_seq_outcome'] == 'DRAW').sum()
        print(f'{threshold}+ seq      | {total:>6} | {wins/total*100:>6.1f}% | {loses/total*100:>6.1f}% | {draws/total*100:>6.1f}%')
    else:
        print(f'{threshold}+ seq      | {total:>6} | {"N/A":>8} | {"N/A":>8} | {"N/A":>8}')

# ============================================================
# 3. POSITIVE CHANGES MARGIN
# ============================================================
print('\n' + '='*80)
print('3. POSITIVE CHANGES MARGIN')
print('='*80)

df['change_margin'] = abs(df['home_positive_changes'] - df['away_positive_changes'])
df['change_margin_pct'] = df['change_margin'] / df['total_windows'] * 100

print('\nMargin % Distribution:')
print(f'  Min: {df["change_margin_pct"].min():.1f}%')
print(f'  Max: {df["change_margin_pct"].max():.1f}%')
print(f'  Mean: {df["change_margin_pct"].mean():.1f}%')
print(f'  Median: {df["change_margin_pct"].median():.1f}%')
print(f'  Quantiles:')
print(f'    10th: {df["change_margin_pct"].quantile(0.10):.1f}%')
print(f'    25th: {df["change_margin_pct"].quantile(0.25):.1f}%')
print(f'    75th: {df["change_margin_pct"].quantile(0.75):.1f}%')

print('\nCumulative Margins:')
print(f'{"Min Margin":<12} | {"Games":>6} | {"WIN":>8} | {"LOSE":>8} | {"DRAW":>8}')
print('-'*55)

for threshold in [0, 5, 10, 15, 20, 25]:
    valid = df[(df['change_outcome'] != 'TIE') & (df['change_margin_pct'] >= threshold)]
    total = len(valid)
    if total > 0:
        wins = (valid['change_outcome'] == 'WIN').sum()
        loses = (valid['change_outcome'] == 'LOSE').sum()
        draws = (valid['change_outcome'] == 'DRAW').sum()
        print(f'{threshold}%+         | {total:>6} | {wins/total*100:>6.1f}% | {loses/total*100:>6.1f}% | {draws/total*100:>6.1f}%')
    else:
        print(f'{threshold}%+         | {total:>6} | {"N/A":>8} | {"N/A":>8} | {"N/A":>8}')

# ============================================================
# 4. LONGEST SEQUENCE MARGIN
# ============================================================
print('\n' + '='*80)
print('4. LONGEST SEQUENCE MARGIN')
print('='*80)

df['longest_margin'] = abs(df['home_longest'] - df['away_longest'])

print('\nMargin Distribution (absolute difference):')
print(f'  Min: {df["longest_margin"].min()}')
print(f'  Max: {df["longest_margin"].max()}')
print(f'  Mean: {df["longest_margin"].mean():.1f}')
print(f'  Median: {df["longest_margin"].median():.1f}')
print(f'  Quantiles:')
print(f'    10th: {df["longest_margin"].quantile(0.10):.1f}')
print(f'    25th: {df["longest_margin"].quantile(0.25):.1f}')
print(f'    75th: {df["longest_margin"].quantile(0.75):.1f}')

print('\nCumulative Margins:')
print(f'{"Min Margin":<12} | {"Games":>6} | {"WIN":>8} | {"LOSE":>8} | {"DRAW":>8}')
print('-'*55)

for threshold in [0, 1, 2, 3, 4, 5]:
    valid = df[(df['longest_outcome'] != 'TIE') & (df['longest_margin'] >= threshold)]
    total = len(valid)
    if total > 0:
        wins = (valid['longest_outcome'] == 'WIN').sum()
        loses = (valid['longest_outcome'] == 'LOSE').sum()
        draws = (valid['longest_outcome'] == 'DRAW').sum()
        print(f'{threshold}+ windows  | {total:>6} | {wins/total*100:>6.1f}% | {loses/total*100:>6.1f}% | {draws/total*100:>6.1f}%')
    else:
        print(f'{threshold}+ windows  | {total:>6} | {"N/A":>8} | {"N/A":>8} | {"N/A":>8}')

# ============================================================
# SUMMARY TABLE
# ============================================================
print('\n' + '='*80)
print('SUMMARY: DASHBOARD vs CALCULATED')
print('='*80)

import json
with open('../outputs/dashboard_metrics.json', 'r') as f:
    json_data = json.load(f)

print('\n--- ABSOLUTE MOMENTUM MARGINS ---')
for threshold in ['0', '5', '10', '15', '20', '25']:
    json_val = json_data['momentum_margins'].get(threshold, {})
    if json_val:
        print(f'{threshold}%+: JSON(Games={json_val["games"]}, WIN={json_val["win_pct"]}%, LOSE={json_val["lose_pct"]}%)')

print('\n--- NUMBER OF SEQUENCES MARGINS ---')
for threshold in ['0', '1', '2', '3', '4', '5']:
    json_val = json_data['num_seq_margins'].get(threshold, {})
    if json_val:
        print(f'{threshold}+: JSON(Games={json_val["games"]}, WIN={json_val["win_pct"]}%, LOSE={json_val["lose_pct"]}%)')

print('\n--- LONGEST SEQUENCE MARGINS ---')
for threshold in ['0', '1', '2', '3', '4', '5']:
    json_val = json_data['longest_margins'].get(threshold, {})
    if json_val:
        print(f'{threshold}+: JSON(Games={json_val["games"]}, WIN={json_val["win_pct"]}%, LOSE={json_val["lose_pct"]}%)')

