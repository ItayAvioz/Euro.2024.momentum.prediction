#!/usr/bin/env python3
"""
Detailed 360° Data Analysis for Euro 2024
Focus on spatial analysis and practical applications
"""

import pandas as pd
import numpy as np

def analyze_360_structure():
    """Detailed analysis of 360° data structure"""
    print("🎯 DETAILED 360° DATA STRUCTURE ANALYSIS")
    print("=" * 50)
    
    try:
        # Load a chunk of 360° data
        df_360 = pd.read_csv('euro_2024_complete/data_360_complete.csv', nrows=1000)
        
        print(f"📊 Loaded {len(df_360):,} 360° data points for analysis")
        print()
        
        print("📋 Column Analysis:")
        for i, col in enumerate(df_360.columns, 1):
            sample_val = df_360[col].iloc[0] if not df_360[col].isna().all() else "N/A"
            dtype = df_360[col].dtype
            print(f"   {i:2d}. {col:20s} ({dtype}) - Sample: {str(sample_val)[:50]}")
        
        print()
        
        # Analyze freeze_frame data (contains player positions)
        if 'freeze_frame' in df_360.columns:
            print("🎯 FREEZE FRAME ANALYSIS (Player Positions):")
            non_null_frames = df_360[df_360['freeze_frame'].notna()]
            if not non_null_frames.empty:
                print(f"   📍 Frames with position data: {len(non_null_frames):,}")
                print(f"   📊 Coverage: {len(non_null_frames)/len(df_360)*100:.1f}% of tracking points")
                
                # Sample freeze frame structure
                sample_frame = non_null_frames['freeze_frame'].iloc[0]
                print(f"   📋 Sample frame structure: {str(sample_frame)[:100]}...")
            
        print()
        
        # Match coverage
        if 'match_id' in df_360.columns:
            matches = df_360['match_id'].nunique()
            print(f"🏟️ Match Coverage:")
            print(f"   📊 Matches with 360° data: {matches}")
            
            match_counts = df_360['match_id'].value_counts().head(5)
            print(f"   📈 Top matches by tracking points:")
            for i, (match_id, count) in enumerate(match_counts.items(), 1):
                print(f"      {i}. Match {match_id}: {count:,} tracking points")
        
        return df_360
        
    except Exception as e:
        print(f"❌ Error loading 360° data: {e}")
        return create_example_360_analysis()

def create_example_360_analysis():
    """Create example 360° analysis when data is not accessible"""
    print("📝 EXAMPLE 360° DATA APPLICATIONS")
    print("=" * 40)
    
    print("🎯 Spatial Analysis Capabilities:")
    print("   ✅ Player Heat Maps:")
    print("      - Track player movement across the field")
    print("      - Identify preferred positions and zones")
    print("      - Compare players across different matches")
    
    print("   ✅ Team Formation Analysis:")
    print("      - Analyze team shape during different phases")
    print("      - Track formation changes throughout match")
    print("      - Compare attacking vs defensive positioning")
    
    print("   ✅ Space Creation Analysis:")
    print("      - Measure space between players")
    print("      - Identify gaps in defensive lines")
    print("      - Track player movements creating space")
    
    print("   ✅ Pressure Analysis:")
    print("      - Calculate defensive pressure on ball carrier")
    print("      - Measure time/space available for decisions")
    print("      - Identify pressing triggers and patterns")
    
    return None

def spatial_analysis_examples():
    """Examples of spatial analysis for move quality prediction"""
    print("\n🔮 SPATIAL ANALYSIS FOR MOVE QUALITY PREDICTION")
    print("=" * 55)
    
    print("📊 PASS QUALITY PREDICTION:")
    print("   🎯 Spatial Features:")
    print("      - Pass distance (Euclidean distance)")
    print("      - Pass angle relative to goal")
    print("      - Number of defenders in passing lane")
    print("      - Receiver's space (nearest defender distance)")
    print("      - Passer's pressure (nearest defender distance)")
    
    print("   📈 Quality Scoring Example:")
    print("      def calculate_pass_quality(passer_pos, receiver_pos, defenders):")
    print("          distance = euclidean_distance(passer_pos, receiver_pos)")
    print("          pressure = min_distance_to_defenders(passer_pos, defenders)")
    print("          space = min_distance_to_defenders(receiver_pos, defenders)")
    print("          angle = angle_to_goal(receiver_pos)")
    print("          return weighted_score(distance, pressure, space, angle)")
    
    print()
    print("🎯 SHOT QUALITY PREDICTION:")
    print("   🎯 Spatial Features:")
    print("      - Distance to goal")
    print("      - Angle to goal (goal mouth visibility)")
    print("      - Goalkeeper position")
    print("      - Defender positions and proximity")
    print("      - Shot location (box, penalty area, etc.)")
    
    print("   📈 Quality Scoring Example:")
    print("      def calculate_shot_quality(shot_pos, goal_pos, gk_pos, defenders):")
    print("          distance = euclidean_distance(shot_pos, goal_pos)")
    print("          angle = calculate_goal_angle(shot_pos)")
    print("          gk_distance = euclidean_distance(shot_pos, gk_pos)")
    print("          defender_pressure = calculate_pressure(shot_pos, defenders)")
    print("          return xG_model(distance, angle, gk_distance, defender_pressure)")

