"""
Analyze: Does winning more MOMENTUM CHANGE windows correlate with winning the match?

For each game:
1. Count 3-minute windows where Team A has POSITIVE momentum change
2. Compare to actual match result
3. Present statistics
"""

import pandas as pd
import numpy as np

print("=" * 70)
print("MOMENTUM CHANGE WINDOWS vs MATCH RESULT ANALYSIS")
print("=" * 70)

# Load momentum data
momentum_df = pd.read_csv('../models/preprocessing/data/targets/momentum_targets_streamlined.csv')

print(f"\nLoaded {len(momentum_df):,} momentum windows")
print(f"Games: {momentum_df['match_id'].nunique()}")

# Load match results to get final scores
events_df = pd.read_csv('../Data/euro_2024_complete_dataset.csv', low_memory=False)

# Get final scores for each match
match_results = {}
for match_id in momentum_df['match_id'].unique():
    match_events = events_df[events_df['match_id'] == match_id]
    if len(match_events) > 0:
        last_event = match_events.iloc[-1]
        home_score = last_event['home_score'] if pd.notna(last_event['home_score']) else 0
        away_score = last_event['away_score'] if pd.notna(last_event['away_score']) else 0
        
        home_team = momentum_df[momentum_df['match_id'] == match_id]['team_home'].iloc[0]
        away_team = momentum_df[momentum_df['match_id'] == match_id]['team_away'].iloc[0]
        
        match_results[match_id] = {
            'home_team': home_team,
            'away_team': away_team,
            'home_score': int(home_score),
            'away_score': int(away_score),
            'result': 'home_win' if home_score > away_score else ('away_win' if away_score > home_score else 'draw')
        }

print(f"Match results loaded: {len(match_results)} games")

# Analyze momentum CHANGE windows per game
analysis_results = []

for match_id in momentum_df['match_id'].unique():
    match_momentum = momentum_df[momentum_df['match_id'] == match_id]
    
    if match_id not in match_results:
        continue
    
    result = match_results[match_id]
    
    # Count POSITIVE momentum change windows for each team
    home_positive = 0
    home_negative = 0
    away_positive = 0
    away_negative = 0
    
    for _, row in match_momentum.iterrows():
        home_change = row['team_home_momentum_change']
        away_change = row['team_away_momentum_change']
        
        if home_change > 0:
            home_positive += 1
        elif home_change < 0:
            home_negative += 1
            
        if away_change > 0:
            away_positive += 1
        elif away_change < 0:
            away_negative += 1
    
    total_windows = len(match_momentum)
    
    # Determine who had more POSITIVE momentum change windows
    if home_positive > away_positive:
        change_winner = 'home'
    elif away_positive > home_positive:
        change_winner = 'away'
    else:
        change_winner = 'tie'
    
    # Calculate margins
    change_margin = abs(home_positive - away_positive)
    change_margin_pct = change_margin / total_windows * 100 if total_windows > 0 else 0
    
    analysis_results.append({
        'match_id': match_id,
        'home_team': result['home_team'],
        'away_team': result['away_team'],
        'home_score': result['home_score'],
        'away_score': result['away_score'],
        'match_result': result['result'],
        'home_positive_changes': home_positive,
        'home_negative_changes': home_negative,
        'away_positive_changes': away_positive,
        'away_negative_changes': away_negative,
        'total_windows': total_windows,
        'change_winner': change_winner,
        'change_margin': change_margin,
        'change_margin_pct': change_margin_pct,
        'home_positive_pct': home_positive / total_windows * 100 if total_windows > 0 else 0,
        'away_positive_pct': away_positive / total_windows * 100 if total_windows > 0 else 0
    })

results_df = pd.DataFrame(analysis_results)

print("\n" + "=" * 70)
print("OVERALL STATISTICS")
print("=" * 70)

print(f"\nTotal games analyzed: {len(results_df)}")
print(f"Average windows per game: {results_df['total_windows'].mean():.1f}")
print(f"Average positive changes (home): {results_df['home_positive_changes'].mean():.1f}")
print(f"Average positive changes (away): {results_df['away_positive_changes'].mean():.1f}")

# Determine outcome for change winner
def get_outcome_for_change_winner(row):
    if row['change_winner'] == 'home':
        if row['match_result'] == 'home_win':
            return 'WIN'
        elif row['match_result'] == 'away_win':
            return 'LOSE'
        else:
            return 'DRAW'
    elif row['change_winner'] == 'away':
        if row['match_result'] == 'away_win':
            return 'WIN'
        elif row['match_result'] == 'home_win':
            return 'LOSE'
        else:
            return 'DRAW'
    else:
        return 'TIE_CHANGE'

results_df['change_winner_outcome'] = results_df.apply(get_outcome_for_change_winner, axis=1)

