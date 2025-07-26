import pandas as pd
import numpy as np
import json

print("=== HOME/AWAY TEAM EVENTS RATIO ANALYSIS ===")

# Load the data
matches = pd.read_csv('../Data/matches_complete.csv')
events = pd.read_csv('../Data/events_complete.csv')

print(f"Total matches: {len(matches)}")
print(f"Total events: {len(events)}")

# Create game-by-game analysis
game_analysis = []

for _, match in matches.iterrows():
    match_id = match['match_id']
    
    # Get match info
    home_team = match['home_team_name']
    away_team = match['away_team_name']
    stage = match['stage']
    
    # Get scores
    home_score = int(match['home_score']) if pd.notna(match['home_score']) else 0
    away_score = int(match['away_score']) if pd.notna(match['away_score']) else 0
    
    # Get match events
    match_events = events[events['match_id'] == match_id].copy()
    
    if len(match_events) == 0:
        continue
    
    # Separate by period
    first_half_events = match_events[match_events['period'] == 1]
    second_half_events = match_events[match_events['period'] == 2]
    
    # Count events by team for first half
    fh_home_events = len(first_half_events[first_half_events['team_name'] == home_team])
    fh_away_events = len(first_half_events[first_half_events['team_name'] == away_team])
    
    # Count events by team for second half
    sh_home_events = len(second_half_events[second_half_events['team_name'] == home_team])
    sh_away_events = len(second_half_events[second_half_events['team_name'] == away_team])
    
    # Calculate ratios (avoid division by zero)
    if fh_away_events > 0:
        fh_ratio = fh_home_events / fh_away_events
    else:
        fh_ratio = float('inf') if fh_home_events > 0 else 1.0
    
    if sh_away_events > 0:
        sh_ratio = sh_home_events / sh_away_events
    else:
        sh_ratio = float('inf') if sh_home_events > 0 else 1.0
    
    # Determine halftime result by counting goals in first half
    fh_home_goals = 0
    fh_away_goals = 0
    
    # Look for shot events that resulted in goals in first half
    fh_shots = first_half_events[first_half_events['shot'].notna()]
    for _, shot_event in fh_shots.iterrows():
        try:
            # Parse shot data
            shot_data = eval(shot_event['shot']) if isinstance(shot_event['shot'], str) else shot_event['shot']
            if isinstance(shot_data, dict) and shot_data.get('outcome', {}).get('name') == 'Goal':
                if shot_event['team_name'] == home_team:
                    fh_home_goals += 1
                elif shot_event['team_name'] == away_team:
                    fh_away_goals += 1
        except:
            continue
    
    # Halftime result
    if fh_home_goals > fh_away_goals:
        ht_result = f"{fh_home_goals}-{fh_away_goals} (H)"
    elif fh_away_goals > fh_home_goals:
        ht_result = f"{fh_home_goals}-{fh_away_goals} (A)"
    else:
        ht_result = f"{fh_home_goals}-{fh_away_goals} (D)"
    
    # Full-time result
    if home_score > away_score:
        ft_result = f"{home_score}-{away_score} (H)"
    elif away_score > home_score:
        ft_result = f"{home_score}-{away_score} (A)"
    else:
        ft_result = f"{home_score}-{away_score} (D)"
    
    game_analysis.append({
        'match_id': match_id,
        'home_team': home_team,
        'away_team': away_team,
        'stage': stage,
        'fh_home_events': fh_home_events,
        'fh_away_events': fh_away_events,
        'fh_events_ratio': fh_ratio,
        'halftime_result': ht_result,
        'sh_home_events': sh_home_events,
        'sh_away_events': sh_away_events,
        'sh_events_ratio': sh_ratio,
        'fulltime_result': ft_result,
        'match_date': match['match_date']
    })

# Convert to DataFrame
games_df = pd.DataFrame(game_analysis)

print(f"\nSuccessfully analyzed {len(games_df)} games")

