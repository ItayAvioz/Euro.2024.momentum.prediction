"""Verify data for Czech Republic vs Turkey game"""
import pandas as pd

df = pd.read_csv('../models/preprocessing/data/targets/momentum_targets_streamlined.csv')

# Find Czech Republic vs Turkey game
game = df[(df['team_home'].str.contains('Czech')) | (df['team_away'].str.contains('Czech'))]
game = game[(game['team_home'].str.contains('Turkey')) | (game['team_away'].str.contains('Turkey'))]

if len(game) > 0:
    print('Game found!')
    print(f"Home: {game['team_home'].iloc[0]}")
    print(f"Away: {game['team_away'].iloc[0]}")
    
    # ALL DATA (before filter)
    game = game.copy()
    game['minute'] = game['minute_range'].apply(lambda x: int(x.split('-')[0]))
    
    print(f"\n=== ALL DATA (before filter) ===")
    print(f"Total windows: {len(game)}")
    home_wins_all = (game['team_home_momentum'] > game['team_away_momentum']).sum()
    away_wins_all = (game['team_away_momentum'] > game['team_home_momentum']).sum()
    print(f"Momentum windows: Home {home_wins_all} - Away {away_wins_all}")
    
    # Filter from minute 3
    game = game[game['minute'] >= 3]
    
    print(f"\n=== FROM MINUTE 3 (after filter) ===")
    print(f"Total windows (from min 3): {len(game)}")
    
    # Calculate stats
    home_wins = (game['team_home_momentum'] > game['team_away_momentum']).sum()
    away_wins = (game['team_away_momentum'] > game['team_home_momentum']).sum()
    print(f"Momentum windows: Home {home_wins} - Away {away_wins}")
    
    home_pos = (game['team_home_momentum_change'] > 0).sum()
    away_pos = (game['team_away_momentum_change'] > 0).sum()
    print(f"Positive changes: Home {home_pos} - Away {away_pos}")
    
    home_avg = game['team_home_momentum'].mean()
    away_avg = game['team_away_momentum'].mean()
    print(f"Avg momentum: Home {home_avg:.2f} - Away {away_avg:.2f}")
    
    # Longest sequence
    home_max_seq = 0
    away_max_seq = 0
    current_home = 0
    current_away = 0
    for _, row in game.iterrows():
        if row['team_home_momentum_change'] > 0:
            current_home += 1
            home_max_seq = max(home_max_seq, current_home)
        else:
            current_home = 0
        if row['team_away_momentum_change'] > 0:
            current_away += 1
            away_max_seq = max(away_max_seq, current_away)
        else:
            current_away = 0
    print(f"Longest sequence: Home {home_max_seq} - Away {away_max_seq}")
else:
    print('Game not found')

