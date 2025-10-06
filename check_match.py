import pandas as pd

df = pd.read_csv('../data/outputs/game_superiority_score_analysis.csv')
match_rows = df[df['match_id'] == 3930159]

print('Match 3930159 data:')
for i, row in match_rows.iterrows():
    team_name = row['team_name']
    team_type = row['team_type']
    team_score = row['team_score']
    opponent_score = row['opponent_score']
    print(f'  {team_name} ({team_type}) score={team_score}, opponent_score={opponent_score}')
