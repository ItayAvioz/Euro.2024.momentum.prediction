#!/usr/bin/env python3
"""
Euro 2024 Data Analysis
Analyzes the connected Euro 2024 data and shows how to use it for commentary and predictions
"""

import pandas as pd
import numpy as np
import os

def analyze_euro_2024_data():
    """
    Analyze the downloaded Euro 2024 connected data
    """
    print("🏆 Euro 2024 Data Analysis")
    print("=" * 50)
    
    # Load the connected data
    data_folder = "euro_2024_data"
    
    if not os.path.exists(f"{data_folder}/connected_data.csv"):
        print("❌ No connected data found. Please run euro_2024_downloader.py first.")
        return
    
    # Load all datasets
    print("📊 Loading Euro 2024 datasets...")
    
    matches_df = pd.read_csv(f"{data_folder}/matches.csv")
    events_df = pd.read_csv(f"{data_folder}/events.csv")
    lineups_df = pd.read_csv(f"{data_folder}/lineups.csv")
    connected_df = pd.read_csv(f"{data_folder}/connected_data.csv")
    
    print(f"✅ Loaded {len(matches_df)} matches, {len(events_df)} events, {len(lineups_df)} lineups")
    print(f"🔗 Connected data: {len(connected_df)} rows")
    print()
    
    # Basic analysis
    print("📈 BASIC ANALYSIS")
    print("-" * 20)
    
    # Match analysis
    print(f"🏟️  Matches: {len(matches_df)}")
    print(f"   📅 Tournament period: {matches_df['match_date'].min()} to {matches_df['match_date'].max()}")
    print(f"   🏆 Stages: {', '.join(matches_df['stage'].unique())}")
    print(f"   ⚽ Total goals: {matches_df['home_score'].sum() + matches_df['away_score'].sum()}")
    print()
    
    # Event analysis
    print(f"⚽ Events Analysis:")
    top_events = connected_df['event_type'].value_counts().head(10)
    for event, count in top_events.items():
        print(f"   {event}: {count:,}")
    print()
    
    # Goals analysis
    goals_df = connected_df[connected_df['event_type'] == 'Goal'].copy()
    if not goals_df.empty:
        print(f"🎯 Goals Analysis ({len(goals_df)} goals):")
        print(f"   👤 Top scorers:")
        top_scorers = goals_df['player_name'].value_counts().head(3)
        for player, goals in top_scorers.items():
            print(f"      {player}: {goals} goals")
    else:
        print("🎯 No goals found in the sample data")
    print()
    
    # Shots analysis
    shots_df = connected_df[connected_df['event_type'] == 'Shot'].copy()
    if not shots_df.empty:
        print(f"🎯 Shots Analysis ({len(shots_df)} shots):")
        print(f"   📊 Shots by match:")
        shots_by_match = shots_df.groupby(['home_team', 'away_team']).size().head(5)
        for (home, away), shots in shots_by_match.items():
            print(f"      {home} vs {away}: {shots} shots")
        print()
        
        print(f"   🏆 Top shooters:")
        top_shooters = shots_df['player_name'].value_counts().head(5)
        for player, shots in top_shooters.items():
            print(f"      {player}: {shots} shots")
    print()
    
    # Passing analysis
    passes_df = connected_df[connected_df['event_type'] == 'Pass'].copy()
    if not passes_df.empty:
        print(f"⚽ Passing Analysis ({len(passes_df):,} passes):")
        print(f"   📊 Passes by team:")
        passes_by_team = passes_df['team_name'].value_counts().head(5)
        for team, passes in passes_by_team.items():
            print(f"      {team}: {passes:,} passes")
        print()
        
        print(f"   🏆 Top passers:")
        top_passers = passes_df['player_name'].value_counts().head(5)
        for player, passes in top_passers.items():
            print(f"      {player}: {passes:,} passes")
    print()
    
    # Commentary generation examples
    print("🎙️ COMMENTARY GENERATION EXAMPLES")
    print("-" * 40)
    
    # Find interesting events for commentary
    interesting_events = connected_df[
        (connected_df['event_type'].isin(['Goal', 'Shot', 'Yellow Card', 'Red Card', 'Substitution'])) &
        (connected_df['player_name'].notna())
    ].head(10)
    
    print("📋 Sample commentary events:")
    for i, (_, event) in enumerate(interesting_events.iterrows(), 1):
        minute = event['minute']
        event_type = event['event_type']
        player = event['player_name']
        home_team = event['home_team']
        away_team = event['away_team']
        
        # Generate commentary text
        if event_type == 'Goal':
            commentary = f"⚽ GOAL! {player} scores for {event['team_name']} in the {minute}th minute!"
        elif event_type == 'Shot':
            commentary = f"🎯 Shot attempt by {player} in the {minute}th minute"
        elif event_type == 'Yellow Card':
            commentary = f"🟨 Yellow card for {player} in the {minute}th minute"
        elif event_type == 'Red Card':
            commentary = f"🟥 Red card! {player} is sent off in the {minute}th minute"
        elif event_type == 'Substitution':
            commentary = f"🔄 Substitution in the {minute}th minute"
        else:
            commentary = f"📝 {event_type} by {player} in the {minute}th minute"
        
        print(f"   {i}. {commentary} | {home_team} vs {away_team}")
    
    print()
    
    # Move quality prediction examples
    print("🔮 MOVE QUALITY PREDICTION EXAMPLES")
    print("-" * 40)
    
    # Analyze pass sequences
    print("📊 Pass sequence analysis:")
    if not passes_df.empty:
        # Group passes by match and team to find sequences
        pass_sequences = passes_df.groupby(['match_id', 'team_name']).size().reset_index(name='pass_count')
        top_sequences = pass_sequences.nlargest(5, 'pass_count')
        
        print("   🏆 Top passing sequences:")
        for _, seq in top_sequences.iterrows():
            match_info = matches_df[matches_df['match_id'] == seq['match_id']].iloc[0]
            print(f"      {seq['team_name']}: {seq['pass_count']} passes | {match_info['home_team_name']} vs {match_info['away_team_name']}")
    
    print()
    
    # Location analysis (if available)
    if 'location_x' in connected_df.columns and 'location_y' in connected_df.columns:
        print("📍 Location analysis:")
        events_with_location = connected_df[
            (connected_df['location_x'].notna()) & 
            (connected_df['location_y'].notna())
        ]
        
        if not events_with_location.empty:
            print(f"   📊 Events with location data: {len(events_with_location):,}")
            print(f"   🎯 Average shot location: x={events_with_location[events_with_location['event_type'] == 'Shot']['location_x'].mean():.1f}, y={events_with_location[events_with_location['event_type'] == 'Shot']['location_y'].mean():.1f}")
    
    print()
    
    # Data connections summary
    print("🔗 DATA CONNECTIONS SUMMARY")
    print("-" * 30)
    print("✅ Available connections:")
    print(f"   📊 Events ↔ Matches: via match_id ({connected_df['match_id'].nunique()} matches)")
    print(f"   👥 Events ↔ Players: via player_id ({connected_df['player_id'].nunique()} unique players)")
    print(f"   🏟️  Events ↔ Teams: via team_id ({connected_df['team_id'].nunique()} teams)")
    print(f"   ⏰ Events ↔ Time: via minute/second ({connected_df['minute'].max()} minutes covered)")
    
    print()
    
    # Next steps
    print("🎯 NEXT STEPS FOR YOUR PROJECT")
    print("-" * 35)
    print("1. 🎙️  Commentary Generation:")
    print("   - Use connected_df to create real-time commentary")
    print("   - Combine event_type + player_name + minute for narrative")
    print("   - Add context using team names and match info")
    print()
    print("2. 🔮 Move Quality Prediction:")
    print("   - Analyze pass sequences leading to goals/shots")
    print("   - Use location data (x,y coordinates) for spatial analysis")
    print("   - Create features from event sequences")
    print()
    print("3. 📊 Advanced Analysis:")
    print("   - Player performance across matches")
    print("   - Team tactical patterns")
    print("   - Event clustering and classification")
    print()
    print("4. 🧠 Text Analysis Integration:")
    print("   - NLP on event descriptions")
    print("   - Sentiment analysis of commentary")
    print("   - Auto-generated match reports")
    
    print()
    print("📁 Files available:")
    print(f"   - {data_folder}/matches.csv - Basic match information")
    print(f"   - {data_folder}/events.csv - All match events")
    print(f"   - {data_folder}/lineups.csv - Player lineups")
    print(f"   - {data_folder}/connected_data.csv - Full connected dataset")
    
    return {
        'matches': matches_df,
        'events': events_df,
        'lineups': lineups_df,
        'connected': connected_df
    }

if __name__ == "__main__":
    # Run the analysis
    data = analyze_euro_2024_data()
    
    print("\n🚀 Ready to start your Euro 2024 project!")
    print("Load the data with: pd.read_csv('euro_2024_data/connected_data.csv')") 