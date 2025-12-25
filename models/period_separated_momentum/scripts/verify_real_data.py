import pandas as pd
import numpy as np

# Load period-separated momentum data
df = pd.read_csv('../outputs/momentum_by_period.csv')

print('PERIOD-SEPARATED DATA')
print('='*60)
print(f'Total rows: {len(df)}')
print(f'Unique matches: {df["match_id"].nunique()}')

# Filter for period 1 and 2 only (not overtime)
df_p1p2 = df[df['period'].isin([1, 2])].copy()
print(f'\nPeriod 1+2 rows: {len(df_p1p2)}')
print(f'Unique matches in P1+P2: {df_p1p2["match_id"].nunique()}')

# For each game, calculate who won more momentum windows
# This is "Absolute Momentum" metric
results = []
game_details = []

for match_id in df_p1p2['match_id'].unique():
    game = df_p1p2[df_p1p2['match_id'] == match_id]
    home_team = game['team_home'].iloc[0]
    away_team = game['team_away'].iloc[0]
    
    home_wins = (game['team_home_momentum'] > game['team_away_momentum']).sum()
    away_wins = (game['team_away_momentum'] > game['team_home_momentum']).sum()
    ties = (game['team_home_momentum'] == game['team_away_momentum']).sum()
    
    if home_wins > away_wins:
        results.append('home_dominant')
        game_details.append((match_id, home_team, away_team, home_wins, away_wins, 'HOME'))
    elif away_wins > home_wins:
        results.append('away_dominant')
        game_details.append((match_id, home_team, away_team, home_wins, away_wins, 'AWAY'))
    else:
        results.append('tie')
        game_details.append((match_id, home_team, away_team, home_wins, away_wins, 'TIE'))

print(f'\nAbsolute Momentum dominance:')
print(f'Home dominant: {results.count("home_dominant")}')
print(f'Away dominant: {results.count("away_dominant")}')
print(f'Tie (no clear winner): {results.count("tie")}')
print(f'Total games with dominance: {results.count("home_dominant") + results.count("away_dominant")}')
print(f'Total games: {len(results)}')

# Show tie games
print('\n' + '='*60)
print('TIE GAMES (where neither team dominated):')
print('='*60)
for detail in game_details:
    if detail[5] == 'TIE':
        print(f'{detail[1]} vs {detail[2]}: Home={detail[3]}, Away={detail[4]}')

# Now load original data and compare
print('\n' + '='*60)
print('ORIGINAL DASHBOARD DATA')
print('='*60)

orig_df = pd.read_csv('../../preprocessing/input_generation/outputs/momentum_targets_streamlined.csv')
print(f'Total rows: {len(orig_df)}')
print(f'Unique matches: {orig_df["match_id"].nunique()}')

# Same calculation
results_orig = []
for match_id in orig_df['match_id'].unique():
    game = orig_df[orig_df['match_id'] == match_id]
    home_wins = (game['team_home_momentum'] > game['team_away_momentum']).sum()
    away_wins = (game['team_away_momentum'] > game['team_home_momentum']).sum()
    
    if home_wins > away_wins:
        results_orig.append('home_dominant')
    elif away_wins > home_wins:
        results_orig.append('away_dominant')
    else:
        results_orig.append('tie')

print(f'\nAbsolute Momentum dominance (Original):')
print(f'Home dominant: {results_orig.count("home_dominant")}')
print(f'Away dominant: {results_orig.count("away_dominant")}')
print(f'Tie: {results_orig.count("tie")}')
print(f'Total games with dominance: {results_orig.count("home_dominant") + results_orig.count("away_dominant")}')
print(f'Total games: {len(results_orig)}')

