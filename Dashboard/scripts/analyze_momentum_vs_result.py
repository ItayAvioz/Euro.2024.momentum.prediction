"""
Analyze: Does winning more momentum windows correlate with winning the match?

For each game:
1. Count 3-minute windows where Team A has higher momentum than Team B
2. Compare to actual match result
3. Present statistics
"""

import pandas as pd
import numpy as np

print("=" * 70)
print("MOMENTUM WINDOWS vs MATCH RESULT ANALYSIS")
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
        # Get last event scores (final result)
        last_event = match_events.iloc[-1]
        home_score = last_event['home_score'] if pd.notna(last_event['home_score']) else 0
        away_score = last_event['away_score'] if pd.notna(last_event['away_score']) else 0
        
        # Get team names
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

# Analyze momentum windows per game
analysis_results = []

for match_id in momentum_df['match_id'].unique():
    match_momentum = momentum_df[momentum_df['match_id'] == match_id]
    
    if match_id not in match_results:
        continue
    
    result = match_results[match_id]
    
    # Count windows won by each team
    home_wins = 0
    away_wins = 0
    ties = 0
    
    for _, row in match_momentum.iterrows():
        home_mom = row['team_home_momentum']
        away_mom = row['team_away_momentum']
        
        if home_mom > away_mom:
            home_wins += 1
        elif away_mom > home_mom:
            away_wins += 1
        else:
            ties += 1
    
    total_windows = home_wins + away_wins + ties
    
    # Determine who won more momentum windows
    if home_wins > away_wins:
        momentum_winner = 'home'
    elif away_wins > home_wins:
        momentum_winner = 'away'
    else:
        momentum_winner = 'tie'
    
    # Compare to match result
    match_winner = result['result'].replace('_win', '')
    
    analysis_results.append({
        'match_id': match_id,
        'home_team': result['home_team'],
        'away_team': result['away_team'],
        'home_score': result['home_score'],
        'away_score': result['away_score'],
        'match_result': result['result'],
        'home_momentum_wins': home_wins,
        'away_momentum_wins': away_wins,
        'momentum_ties': ties,
        'total_windows': total_windows,
        'momentum_winner': momentum_winner,
        'momentum_win_pct_home': home_wins / total_windows * 100 if total_windows > 0 else 0,
        'momentum_win_pct_away': away_wins / total_windows * 100 if total_windows > 0 else 0,
        'momentum_matches_result': (momentum_winner == match_winner) or 
                                   (momentum_winner == 'home' and result['result'] == 'home_win') or
                                   (momentum_winner == 'away' and result['result'] == 'away_win')
    })

results_df = pd.DataFrame(analysis_results)

print("\n" + "=" * 70)
print("OVERALL STATISTICS")
print("=" * 70)

print(f"\nTotal games analyzed: {len(results_df)}")
print(f"Average windows per game: {results_df['total_windows'].mean():.1f}")

# Stats: Does momentum winner = match winner?
print("\n" + "-" * 50)
print("CORRELATION: Momentum Winner vs Match Winner")
print("-" * 50)

# Count cases
momentum_home_match_home = len(results_df[(results_df['momentum_winner'] == 'home') & (results_df['match_result'] == 'home_win')])
momentum_home_match_away = len(results_df[(results_df['momentum_winner'] == 'home') & (results_df['match_result'] == 'away_win')])
momentum_home_match_draw = len(results_df[(results_df['momentum_winner'] == 'home') & (results_df['match_result'] == 'draw')])

momentum_away_match_home = len(results_df[(results_df['momentum_winner'] == 'away') & (results_df['match_result'] == 'home_win')])
momentum_away_match_away = len(results_df[(results_df['momentum_winner'] == 'away') & (results_df['match_result'] == 'away_win')])
momentum_away_match_draw = len(results_df[(results_df['momentum_winner'] == 'away') & (results_df['match_result'] == 'draw')])

momentum_tie_match_home = len(results_df[(results_df['momentum_winner'] == 'tie') & (results_df['match_result'] == 'home_win')])
momentum_tie_match_away = len(results_df[(results_df['momentum_winner'] == 'tie') & (results_df['match_result'] == 'away_win')])
momentum_tie_match_draw = len(results_df[(results_df['momentum_winner'] == 'tie') & (results_df['match_result'] == 'draw')])

total_momentum_home = momentum_home_match_home + momentum_home_match_away + momentum_home_match_draw
total_momentum_away = momentum_away_match_home + momentum_away_match_away + momentum_away_match_draw
total_momentum_tie = momentum_tie_match_home + momentum_tie_match_away + momentum_tie_match_draw

