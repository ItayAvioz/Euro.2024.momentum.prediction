import pandas as pd
import numpy as np

print("=== EVENTS RATIO vs SCORE REFLECTION ANALYSIS ===")
print("(Ignoring Home/Away - Euro 2024 was all in Germany)")

# Load the data
matches = pd.read_csv('../Data/matches_complete.csv')
events = pd.read_csv('../Data/events_complete.csv')

print(f"Total matches: {len(matches)}")
print(f"Total events: {len(events)}")

# Create game-by-game analysis
score_reflection_analysis = []

for _, match in matches.iterrows():
    match_id = match['match_id']
    
    # Get match info (ignoring home/away)
    team_a = match['home_team_name']
    team_b = match['away_team_name']
    stage = match['stage']
    
    # Get scores
    team_a_score = int(match['home_score']) if pd.notna(match['home_score']) else 0
    team_b_score = int(match['away_score']) if pd.notna(match['away_score']) else 0
    
    # Get match events
    match_events = events[events['match_id'] == match_id].copy()
    
    if len(match_events) == 0:
        continue
    
    # Separate by period
    first_half_events = match_events[match_events['period'] == 1]
    second_half_events = match_events[match_events['period'] == 2]
    
    # Count events by team
    fh_team_a_events = len(first_half_events[first_half_events['team_name'] == team_a])
    fh_team_b_events = len(first_half_events[first_half_events['team_name'] == team_b])
    
    sh_team_a_events = len(second_half_events[second_half_events['team_name'] == team_a])
    sh_team_b_events = len(second_half_events[second_half_events['team_name'] == team_b])
    
    # Total game events
    total_team_a_events = fh_team_a_events + sh_team_a_events
    total_team_b_events = fh_team_b_events + sh_team_b_events
    
    # Calculate ratios (avoid division by zero)
    if fh_team_b_events > 0:
        fh_ratio = fh_team_a_events / fh_team_b_events
    else:
        fh_ratio = float('inf') if fh_team_a_events > 0 else 1.0
    
    if sh_team_b_events > 0:
        sh_ratio = sh_team_a_events / sh_team_b_events
    else:
        sh_ratio = float('inf') if sh_team_a_events > 0 else 1.0
    
    if total_team_b_events > 0:
        total_ratio = total_team_a_events / total_team_b_events
    else:
        total_ratio = float('inf') if total_team_a_events > 0 else 1.0
    
    # Determine score outcomes
    if team_a_score > team_b_score:
        score_outcome = f"Team A Won ({team_a_score}-{team_b_score})"
        winning_team = team_a
        score_difference = team_a_score - team_b_score
    elif team_b_score > team_a_score:
        score_outcome = f"Team B Won ({team_a_score}-{team_b_score})"
        winning_team = team_b
        score_difference = team_b_score - team_a_score
    else:
        score_outcome = f"Draw ({team_a_score}-{team_b_score})"
        winning_team = "Draw"
        score_difference = 0
    
    # Check if event ratio reflects score
    # Team A won: expect ratio > 1.0
    # Team B won: expect ratio < 1.0
    # Draw: expect ratio around 1.0
    
    # First Half Reflection
    if team_a_score > team_b_score and fh_ratio > 1.0:
        fh_reflects_score = "YES - Team A had more events and won"
    elif team_b_score > team_a_score and fh_ratio < 1.0:
        fh_reflects_score = "YES - Team B had more events and won"
    elif team_a_score == team_b_score and 0.8 <= fh_ratio <= 1.2:
        fh_reflects_score = "YES - Balanced events for draw"
    else:
        fh_reflects_score = "NO - Events don't match result"
    
    # Second Half Reflection
    if team_a_score > team_b_score and sh_ratio > 1.0:
        sh_reflects_score = "YES - Team A had more events and won"
    elif team_b_score > team_a_score and sh_ratio < 1.0:
        sh_reflects_score = "YES - Team B had more events and won"
    elif team_a_score == team_b_score and 0.8 <= sh_ratio <= 1.2:
        sh_reflects_score = "YES - Balanced events for draw"
    else:
        sh_reflects_score = "NO - Events don't match result"
    
    # Total Game Reflection
    if team_a_score > team_b_score and total_ratio > 1.0:
        total_reflects_score = "YES - Team A had more events and won"
    elif team_b_score > team_a_score and total_ratio < 1.0:
        total_reflects_score = "YES - Team B had more events and won"
    elif team_a_score == team_b_score and 0.8 <= total_ratio <= 1.2:
        total_reflects_score = "YES - Balanced events for draw"
    else:
        total_reflects_score = "NO - Events don't match result"
    
    score_reflection_analysis.append({
        'match_id': match_id,
        'team_a': team_a,
        'team_b': team_b,
        'team_a_score': team_a_score,
        'team_b_score': team_b_score,
        'score_difference': score_difference,
        'winning_team': winning_team,
        'score_outcome': score_outcome,
        'stage': stage,
        'fh_team_a_events': fh_team_a_events,
        'fh_team_b_events': fh_team_b_events,
        'fh_ratio': fh_ratio,
        'fh_reflects_score': fh_reflects_score,
        'sh_team_a_events': sh_team_a_events,
        'sh_team_b_events': sh_team_b_events,
        'sh_ratio': sh_ratio,
        'sh_reflects_score': sh_reflects_score,
        'total_team_a_events': total_team_a_events,
        'total_team_b_events': total_team_b_events,
        'total_ratio': total_ratio,
        'total_reflects_score': total_reflects_score,
        'match_date': match['match_date']
    })

