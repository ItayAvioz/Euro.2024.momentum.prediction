import pandas as pd
import numpy as np

# Load pre-calculated metrics analysis
df = pd.read_csv('../outputs/metrics_vs_result_analysis.csv')

# Calculate margins
df['seq_margin'] = abs(df['home_num_seq'] - df['away_num_seq'])
df['longest_margin_calc'] = abs(df['home_longest'] - df['away_longest'])
df['change_margin_pct_calc'] = abs(df['home_positive_changes'] - df['away_positive_changes']) / df['total_windows'] * 100

# ============================================================
# 1. WINNING METRICS: Absolute Momentum + Number of Sequences (SAME TEAM)
# ============================================================
print('='*80)
print('1. WINNING METRICS AGREE: Absolute Momentum + Number of Sequences')
print('='*80)

print(f'{"Abs Mom %":<10} | {"Seq":<6} | {"Games":>6} | {"WIN":>7} | {"LOSE":>7} | {"DRAW":>7}')
print('-'*60)

for mom_th in [0, 10, 15, 20]:
    for seq_th in [0, 2, 3, 4]:
        valid = df[
            (df['momentum_outcome'] != 'TIE') & 
            (df['num_seq_outcome'] != 'TIE') &
            (df['momentum_margin_pct'] >= mom_th) & 
            (df['seq_margin'] >= seq_th) &
            (df['momentum_winner'] == df['num_seq_winner'])
        ]
        total = len(valid)
        if total > 0:
            wins = (valid['momentum_outcome'] == 'WIN').sum()
            loses = (valid['momentum_outcome'] == 'LOSE').sum()
            draws = (valid['momentum_outcome'] == 'DRAW').sum()
            print(f'{mom_th}%+       | {seq_th}+    | {total:>6} | {wins/total*100:>5.1f}% | {loses/total*100:>5.1f}% | {draws/total*100:>5.1f}%')

# ============================================================
# 2. CHASING METRICS: Positive Changes + Longest Sequence (SAME TEAM)
# ============================================================
print('\n' + '='*80)
print('2. CHASING METRICS AGREE: Positive Changes + Longest Sequence')
print('='*80)

print(f'{"Pos Chg %":<10} | {"Long":<6} | {"Games":>6} | {"WIN":>7} | {"LOSE":>7} | {"DRAW":>7}')
print('-'*60)

for chg_th in [0, 5, 10]:
    for long_th in [0, 2, 3, 4]:
        valid = df[
            (df['change_outcome'] != 'TIE') & 
            (df['longest_outcome'] != 'TIE') &
            (df['change_margin_pct_calc'] >= chg_th) & 
            (df['longest_margin_calc'] >= long_th) &
            (df['change_winner'] == df['longest_winner'])
        ]
        total = len(valid)
        if total > 0:
            wins = (valid['change_outcome'] == 'WIN').sum()
            loses = (valid['change_outcome'] == 'LOSE').sum()
            draws = (valid['change_outcome'] == 'DRAW').sum()
            print(f'{chg_th}%+       | {long_th}+    | {total:>6} | {wins/total*100:>5.1f}% | {loses/total*100:>5.1f}% | {draws/total*100:>5.1f}%')

# ============================================================
# 3. CROSS: Winning Momentum + Chasing Positive Changes (DIFFERENT TEAMS)
# ============================================================
print('\n' + '='*80)
print('3. DIFFERENT TEAMS: Winning (Abs Mom) → A, Chasing (Pos Chg) → B')
print('='*80)

print(f'{"Abs Mom %":<10} | {"Pos %":<6} | {"Games":>6} | {"WIN":>7} | {"LOSE":>7} | {"DRAW":>7}')
print('-'*60)

for mom_th in [0, 10, 15, 20]:
    for chg_th in [0, 5]:
        valid = df[
            (df['momentum_outcome'] != 'TIE') & 
            (df['change_outcome'] != 'TIE') &
            (df['momentum_margin_pct'] >= mom_th) & 
            (df['change_margin_pct_calc'] >= chg_th) &
            (df['momentum_winner'] != df['change_winner'])
        ]
        total = len(valid)
        if total > 0:
            # Use momentum_outcome since winning metric points to this team
            wins = (valid['momentum_outcome'] == 'WIN').sum()
            loses = (valid['momentum_outcome'] == 'LOSE').sum()
            draws = (valid['momentum_outcome'] == 'DRAW').sum()
            print(f'{mom_th}%+       | {chg_th}%+   | {total:>6} | {wins/total*100:>5.1f}% | {loses/total*100:>5.1f}% | {draws/total*100:>5.1f}%')

# ============================================================
# 4. CROSS: Winning Num Seq + Chasing Longest (DIFFERENT TEAMS)
# ============================================================
print('\n' + '='*80)
print('4. DIFFERENT TEAMS: Winning (Num Seq) → A, Chasing (Longest) → B')
print('='*80)

print(f'{"Seq":<10} | {"Long":<6} | {"Games":>6} | {"WIN":>7} | {"LOSE":>7} | {"DRAW":>7}')
print('-'*60)

for seq_th in [0, 2, 3, 4]:
    for long_th in [0, 2, 3]:
        valid = df[
            (df['num_seq_outcome'] != 'TIE') & 
            (df['longest_outcome'] != 'TIE') &
            (df['seq_margin'] >= seq_th) & 
            (df['longest_margin_calc'] >= long_th) &
            (df['num_seq_winner'] != df['longest_winner'])
        ]
        total = len(valid)
        if total > 0:
            # Use num_seq_outcome since winning metric points to this team
            wins = (valid['num_seq_outcome'] == 'WIN').sum()
            loses = (valid['num_seq_outcome'] == 'LOSE').sum()
            draws = (valid['num_seq_outcome'] == 'DRAW').sum()
            print(f'{seq_th}+        | {long_th}+    | {total:>6} | {wins/total*100:>5.1f}% | {loses/total*100:>5.1f}% | {draws/total*100:>5.1f}%')