# ===== DISPLAY RESULTS AS REQUESTED =====
print("\n" + "="*150)
print("HOME/AWAY EVENTS RATIO FOR EACH GAME")
print("="*150)
print("Format: Home Team Events / Away Team Events for First Half | Half Result | Home Team Events / Away Team Events for Second Half | 90 Minutes Result | Stage")
print("-"*150)

for _, game in games_df.iterrows():
    # Format the ratios
    if game['fh_events_ratio'] == float('inf'):
        fh_ratio_str = f"{game['fh_home_events']}/0 (∞)"
    else:
        fh_ratio_str = f"{game['fh_home_events']}/{game['fh_away_events']} ({game['fh_events_ratio']:.2f})"
    
    if game['sh_events_ratio'] == float('inf'):
        sh_ratio_str = f"{game['sh_home_events']}/0 (∞)"
    else:
        sh_ratio_str = f"{game['sh_home_events']}/{game['sh_away_events']} ({game['sh_events_ratio']:.2f})"
    
    print(f"{game['home_team']} vs {game['away_team']}")
    print(f"First Half: {fh_ratio_str} | Half Result: {game['halftime_result']} | Second Half: {sh_ratio_str} | 90 Min Result: {game['fulltime_result']} | Stage: {game['stage']}")
    print("-"*150)

# ===== SUMMARY STATISTICS =====
print("\n" + "="*100)
print("SUMMARY STATISTICS")
print("="*100)

# Overall stats
valid_fh_ratios = games_df[games_df['fh_events_ratio'] != float('inf')]['fh_events_ratio']
valid_sh_ratios = games_df[games_df['sh_events_ratio'] != float('inf')]['sh_events_ratio']

print(f"FIRST HALF EVENT RATIOS:")
print(f"Average ratio: {valid_fh_ratios.mean():.3f}")
print(f"Median ratio: {valid_fh_ratios.median():.3f}")
print(f"Min ratio: {valid_fh_ratios.min():.3f}")
print(f"Max ratio: {valid_fh_ratios.max():.3f}")
print(f"Standard deviation: {valid_fh_ratios.std():.3f}")

print(f"\nSECOND HALF EVENT RATIOS:")
print(f"Average ratio: {valid_sh_ratios.mean():.3f}")
print(f"Median ratio: {valid_sh_ratios.median():.3f}")
print(f"Min ratio: {valid_sh_ratios.min():.3f}")
print(f"Max ratio: {valid_sh_ratios.max():.3f}")
print(f"Standard deviation: {valid_sh_ratios.std():.3f}")

# Ratio distribution
print(f"\nEVENT RATIO DISTRIBUTION:")
print(f"First Half - Home Advantage (>1.0): {len(valid_fh_ratios[valid_fh_ratios > 1.0])} games ({(len(valid_fh_ratios[valid_fh_ratios > 1.0])/len(valid_fh_ratios)*100):.1f}%)")
print(f"First Half - Away Advantage (<1.0): {len(valid_fh_ratios[valid_fh_ratios < 1.0])} games ({(len(valid_fh_ratios[valid_fh_ratios < 1.0])/len(valid_fh_ratios)*100):.1f}%)")
print(f"First Half - Equal (=1.0): {len(valid_fh_ratios[valid_fh_ratios == 1.0])} games ({(len(valid_fh_ratios[valid_fh_ratios == 1.0])/len(valid_fh_ratios)*100):.1f}%)")

print(f"Second Half - Home Advantage (>1.0): {len(valid_sh_ratios[valid_sh_ratios > 1.0])} games ({(len(valid_sh_ratios[valid_sh_ratios > 1.0])/len(valid_sh_ratios)*100):.1f}%)")
print(f"Second Half - Away Advantage (<1.0): {len(valid_sh_ratios[valid_sh_ratios < 1.0])} games ({(len(valid_sh_ratios[valid_sh_ratios < 1.0])/len(valid_sh_ratios)*100):.1f}%)")
print(f"Second Half - Equal (=1.0): {len(valid_sh_ratios[valid_sh_ratios == 1.0])} games ({(len(valid_sh_ratios[valid_sh_ratios == 1.0])/len(valid_sh_ratios)*100):.1f}%)")