# Convert to DataFrame
reflection_df = pd.DataFrame(score_reflection_analysis)

print(f"\nSuccessfully analyzed {len(reflection_df)} games")

# ===== DISPLAY RESULTS =====
print("\n" + "="*130)
print("EVENTS RATIO vs SCORE REFLECTION ANALYSIS")
print("="*130)
print("Format: Team A vs Team B | Score | Events Ratio | Does Ratio Reflect Score?")
print("-"*130)

for _, game in reflection_df.iterrows():
    print(f"\n{game['team_a']} vs {game['team_b']} | Stage: {game['stage']}")
    print(f"Final Score: {game['team_a_score']}-{game['team_b_score']} ({game['winning_team']} {'won' if game['winning_team'] not in ['Draw'] else 'draw'})")
    
    # Format ratios
    if game['fh_ratio'] == float('inf'):
        fh_ratio_str = f"{game['fh_team_a_events']}/0 (∞)"
    else:
        fh_ratio_str = f"{game['fh_team_a_events']}/{game['fh_team_b_events']} ({game['fh_ratio']:.2f})"
    
    if game['sh_ratio'] == float('inf'):
        sh_ratio_str = f"{game['sh_team_a_events']}/0 (∞)"
    else:
        sh_ratio_str = f"{game['sh_team_a_events']}/{game['sh_team_b_events']} ({game['sh_ratio']:.2f})"
    
    if game['total_ratio'] == float('inf'):
        total_ratio_str = f"{game['total_team_a_events']}/0 (∞)"
    else:
        total_ratio_str = f"{game['total_team_a_events']}/{game['total_team_b_events']} ({game['total_ratio']:.2f})"
    
    print(f"First Half Events: {fh_ratio_str} - {game['fh_reflects_score']}")
    print(f"Second Half Events: {sh_ratio_str} - {game['sh_reflects_score']}")
    print(f"Total Game Events: {total_ratio_str} - {game['total_reflects_score']}")
    print("-"*130)

# ===== REFLECTION STATISTICS =====
print("\n" + "="*100)
print("SCORE REFLECTION STATISTICS")
print("="*100)

