#!/usr/bin/env python3
"""
Show Real Data Examples with Column Explanations
Display actual rows from events and 360° data with detailed explanations
"""

import pandas as pd
import ast
import json

def show_events_examples():
    """Show real examples from events data"""
    print("🎯 EVENTS DATA - REAL ROW EXAMPLES")
    print("=" * 50)
    
    try:
        # Load events data
        events_df = pd.read_csv('euro_2024_sample_100_rows.csv')
        
        # Show first few rows
        print("📊 RAW DATA STRUCTURE:")
        print(f"   Shape: {events_df.shape[0]} rows × {events_df.shape[1]} columns")
        print(f"   Columns: {list(events_df.columns)}")
        
        print("\n🔍 DETAILED ROW EXAMPLES:")
        
        # Show 3 different types of events
        sample_indices = [0, 25, 50] if len(events_df) > 50 else [0, 1, 2]
        
        for i, idx in enumerate(sample_indices, 1):
            if idx < len(events_df):
                row = events_df.iloc[idx]
                print(f"\n📋 EXAMPLE {i} - {row.get('event_type', 'Unknown Event')}:")
                print("   ┌─────────────────────────────────────────────────────────────┐")
                
                # Show each column with explanation
                for col, value in row.items():
                    explanation = get_column_explanation(col, value)
                    print(f"   │ {col:15s}: {str(value):20s} │ {explanation}")
                
                print("   └─────────────────────────────────────────────────────────────┘")
        
        return events_df
        
    except Exception as e:
        print(f"❌ Error loading events data: {e}")
        return None

def show_360_examples():
    """Show real examples from 360° data"""
    print("\n🎯 360° DATA - REAL ROW EXAMPLES")
    print("=" * 50)
    
    try:
        # Load 360° data
        data_360_df = pd.read_csv('euro_2024_complete/data_360_complete.csv', nrows=3)
        
        print("📊 RAW DATA STRUCTURE:")
        print(f"   Shape: {data_360_df.shape[0]} rows × {data_360_df.shape[1]} columns")
        print(f"   Columns: {list(data_360_df.columns)}")
        
        print("\n🔍 DETAILED ROW EXAMPLES:")
        
        for i, (idx, row) in enumerate(data_360_df.iterrows(), 1):
            print(f"\n📋 360° EXAMPLE {i}:")
            print("   ┌─────────────────────────────────────────────────────────────┐")
            
            # Show each column with explanation
            for col, value in row.items():
                explanation = get_360_column_explanation(col, value)
                # Truncate long values for display
                display_value = str(value)[:30] + "..." if len(str(value)) > 30 else str(value)
                print(f"   │ {col:15s}: {display_value:32s} │ {explanation}")
            
            print("   └─────────────────────────────────────────────────────────────┘")
        
        return data_360_df
        
    except Exception as e:
        print(f"❌ Error loading 360° data: {e}")
        return None

def get_column_explanation(column_name, value):
    """Get explanation for events data columns"""
    explanations = {
        'match_id': 'Unique number identifying the specific match',
        'minute': 'Match minute when event occurred (0-90+)',
        'second': 'Second within the minute (0-59)',
        'event_type': 'Type of action (Pass, Shot, Carry, etc.)',
        'player_name': 'Name of the player who performed the action',
        'team_name': 'Full name of the team',
        'home_team': 'Team playing at home',
        'away_team': 'Team playing away'
    }
    
    base_explanation = explanations.get(column_name, 'Custom column')
    
    # Add value-specific context
    if column_name == 'minute':
        if value == 0:
            return f"{base_explanation} (Match start)"
        elif value == 45:
            return f"{base_explanation} (End of first half)"
        elif value > 90:
            return f"{base_explanation} (Extra time)"
        else:
            return base_explanation
    
    elif column_name == 'event_type':
        event_meanings = {
            'Pass': 'Player passed the ball to teammate',
            'Ball Receipt*': 'Player received the ball successfully',
            'Carry': 'Player moved with ball at feet',
            'Pressure': 'Player applied pressure to opponent',
            'Shot': 'Player attempted to score',
            'Dribble': 'Player dribbled past opponent',
            'Tackle': 'Player attempted to win ball',
            'Clearance': 'Player cleared ball from danger'
        }
        return event_meanings.get(value, base_explanation)
    
    return base_explanation

