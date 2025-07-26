#!/usr/bin/env python3
"""
Analyze Complete Euro 2024 Dataset
Quick analysis of the full tournament data
"""

import pandas as pd

def analyze_complete_dataset():
    """Analyze the complete Euro 2024 dataset"""
    print("🏆 COMPLETE Euro 2024 Dataset Analysis")
    print("=" * 60)
    
    # Load the complete connected dataset
    df = pd.read_csv('euro_2024_complete/connected_complete.csv')
    matches = pd.read_csv('euro_2024_complete/matches_complete.csv')
    
    print(f"📊 Dataset Overview:")
    print(f"   Total events: {len(df):,}")
    print(f"   Total matches: {len(matches)}")
    print(f"   Unique players: {df['player_id'].nunique()}")
    print(f"   Tournament period: {matches['match_date'].min()} to {matches['match_date'].max()}")
    print()
    
    # Tournament structure
    print("🏆 Tournament Structure:")
    stage_counts = matches['stage'].value_counts()
    for stage, count in stage_counts.items():
        print(f"   {stage}: {count} matches")
    print()
    
    # Event analysis
    print("⚽ Event Analysis:")
    top_events = df['event_type'].value_counts().head(10)
    for event, count in top_events.items():
        print(f"   {event}: {count:,}")
    print()
    
    # Goals analysis
    goals = df[df['event_type'] == 'Goal']
    print(f"🎯 Goals Analysis:")
    print(f"   Total goals: {len(goals)}")
    print(f"   Average goals per match: {len(goals) / len(matches):.1f}")
    print()
    
    # Player analysis
    print("👥 Player Analysis:")
    player_events = df.groupby('player_name').size().reset_index(name='events')
    top_players = player_events.nlargest(10, 'events')
    print("   Most active players:")
    for _, player in top_players.iterrows():
        if pd.notna(player['player_name']):
            print(f"      {player['player_name']}: {player['events']:,} events")
    print()
    
    print("🎯 Your Complete Euro 2024 Dataset is Ready!")
    print("   - Load with: pd.read_csv('euro_2024_complete/connected_complete.csv')")
    print("   - Perfect for commentary generation and move quality prediction")
    print("   - Complete tournament coverage with all events and players")

if __name__ == "__main__":
    analyze_complete_dataset() 