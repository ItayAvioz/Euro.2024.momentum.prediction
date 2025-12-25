"""
Analyze: How does momentum window margin affect match outcome?
Check win/lose/draw rates for 5%, 10%, 15%, 20%+ momentum advantages
"""

import pandas as pd
import numpy as np

print("=" * 70)
print("MOMENTUM MARGIN vs MATCH RESULT ANALYSIS")
print("=" * 70)

# Load the analysis results from previous script
results_df = pd.read_csv('momentum_vs_result_analysis.csv')

print(f"\nLoaded {len(results_df)} games")

# Calculate momentum margin (difference in win percentage)
results_df['momentum_margin'] = abs(results_df['momentum_win_pct_home'] - results_df['momentum_win_pct_away'])

# For each game, determine if momentum winner won/lost/drew
def get_outcome_for_momentum_winner(row):
    if row['momentum_winner'] == 'home':
        if row['match_result'] == 'home_win':
            return 'WIN'
        elif row['match_result'] == 'away_win':
            return 'LOSE'
        else:
            return 'DRAW'
    elif row['momentum_winner'] == 'away':
        if row['match_result'] == 'away_win':
            return 'WIN'
        elif row['match_result'] == 'home_win':
            return 'LOSE'
        else:
            return 'DRAW'
    else:
        return 'TIE_MOMENTUM'

results_df['momentum_winner_outcome'] = results_df.apply(get_outcome_for_momentum_winner, axis=1)

print("\n" + "=" * 70)
print("MOMENTUM MARGIN DISTRIBUTION")
print("=" * 70)

print(f"\nMomentum margin statistics:")
print(f"  Min: {results_df['momentum_margin'].min():.1f}%")
print(f"  Max: {results_df['momentum_margin'].max():.1f}%")
print(f"  Mean: {results_df['momentum_margin'].mean():.1f}%")
print(f"  Median: {results_df['momentum_margin'].median():.1f}%")

print("\n" + "=" * 70)
print("WIN/LOSE/DRAW RATES BY MOMENTUM MARGIN")
print("=" * 70)

# Define margin thresholds
thresholds = [
    (0, 5, "0-5%"),
    (5, 10, "5-10%"),
    (10, 15, "10-15%"),
    (15, 20, "15-20%"),
    (20, 100, "20%+")
]

print("\n" + "-" * 70)
print(f"{'Margin':<12} | {'Games':>6} | {'WIN':>8} | {'LOSE':>8} | {'DRAW':>8} | {'Win Rate':>10}")
print("-" * 70)

for min_m, max_m, label in thresholds:
    subset = results_df[(results_df['momentum_margin'] >= min_m) & (results_df['momentum_margin'] < max_m)]
    
    total = len(subset)
    wins = len(subset[subset['momentum_winner_outcome'] == 'WIN'])
    losses = len(subset[subset['momentum_winner_outcome'] == 'LOSE'])
    draws = len(subset[subset['momentum_winner_outcome'] == 'DRAW'])
    
    win_rate = wins / total * 100 if total > 0 else 0
    lose_rate = losses / total * 100 if total > 0 else 0
    draw_rate = draws / total * 100 if total > 0 else 0
    
    print(f"{label:<12} | {total:>6} | {wins:>3} ({win_rate:>4.1f}%) | {losses:>3} ({lose_rate:>4.1f}%) | {draws:>3} ({draw_rate:>4.1f}%) | {win_rate:>8.1f}%")

print("-" * 70)

# Also check cumulative: 5+, 10+, 15+, 20+
print("\n" + "=" * 70)
print("CUMULATIVE: WIN RATE BY MINIMUM MARGIN")
print("=" * 70)

cumulative_thresholds = [5, 10, 15, 20, 25, 30]

print("\n" + "-" * 70)
print(f"{'Min Margin':<12} | {'Games':>6} | {'WIN':>8} | {'LOSE':>8} | {'DRAW':>8} | {'Win Rate':>10}")
print("-" * 70)

for min_margin in cumulative_thresholds:
    subset = results_df[results_df['momentum_margin'] >= min_margin]
    
    total = len(subset)
    wins = len(subset[subset['momentum_winner_outcome'] == 'WIN'])
    losses = len(subset[subset['momentum_winner_outcome'] == 'LOSE'])
    draws = len(subset[subset['momentum_winner_outcome'] == 'DRAW'])
    
    win_rate = wins / total * 100 if total > 0 else 0
    lose_rate = losses / total * 100 if total > 0 else 0
    draw_rate = draws / total * 100 if total > 0 else 0
    
    print(f"{min_margin}%+{'':<9} | {total:>6} | {wins:>3} ({win_rate:>4.1f}%) | {losses:>3} ({lose_rate:>4.1f}%) | {draws:>3} ({draw_rate:>4.1f}%) | {win_rate:>8.1f}%")

print("-" * 70)

print("\n" + "=" * 70)
print("KEY FINDING: LOSE RATE BY MARGIN")
print("=" * 70)

print("\nAs momentum margin increases, LOSE rate decreases:")
print()

for min_margin in [0, 5, 10, 15, 20, 25, 30]:
    subset = results_df[results_df['momentum_margin'] >= min_margin]
    total = len(subset)
    losses = len(subset[subset['momentum_winner_outcome'] == 'LOSE'])
    lose_rate = losses / total * 100 if total > 0 else 0
    
    bar = "█" * int(lose_rate / 2) + "░" * (25 - int(lose_rate / 2))
    print(f"  {min_margin:>2}%+ margin: {bar} {lose_rate:>5.1f}% lose ({losses}/{total} games)")

print("\n" + "=" * 70)
print("EXAMPLE GAMES BY MARGIN CATEGORY")
print("=" * 70)

for min_m, max_m, label in thresholds:
    subset = results_df[(results_df['momentum_margin'] >= min_m) & (results_df['momentum_margin'] < max_m)]
    if len(subset) > 0:
        print(f"\n>>> {label} margin games:")
        for _, row in subset.head(3).iterrows():
            mom_winner = row['home_team'] if row['momentum_winner'] == 'home' else row['away_team']
            print(f"  {row['home_team']} {row['home_score']}-{row['away_score']} {row['away_team']}")
            print(f"    Momentum: {row['home_momentum_wins']}-{row['away_momentum_wins']} ({row['momentum_margin']:.1f}% margin) → {row['momentum_winner_outcome']}")

# Save detailed results
results_df.to_csv('momentum_margin_analysis.csv', index=False)
print(f"\n✅ Detailed results saved to: momentum_margin_analysis.csv")