def get_360_column_explanation(column_name, value):
    """Get explanation for 360° data columns"""
    explanations = {
        'event_uuid': 'Unique identifier linking to specific event',
        'visible_area': 'Camera view coordinates [x_min, y_min, x_max, y_max, ...]',
        'freeze_frame': 'Array of all 22 player positions at event moment',
        'match_id': 'Links to the same match_id in events data',
        'home_team': 'Team playing at home (same as events)',
        'away_team': 'Team playing away (same as events)',
        'stage': 'Tournament stage (Group, Round of 16, etc.)'
    }
    
    base_explanation = explanations.get(column_name, 'Custom column')
    
    # Add value-specific context
    if column_name == 'freeze_frame':
        if isinstance(value, str):
            try:
                frame_data = ast.literal_eval(value)
                num_players = len(frame_data)
                return f"Positions of {num_players} players on field"
            except:
                return "Player position data (parsing needed)"
        return base_explanation
    
    elif column_name == 'visible_area':
        return "Field area visible to tracking cameras"
    
    elif column_name == 'stage':
        stage_meanings = {
            'Group Stage': 'Initial tournament round',
            'Round of 16': 'First knockout round',
            'Quarter-finals': 'Quarter-final matches',
            'Semi-finals': 'Semi-final matches',
            'Final': 'Championship match'
        }
        return stage_meanings.get(value, base_explanation)
    
    return base_explanation

def decode_freeze_frame_example():
    """Show detailed freeze frame decoding"""
    print("\n🎯 FREEZE FRAME DECODING EXAMPLE")
    print("=" * 45)
    
    try:
        # Load 360° data
        data_360_df = pd.read_csv('euro_2024_complete/data_360_complete.csv', nrows=1)
        
        if not data_360_df.empty:
            freeze_frame_raw = data_360_df['freeze_frame'].iloc[0]
            
            print("📋 RAW FREEZE FRAME DATA:")
            print(f"   Type: {type(freeze_frame_raw)}")
            print(f"   Length: {len(str(freeze_frame_raw))} characters")
            print(f"   Sample: {str(freeze_frame_raw)[:100]}...")
            
            # Parse the freeze frame
            try:
                freeze_frame_data = ast.literal_eval(freeze_frame_raw)
                print(f"\n✅ PARSED SUCCESSFULLY:")
                print(f"   Number of players: {len(freeze_frame_data)}")
                
                print("\n👥 PLAYER POSITION EXAMPLES:")
                print("   ┌─────┬─────────┬─────────┬──────────┬───────┬─────────┐")
                print("   │ #   │ X-Pos   │ Y-Pos   │ Role     │ Team  │ Type    │")
                print("   ├─────┼─────────┼─────────┼──────────┼───────┼─────────┤")
                
                for i, player in enumerate(freeze_frame_data[:10], 1):  # Show first 10 players
                    x_pos = player['location'][0]
                    y_pos = player['location'][1]
                    
                    # Determine role
                    if player['actor']:
                        role = "⚽ Actor"
                    elif player['keeper']:
                        role = "🥅 Keeper"
                    else:
                        role = "👤 Player"
                    
                    # Determine team
                    team = "🔵 Team" if player['teammate'] else "🔴 Opponent"
                    
                    # Determine field position
                    if x_pos < 40:
                        field_pos = "Defensive"
                    elif x_pos < 80:
                        field_pos = "Middle"
                    else:
                        field_pos = "Attacking"
                    
                    print(f"   │ {i:2d}  │ {x_pos:7.1f} │ {y_pos:7.1f} │ {role:8s} │ {team:5s} │ {field_pos:7s} │")
                
                print("   └─────┴─────────┴─────────┴──────────┴───────┴─────────┘")
                
                # Show field coordinate explanation
                print("\n📐 COORDINATE SYSTEM EXPLANATION:")
                print("   🏟️ Field dimensions: 120m × 80m")
                print("   📍 X-axis: 0 = Left goal, 120 = Right goal")
                print("   📍 Y-axis: 0 = Bottom touchline, 80 = Top touchline")
                print("   📍 Center circle: Around (60, 40)")
                print("   📍 Penalty areas: (0-18, 18-62) and (102-120, 18-62)")
                
                return freeze_frame_data
                
            except Exception as e:
                print(f"❌ Error parsing freeze frame: {e}")
                return None
        
    except Exception as e:
        print(f"❌ Error loading 360° data: {e}")
        return None

