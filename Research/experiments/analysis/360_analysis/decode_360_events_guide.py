#!/usr/bin/env python3
"""
Complete Guide to Decoding 360° Data and Events
Focus on time synchronization and data structure parsing
"""

import pandas as pd
import numpy as np
import json
import ast
from datetime import datetime, timedelta

def load_and_examine_data():
    """Load and examine the raw data structures"""
    print("🔍 DATA STRUCTURE EXAMINATION")
    print("=" * 50)
    
    # Load sample data
    try:
        events_df = pd.read_csv('euro_2024_sample_100_rows.csv')
        print(f"✅ Loaded {len(events_df)} events for analysis")
        
        # Try to load 360° data
        data_360_df = pd.read_csv('euro_2024_complete/data_360_complete.csv', nrows=10)
        print(f"✅ Loaded {len(data_360_df)} 360° tracking points")
        
        return events_df, data_360_df
    except Exception as e:
        print(f"⚠️ Data loading note: {e}")
        return create_example_structures()

def create_example_structures():
    """Create example data structures for demonstration"""
    print("📝 Creating example data structures...")
    
    # Example events data
    events_example = pd.DataFrame({
        'match_id': [3942819, 3942819, 3942819],
        'minute': [23, 23, 24],
        'second': [15, 45, 12],
        'event_type': ['Pass', 'Ball Receipt*', 'Carry'],
        'player_name': ['Declan Rice', 'Jude Bellingham', 'Jude Bellingham'],
        'team_name': ['England', 'England', 'England'],
        'home_team': ['Netherlands', 'Netherlands', 'Netherlands'],
        'away_team': ['England', 'England', 'England']
    })
    
    # Example 360° data structure
    data_360_example = pd.DataFrame({
        'event_uuid': ['uuid-1', 'uuid-2', 'uuid-3'],
        'visible_area': [
            '[82.05, 80.0, 37.46, 80.0]',
            '[81.2, 79.5, 38.1, 79.8]',
            '[80.8, 79.2, 38.5, 79.5]'
        ],
        'freeze_frame': [
            "[{'teammate': True, 'actor': False, 'keeper': True, 'location': [22.7, 41.0]}]",
            "[{'teammate': False, 'actor': True, 'keeper': False, 'location': [45.2, 35.8]}]",
            "[{'teammate': True, 'actor': False, 'keeper': False, 'location': [50.1, 42.3]}]"
        ],
        'match_id': [3942819, 3942819, 3942819]
    })
    
    return events_example, data_360_example

def decode_time_columns(events_df):
    """Decode time-related columns in events data"""
    print("\n⏰ DECODING TIME COLUMNS")
    print("=" * 35)
    
    if 'minute' in events_df.columns and 'second' in events_df.columns:
        print("📊 TIME STRUCTURE ANALYSIS:")
        print(f"   🕐 Minute column: {events_df['minute'].dtype}")
        print(f"   🕐 Second column: {events_df['second'].dtype}")
        print(f"   📈 Time range: {events_df['minute'].min()}:{events_df['second'].min()} to {events_df['minute'].max()}:{events_df['second'].max()}")
        
        # Create combined timestamp
        events_df['timestamp_seconds'] = events_df['minute'] * 60 + events_df['second']
        events_df['time_display'] = events_df['minute'].astype(str) + ':' + events_df['second'].astype(str).str.zfill(2)
        
        print("\n✅ TIME DECODING EXAMPLES:")
        sample_times = events_df[['minute', 'second', 'timestamp_seconds', 'time_display']].head(5)
        for idx, row in sample_times.iterrows():
            print(f"   {idx+1}. Minute: {row['minute']}, Second: {row['second']} → {row['time_display']} ({row['timestamp_seconds']}s)")
        
        # Analyze time patterns
        print("\n📊 TIME PATTERN ANALYSIS:")
        time_gaps = events_df['timestamp_seconds'].diff().dropna()
        print(f"   ⏱️ Average time between events: {time_gaps.mean():.2f} seconds")
        print(f"   🏃 Fastest succession: {time_gaps.min():.2f} seconds")
        print(f"   🐌 Longest gap: {time_gaps.max():.2f} seconds")
        
        return events_df
    else:
        print("⚠️ Time columns not found in standard format")
        return events_df

