import pandas as pd

# Original data
orig = pd.read_csv('../../preprocessing/output_generation/data/targets/momentum_targets_streamlined.csv')
print(f'Original unique matches: {orig["match_id"].nunique()}')

results = []
tie_games = []
for mid in orig['match_id'].unique():
    g = orig[orig['match_id']==mid]
    hw = (g['team_home_momentum'] > g['team_away_momentum']).sum()
    aw = (g['team_away_momentum'] > g['team_home_momentum']).sum()
    home = g['team_home'].iloc[0]
    away = g['team_away'].iloc[0]
    if hw > aw: 
        results.append('H')
    elif aw > hw: 
        results.append('A')
    else: 
        results.append('T')
        tie_games.append(f'{home} vs {away}: {hw}-{aw}')

print(f'Home dom: {results.count("H")}')
print(f'Away dom: {results.count("A")}')
print(f'Tie: {results.count("T")}')
print(f'Total with dom: {results.count("H")+results.count("A")}')

if tie_games:
    print('\nTie games:')
    for t in tie_games:
        print(f'  {t}')

