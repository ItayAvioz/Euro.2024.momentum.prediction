#!/usr/bin/env python3
"""
Show Real Data Examples with Column Explanations
Display actual rows from events and 360° data with detailed explanations
"""

import pandas as pd
import ast

def show_events_examples():
    """Show real examples from events data"""
    print("🎯 EVENTS DATA - REAL ROW EXAMPLES")
    print("=" * 60)
    
    # Load events data
    events_df = pd.read_csv('euro_2024_sample_100_rows.csv')
    
    print("📊 EVENTS DATA STRUCTURE:")
    print(f"   Shape: {events_df.shape[0]} rows × {events_df.shape[1]} columns")
    print(f"   Columns: {list(events_df.columns)}")
    print()
    
    # Show different event types
    print("🔍 DIFFERENT EVENT TYPE EXAMPLES:")
    print()
    
    # Find examples of different event types
    event_types_to_show = ['Pass', 'Ball Receipt*', 'Carry', 'Pressure', 'Shot', 'Dribble']
    
    for event_type in event_types_to_show:
        matching_rows = events_df[events_df['event_type'] == event_type]
        if not matching_rows.empty:
            row = matching_rows.iloc[0]
            print(f"📋 {event_type.upper()} EXAMPLE:")
            print("   ┌─────────────────────────────────────────────────────────────┐")
            print(f"   │ match_id       : {row['match_id']:<40} │")
            print(f"   │ minute         : {row['minute']:<40} │")
            print(f"   │ second         : {row['second']:<40} │")
            print(f"   │ event_type     : {row['event_type']:<40} │")
            print(f"   │ player_name    : {str(row['player_name']):<40} │")
            print(f"   │ team_name      : {str(row['team_name']):<40} │")
            print(f"   │ home_team      : {str(row['home_team']):<40} │")
            print(f"   │ away_team      : {str(row['away_team']):<40} │")
            print("   └─────────────────────────────────────────────────────────────┘")
            
            # Add explanation for this event type
            event_explanations = {
                'Pass': 'Player passed ball to teammate',
                'Ball Receipt*': 'Player successfully received the ball',
                'Carry': 'Player moved forward with ball at feet',
                'Pressure': 'Player applied pressure to opponent',
                'Shot': 'Player attempted to score',
                'Dribble': 'Player dribbled past opponent'
            }
            
            if event_type in event_explanations:
                print(f"   💡 Meaning: {event_explanations[event_type]}")
            
            print()
    
    # Show time progression
    print("⏰ TIME PROGRESSION IN MATCH:")
    print("   Shows how events unfold chronologically")
    print("   ┌─────────┬─────────────────┬─────────────────────┬─────────────────┐")
    print("   │ Time    │ Event Type      │ Player              │ Team            │")
    print("   ├─────────┼─────────────────┼─────────────────────┼─────────────────┤")
    
    for i in range(min(10, len(events_df))):
        row = events_df.iloc[i]
        time_str = f"{row['minute']:02d}:{row['second']:02d}"
        event_type = str(row['event_type'])[:14]
        player = str(row['player_name'])[:18] if pd.notna(row['player_name']) else 'N/A'
        team = str(row['team_name'])[:14] if pd.notna(row['team_name']) else 'N/A'
        
        print(f"   │ {time_str:7s} │ {event_type:15s} │ {player:19s} │ {team:15s} │")
    
    print("   └─────────┴─────────────────┴─────────────────────┴─────────────────┘")
    
    return events_df

def show_360_examples():
    """Show real examples from 360° data"""
    print("\n🎯 360° DATA - REAL ROW EXAMPLES")
    print("=" * 60)
    
    try:
        # Load 360° data
        data_360_df = pd.read_csv('euro_2024_complete/data_360_complete.csv', nrows=2)
        
        print("📊 360° DATA STRUCTURE:")
        print(f"   Shape: {data_360_df.shape[0]} rows × {data_360_df.shape[1]} columns")
        print(f"   Columns: {list(data_360_df.columns)}")
        print()
        
        # Show detailed examples
        for i, (idx, row) in enumerate(data_360_df.iterrows(), 1):
            print(f"📋 360° EXAMPLE {i}:")
            print("   ┌─────────────────────────────────────────────────────────────┐")
            print(f"   │ event_uuid     : {str(row['event_uuid']):<40} │")
            print(f"   │ match_id       : {row['match_id']:<40} │")
            print(f"   │ home_team      : {str(row['home_team']):<40} │")
            print(f"   │ away_team      : {str(row['away_team']):<40} │")
            print(f"   │ stage          : {str(row['stage']):<40} │")
            print(f"   │ visible_area   : {str(row['visible_area'])[:40]:<40} │")
            print(f"   │ freeze_frame   : {str(row['freeze_frame'])[:40]:<40} │")
            print("   └─────────────────────────────────────────────────────────────┘")
            print()
        
        return data_360_df
        
    except Exception as e:
        print(f"❌ Error loading 360° data: {e}")
        return None