def decode_360_freeze_frame(data_360_df):
    """Decode the freeze_frame column containing player positions"""
    print("\n🎯 DECODING 360° FREEZE FRAME DATA")
    print("=" * 40)
    
    if 'freeze_frame' in data_360_df.columns:
        print("📊 FREEZE FRAME STRUCTURE:")
        
        # Examine a sample freeze frame
        sample_frame = data_360_df['freeze_frame'].iloc[0]
        print(f"   📋 Raw freeze frame sample:")
        print(f"      {str(sample_frame)[:100]}...")
        
        # Parse freeze frame data
        def parse_freeze_frame(frame_str):
            """Parse a freeze frame string into structured data"""
            try:
                # Convert string to list of dictionaries
                if isinstance(frame_str, str):
                    frame_data = ast.literal_eval(frame_str)
                else:
                    frame_data = frame_str
                
                parsed_players = []
                for player in frame_data:
                    parsed_player = {
                        'is_teammate': player.get('teammate', False),
                        'is_actor': player.get('actor', False),
                        'is_keeper': player.get('keeper', False),
                        'x_position': player.get('location', [0, 0])[0],
                        'y_position': player.get('location', [0, 0])[1],
                        'player_id': player.get('player', {}).get('id', None) if 'player' in player else None,
                        'player_name': player.get('player', {}).get('name', None) if 'player' in player else None
                    }
                    parsed_players.append(parsed_player)
                
                return parsed_players
            except Exception as e:
                print(f"   ⚠️ Error parsing frame: {e}")
                return []
        
        # Parse first few freeze frames
        print("\n✅ PARSED FREEZE FRAME EXAMPLES:")
        for i in range(min(3, len(data_360_df))):
            frame = data_360_df['freeze_frame'].iloc[i]
            parsed = parse_freeze_frame(frame)
            
            print(f"\n   🎯 Frame {i+1} - {len(parsed)} players:")
            for j, player in enumerate(parsed[:5]):  # Show first 5 players
                role = "⚽" if player['is_actor'] else "🥅" if player['is_keeper'] else "👤"
                team = "🔵" if player['is_teammate'] else "🔴"
                print(f"      {j+1}. {role} {team} Position: ({player['x_position']:.1f}, {player['y_position']:.1f})")
        
        return parse_freeze_frame
    
    else:
        print("⚠️ Freeze frame column not found")
        return None

def decode_visible_area(data_360_df):
    """Decode the visible_area column"""
    print("\n📐 DECODING VISIBLE AREA DATA")
    print("=" * 35)
    
    if 'visible_area' in data_360_df.columns:
        print("📊 VISIBLE AREA STRUCTURE:")
        
        sample_area = data_360_df['visible_area'].iloc[0]
        print(f"   📋 Raw visible area sample: {sample_area}")
        
        def parse_visible_area(area_str):
            """Parse visible area string into coordinates"""
            try:
                if isinstance(area_str, str):
                    # Remove brackets and split by commas
                    coords = area_str.strip('[]').split(',')
                    coords = [float(x.strip()) for x in coords]
                else:
                    coords = area_str
                
                return {
                    'x_min': coords[0],
                    'y_min': coords[1], 
                    'x_max': coords[2],
                    'y_max': coords[3],
                    'width': coords[2] - coords[0],
                    'height': coords[3] - coords[1]
                }
            except Exception as e:
                print(f"   ⚠️ Error parsing visible area: {e}")
                return None
        
        # Parse examples
        print("\n✅ PARSED VISIBLE AREA EXAMPLES:")
        for i in range(min(3, len(data_360_df))):
            area = data_360_df['visible_area'].iloc[i]
            parsed = parse_visible_area(area)
            
            if parsed:
                print(f"   {i+1}. X: {parsed['x_min']:.1f} to {parsed['x_max']:.1f} (width: {parsed['width']:.1f})")
                print(f"      Y: {parsed['y_min']:.1f} to {parsed['y_max']:.1f} (height: {parsed['height']:.1f})")
        
        return parse_visible_area
    
    else:
        print("⚠️ Visible area column not found")
        return None