def commentary_enhancement_examples():
    """Examples of using 360° data for commentary enhancement"""
    print("\n🎙️ COMMENTARY ENHANCEMENT WITH 360° DATA")
    print("=" * 45)
    
    print("📝 SPATIAL CONTEXT TEMPLATES:")
    
    templates = {
        "Pass with Space": "{player} has time and space, plays it to {receiver}",
        "Pass under Pressure": "{player} under pressure from {defender}, quick ball to {receiver}",
        "Long Pass": "{player} switches play with a {distance}m pass to {receiver}",
        "Through Ball": "{player} slides it through for {receiver} to chase",
        "Shot with Angle": "{player} shoots from a tight angle {distance}m out",
        "Shot with Space": "{player} has space and time, {distance}m shot!",
        "Crowded Box": "{player} shoots in a crowded penalty area",
        "Counter Attack": "Quick counter! {player} breaks forward with space ahead"
    }
    
    print("   🎯 Enhanced Commentary Examples:")
    for situation, template in templates.items():
        print(f"      {situation}: {template}")
    
    print()
    print("📊 CONTEXT CALCULATION EXAMPLES:")
    print("   def get_spatial_context(player_pos, all_positions):")
    print("       # Calculate space around player")
    print("       nearest_opponents = find_nearest_opponents(player_pos, all_positions)")
    print("       space_available = calculate_space(player_pos, nearest_opponents)")
    print("       ")
    print("       if space_available > 10:  # meters")
    print("           return 'has time and space'")
    print("       elif space_available < 3:")
    print("           return 'under intense pressure'")
    print("       else:")
    print("           return 'tightly marked'")

def tactical_analysis_insights():
    """Tactical analysis insights from 360° data"""
    print("\n⚔️ TACTICAL ANALYSIS INSIGHTS")
    print("=" * 35)
    
    print("🎯 FORMATION ANALYSIS:")
    print("   📊 Team Shape Metrics:")
    print("      - Team width (distance between widest players)")
    print("      - Team length (distance between deepest/highest players)")
    print("      - Team compactness (average distance between players)")
    print("      - Defensive line height")
    print("      - Midfield density")
    
    print()
    print("🎯 PRESSING ANALYSIS:")
    print("   📊 Pressure Metrics:")
    print("      - PPDA (Passes per Defensive Action)")
    print("      - High press success rate")
    print("      - Time to pressure (seconds from ball receipt to pressure)")
    print("      - Pressure triggers (situations that start pressing)")
    
    print()
    print("🎯 SPACE ANALYSIS:")
    print("   📊 Space Metrics:")
    print("      - Available space per player")
    print("      - Space creation through movement")
    print("      - Overloads (numerical advantages in areas)")
    print("      - Gaps between lines")

def main():
    """Main analysis function"""
    print("🎯 DETAILED 360° POSITION ANALYSIS")
    print("=" * 50)
    print("📊 Deep dive into spatial data for move quality prediction")
    print()
    
    # Run detailed analyses
    data_360 = analyze_360_structure()
    spatial_analysis_examples()
    commentary_enhancement_examples()
    tactical_analysis_insights()
    
    print("\n✅ DETAILED ANALYSIS COMPLETE!")
    print("🎯 Your 360° data enables:")
    print("   - Precise spatial context for commentary")
    print("   - Advanced move quality prediction")
    print("   - Tactical pattern recognition")
    print("   - Real-time space and pressure analysis")

if __name__ == "__main__":
    main() 