#!/usr/bin/env python3
"""
Present 20 sample rows from Euro 2024 data in a clean table format
"""

import pandas as pd

def present_data_table():
    """Present sample data in a clean table format"""
    print("🏆 Euro 2024 Connected Data - Table Presentation")
    print("=" * 100)
    
    # Load the connected data
    df = pd.read_csv('euro_2024_data/connected_data.csv')
    
    # Select key columns for presentation
    columns_to_show = [
        'match_id', 'minute', 'second', 'event_type', 'player_name', 
        'team_name', 'home_team', 'away_team'
    ]
    
    # Get first 20 rows
    sample_df = df[columns_to_show].head(20).copy()
    
    # Clean up the data for better presentation
    sample_df['player_name'] = sample_df['player_name'].fillna('N/A')
    sample_df['team_name'] = sample_df['team_name'].fillna('N/A')
    
    # Truncate long names for better display
    sample_df['player_name'] = sample_df['player_name'].apply(
        lambda x: x[:20] + '...' if isinstance(x, str) and len(x) > 20 else x
    )
    
    print("📊 Dataset Overview:")
    print(f"   Total rows: {len(df):,}")
    print(f"   Total columns: {len(df.columns)}")
    print(f"   Match: {sample_df['home_team'].iloc[0]} vs {sample_df['away_team'].iloc[0]}")
    print(f"   Match ID: {sample_df['match_id'].iloc[0]}")
    print()
    
    print("📋 20 Sample Rows:")
    print("-" * 100)
    
    # Set pandas display options for better table formatting
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', 20)
    
    # Display the table
    print(sample_df.to_string(index=True, justify='left'))
    
    print()
    print("-" * 100)
    
    # Summary statistics
    print("📈 Summary of Sample Data:")
    print(f"   🕐 Time range: {sample_df['minute'].min()}:{sample_df['second'].min():02d} - {sample_df['minute'].max()}:{sample_df['second'].max():02d}")
    print(f"   ⚽ Event types: {sample_df['event_type'].nunique()} unique")
    print(f"   👥 Players: {sample_df[sample_df['player_name'] != 'N/A']['player_name'].nunique()} unique")
    print(f"   🏟️ Teams: {sample_df['team_name'].nunique()} teams")
    
    print()
    print("📊 Event Type Breakdown:")
    event_counts = sample_df['event_type'].value_counts()
    for event_type, count in event_counts.items():
        print(f"   {event_type}: {count} events")
    
    print()
    print("🎯 Key Features for Your Project:")
    print("   ✅ Match-Event Connection: All events linked to match_id")
    print("   ✅ Player-Event Connection: Player names with event context")
    print("   ✅ Team-Event Connection: Team context for each event")
    print("   ✅ Time-Event Connection: Precise minute:second timestamps")
    print("   ✅ Commentary Ready: Event + Player + Time = Auto-commentary")
    print("   ✅ Sequence Analysis: Chronological events for move quality prediction")

if __name__ == "__main__":
    present_data_table() 