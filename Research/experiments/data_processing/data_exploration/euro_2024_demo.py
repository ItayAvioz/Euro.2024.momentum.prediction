#!/usr/bin/env python3
"""
Euro 2024 Data Demo
Quick demonstration of how to use the connected Euro 2024 data for your project
"""

import pandas as pd
import numpy as np

def load_euro_2024_data():
    """Load the Euro 2024 connected data"""
    print("🏆 Loading Euro 2024 Connected Data")
    print("=" * 40)
    
    # Load the main connected dataset
    df = pd.read_csv('euro_2024_data/connected_data.csv')
    
    print(f"✅ Loaded {len(df):,} events from Euro 2024")
    print(f"📊 Columns: {len(df.columns)} columns")
    print(f"🏟️  Matches: {df['match_id'].nunique()}")
    print(f"👥 Players: {df['player_id'].nunique()}")
    print(f"🏳️ Teams: {df['team_id'].nunique()}")
    print()
    
    return df

def demo_commentary_generation(df):
    """Demo automatic commentary generation"""
    print("🎙️ COMMENTARY GENERATION DEMO")
    print("-" * 30)
    
    # Get interesting events
    shots = df[df['event_type'] == 'Shot'].copy()
    substitutions = df[df['event_type'] == 'Substitution'].copy()
    
    print("📋 Sample auto-generated commentary:")
    print()
    
    # Commentary for shots
    if not shots.empty:
        for i, (_, shot) in enumerate(shots.head(5).iterrows(), 1):
            minute = shot['minute']
            player = shot['player_name']
            team = shot['team_name']
            match = f"{shot['home_team']} vs {shot['away_team']}"
            
            commentary = f"🎯 Minute {minute}: {player} ({team}) attempts a shot! | {match}"
            print(f"{i}. {commentary}")
    
    print()
    
    # Commentary for substitutions
    if not substitutions.empty:
        print("🔄 Substitution commentary:")
        for i, (_, sub) in enumerate(substitutions.head(3).iterrows(), 1):
            minute = sub['minute']
            team = sub['team_name']
            match = f"{sub['home_team']} vs {sub['away_team']}"
            
            commentary = f"🔄 Minute {minute}: Tactical change by {team} | {match}"
            print(f"{i}. {commentary}")
    
    print()

def demo_move_quality_prediction(df):
    """Demo move quality prediction features"""
    print("🔮 MOVE QUALITY PREDICTION DEMO")
    print("-" * 35)
    
    # Analyze pass sequences
    passes = df[df['event_type'] == 'Pass'].copy()
    
    if not passes.empty:
        print("📊 Pass Quality Analysis:")
        
        # Group by team and match to analyze passing performance
        pass_stats = passes.groupby(['match_id', 'team_name']).agg({
            'player_id': 'count',  # Total passes
            'minute': ['min', 'max']  # Time span
        }).round(2)
        
        pass_stats.columns = ['total_passes', 'first_pass_minute', 'last_pass_minute']
        pass_stats = pass_stats.reset_index()
        
        # Calculate pass rate (passes per minute)
        pass_stats['pass_rate'] = pass_stats['total_passes'] / (pass_stats['last_pass_minute'] - pass_stats['first_pass_minute'] + 1)
        
        print("\n🏆 Top team passing performances:")
        top_passing = pass_stats.nlargest(5, 'total_passes')
        
        for i, (_, team) in enumerate(top_passing.iterrows(), 1):
            print(f"{i}. {team['team_name']}: {team['total_passes']} passes ({team['pass_rate']:.1f} passes/min)")
    
    print()
    
    # Analyze shot quality
    shots = df[df['event_type'] == 'Shot'].copy()
    
    if not shots.empty:
        print("🎯 Shot Quality Analysis:")
        
        # Group by player
        shot_stats = shots.groupby('player_name').agg({
            'minute': 'count',  # Total shots
            'match_id': 'nunique'  # Matches played
        }).reset_index()
        
        shot_stats.columns = ['player_name', 'total_shots', 'matches_played']
        shot_stats['shots_per_match'] = shot_stats['total_shots'] / shot_stats['matches_played']
        
        print("\n🏆 Top shooters:")
        top_shooters = shot_stats.nlargest(5, 'total_shots')
        
        for i, (_, player) in enumerate(top_shooters.iterrows(), 1):
            print(f"{i}. {player['player_name']}: {player['total_shots']} shots ({player['shots_per_match']:.1f} shots/match)")
    
    print()