print("\n>>> When TEAM A wins MORE momentum windows:")
print(f"    Team A WON the match:    {momentum_home_match_home + momentum_away_match_away} games")
print(f"    Team A LOST the match:   {momentum_home_match_away + momentum_away_match_home} games")
print(f"    Match was DRAW:          {momentum_home_match_draw + momentum_away_match_draw} games")

total_momentum_winner = total_momentum_home + total_momentum_away
team_a_won = momentum_home_match_home + momentum_away_match_away
team_a_lost = momentum_home_match_away + momentum_away_match_home
team_a_draw = momentum_home_match_draw + momentum_away_match_draw

print(f"\n    TOTAL games with momentum winner: {total_momentum_winner}")

if total_momentum_winner > 0:
    print(f"\n    WIN rate:  {team_a_won}/{total_momentum_winner} = {team_a_won/total_momentum_winner*100:.1f}%")
    print(f"    LOSE rate: {team_a_lost}/{total_momentum_winner} = {team_a_lost/total_momentum_winner*100:.1f}%")
    print(f"    DRAW rate: {team_a_draw}/{total_momentum_winner} = {team_a_draw/total_momentum_winner*100:.1f}%")

print("\n>>> When momentum is TIED (same windows won):")
print(f"    Home WON:   {momentum_tie_match_home} games")
print(f"    Away WON:   {momentum_tie_match_away} games")
print(f"    DRAW:       {momentum_tie_match_draw} games")
print(f"    TOTAL:      {total_momentum_tie} games")

print("\n" + "=" * 70)
print("DETAILED BREAKDOWN")
print("=" * 70)

print("\nContingency Table:")
print("                          MATCH RESULT")
print("                    Win      Lose     Draw     TOTAL")
print("            +------------------------------------------")
print(f"MOMENTUM    Home   | {momentum_home_match_home:>4}     {momentum_home_match_away:>4}     {momentum_home_match_draw:>4}     {total_momentum_home:>4}")
print(f"WINNER      Away   | {momentum_away_match_home:>4}     {momentum_away_match_away:>4}     {momentum_away_match_draw:>4}     {total_momentum_away:>4}")
print(f"            Tie    | {momentum_tie_match_home:>4}     {momentum_tie_match_away:>4}     {momentum_tie_match_draw:>4}     {total_momentum_tie:>4}")
print("            +------------------------------------------")
print(f"            TOTAL  | {momentum_home_match_home + momentum_away_match_home + momentum_tie_match_home:>4}     {momentum_home_match_away + momentum_away_match_away + momentum_tie_match_away:>4}     {momentum_home_match_draw + momentum_away_match_draw + momentum_tie_match_draw:>4}     {len(results_df):>4}")

print("\n" + "=" * 70)
print("KEY FINDING")
print("=" * 70)

# Calculate the key metric: when a team wins more momentum windows, do they win the match?
correct_predictions = team_a_won
total_non_tie = total_momentum_winner
accuracy = correct_predictions / total_non_tie * 100 if total_non_tie > 0 else 0

print(f"\nWhen a team wins MORE momentum windows than opponent:")
print(f"  → They WIN the match: {correct_predictions}/{total_non_tie} = {accuracy:.1f}%")
print(f"  → They LOSE the match: {team_a_lost}/{total_non_tie} = {team_a_lost/total_non_tie*100:.1f}%")
print(f"  → Match is DRAW: {team_a_draw}/{total_non_tie} = {team_a_draw/total_non_tie*100:.1f}%")

print("\n" + "=" * 70)
print("SAMPLE GAMES")
print("=" * 70)

# Show some examples
print("\n>>> Games where momentum winner WON the match:")
won_games = results_df[results_df['momentum_matches_result'] == True].head(5)
for _, row in won_games.iterrows():
    print(f"  {row['home_team']} {row['home_score']}-{row['away_score']} {row['away_team']}")
    print(f"    Momentum: {row['home_team']} {row['home_momentum_wins']} - {row['away_momentum_wins']} {row['away_team']}")

print("\n>>> Games where momentum winner LOST the match:")
lost_games = results_df[(results_df['momentum_matches_result'] == False) & (results_df['momentum_winner'] != 'tie')].head(5)
for _, row in lost_games.iterrows():
    winner = row['home_team'] if row['momentum_winner'] == 'home' else row['away_team']
    print(f"  {row['home_team']} {row['home_score']}-{row['away_score']} {row['away_team']}")
    print(f"    Momentum winner: {winner} ({row['home_momentum_wins']}-{row['away_momentum_wins']}) but LOST!")

# Save results
results_df.to_csv('momentum_vs_result_analysis.csv', index=False)
print(f"\n✅ Detailed results saved to: momentum_vs_result_analysis.csv")

