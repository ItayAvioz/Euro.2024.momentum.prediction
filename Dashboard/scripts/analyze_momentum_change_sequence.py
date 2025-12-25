"""
Analyze: Does winning more MOMENTUM CHANGE SEQUENCES correlate with winning the match?

A sequence = consecutive windows where team has POSITIVE momentum change
E.g., +, +, +, -, + = one sequence of 3, then one sequence of 1

For each game:
1. Count sequences of consecutive positive momentum changes
2. Find longest sequence per team
3. Compare to actual match result
"""

import pandas as pd
import numpy as np

print("=" * 70)
print("MOMENTUM CHANGE SEQUENCE vs MATCH RESULT ANALYSIS")
print("=" * 70)

# Load momentum data
momentum_df = pd.read_csv('../models/preprocessing/data/targets/momentum_targets_streamlined.csv')

print(f"\nLoaded {len(momentum_df):,} momentum windows")
print(f"Games: {momentum_df['match_id'].nunique()}")

# Load match results
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

def count_sequences(changes):
    """Count sequences of consecutive positive changes and find longest"""
    sequences = []
    current_seq = 0
    
    for change in changes:
        if change > 0:
            current_seq += 1
        else:
            if current_seq > 0:
                sequences.append(current_seq)
            current_seq = 0
    
    # Don't forget the last sequence
    if current_seq > 0:
        sequences.append(current_seq)
    
    return {
        'num_sequences': len(sequences),
        'longest_sequence': max(sequences) if sequences else 0,
        'total_in_sequences': sum(sequences),
        'avg_sequence_length': np.mean(sequences) if sequences else 0,
        'sequences': sequences
    }

# Analyze momentum change sequences per game
analysis_results = []

for match_id in momentum_df['match_id'].unique():
    match_momentum = momentum_df[momentum_df['match_id'] == match_id].sort_values('minute_range')
    
    if match_id not in match_results:
        continue
    
    result = match_results[match_id]
    
    # Get sequences for each team
    home_changes = match_momentum['team_home_momentum_change'].values
    away_changes = match_momentum['team_away_momentum_change'].values
    
    home_seq = count_sequences(home_changes)
    away_seq = count_sequences(away_changes)
    
    total_windows = len(match_momentum)
    
    # Determine who had longer LONGEST sequence
    if home_seq['longest_sequence'] > away_seq['longest_sequence']:
        longest_winner = 'home'
    elif away_seq['longest_sequence'] > home_seq['longest_sequence']:
        longest_winner = 'away'
    else:
        longest_winner = 'tie'
    
    # Determine who had more sequences
    if home_seq['num_sequences'] > away_seq['num_sequences']:
        more_seq_winner = 'home'
    elif away_seq['num_sequences'] > home_seq['num_sequences']:
        more_seq_winner = 'away'
    else:
        more_seq_winner = 'tie'
    
    # Calculate margin for longest sequence
    longest_margin = abs(home_seq['longest_sequence'] - away_seq['longest_sequence'])
    
    analysis_results.append({
        'match_id': match_id,
        'home_team': result['home_team'],
        'away_team': result['away_team'],
        'home_score': result['home_score'],
        'away_score': result['away_score'],
        'match_result': result['result'],
        'home_num_sequences': home_seq['num_sequences'],
        'away_num_sequences': away_seq['num_sequences'],
        'home_longest_seq': home_seq['longest_sequence'],
        'away_longest_seq': away_seq['longest_sequence'],
        'home_avg_seq_len': home_seq['avg_sequence_length'],
        'away_avg_seq_len': away_seq['avg_sequence_length'],
        'total_windows': total_windows,
        'longest_winner': longest_winner,
        'more_seq_winner': more_seq_winner,
        'longest_margin': longest_margin
    })

results_df = pd.DataFrame(analysis_results)

print("\n" + "=" * 70)
print("OVERALL STATISTICS")
print("=" * 70)

