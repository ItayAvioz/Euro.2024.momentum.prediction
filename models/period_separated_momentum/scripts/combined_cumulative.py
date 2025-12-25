import pandas as pd
import numpy as np

# Load pre-calculated metrics analysis
df = pd.read_csv('../outputs/metrics_vs_result_analysis.csv')

# Calculate margins
df['seq_margin'] = abs(df['home_num_seq'] - df['away_num_seq'])

print('='*80)
print('COMBINED WINNING METRICS CUMULATIVE ANALYSIS')
print('Absolute Momentum % + Number of Sequences margin')
print('='*80)

# Define thresholds
mom_thresholds = [0, 10, 15, 20, 25, 30]
seq_thresholds = [0, 1, 2, 3, 4]

print('\n' + '-'*80)
print(f'{"Abs Mom %":<12} | {"Seq Margin":<12} | {"Games":>6} | {"WIN":>8} | {"LOSE":>8} | {"DRAW":>8}')
print('-'*80)

results = []
for mom_th in mom_thresholds:
    for seq_th in seq_thresholds:
        # Both conditions must be met AND both must have a winner (not TIE)
        valid = df[
            (df['momentum_outcome'] != 'TIE') & 
            (df['num_seq_outcome'] != 'TIE') &
            (df['momentum_margin_pct'] >= mom_th) & 
            (df['seq_margin'] >= seq_th)
        ]
        
        # Check if BOTH metrics point to same team
        # momentum_winner and num_seq_winner should match
        same_team = valid[valid['momentum_winner'] == valid['num_seq_winner']]
        
        total = len(same_team)
        if total > 0:
            # When both agree, use momentum_outcome (same as num_seq_outcome when they agree)
            wins = (same_team['momentum_outcome'] == 'WIN').sum()
            loses = (same_team['momentum_outcome'] == 'LOSE').sum()
            draws = (same_team['momentum_outcome'] == 'DRAW').sum()
            
            results.append({
                'mom_th': mom_th,
                'seq_th': seq_th,
                'games': total,
                'win_pct': wins/total*100,
                'lose_pct': loses/total*100,
                'draw_pct': draws/total*100
            })
            
            print(f'{mom_th}%+         | {seq_th}+ seq      | {total:>6} | {wins/total*100:>6.1f}% | {loses/total*100:>6.1f}% | {draws/total*100:>6.1f}%')

# Show key findings
print('\n' + '='*80)
print('KEY FINDINGS - Best Combined Thresholds')
print('='*80)

results_df = pd.DataFrame(results)

# Sort by win rate
best_by_win = results_df[results_df['games'] >= 5].sort_values('win_pct', ascending=False).head(10)
print('\nTop 10 by WIN rate (min 5 games):')
for _, row in best_by_win.iterrows():
    print(f"  Mom {row['mom_th']}%+ & Seq {row['seq_th']}+: {row['games']} games, WIN={row['win_pct']:.1f}%, LOSE={row['lose_pct']:.1f}%")

# Sort by lowest lose rate
best_by_lose = results_df[results_df['games'] >= 5].sort_values('lose_pct', ascending=True).head(10)
print('\nTop 10 by lowest LOSE rate (min 5 games):')
for _, row in best_by_lose.iterrows():
    print(f"  Mom {row['mom_th']}%+ & Seq {row['seq_th']}+: {row['games']} games, WIN={row['win_pct']:.1f}%, LOSE={row['lose_pct']:.1f}%")