def synchronize_events_and_360(events_df, data_360_df):
    """Show how to synchronize events with 360° data"""
    print("\n🔗 SYNCHRONIZING EVENTS WITH 360° DATA")
    print("=" * 45)
    
    print("📊 SYNCHRONIZATION METHODS:")
    print("   1️⃣ By event_uuid (direct match)")
    print("   2️⃣ By match_id + timestamp")
    print("   3️⃣ By match_id + event sequence")
    
    # Method 1: Direct UUID matching (ideal)
    print("\n✅ METHOD 1 - UUID MATCHING:")
    print("   if 'event_uuid' in both datasets:")
    print("      merged = events_df.merge(data_360_df, on='event_uuid', how='inner')")
    print("      # This gives exact event-to-position matching")
    
    # Method 2: Time-based matching
    print("\n✅ METHOD 2 - TIME-BASED MATCHING:")
    print("   # Convert events to timestamps")
    print("   events_df['timestamp'] = events_df['minute'] * 60 + events_df['second']")
    print("   # Match by closest timestamp within same match")
    print("   # This requires more complex logic for fuzzy matching")
    
    # Method 3: Sequence matching
    print("\n✅ METHOD 3 - SEQUENCE MATCHING:")
    print("   # Use event order within match")
    print("   events_df['event_order'] = events_df.groupby('match_id').cumcount()")
    print("   # Match by event sequence number")
    
    # Show example of creating synchronized dataset
    if len(events_df) > 0 and len(data_360_df) > 0:
        print("\n📝 EXAMPLE SYNCHRONIZED DATA:")
        print("   Event + 360° Data Structure:")
        print("   ┌─────────────────────────────────────────────────────────────┐")
        print("   │ match_id | minute | second | event_type | player_positions │")
        print("   ├─────────────────────────────────────────────────────────────┤")
        
        # Create example synchronized row
        for i in range(min(2, len(events_df))):
            event = events_df.iloc[i]
            print(f"   │ {event['match_id']:<8} | {event['minute']:<6} | {event['second']:<6} | {event['event_type']:<10} | [22 players]   │")
        
        print("   └─────────────────────────────────────────────────────────────┘")

def demonstrate_practical_applications():
    """Demonstrate practical applications of decoded data"""
    print("\n🚀 PRACTICAL APPLICATIONS")
    print("=" * 35)
    
    print("🎯 1. REAL-TIME COMMENTARY GENERATION:")
    print("   def generate_commentary(event, positions):")
    print("       player = event['player_name']")
    print("       minute = event['minute']")
    print("       event_type = event['event_type']")
    print("       ")
    print("       # Get spatial context from 360° data")
    print("       space = calculate_space_around_player(positions, player)")
    print("       pressure = calculate_pressure(positions, player)")
    print("       ")
    print("       if event_type == 'Pass' and space > 10:")
    print("           return f'{player} has time and space in minute {minute}'")
    print("       elif event_type == 'Shot' and pressure < 3:")
    print("           return f'{player} shoots under pressure in minute {minute}!'")
    
    print("\n🎯 2. MOVE QUALITY PREDICTION:")
    print("   def predict_pass_success(event, positions):")
    print("       passer_pos = get_player_position(positions, event['player_name'])")
    print("       target_pos = get_pass_target(event)")
    print("       ")
    print("       distance = calculate_distance(passer_pos, target_pos)")
    print("       defenders_in_lane = count_defenders_in_path(positions, passer_pos, target_pos)")
    print("       pressure = calculate_pressure(positions, event['player_name'])")
    print("       ")
    print("       return ml_model.predict([distance, defenders_in_lane, pressure])")
    
    print("\n🎯 3. TACTICAL ANALYSIS:")
    print("   def analyze_team_shape(positions, team):")
    print("       team_players = filter_team_players(positions, team)")
    print("       ")
    print("       width = max(p['x_position'] for p in team_players) - min(p['x_position'] for p in team_players)")
    print("       length = max(p['y_position'] for p in team_players) - min(p['y_position'] for p in team_players)")
    print("       compactness = calculate_average_distance(team_players)")
    print("       ")
    print("       return {'width': width, 'length': length, 'compactness': compactness}")