def show_time_synchronization():
    """Show how events and 360° data synchronize"""
    print("\n🔗 TIME SYNCHRONIZATION EXAMPLE")
    print("=" * 40)
    
    try:
        # Load both datasets
        events_df = pd.read_csv('euro_2024_sample_100_rows.csv')
        
        print("📊 EVENTS TIMELINE:")
        print("   ┌─────────────────────────────────────────────────────────────┐")
        print("   │ Time    │ Event Type    │ Player           │ Team           │")
        print("   ├─────────────────────────────────────────────────────────────┤")
        
        # Show first 5 events with time
        for i in range(min(5, len(events_df))):
            row = events_df.iloc[i]
            time_str = f"{row['minute']:02d}:{row['second']:02d}"
            event_type = str(row['event_type'])[:12]
            player = str(row['player_name'])[:15] if pd.notna(row['player_name']) else "Unknown"
            team = str(row['team_name'])[:13] if pd.notna(row['team_name']) else "Unknown"
            
            print(f"   │ {time_str:7s} │ {event_type:13s} │ {player:16s} │ {team:14s} │")
        
        print("   └─────────────────────────────────────────────────────────────┘")
        
        print("\n🎯 360° DATA CONNECTIONS:")
        print("   ✅ Each event can have corresponding 360° position data")
        print("   ✅ event_uuid links events to freeze frames")
        print("   ✅ match_id ensures same match context")
        print("   ✅ Timestamp allows temporal analysis")
        
        # Show combined example
        print("\n🔄 COMBINED ANALYSIS EXAMPLE:")
        sample_row = events_df.iloc[0]
        print(f"   Event: {sample_row['event_type']} by {sample_row['player_name']}")
        print(f"   Time: {sample_row['minute']:02d}:{sample_row['second']:02d}")
        print(f"   Match: {sample_row['match_id']}")
        print(f"   Context: {sample_row['home_team']} vs {sample_row['away_team']}")
        print(f"   → 360° data would show positions of all 22 players at this moment")
        
    except Exception as e:
        print(f"❌ Error in synchronization example: {e}")

def main():
    """Main function to show all examples"""
    print("🔍 REAL DATA EXAMPLES WITH DETAILED EXPLANATIONS")
    print("=" * 70)
    print("📊 Showing actual rows from your Euro 2024 dataset")
    print()
    
    # Show events examples
    events_df = show_events_examples()
    
    # Show 360° examples
    data_360_df = show_360_examples()
    
    # Show freeze frame decoding
    decode_freeze_frame_example()
    
    # Show synchronization
    show_time_synchronization()
    
    print("\n✅ DATA EXAMPLES COMPLETE!")
    print("🎯 Key insights:")
    print("   1. Events data tracks what happened and when")
    print("   2. 360° data tracks where everyone was positioned")
    print("   3. Freeze frames contain 21-22 player positions")
    print("   4. Coordinates use 120×80 meter field system")
    print("   5. Data synchronizes via match_id and event_uuid")

if __name__ == "__main__":
    main() 