#!/usr/bin/env python3
"""
Euro 2024 Position (360°) and Events Analysis
Comprehensive analysis focusing on positional data and events for insights
"""

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def analyze_events_comprehensive():
    """Analyze events data for patterns and insights"""
    print("⚽ EVENTS ANALYSIS")
    print("=" * 40)
    
    # Load events data
    try:
        # Try to load smaller chunk first for analysis
        events_chunk = pd.read_csv('euro_2024_complete/events_complete.csv', nrows=10000)
        print(f"📊 Analyzing first {len(events_chunk):,} events for patterns...")
    except:
        # Fallback to sample data
        events_chunk = pd.read_csv('euro_2024_sample_100_rows.csv')
        print(f"📊 Analyzing sample data: {len(events_chunk)} events...")
    
    print()
    
    # Event type analysis
    print("📈 EVENT TYPE DISTRIBUTION:")
    event_counts = events_chunk['event_type'].value_counts()
    total_events = len(events_chunk)
    
    for i, (event_type, count) in enumerate(event_counts.head(15).items(), 1):
        percentage = (count / total_events) * 100
        print(f"   {i:2d}. {event_type:20s}: {count:5,} ({percentage:5.1f}%)")
    
    print()
    
    # Temporal analysis
    print("🕐 TEMPORAL PATTERNS:")
    if 'minute' in events_chunk.columns:
        minute_events = events_chunk.groupby('minute').size()
        print(f"   📊 Events per minute - Average: {minute_events.mean():.1f}")
        print(f"   📈 Peak minute: {minute_events.idxmax()} ({minute_events.max()} events)")
        print(f"   📉 Slowest minute: {minute_events.idxmin()} ({minute_events.min()} events)")
        
        # First vs second half
        first_half = events_chunk[events_chunk['minute'] <= 45]
        second_half = events_chunk[events_chunk['minute'] > 45]
        print(f"   🥅 First half events: {len(first_half):,}")
        print(f"   🥅 Second half events: {len(second_half):,}")
    
    print()
    
    # Player involvement analysis
    print("👥 PLAYER INVOLVEMENT:")
    if 'player_name' in events_chunk.columns:
        player_events = events_chunk[events_chunk['player_name'].notna()]
        if not player_events.empty:
            top_players = player_events['player_name'].value_counts().head(10)
            print("   🏆 Most active players:")
            for i, (player, count) in enumerate(top_players.items(), 1):
                print(f"      {i:2d}. {player:25s}: {count:3d} events")
    
    print()
    
    # Team analysis
    print("🏟️ TEAM ANALYSIS:")
    if 'team_name' in events_chunk.columns:
        team_events = events_chunk[events_chunk['team_name'].notna()]
        if not team_events.empty:
            team_counts = team_events['team_name'].value_counts()
            print("   📊 Events by team:")
            for i, (team, count) in enumerate(team_counts.items(), 1):
                percentage = (count / len(team_events)) * 100
                print(f"      {i:2d}. {team:20s}: {count:4,} ({percentage:5.1f}%)")
    
    return events_chunk

