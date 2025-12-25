"""
Check cumulative analysis for Number of Sequences
"""

import pandas as pd
import numpy as np

print("=" * 70)
print("NUMBER OF SEQUENCES - CUMULATIVE MARGIN ANALYSIS")
print("=" * 70)

# Load sequence analysis
sequence_df = pd.read_csv('momentum_sequence_vs_result_analysis.csv')

print(f"\nLoaded {len(sequence_df)} games")

# Calculate margin for number of sequences
sequence_df['num_seq_margin'] = abs(sequence_df['home_num_sequences'] - sequence_df['away_num_sequences'])

print(f"\nNumber of Sequences margin statistics:")
print(f"  Min: {sequence_df['num_seq_margin'].min()}")
print(f"  Max: {sequence_df['num_seq_margin'].max()}")
print(f"  Mean: {sequence_df['num_seq_margin'].mean():.1f}")
print(f"  Median: {sequence_df['num_seq_margin'].median():.1f}")

# Distribution
print("\nMargin distribution:")
for margin in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
    count = len(sequence_df[sequence_df['num_seq_margin'] >= margin])
    print(f"  {margin}+ sequences: {count} games")

# Get outcome for sequence winner
def get_outcome(row):
    winner = row['more_seq_winner']
    if winner == 'home':
        if row['match_result'] == 'home_win':
            return 'WIN'
        elif row['match_result'] == 'away_win':
            return 'LOSE'
        else:
            return 'DRAW'
    elif winner == 'away':
        if row['match_result'] == 'away_win':
            return 'WIN'
        elif row['match_result'] == 'home_win':
            return 'LOSE'
        else:
            return 'DRAW'
    else:
        return 'TIE'

sequence_df['outcome'] = sequence_df.apply(get_outcome, axis=1)

print("\n" + "=" * 70)
print("CUMULATIVE ANALYSIS: WIN/LOSE/DRAW BY MINIMUM MARGIN")
print("=" * 70)

print("\n" + "-" * 70)
print(f"{'Min Margin':<15} | {'Games':>6} | {'WIN':>12} | {'LOSE':>12} | {'DRAW':>12}")
print("-" * 70)

for min_margin in [0, 1, 2, 3, 4, 5, 6, 7, 8]:
    subset = sequence_df[(sequence_df['num_seq_margin'] >= min_margin) & (sequence_df['more_seq_winner'] != 'tie')]
    
    total = len(subset)
    if total == 0:
        continue
        
    wins = len(subset[subset['outcome'] == 'WIN'])
    losses = len(subset[subset['outcome'] == 'LOSE'])
    draws = len(subset[subset['outcome'] == 'DRAW'])
    
    win_rate = wins / total * 100 if total > 0 else 0
    lose_rate = losses / total * 100 if total > 0 else 0
    draw_rate = draws / total * 100 if total > 0 else 0
    
    print(f"{min_margin}+ sequences{'':<3} | {total:>6} | {wins:>3} ({win_rate:>5.1f}%) | {losses:>3} ({lose_rate:>5.1f}%) | {draws:>3} ({draw_rate:>5.1f}%)")

print("-" * 70)

print("\n" + "=" * 70)
print("KEY FINDING: Does margin improve prediction?")
print("=" * 70)

baseline = sequence_df[(sequence_df['more_seq_winner'] != 'tie')]
base_win = len(baseline[baseline['outcome'] == 'WIN']) / len(baseline) * 100
base_lose = len(baseline[baseline['outcome'] == 'LOSE']) / len(baseline) * 100

print(f"\nBaseline (all games): WIN {base_win:.1f}%, LOSE {base_lose:.1f}%")

for min_margin in [2, 3, 4, 5, 6]:
    subset = sequence_df[(sequence_df['num_seq_margin'] >= min_margin) & (sequence_df['more_seq_winner'] != 'tie')]
    total = len(subset)
    if total < 3:
        continue
    
    wins = len(subset[subset['outcome'] == 'WIN'])
    losses = len(subset[subset['outcome'] == 'LOSE'])
    
    win_rate = wins / total * 100
    lose_rate = losses / total * 100
    
    win_diff = win_rate - base_win
    lose_diff = lose_rate - base_lose
    
    print(f"{min_margin}+ margin ({total} games): WIN {win_rate:.1f}% ({win_diff:+.1f}), LOSE {lose_rate:.1f}% ({lose_diff:+.1f})")

