"""
Analyze Event Sequences for Commentary Generation
=================================================
Understand the structure of event sequences and create templates
for natural language commentary.
"""

import pandas as pd
import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def load_training_data():
    """Load the commentator training data"""
    csv_path = os.path.join(SCRIPT_DIR, 'commentator_training_data.csv')
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} events from {df['sequence_id'].nunique()} sequences")
    return df

def safe_parse_json(value):
    """Safely parse JSON-like string"""
    if pd.isna(value):
        return None
    if isinstance(value, str):
        try:
            # Replace single quotes with double quotes for proper JSON
            value = value.replace("'", '"')
            return json.loads(value)
        except:
            try:
                return eval(value.replace('"', "'"))
            except:
                return None
    return value

def analyze_sequence(df, sequence_id):
    """Analyze a single sequence and extract all metadata"""
    
    sequence = df[df['sequence_id'] == sequence_id].copy()
    sequence = sequence.sort_values('event_position')
    
    # Metadata
    metadata = {
        'sequence_id': sequence_id,
        'sequence_type': sequence['sequence_type'].iloc[0],
        'sequence_key_event': sequence['sequence_key_event'].iloc[0],
        'sequence_length': sequence['sequence_length'].iloc[0],
        'match_id': sequence['match_id'].iloc[0],
        'home_team': sequence['home_team_name'].iloc[0],
        'away_team': sequence['away_team_name'].iloc[0],
        'events': []
    }
    
    # Parse each event
    for idx, row in sequence.iterrows():
        
        # Parse JSON fields
        event_type = safe_parse_json(row['type'])
        player = safe_parse_json(row['player'])
        team = safe_parse_json(row['team'])
        possession_team = safe_parse_json(row['possession_team'])
        location = safe_parse_json(row['location'])
        position = safe_parse_json(row['position'])
        play_pattern = safe_parse_json(row['play_pattern'])
        
        # Event-specific details
        shot_details = safe_parse_json(row['shot'])
        pass_details = safe_parse_json(row['pass'])
        dribble_details = safe_parse_json(row['dribble'])
        carry_details = safe_parse_json(row['carry'])
        duel_details = safe_parse_json(row['duel'])
        
        # Parse related events
        related_events = safe_parse_json(row['related_events'])
        
        event_data = {
            'event_position': row['event_position'],
            'is_key_event': row['is_key_event'],
            'minute': row['minute'],
            'second': row['second'],
            'period': row['period'],
            'timestamp': row['timestamp'],
            
            # Core info
            'event_type': event_type.get('name') if event_type else None,
            'player_name': player.get('name') if player else None,
            'player_id': player.get('id') if player else None,
            'team_name': team.get('name') if team else None,
            'possession_team': possession_team.get('name') if possession_team else None,
            'player_position': position.get('name') if position else None,
            
            # Location
            'location': location,
            'location_x': location[0] if location else None,
            'location_y': location[1] if location else None,
            
            # Context
            'under_pressure': row['under_pressure'] if not pd.isna(row['under_pressure']) else False,
            'duration': row['duration'],
            'play_pattern': play_pattern.get('name') if play_pattern else None,
            
            # Event details
            'shot': shot_details,
            'pass': pass_details,
            'dribble': dribble_details,
            'carry': carry_details,
            'duel': duel_details,
            
            # Related events
            'related_events': related_events if related_events else []
        }
        
        metadata['events'].append(event_data)
    
    return metadata

def print_sequence_analysis(metadata):
    """Print detailed sequence analysis"""
    
    print(f"\n{'='*80}")
    print(f"SEQUENCE {metadata['sequence_id']}: {metadata['sequence_type']}")
    print(f"{'='*80}")
    
    print(f"\nMETADATA:")
    print(f"  Match: {metadata['home_team']} vs {metadata['away_team']}")
    print(f"  Key Event: {metadata['sequence_key_event']}")
    print(f"  Length: {metadata['sequence_length']} events")
    
    print(f"\nEVENTS:")
    for i, event in enumerate(metadata['events'], 1):
        print(f"\n  [{i}] {event['event_type']}")
        if event['is_key_event']:
            print(f"      ⭐ KEY EVENT ⭐")
        
        print(f"      Time: {event['minute']}:{event['second']:02d} (Period {event['period']})")
        print(f"      Player: {event['player_name']} ({event['player_position']})")
        print(f"      Team: {event['team_name']}")
        
        if event['location_x'] and event['location_y']:
            print(f"      Location: ({event['location_x']:.1f}, {event['location_y']:.1f})")
        
        if event['under_pressure']:
            print(f"      ⚠️  Under Pressure")
        
        # Event-specific details
        if event['pass']:
            pass_info = event['pass']
            recipient = pass_info.get('recipient', {})
            print(f"      Pass Details:")
            print(f"        → To: {recipient.get('name', 'Unknown')}")
            print(f"        → Length: {pass_info.get('length', 0):.1f}m")
            print(f"        → Height: {pass_info.get('height', {}).get('name', 'Unknown')}")
            if pass_info.get('outcome'):
                print(f"        → Outcome: {pass_info['outcome'].get('name')}")
        
        if event['shot']:
            shot_info = event['shot']
            print(f"      Shot Details:")
            print(f"        → xG: {shot_info.get('statsbomb_xg', 0):.3f}")
            print(f"        → Body Part: {shot_info.get('body_part', {}).get('name', 'Unknown')}")
            print(f"        → Outcome: {shot_info.get('outcome', {}).get('name', 'Unknown')}")
        
        if event['dribble']:
            dribble_info = event['dribble']
            print(f"      Dribble Details:")
            print(f"        → Outcome: {dribble_info.get('outcome', {}).get('name', 'Unknown')}")
            if dribble_info.get('nutmeg'):
                print(f"        → 🔥 NUTMEG!")
        
        if event['carry']:
            carry_info = event['carry']
            end_loc = carry_info.get('end_location', [])
            if end_loc:
                print(f"      Carry Details:")
                print(f"        → End: ({end_loc[0]:.1f}, {end_loc[1]:.1f})")
        
        if event['related_events']:
            print(f"      Related Events: {len(event['related_events'])} connections")