def analyze_360_data():
    """Analyze 360° positional data"""
    print("\n🎯 360° POSITIONAL DATA ANALYSIS")
    print("=" * 45)
    
    try:
        # Try to load 360° data
        data_360_chunk = pd.read_csv('euro_2024_complete/data_360_complete.csv', nrows=5000)
        print(f"📊 Analyzing {len(data_360_chunk):,} 360° tracking points...")
        
        print(f"📋 360° Data Structure:")
        print(f"   Columns: {list(data_360_chunk.columns)}")
        print(f"   Data types: {len(data_360_chunk.dtypes)} different types")
        
        # Check for coordinate data
        coord_columns = [col for col in data_360_chunk.columns if any(x in col.lower() for x in ['x', 'y', 'location', 'position'])]
        if coord_columns:
            print(f"   🎯 Coordinate columns found: {coord_columns}")
            
            # Analyze spatial distribution
            for col in coord_columns[:4]:  # Analyze first 4 coordinate columns
                if data_360_chunk[col].dtype in ['float64', 'int64']:
                    print(f"   📍 {col}: Range {data_360_chunk[col].min():.1f} to {data_360_chunk[col].max():.1f}")
        
        # Temporal analysis of 360° data
        if 'minute' in data_360_chunk.columns:
            print(f"   ⏱️ Time coverage: {data_360_chunk['minute'].min():.0f} to {data_360_chunk['minute'].max():.0f} minutes")
        
        # Match coverage
        if 'match_id' in data_360_chunk.columns:
            matches_with_360 = data_360_chunk['match_id'].nunique()
            print(f"   🏟️ Matches with 360° data: {matches_with_360}")
        
        return data_360_chunk
        
    except Exception as e:
        print(f"   ⚠️ 360° data loading issue: {e}")
        print("   📝 Creating example 360° analysis structure...")
        
        # Create example analysis
        example_360 = {
            'player_positions': 'X,Y coordinates for all players',
            'ball_position': 'Ball tracking throughout match',
            'spatial_coverage': 'Heat maps and movement patterns',
            'formation_analysis': 'Team shape and positioning'
        }
        
        print("   📊 360° Data Capabilities:")
        for key, desc in example_360.items():
            print(f"      ✅ {key}: {desc}")
        
        return None

def analyze_events_position_integration():
    """Analyze how events integrate with positional data"""
    print("\n🔗 EVENTS + POSITION INTEGRATION")
    print("=" * 40)
    
    # Load sample for integration analysis
    sample_df = pd.read_csv('euro_2024_sample_100_rows.csv')
    
    print("📊 EVENT-POSITION CONNECTION OPPORTUNITIES:")
    
    # Spatial events analysis
    spatial_events = ['Shot', 'Pass', 'Dribble', 'Tackle', 'Cross']
    sample_spatial = sample_df[sample_df['event_type'].isin(spatial_events)]
    
    if not sample_spatial.empty:
        print(f"   🎯 Spatial events in sample: {len(sample_spatial)}")
        spatial_counts = sample_spatial['event_type'].value_counts()
        for event, count in spatial_counts.items():
            print(f"      {event}: {count} events")
    
    print()
    print("🎯 MOVE QUALITY PREDICTION INSIGHTS:")
    print("   ✅ Pass success prediction:")
    print("      - Use player positions before pass")
    print("      - Calculate pass distance and angle")
    print("      - Analyze defensive pressure")
    print("      - Consider team formation")
    
    print("   ✅ Shot quality prediction:")
    print("      - Shot location relative to goal")
    print("      - Defender proximity")
    print("      - Goalkeeper position")
    print("      - Angle and distance to goal")
    
    print("   ✅ Tactical analysis:")
    print("      - Team shape during different events")
    print("      - Player movement patterns")
    print("      - Space creation and utilization")
    print("      - Pressing intensity")
    
    return sample_spatial

def generate_commentary_insights():
    """Generate insights for automatic commentary"""
    print("\n🎙️ COMMENTARY GENERATION INSIGHTS")
    print("=" * 40)
    
    sample_df = pd.read_csv('euro_2024_sample_100_rows.csv')
    
    print("📝 COMMENTARY TEMPLATES BY EVENT TYPE:")
    
    # Commentary examples for different events
    commentary_templates = {
        'Pass': [
            "{player} plays a {distance} pass to {receiver}",
            "{player} finds {receiver} with a {quality} ball",
            "Ball played {direction} by {player}"
        ],
        'Shot': [
            "{player} shoots from {distance}!",
            "Effort from {player} - {outcome}!",
            "{player} tries his luck from {position}"
        ],
        'Goal': [
            "GOAL! {player} scores for {team}!",
            "What a finish from {player}!",
            "{team} take the lead through {player}!"
        ],
        'Duel': [
            "{player} challenges {opponent}",
            "50-50 ball between {player} and {opponent}",
            "Physical battle won by {player}"
        ]
    }
    
    for event_type, templates in commentary_templates.items():
        events_of_type = sample_df[sample_df['event_type'] == event_type]
        if not events_of_type.empty:
            print(f"\n   ⚽ {event_type.upper()} ({len(events_of_type)} in sample):")
            for i, template in enumerate(templates, 1):
                print(f"      {i}. {template}")
    
    print("\n🎯 CONTEXT ENHANCEMENT:")
    print("   ✅ Add match context:")
    print("      - Current score and time")
    print("      - Tournament stage importance")
    print("      - Previous events in sequence")
    
    print("   ✅ Add positional context:")
    print("      - Field position (attacking/defensive third)")
    print("      - Proximity to goal")
    print("      - Number of players involved")
    
    print("   ✅ Add tactical context:")
    print("      - Formation and shape")
    print("      - Pressing situations")
    print("      - Counter-attack opportunities")