def create_data_dictionary():
    """Create a comprehensive data dictionary"""
    print("\n📚 COMPREHENSIVE DATA DICTIONARY")
    print("=" * 40)
    
    print("🎯 EVENTS DATA COLUMNS:")
    events_columns = {
        'match_id': 'Unique identifier for each match',
        'minute': 'Match minute (0-90+ for regular time)',
        'second': 'Second within the minute (0-59)',
        'event_type': 'Type of event (Pass, Shot, Carry, etc.)',
        'player_name': 'Name of player involved in event',
        'team_name': 'Team name (full name)',
        'home_team': 'Home team name',
        'away_team': 'Away team name'
    }
    
    for col, desc in events_columns.items():
        print(f"   📊 {col:15s}: {desc}")
    
    print("\n🎯 360° DATA COLUMNS:")
    data_360_columns = {
        'event_uuid': 'Unique identifier linking to specific event',
        'visible_area': 'Field area visible to cameras [x_min, y_min, x_max, y_max]',
        'freeze_frame': 'Array of player positions at event moment',
        'match_id': 'Match identifier (links to events)',
        'home_team': 'Home team name',
        'away_team': 'Away team name',
        'stage': 'Tournament stage (Group, Round of 16, etc.)'
    }
    
    for col, desc in data_360_columns.items():
        print(f"   🎯 {col:15s}: {desc}")
    
    print("\n🎯 FREEZE FRAME PLAYER OBJECT:")
    freeze_frame_structure = {
        'teammate': 'Boolean - True if player is teammate of event actor',
        'actor': 'Boolean - True if player is the event actor',
        'keeper': 'Boolean - True if player is goalkeeper',
        'location': 'Array [x, y] - Player position coordinates',
        'player': 'Object with player id and name (when available)'
    }
    
    for field, desc in freeze_frame_structure.items():
        print(f"   👤 {field:15s}: {desc}")
    
    print("\n🎯 COORDINATE SYSTEM:")
    print("   📐 X-axis: 0-120 (field length in meters)")
    print("   📐 Y-axis: 0-80 (field width in meters)")
    print("   📐 Origin: Bottom-left corner of field")
    print("   📐 Goals: X=0 (left goal), X=120 (right goal)")

def main():
    """Main function to demonstrate data decoding"""
    print("🔍 COMPLETE GUIDE TO DECODING 360° DATA AND EVENTS")
    print("=" * 60)
    print("📊 Understanding data structures, timing, and synchronization")
    print()
    
    # Load and examine data
    events_df, data_360_df = load_and_examine_data()
    
    # Decode different aspects
    events_df = decode_time_columns(events_df)
    parse_freeze_frame = decode_360_freeze_frame(data_360_df)
    parse_visible_area = decode_visible_area(data_360_df)
    
    # Show synchronization
    synchronize_events_and_360(events_df, data_360_df)
    
    # Demonstrate applications
    demonstrate_practical_applications()
    
    # Create data dictionary
    create_data_dictionary()
    
    print("\n✅ DECODING GUIDE COMPLETE!")
    print("🎯 Key Takeaways:")
    print("   1. Events provide temporal context (minute:second)")
    print("   2. 360° data provides spatial context (player positions)")
    print("   3. Freeze frames contain detailed player position arrays")
    print("   4. Synchronization enables real-time spatial analysis")
    print("   5. Combined data enables commentary + move quality prediction")

if __name__ == "__main__":
    main() 