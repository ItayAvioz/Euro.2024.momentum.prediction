#!/usr/bin/env python3
"""
Display 20 sample rows from the connected Euro 2024 data
"""

import pandas as pd

def show_sample_data():
    """Display sample rows from the connected Euro 2024 data"""
    print("🏆 Euro 2024 Connected Data - 20 Sample Rows")
    print("=" * 80)
    
    # Load the connected data
    df = pd.read_csv('euro_2024_data/connected_data.csv')
    
    print(f"📊 Full dataset: {len(df):,} rows, {len(df.columns)} columns")
    print()
    
    # Select key columns for display
    key_columns = [
        'match_id', 'minute', 'second', 'event_type', 'player_name', 
        'team_name', 'position', 'home_team', 'away_team', 'match_date'
    ]
    
    # Filter to columns that exist
    available_columns = [col for col in key_columns if col in df.columns]
    
    print(f"📋 Showing columns: {', '.join(available_columns)}")
    print()
    
    # Get sample data - mix of different event types
    sample_data = df[available_columns].head(20)
    
    print("🎯 20 Sample Rows:")
    print("-" * 80)
    
    # Display each row formatted nicely
    for i, (_, row) in enumerate(sample_data.iterrows(), 1):
        print(f"Row {i:2d}:")
        for col in available_columns:
            value = row[col]
            if pd.isna(value):
                value = "N/A"
            elif isinstance(value, str) and len(str(value)) > 30:
                value = str(value)[:30] + "..."
            print(f"  {col:15}: {value}")
        print()
    
    print("=" * 80)
    print("📈 Event Type Distribution in Sample:")
    event_counts = sample_data['event_type'].value_counts()
    for event_type, count in event_counts.items():
        print(f"  {event_type}: {count}")
    
    print()
    print("👥 Players in Sample:")
    players = sample_data['player_name'].dropna().unique()
    for i, player in enumerate(players[:10], 1):
        print(f"  {i}. {player}")
    
    print()
    print("🏟️ Matches in Sample:")
    matches = sample_data[['home_team', 'away_team']].drop_duplicates()
    for i, (_, match) in enumerate(matches.iterrows(), 1):
        print(f"  {i}. {match['home_team']} vs {match['away_team']}")

if __name__ == "__main__":
    show_sample_data() 