# Count cases
total_with_winner = len(results_df[results_df['change_winner'] != 'tie'])
change_wins = len(results_df[results_df['change_winner_outcome'] == 'WIN'])
change_loses = len(results_df[results_df['change_winner_outcome'] == 'LOSE'])
change_draws = len(results_df[results_df['change_winner_outcome'] == 'DRAW'])
change_ties = len(results_df[results_df['change_winner_outcome'] == 'TIE_CHANGE'])

print("\n" + "-" * 50)
print("CORRELATION: Momentum CHANGE Winner vs Match Winner")
print("-" * 50)

print(f"\n>>> When TEAM A has MORE positive momentum change windows:")
print(f"    Team A WON the match:    {change_wins} games")
print(f"    Team A LOST the match:   {change_loses} games")
print(f"    Match was DRAW:          {change_draws} games")
print(f"    Momentum change was TIED: {change_ties} games")

print(f"\n    TOTAL games with change winner: {total_with_winner}")

if total_with_winner > 0:
    print(f"\n    WIN rate:  {change_wins}/{total_with_winner} = {change_wins/total_with_winner*100:.1f}%")
    print(f"    LOSE rate: {change_loses}/{total_with_winner} = {change_loses/total_with_winner*100:.1f}%")
    print(f"    DRAW rate: {change_draws}/{total_with_winner} = {change_draws/total_with_winner*100:.1f}%")

print("\n" + "=" * 70)
print("MARGIN ANALYSIS: WIN/LOSE/DRAW BY MOMENTUM CHANGE MARGIN")
print("=" * 70)

# Cumulative margin analysis
print("\n" + "-" * 70)
print(f"{'Min Margin':<12} | {'Games':>6} | {'WIN':>12} | {'LOSE':>12} | {'DRAW':>12}")
print("-" * 70)

for min_margin in [0, 5, 10, 15, 20, 25]:
    subset = results_df[(results_df['change_margin_pct'] >= min_margin) & (results_df['change_winner'] != 'tie')]
    
    total = len(subset)
    wins = len(subset[subset['change_winner_outcome'] == 'WIN'])
    losses = len(subset[subset['change_winner_outcome'] == 'LOSE'])
    draws = len(subset[subset['change_winner_outcome'] == 'DRAW'])
    
    win_rate = wins / total * 100 if total > 0 else 0
    lose_rate = losses / total * 100 if total > 0 else 0
    draw_rate = draws / total * 100 if total > 0 else 0
    
    print(f"{min_margin}%+{'':<9} | {total:>6} | {wins:>3} ({win_rate:>5.1f}%) | {losses:>3} ({lose_rate:>5.1f}%) | {draws:>3} ({draw_rate:>5.1f}%)")

print("-" * 70)

print("\n" + "=" * 70)
print("KEY FINDING: LOSE RATE BY MARGIN")
print("=" * 70)

print("\nAs momentum CHANGE margin increases, LOSE rate:")
print()

for min_margin in [0, 5, 10, 15, 20, 25]:
    subset = results_df[(results_df['change_margin_pct'] >= min_margin) & (results_df['change_winner'] != 'tie')]
    total = len(subset)
    losses = len(subset[subset['change_winner_outcome'] == 'LOSE'])
    lose_rate = losses / total * 100 if total > 0 else 0
    
    bar = "█" * int(lose_rate / 2) + "░" * (25 - int(lose_rate / 2))
    print(f"  {min_margin:>2}%+ margin: {bar} {lose_rate:>5.1f}% lose ({losses}/{total} games)")

print("\n" + "=" * 70)
print("EXAMPLE GAMES")
print("=" * 70)

# Show some examples
print("\n>>> Games where momentum CHANGE winner WON the match:")
won_games = results_df[results_df['change_winner_outcome'] == 'WIN'].head(5)
for _, row in won_games.iterrows():
    winner = row['home_team'] if row['change_winner'] == 'home' else row['away_team']
    print(f"  {row['home_team']} {row['home_score']}-{row['away_score']} {row['away_team']}")
    print(f"    Positive changes: {row['home_team']} {row['home_positive_changes']} - {row['away_positive_changes']} {row['away_team']}")

print("\n>>> Games where momentum CHANGE winner LOST the match:")
lost_games = results_df[results_df['change_winner_outcome'] == 'LOSE'].head(5)
for _, row in lost_games.iterrows():
    winner = row['home_team'] if row['change_winner'] == 'home' else row['away_team']
    print(f"  {row['home_team']} {row['home_score']}-{row['away_score']} {row['away_team']}")
    print(f"    Positive changes: {row['home_team']} {row['home_positive_changes']} - {row['away_positive_changes']} {row['away_team']} → {winner} had MORE but LOST!")

# Save results
results_df.to_csv('momentum_change_vs_result_analysis.csv', index=False)
print(f"\n✅ Detailed results saved to: momentum_change_vs_result_analysis.csv")