# Count matches where events reflect score
fh_reflects_count = len(reflection_df[reflection_df['fh_reflects_score'].str.contains('YES')])
sh_reflects_count = len(reflection_df[reflection_df['sh_reflects_score'].str.contains('YES')])
total_reflects_count = len(reflection_df[reflection_df['total_reflects_score'].str.contains('YES')])

total_games = len(reflection_df)

print(f"FIRST HALF EVENTS REFLECT SCORE:")
print(f"  YES: {fh_reflects_count} games ({(fh_reflects_count/total_games)*100:.1f}%)")
print(f"  NO: {total_games - fh_reflects_count} games ({((total_games - fh_reflects_count)/total_games)*100:.1f}%)")

print(f"\nSECOND HALF EVENTS REFLECT SCORE:")
print(f"  YES: {sh_reflects_count} games ({(sh_reflects_count/total_games)*100:.1f}%)")
print(f"  NO: {total_games - sh_reflects_count} games ({((total_games - sh_reflects_count)/total_games)*100:.1f}%)")

print(f"\nTOTAL GAME EVENTS REFLECT SCORE:")
print(f"  YES: {total_reflects_count} games ({(total_reflects_count/total_games)*100:.1f}%)")
print(f"  NO: {total_games - total_reflects_count} games ({((total_games - total_reflects_count)/total_games)*100:.1f}%)")

# ===== MISMATCH ANALYSIS =====
print(f"\n" + "="*100)
print("EVENTS vs SCORE MISMATCH ANALYSIS")
print("="*100)

# Find games where events don't reflect score
fh_mismatches = reflection_df[reflection_df['fh_reflects_score'].str.contains('NO')]
sh_mismatches = reflection_df[reflection_df['sh_reflects_score'].str.contains('NO')]
total_mismatches = reflection_df[reflection_df['total_reflects_score'].str.contains('NO')]

print(f"FIRST HALF MISMATCHES ({len(fh_mismatches)} games):")
for _, mismatch in fh_mismatches.iterrows():
    ratio_str = f"{mismatch['fh_ratio']:.2f}" if mismatch['fh_ratio'] != float('inf') else "∞"
    print(f"  {mismatch['team_a']} vs {mismatch['team_b']}: Score {mismatch['team_a_score']}-{mismatch['team_b_score']}, Events Ratio {ratio_str}")

print(f"\nSECOND HALF MISMATCHES ({len(sh_mismatches)} games):")
for _, mismatch in sh_mismatches.iterrows():
    ratio_str = f"{mismatch['sh_ratio']:.2f}" if mismatch['sh_ratio'] != float('inf') else "∞"
    print(f"  {mismatch['team_a']} vs {mismatch['team_b']}: Score {mismatch['team_a_score']}-{mismatch['team_b_score']}, Events Ratio {ratio_str}")

print(f"\nTOTAL GAME MISMATCHES ({len(total_mismatches)} games):")
for _, mismatch in total_mismatches.iterrows():
    ratio_str = f"{mismatch['total_ratio']:.2f}" if mismatch['total_ratio'] != float('inf') else "∞"
    print(f"  {mismatch['team_a']} vs {mismatch['team_b']}: Score {mismatch['team_a_score']}-{mismatch['team_b_score']}, Events Ratio {ratio_str}")

# ===== STAGE ANALYSIS =====
print(f"\n" + "="*100)
print("REFLECTION ACCURACY BY STAGE")
print("="*100)

for stage in reflection_df['stage'].unique():
    stage_games = reflection_df[reflection_df['stage'] == stage]
    stage_total_reflects = len(stage_games[stage_games['total_reflects_score'].str.contains('YES')])
    stage_total_games = len(stage_games)
    
    print(f"{stage.upper()}: {stage_total_reflects}/{stage_total_games} games ({(stage_total_reflects/stage_total_games)*100:.1f}%) events reflect score")

# ===== SCORE DIFFERENCE ANALYSIS =====
print(f"\n" + "="*100)
print("REFLECTION ACCURACY BY SCORE DIFFERENCE")
print("="*100)