# ===== STAGE ANALYSIS =====
print(f"\n" + "="*100)
print("ANALYSIS BY STAGE")
print("="*100)

for stage in games_df['stage'].unique():
    stage_games = games_df[games_df['stage'] == stage]
    stage_fh_ratios = stage_games[stage_games['fh_events_ratio'] != float('inf')]['fh_events_ratio']
    stage_sh_ratios = stage_games[stage_games['sh_events_ratio'] != float('inf')]['sh_events_ratio']
    
    print(f"\n{stage.upper()} ({len(stage_games)} games):")
    if len(stage_fh_ratios) > 0:
        print(f"  First Half - Avg Ratio: {stage_fh_ratios.mean():.3f}")
        print(f"  First Half - Home Advantage: {len(stage_fh_ratios[stage_fh_ratios > 1.0])} games ({(len(stage_fh_ratios[stage_fh_ratios > 1.0])/len(stage_fh_ratios)*100):.1f}%)")
    
    if len(stage_sh_ratios) > 0:
        print(f"  Second Half - Avg Ratio: {stage_sh_ratios.mean():.3f}")
        print(f"  Second Half - Home Advantage: {len(stage_sh_ratios[stage_sh_ratios > 1.0])} games ({(len(stage_sh_ratios[stage_sh_ratios > 1.0])/len(stage_sh_ratios)*100):.1f}%)")

# ===== CORRELATION ANALYSIS =====
print(f"\n" + "="*100)
print("CORRELATION ANALYSIS")
print("="*100)

# Home advantage vs result correlation
games_df['home_win'] = games_df['fulltime_result'].str.contains('\\(H\\)', regex=True)
games_df['away_win'] = games_df['fulltime_result'].str.contains('\\(A\\)', regex=True)
games_df['draw'] = games_df['fulltime_result'].str.contains('\\(D\\)', regex=True)

# Calculate correlations for valid ratios only
valid_games = games_df[(games_df['fh_events_ratio'] != float('inf')) & (games_df['sh_events_ratio'] != float('inf'))]

if len(valid_games) > 0:
    # Event ratio vs result
    fh_home_wins = valid_games[valid_games['home_win']]['fh_events_ratio'].mean()
    fh_away_wins = valid_games[valid_games['away_win']]['fh_events_ratio'].mean()
    fh_draws = valid_games[valid_games['draw']]['fh_events_ratio'].mean()
    
    sh_home_wins = valid_games[valid_games['home_win']]['sh_events_ratio'].mean()
    sh_away_wins = valid_games[valid_games['away_win']]['sh_events_ratio'].mean()
    sh_draws = valid_games[valid_games['draw']]['sh_events_ratio'].mean()
    
    print(f"FIRST HALF EVENT RATIO BY RESULT:")
    print(f"  Home Wins: {fh_home_wins:.3f}")
    print(f"  Away Wins: {fh_away_wins:.3f}")
    print(f"  Draws: {fh_draws:.3f}")
    
    print(f"\nSECOND HALF EVENT RATIO BY RESULT:")
    print(f"  Home Wins: {sh_home_wins:.3f}")
    print(f"  Away Wins: {sh_away_wins:.3f}")
    print(f"  Draws: {sh_draws:.3f}")

# ===== SAVE RESULTS =====
print(f"\n" + "="*100)
print("SAVING RESULTS")
print("="*100)

games_df.to_csv('home_away_events_ratio_detailed.csv', index=False)
print("File saved: home_away_events_ratio_detailed.csv")

print(f"\n=== HOME/AWAY EVENTS RATIO ANALYSIS COMPLETE ===")
print(f"Analyzed {len(games_df)} games across {len(games_df['stage'].unique())} stages")
print(f"Home event advantage found in {len(valid_fh_ratios[valid_fh_ratios > 1.0])} first halves and {len(valid_sh_ratios[valid_sh_ratios > 1.0])} second halves") 