def demo_match_analysis(df):
    """Demo match-by-match analysis"""
    print("📊 MATCH ANALYSIS DEMO")
    print("-" * 25)
    
    # Load match info
    matches = pd.read_csv('euro_2024_data/matches.csv')
    
    print("🏟️ Match Overview:")
    sample_matches = matches[['home_team_name', 'away_team_name', 'home_score', 'away_score', 'stage']].head(5)
    
    for i, (_, match) in enumerate(sample_matches.iterrows(), 1):
        result = f"{match['home_team_name']} {match['home_score']}-{match['away_score']} {match['away_team_name']}"
        print(f"{i}. {result} | {match['stage']}")
    
    print()
    
    # Event distribution by match
    print("📈 Event Distribution:")
    event_counts = df.groupby(['home_team', 'away_team', 'event_type']).size().reset_index(name='count')
    
    # Show top events for one match
    sample_match = event_counts[event_counts['event_type'].isin(['Pass', 'Shot', 'Duel'])].head(10)
    
    for _, event in sample_match.iterrows():
        match_name = f"{event['home_team']} vs {event['away_team']}"
        print(f"   {match_name}: {event['count']} {event['event_type']}s")
    
    print()

def demo_player_performance(df):
    """Demo player performance analysis"""
    print("👥 PLAYER PERFORMANCE DEMO")
    print("-" * 30)
    
    # Player activity across events
    player_stats = df.groupby('player_name').agg({
        'event_type': 'count',  # Total events
        'match_id': 'nunique',  # Matches played
        'minute': ['min', 'max']  # Active time range
    }).reset_index()
    
    player_stats.columns = ['player_name', 'total_events', 'matches_played', 'first_event_minute', 'last_event_minute']
    player_stats['events_per_match'] = player_stats['total_events'] / player_stats['matches_played']
    
    print("🏆 Most active players:")
    top_players = player_stats.nlargest(10, 'total_events')
    
    for i, (_, player) in enumerate(top_players.iterrows(), 1):
        if pd.notna(player['player_name']):
            print(f"{i}. {player['player_name']}: {player['total_events']} events ({player['events_per_match']:.1f} events/match)")
    
    print()
    
    # Position analysis
    lineups = pd.read_csv('euro_2024_data/lineups.csv')
    
    if not lineups.empty:
        print("📍 Position Analysis:")
        position_counts = lineups['position'].value_counts().head(5)
        
        for pos, count in position_counts.items():
            if pd.notna(pos):
                print(f"   {pos}: {count} players")
    
    print()

def main():
    """Main demo function"""
    print("🚀 Euro 2024 Data Demo")
    print("=" * 50)
    print("This demo shows how to use the connected Euro 2024 data")
    print("for commentary generation and move quality prediction.")
    print()
    
    # Load data
    df = load_euro_2024_data()
    
    # Run demos
    demo_commentary_generation(df)
    demo_move_quality_prediction(df)
    demo_match_analysis(df)
    demo_player_performance(df)
    
    print("🎯 NEXT STEPS FOR YOUR PROJECT")
    print("=" * 40)
    print("1. 🎙️ Commentary Generation:")
    print("   - Expand the commentary templates")
    print("   - Add context from previous events")
    print("   - Include team tactics and formations")
    print()
    print("2. 🔮 Move Quality Prediction:")
    print("   - Create features from event sequences")
    print("   - Use location data for spatial analysis")
    print("   - Build ML models to predict shot success")
    print()
    print("3. 📊 Advanced Analysis:")
    print("   - Player network analysis")
    print("   - Team performance metrics")
    print("   - Tactical pattern recognition")
    print()
    print("4. 🧠 Text Analysis:")
    print("   - NLP on event descriptions")
    print("   - Sentiment analysis")
    print("   - Auto-generated match reports")
    print()
    print("📁 Your data is ready in:")
    print("   - euro_2024_data/connected_data.csv (main dataset)")
    print("   - euro_2024_data/matches.csv (match info)")
    print("   - euro_2024_data/events.csv (all events)")
    print("   - euro_2024_data/lineups.csv (player lineups)")

if __name__ == "__main__":
    main() 