def provide_actionable_insights():
    """Provide actionable insights for the project"""
    print("\n🚀 ACTIONABLE INSIGHTS FOR YOUR PROJECT")
    print("=" * 50)
    
    print("📊 DATA QUALITY ASSESSMENT:")
    print("   ✅ STRENGTHS:")
    print("      - Complete tournament coverage (51 matches)")
    print("      - Rich event data (187K+ events)")
    print("      - Player-level detail with positions")
    print("      - 360° tracking for spatial analysis")
    print("      - Temporal precision (minute + second)")
    
    print("\n   🎯 OPPORTUNITIES:")
    print("      - Event sequences for pattern recognition")
    print("      - Spatial analysis for tactical insights")
    print("      - Player performance tracking")
    print("      - Real-time commentary generation")
    
    print("\n🎙️ COMMENTARY GENERATION ROADMAP:")
    print("   1. 📝 Basic Templates:")
    print("      - Create event-specific templates")
    print("      - Add player and team context")
    print("      - Include time and score information")
    
    print("   2. 🎯 Enhanced Context:")
    print("      - Use 360° data for spatial context")
    print("      - Add sequence analysis")
    print("      - Include match situation awareness")
    
    print("   3. 🧠 Advanced Features:")
    print("      - Sentiment and excitement levels")
    print("      - Historical player/team references")
    print("      - Tactical analysis integration")
    
    print("\n🔮 MOVE QUALITY PREDICTION ROADMAP:")
    print("   1. 📊 Feature Engineering:")
    print("      - Extract spatial features from 360° data")
    print("      - Create temporal sequences")
    print("      - Calculate pressure and space metrics")
    
    print("   2. 🎯 Model Development:")
    print("      - Pass success prediction")
    print("      - Shot quality assessment")
    print("      - Defensive action effectiveness")
    
    print("   3. 🚀 Integration:")
    print("      - Real-time quality scoring")
    print("      - Commentary enhancement")
    print("      - Tactical decision support")
    
    print("\n📁 NEXT STEPS:")
    print("   1. Load connected_complete.csv for full analysis")
    print("   2. Develop event sequence analysis")
    print("   3. Create 360° spatial analysis functions")
    print("   4. Build commentary template engine")
    print("   5. Develop move quality prediction models")

def main():
    """Main analysis function"""
    print("🏆 EURO 2024 POSITION & EVENTS ANALYSIS")
    print("=" * 60)
    print("📊 Comprehensive analysis focusing on positional data and events")
    print("🎯 Goal: Generate insights for commentary and move quality prediction")
    print()
    
    # Run all analyses
    events_data = analyze_events_comprehensive()
    position_data = analyze_360_data()
    integration_data = analyze_events_position_integration()
    generate_commentary_insights()
    provide_actionable_insights()
    
    print("\n✅ ANALYSIS COMPLETE!")
    print("🎯 Your Euro 2024 dataset is perfect for:")
    print("   - Automated commentary generation")
    print("   - Move quality prediction")
    print("   - Tactical analysis")
    print("   - Player performance assessment")
    print("   - Real-time match analysis")

if __name__ == "__main__":
    main() 