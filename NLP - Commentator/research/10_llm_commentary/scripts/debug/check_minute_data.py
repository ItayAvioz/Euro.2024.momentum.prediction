"""Check actual data for minutes 9 and 13 to understand the bug."""

import pandas as pd
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Load match data (same way as batch_generate_v6 does)
from pathlib import Path
PHASE7_DATA = Path("C:/Users/yonatanam/Desktop/Euro 2024 - momentum - DS-AI project/07_all_games_commentary/data")
match_id = 3942382  # Netherlands vs Turkey

df = pd.read_csv(PHASE7_DATA / f"match_{match_id}_rich_commentary.csv")

print('='*70)
print('MINUTE 9 - ACTUAL DATA')
print('='*70)

min9 = df[(df['minute'] == 9) & (df['period'] == 1)]
print(f'\nTotal events: {len(min9)}')

if len(min9) > 0:
    # Possession stats
    if 'possession_team' in min9.columns:
        poss_counts = min9['possession_team'].value_counts()
        total = len(min9)
        print('\nPossession by team:')
        for team, count in poss_counts.items():
            pct = (count / total) * 100
            print(f'  {team}: {count} events ({pct:.0f}%)')
    
    # All players
    if 'player_name' in min9.columns:
        print('\nAll players (with event counts):')
        player_counts = min9['player_name'].dropna().value_counts()
        for player, count in player_counts.items():
            # Get team for this player
            player_rows = min9[min9['player_name'] == player]
            team = player_rows['team_name'].iloc[0] if len(player_rows) > 0 else 'Unknown'
            print(f'  {player} ({team}): {count} events')
    
    # Most active player (as calculated by get_most_active_player)
    if 'player_name' in min9.columns:
        player_counts = min9['player_name'].dropna().value_counts()
        if len(player_counts) > 0:
            top_player = player_counts.index[0]
            count = player_counts.iloc[0]
            player_rows = min9[min9['player_name'] == top_player]
            team = player_rows['team_name'].iloc[0] if len(player_rows) > 0 else ''
            print(f'\nMost active player (current logic): {top_player} ({team}) - {count} events')

print('\n\n' + '='*70)
print('MINUTE 13 - ACTUAL DATA')
print('='*70)

min13 = df[(df['minute'] == 13) & (df['period'] == 1)]
print(f'\nTotal events: {len(min13)}')

if len(min13) > 0:
    # Possession stats
    if 'possession_team' in min13.columns:
        poss_counts = min13['possession_team'].value_counts()
        total = len(min13)
        print('\nPossession by team:')
        for team, count in poss_counts.items():
            pct = (count / total) * 100
            print(f'  {team}: {count} events ({pct:.0f}%)')
    
    # All players
    if 'player_name' in min13.columns:
        print('\nAll players (with event counts):')
        player_counts = min13['player_name'].dropna().value_counts()
        for player, count in player_counts.items():
            # Get team for this player
            player_rows = min13[min13['player_name'] == player]
            team = player_rows['team_name'].iloc[0] if len(player_rows) > 0 else 'Unknown'
            print(f'  {player} ({team}): {count} events')
    
    # Most active player (as calculated by get_most_active_player)
    if 'player_name' in min13.columns:
        player_counts = min13['player_name'].dropna().value_counts()
        if len(player_counts) > 0:
            top_player = player_counts.index[0]
            count = player_counts.iloc[0]
            player_rows = min13[min13['player_name'] == top_player]
            team = player_rows['team_name'].iloc[0] if len(player_rows) > 0 else ''
            print(f'\nMost active player (current logic): {top_player} ({team}) - {count} events')