score_diff_analysis = reflection_df.groupby('score_difference').agg({
    'total_reflects_score': lambda x: len(x[x.str.contains('YES')]),
    'match_id': 'count'
}).rename(columns={'total_reflects_score': 'reflects_count', 'match_id': 'total_count'})

score_diff_analysis['reflection_percentage'] = (score_diff_analysis['reflects_count'] / score_diff_analysis['total_count']) * 100

print("Score Difference | Games | Events Reflect Score | Percentage")
print("-" * 60)
for diff, row in score_diff_analysis.iterrows():
    if diff == 0:
        print(f"Draw (0)         | {row['total_count']:5} | {row['reflects_count']:18} | {row['reflection_percentage']:8.1f}%")
    else:
        print(f"{diff} goal{'s' if diff > 1 else ''} difference | {row['total_count']:5} | {row['reflects_count']:18} | {row['reflection_percentage']:8.1f}%")

# ===== CORRELATION ANALYSIS =====
print(f"\n" + "="*100)
print("EVENT RATIO vs SCORE CORRELATION")
print("="*100)

# Filter valid ratios
valid_games = reflection_df[reflection_df['total_ratio'] != float('inf')]

if len(valid_games) > 0:
    # Calculate correlation between event ratio and score difference
    # For this, we need to adjust score difference based on which team had more events
    adjusted_score_diff = []
    
    for _, game in valid_games.iterrows():
        if game['total_ratio'] > 1.0:  # Team A had more events
            if game['team_a_score'] > game['team_b_score']:  # Team A won
                adjusted_score_diff.append(game['score_difference'])
            elif game['team_b_score'] > game['team_a_score']:  # Team B won (mismatch)
                adjusted_score_diff.append(-game['score_difference'])
            else:  # Draw
                adjusted_score_diff.append(0)
        else:  # Team B had more events
            if game['team_b_score'] > game['team_a_score']:  # Team B won
                adjusted_score_diff.append(game['score_difference'])
            elif game['team_a_score'] > game['team_b_score']:  # Team A won (mismatch)
                adjusted_score_diff.append(-game['score_difference'])
            else:  # Draw
                adjusted_score_diff.append(0)
    
    valid_games_copy = valid_games.copy()
    valid_games_copy['adjusted_score_diff'] = adjusted_score_diff
    
    correlation = valid_games_copy['total_ratio'].corr(valid_games_copy['adjusted_score_diff'])
    print(f"Correlation between total event ratio and score outcome: {correlation:.3f}")
    
    # Average ratios by outcome
    wins_with_more_events = valid_games_copy[valid_games_copy['adjusted_score_diff'] > 0]['total_ratio'].mean()
    losses_with_more_events = valid_games_copy[valid_games_copy['adjusted_score_diff'] < 0]['total_ratio'].mean()
    draws_ratio = valid_games_copy[valid_games_copy['adjusted_score_diff'] == 0]['total_ratio'].mean()
    
    print(f"\nAverage event ratios:")
    print(f"  Teams that won with more events: {wins_with_more_events:.3f}")
    print(f"  Teams that lost despite more events: {losses_with_more_events:.3f}")
    print(f"  Draws: {draws_ratio:.3f}")

# ===== SAVE RESULTS =====
print(f"\n" + "="*100)
print("SAVING RESULTS")
print("="*100)

reflection_df.to_csv('events_ratio_vs_score_reflection.csv', index=False)
print("File saved: events_ratio_vs_score_reflection.csv")

print(f"\n=== EVENTS RATIO vs SCORE REFLECTION ANALYSIS COMPLETE ===")
print(f"Key Finding: Total game events reflect final score in {total_reflects_count}/{total_games} games ({(total_reflects_count/total_games)*100:.1f}%)")
print(f"Event control effectiveness varies by stage and score margin") 