def decode_freeze_frame_example():
    """Show detailed freeze frame decoding"""
    print("🎯 FREEZE FRAME DECODING EXAMPLE")
    print("=" * 50)
    
    try:
        # Load 360° data
        data_360_df = pd.read_csv('euro_2024_complete/data_360_complete.csv', nrows=1)
        
        if not data_360_df.empty:
            freeze_frame_raw = data_360_df['freeze_frame'].iloc[0]
            
            print("📋 RAW FREEZE FRAME:")
            print(f"   Type: {type(freeze_frame_raw)}")
            print(f"   Length: {len(str(freeze_frame_raw))} characters")
            print(f"   Sample: {str(freeze_frame_raw)[:100]}...")
            print()
            
            # Parse the freeze frame
            try:
                freeze_frame_data = ast.literal_eval(freeze_frame_raw)
                print("✅ PARSED FREEZE FRAME:")
                print(f"   Number of players tracked: {len(freeze_frame_data)}")
                print()
                
                print("👥 PLAYER POSITIONS (First 10 players):")
                print("   ┌─────┬─────────┬─────────┬──────────┬───────────┬─────────────┐")
                print("   │ #   │ X-Pos   │ Y-Pos   │ Role     │ Team      │ Field Zone  │")
                print("   ├─────┼─────────┼─────────┼──────────┼───────────┼─────────────┤")
                
                for i, player in enumerate(freeze_frame_data[:10], 1):
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
                    team = "🔵 Teammate" if player['teammate'] else "🔴 Opponent"
                    
                    # Determine field zone
                    if x_pos < 40:
                        field_zone = "Defensive"
                    elif x_pos < 80:
                        field_zone = "Middle"
                    else:
                        field_zone = "Attacking"
                    
                    print(f"   │ {i:2d}  │ {x_pos:7.1f} │ {y_pos:7.1f} │ {role:8s} │ {team:9s} │ {field_zone:11s} │")
                
                print("   └─────┴─────────┴─────────┴──────────┴───────────┴─────────────┘")
                
                # Show coordinate system explanation
                print("\n📐 COORDINATE SYSTEM EXPLANATION:")
                print("   🏟️ Field: 120m × 80m (Length × Width)")
                print("   📍 X-axis: 0 = Left goal, 60 = Center, 120 = Right goal")
                print("   📍 Y-axis: 0 = Bottom line, 40 = Center, 80 = Top line")
                print("   🥅 Goals: Left (0, 36-44), Right (120, 36-44)")
                print("   📦 Penalty areas: (0-18, 18-62) and (102-120, 18-62)")
                
                return freeze_frame_data
                
            except Exception as e:
                print(f"❌ Error parsing freeze frame: {e}")
                return None
        
    except Exception as e:
        print(f"❌ Error loading 360° data: {e}")
        return None

def show_column_meanings():
    """Show detailed column meanings"""
    print("\n📚 DETAILED COLUMN MEANINGS")
    print("=" * 45)
    
    print("🎯 EVENTS DATA COLUMNS:")
    events_columns = {
        'match_id': 'Unique number for each match (e.g., 3942819)',
        'minute': 'Match minute (0-90+ for regular time, 90+ for extra time)',
        'second': 'Second within the minute (0-59)',
        'event_type': 'What happened (Pass, Shot, Carry, Ball Receipt, etc.)',
        'player_name': 'Name of player who performed the action',
        'team_name': 'Full team name (Netherlands, England, etc.)',
        'home_team': 'Team playing at home venue',
        'away_team': 'Team playing away from home'
    }
    
    for col, meaning in events_columns.items():
        print(f"   ✅ {col:15s}: {meaning}")
    
    print("\n🎯 360° DATA COLUMNS:")
    data_360_columns = {
        'event_uuid': 'Unique ID linking to specific event in events data',
        'match_id': 'Same match ID as in events data',
        'visible_area': 'Camera field of view coordinates [x_min, y_min, x_max, y_max]',
        'freeze_frame': 'Positions of all 22 players at event moment',
        'home_team': 'Home team name (matches events data)',
        'away_team': 'Away team name (matches events data)',
        'stage': 'Tournament stage (Group, Round of 16, Semi-finals, etc.)'
    }
    
    for col, meaning in data_360_columns.items():
        print(f"   ✅ {col:15s}: {meaning}")
    
    print("\n🎯 FREEZE FRAME PLAYER OBJECT:")
    freeze_frame_fields = {
        'location': 'Array [x, y] with player position on field',
        'teammate': 'True if player is on same team as event actor',
        'actor': 'True if this player performed the event',
        'keeper': 'True if player is goalkeeper',
        'player': 'Object with player ID and name (when available)'
    }
    
    for field, meaning in freeze_frame_fields.items():
        print(f"   ✅ {field:15s}: {meaning}")

def main():
    """Main function to show all examples"""
    print("🔍 REAL DATA EXAMPLES WITH DETAILED EXPLANATIONS")
    print("=" * 80)
    print("📊 Showing actual rows from your Euro 2024 dataset")
    print()
    
    # Show events examples
    events_df = show_events_examples()
    
    # Show 360° examples
    data_360_df = show_360_examples()
    
    # Show freeze frame decoding
    decode_freeze_frame_example()
    
    # Show column meanings
    show_column_meanings()
    
    print("\n✅ REAL DATA EXAMPLES COMPLETE!")
    print("🎯 Key insights from your actual data:")
    print("   1. Match 3942819 = Netherlands vs England (Semi-final)")
    print("   2. Events tracked from 00:00 to 90:00+ with second precision")
    print("   3. 21-22 players tracked per freeze frame")
    print("   4. Field coordinates: 120m × 80m system")
    print("   5. Each event can have corresponding 360° position data")

if __name__ == "__main__":
    main() 