print(f"\nTotal games analyzed: {len(results_df)}")
print(f"\nAverage LONGEST sequence (home): {results_df['home_longest_seq'].mean():.1f} windows")
print(f"Average LONGEST sequence (away): {results_df['away_longest_seq'].mean():.1f} windows")
print(f"\nAverage NUMBER of sequences (home): {results_df['home_num_sequences'].mean():.1f}")
print(f"Average NUMBER of sequences (away): {results_df['away_num_sequences'].mean():.1f}")

# Determine outcome for longest sequence winner
def get_outcome(row, winner_col):
    winner = row[winner_col]
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

results_df['longest_outcome'] = results_df.apply(lambda r: get_outcome(r, 'longest_winner'), axis=1)
results_df['more_seq_outcome'] = results_df.apply(lambda r: get_outcome(r, 'more_seq_winner'), axis=1)

print("\n" + "=" * 70)
print("ANALYSIS 1: LONGEST POSITIVE SEQUENCE vs MATCH RESULT")
print("=" * 70)

# Filter out ties
longest_df = results_df[results_df['longest_winner'] != 'tie']
total_longest = len(longest_df)
longest_wins = len(longest_df[longest_df['longest_outcome'] == 'WIN'])
longest_loses = len(longest_df[longest_df['longest_outcome'] == 'LOSE'])
longest_draws = len(longest_df[longest_df['longest_outcome'] == 'DRAW'])
longest_ties = len(results_df[results_df['longest_winner'] == 'tie'])

print(f"\n>>> When TEAM A has the LONGEST positive momentum sequence:")
print(f"    Team A WON the match:    {longest_wins} games")
print(f"    Team A LOST the match:   {longest_loses} games")
print(f"    Match was DRAW:          {longest_draws} games")
print(f"    Longest sequence TIED:   {longest_ties} games (excluded)")

print(f"\n    TOTAL games with sequence winner: {total_longest}")

if total_longest > 0:
    print(f"\n    WIN rate:  {longest_wins}/{total_longest} = {longest_wins/total_longest*100:.1f}%")
    print(f"    LOSE rate: {longest_loses}/{total_longest} = {longest_loses/total_longest*100:.1f}%")
    print(f"    DRAW rate: {longest_draws}/{total_longest} = {longest_draws/total_longest*100:.1f}%")

print("\n" + "=" * 70)
print("MARGIN ANALYSIS: LONGEST SEQUENCE MARGIN")
print("=" * 70)

print("\n" + "-" * 70)
print(f"{'Min Margin':<15} | {'Games':>6} | {'WIN':>12} | {'LOSE':>12} | {'DRAW':>12}")
print("-" * 70)

for min_margin in [0, 1, 2, 3, 4, 5]:
    subset = results_df[(results_df['longest_margin'] >= min_margin) & (results_df['longest_winner'] != 'tie')]
    
    total = len(subset)
    wins = len(subset[subset['longest_outcome'] == 'WIN'])
    losses = len(subset[subset['longest_outcome'] == 'LOSE'])
    draws = len(subset[subset['longest_outcome'] == 'DRAW'])
    
    win_rate = wins / total * 100 if total > 0 else 0
    lose_rate = losses / total * 100 if total > 0 else 0
    draw_rate = draws / total * 100 if total > 0 else 0
    
    print(f"{min_margin}+ windows{'':<5} | {total:>6} | {wins:>3} ({win_rate:>5.1f}%) | {losses:>3} ({lose_rate:>5.1f}%) | {draws:>3} ({draw_rate:>5.1f}%)")

print("-" * 70)

print("\n" + "=" * 70)
print("ANALYSIS 2: NUMBER OF SEQUENCES vs MATCH RESULT")
print("=" * 70)