def main():
    """Main analysis"""
    
    print("="*80)
    print("EVENT SEQUENCE ANALYSIS FOR COMMENTARY")
    print("="*80)
    
    # Load data
    df = load_training_data()
    
    # Get summary statistics
    print(f"\n📊 DATASET OVERVIEW:")
    print(f"   Total Events: {len(df)}")
    print(f"   Total Sequences: {df['sequence_id'].nunique()}")
    print(f"   Matches: {df['match_id'].nunique()}")
    
    print(f"\n📊 SEQUENCE TYPES:")
    sequence_types = df.groupby('sequence_type')['sequence_id'].nunique()
    for seq_type, count in sequence_types.items():
        print(f"   {seq_type}: {count} sequences")
    
    print(f"\n📊 EVENT TYPES:")
    event_types = df['type'].apply(lambda x: safe_parse_json(x).get('name') if safe_parse_json(x) else 'Unknown').value_counts()
    for event_type, count in event_types.head(10).items():
        print(f"   {event_type}: {count} events")
    
    # Analyze 3 diverse sequences
    print(f"\n{'='*80}")
    print("ANALYZING 3 EXAMPLE SEQUENCES")
    print(f"{'='*80}")
    
    # Select diverse examples
    shot_seq = df[df['sequence_type'] == 'shot_sequence']['sequence_id'].iloc[0]
    dribble_seq = df[df['sequence_type'] == 'dribble_sequence']['sequence_id'].iloc[0]
    pressure_seq = df[df['sequence_type'] == 'pressure_sequence']['sequence_id'].iloc[0]
    
    for seq_id in [shot_seq, dribble_seq, pressure_seq]:
        metadata = analyze_sequence(df, seq_id)
        print_sequence_analysis(metadata)
    
    print(f"\n{'='*80}")
    print("KEY INSIGHTS FOR COMMENTARY GENERATION")
    print(f"{'='*80}")
    
    print("""
    📌 METADATA TO EXTRACT:
    
    1. MATCH CONTEXT:
       - Home team vs Away team
       - Current minute and period
       - Possession team
    
    2. EVENT DETAILS:
       - Event type (Shot, Pass, Dribble, Carry, Pressure, etc.)
       - Player name and position
       - Team executing the event
       - Location on pitch (x, y coordinates)
       - Timestamp
    
    3. EVENT-SPECIFIC DATA:
       
       PASS:
       - Recipient (who receives)
       - Length (distance)
       - Height (ground, low, high)
       - Angle (direction)
       - Outcome (complete, incomplete, out)
       - Body part (left foot, right foot, head)
       
       SHOT:
       - xG (expected goals)
       - End location
       - Body part
       - Outcome (goal, saved, blocked, off target)
       - Technique (normal, volley, overhead)
       
       DRIBBLE:
       - Outcome (complete, incomplete)
       - Special attributes (nutmeg, overrun)
       
       CARRY:
       - Start location
       - End location
       - Distance covered
       
       PRESSURE:
       - Duration
       - Effect on opponent's action
    
    4. SEQUENCE CONTEXT:
       - Position in sequence (1st, 2nd, etc.)
       - Is key event? (most important event)
       - Related events (connections)
       - Play pattern (regular play, counter, set piece)
       - Under pressure flag
    
    5. FIELD ZONES:
       - Defensive third (0-40)
       - Middle third (40-80)
       - Attacking third (80-120)
       - Left/Center/Right channels
    
    📌 COMMENTARY TEMPLATES:
    
    PASS SEQUENCE:
    "[Player] plays it to [Recipient], 
     {length} pass {on the ground/through the air},
     {under pressure context}"
    
    SHOT SEQUENCE:
    "[Player] {receives/carries} → 
     [Player2] {passes} → 
     [Player3] SHOOTS! 
     {outcome with emotion}"
    
    DRIBBLE SEQUENCE:
    "[Player] takes on [Opponent],
     {nutmeg/beats him/loses it},
     {carries forward/location}"
    
    PRESSURE SEQUENCE:
    "[Player] under pressure from [Opponent],
     {manages to pass/loses possession/wins foul}"
    """)
    
    print("\n" + "="*80)

if __name__ == "__main__":
    main()
