import pandas as pd
import os

# Load matches
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(script_dir))))
matches_path = os.path.join(project_root, 'Data', 'matches_complete.csv')

matches = pd.read_csv(matches_path)

print("\nAvailable columns:", matches.columns.tolist())

print("\nEuro 2024 Semi-Finals:")
print("="*70)

# Try to find semi-finals - check different column names
stage_col = None
for col in matches.columns:
    if 'stage' in col.lower():
        stage_col = col
        print(f"Using stage column: {stage_col}")
        break

if stage_col:
    semis = matches[matches[stage_col].str.contains('Semi', case=False, na=False)]
else:
    # Try by team names we know played
    semis = matches[
        ((matches['home_team_name'] == 'Spain') & (matches['away_team_name'] == 'France')) |
        ((matches['home_team_name'] == 'France') & (matches['away_team_name'] == 'Spain')) |
        ((matches['home_team_name'] == 'Netherlands') & (matches['away_team_name'] == 'England')) |
        ((matches['home_team_name'] == 'England') & (matches['away_team_name'] == 'Netherlands'))
    ]

for _, m in semis.iterrows():
    print(f"\n Match ID: {m['match_id']}")
    print(f"   Teams: {m['home_team_name']} vs {m['away_team_name']}")
    print(f"   Score: {m['home_score']}-{m['away_score']}")
    print(f"   Date: {m['match_date']}")
    if stage_col in m:
        print(f"   Stage: {m[stage_col]}")

