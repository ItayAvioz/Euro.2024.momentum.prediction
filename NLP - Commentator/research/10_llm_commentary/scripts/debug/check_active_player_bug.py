"""Check active player bug for minutes 9 and 13."""

import pandas as pd
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Load data
df = pd.read_csv('C:/Users/yonatanam/Desktop/Euro 2024 - momentum - DS-AI project/Data/euro_2024_complete_dataset.csv')
match = df[(df['home_team'] == 'Netherlands') & (df['away_team'] == 'Turkey')]

print('='*70)
print('MINUTE 9 ANALYSIS')
print('='*70)

min9 = match[(match['minute'] == 9) & (match['period'] == 1)]
print(f'\nTotal events: {len(min9)}')

if len(min9) > 0:
    print('\nEvents by team:')
    team_counts = min9.groupby('possession_team').size()
    print(team_counts)
    
    print('\nEvents by player (all):')
    player_counts = min9['player'].value_counts()
    print(player_counts)
    
    print('\nNetherlands players:')
    nl_events = min9[min9['possession_team'] == 'Netherlands']
    if len(nl_events) > 0:
        print(nl_events['player'].value_counts())
    
    print('\nTurkey players:')
    tr_events = min9[min9['possession_team'] == 'Turkey']
    if len(tr_events) > 0:
        print(tr_events['player'].value_counts())
    
    print(f'\nXavi Simons events: {len(min9[min9["player"] == "Xavi Simons"])}')
    print(f'Xavi Simons team: {min9[min9["player"] == "Xavi Simons"]["possession_team"].unique() if len(min9[min9["player"] == "Xavi Simons"]) > 0 else "N/A"}')
    print(f'Turkey events: {len(min9[min9["possession_team"] == "Turkey"])}')
    print(f'Netherlands events: {len(min9[min9["possession_team"] == "Netherlands"])}')

print('\n\n' + '='*70)
print('MINUTE 13 ANALYSIS')
print('='*70)

min13 = match[(match['minute'] == 13) & (match['period'] == 1)]
print(f'\nTotal events: {len(min13)}')

if len(min13) > 0:
    print('\nEvents by team:')
    team_counts = min13.groupby('possession_team').size()
    print(team_counts)
    
    print('\nEvents by player (all):')
    player_counts = min13['player'].value_counts()
    print(player_counts)
    
    print('\nNetherlands players:')
    nl_events = min13[min13['possession_team'] == 'Netherlands']
    if len(nl_events) > 0:
        print(nl_events['player'].value_counts())
    
    print('\nTurkey players:')
    tr_events = min13[min13['possession_team'] == 'Turkey']
    if len(tr_events) > 0:
        print(tr_events['player'].value_counts())
    
    print(f'\nGakpo events: {len(min13[min13["player"] == "Cody Gakpo"])}')
    print(f'Gakpo team: {min13[min13["player"] == "Cody Gakpo"]["possession_team"].unique() if len(min13[min13["player"] == "Cody Gakpo"]) > 0 else "N/A"}')
    print(f'Turkey events: {len(min13[min13["possession_team"] == "Turkey"])}')
    print(f'Netherlands events: {len(min13[min13["possession_team"] == "Netherlands"])}')