# Filter out ties
more_seq_df = results_df[results_df['more_seq_winner'] != 'tie']
total_more = len(more_seq_df)
more_wins = len(more_seq_df[more_seq_df['more_seq_outcome'] == 'WIN'])
more_loses = len(more_seq_df[more_seq_df['more_seq_outcome'] == 'LOSE'])
more_draws = len(more_seq_df[more_seq_df['more_seq_outcome'] == 'DRAW'])
more_ties = len(results_df[results_df['more_seq_winner'] == 'tie'])

print(f"\n>>> When TEAM A has MORE positive momentum sequences:")
print(f"    Team A WON the match:    {more_wins} games")
print(f"    Team A LOST the match:   {more_loses} games")
print(f"    Match was DRAW:          {more_draws} games")
print(f"    Number of sequences TIED: {more_ties} games (excluded)")

print(f"\n    TOTAL games with more sequences: {total_more}")

if total_more > 0:
    print(f"\n    WIN rate:  {more_wins}/{total_more} = {more_wins/total_more*100:.1f}%")
    print(f"    LOSE rate: {more_loses}/{total_more} = {more_loses/total_more*100:.1f}%")
    print(f"    DRAW rate: {more_draws}/{total_more} = {more_draws/total_more*100:.1f}%")

print("\n" + "=" * 70)
print("KEY FINDING: LOSE RATE BY LONGEST SEQUENCE MARGIN")
print("=" * 70)

print("\nAs longest sequence margin increases:")
print()

for min_margin in [0, 1, 2, 3, 4, 5]:
    subset = results_df[(results_df['longest_margin'] >= min_margin) & (results_df['longest_winner'] != 'tie')]
    total = len(subset)
    losses = len(subset[subset['longest_outcome'] == 'LOSE'])
    lose_rate = losses / total * 100 if total > 0 else 0
    
    bar = "█" * int(lose_rate / 2) + "░" * (25 - int(lose_rate / 2))
    print(f"  {min_margin}+ windows: {bar} {lose_rate:>5.1f}% lose ({losses}/{total} games)")

print("\n" + "=" * 70)
print("EXAMPLE GAMES")
print("=" * 70)

# Sort by longest sequence margin to show best examples
results_df_sorted = results_df.sort_values('longest_margin', ascending=False)

print("\n>>> Games with LARGE longest sequence difference:")
for _, row in results_df_sorted.head(5).iterrows():
    winner = row['home_team'] if row['longest_winner'] == 'home' else (row['away_team'] if row['longest_winner'] == 'away' else 'TIE')
    print(f"  {row['home_team']} {row['home_score']}-{row['away_score']} {row['away_team']}")
    print(f"    Longest seq: {row['home_team']} {row['home_longest_seq']} - {row['away_longest_seq']} {row['away_team']} → {row['longest_outcome']}")

print("\n>>> Games where longest sequence winner WON match:")
won_games = results_df[results_df['longest_outcome'] == 'WIN'].sort_values('longest_margin', ascending=False).head(5)
for _, row in won_games.iterrows():
    print(f"  {row['home_team']} {row['home_score']}-{row['away_score']} {row['away_team']}")
    print(f"    Longest seq: {row['home_team']} {row['home_longest_seq']} - {row['away_longest_seq']} {row['away_team']}")

print("\n>>> Games where longest sequence winner LOST match:")
lost_games = results_df[results_df['longest_outcome'] == 'LOSE'].sort_values('longest_margin', ascending=False).head(5)
for _, row in lost_games.iterrows():
    winner = row['home_team'] if row['longest_winner'] == 'home' else row['away_team']
    print(f"  {row['home_team']} {row['home_score']}-{row['away_score']} {row['away_team']}")
    print(f"    Longest seq: {row['home_team']} {row['home_longest_seq']} - {row['away_longest_seq']} {row['away_team']} → {winner} LOST!")

# Save results
results_df.to_csv('momentum_sequence_vs_result_analysis.csv', index=False)
print(f"\n✅ Detailed results saved to: momentum_sequence_vs_result_analysis.csv")

