import pandas as pd

df = pd.read_csv('euro_2024_sample_100_rows.csv')
print(f"📊 Sample CSV: {len(df)} rows, {len(df.columns)} columns")
print(f"🏟️ Match: {df.iloc[0]['home_team']} vs {df.iloc[0]['away_team']}")
print(f"⚽ Events: {df['event_type'].nunique()} unique types")
print(f"👥 Players: {len(df[df['player_name'] != 'N/A'])} with player names")
print(f"📋 Columns: {list(df.columns)}") 