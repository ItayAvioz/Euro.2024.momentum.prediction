"""
Generate Event Commentary with Full Metadata
============================================
Create natural language commentary from event sequences
with complete metadata extraction.
"""

import pandas as pd
import json
import os
import math

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def safe_parse_json(value):
    """Safely parse JSON-like string"""
    if pd.isna(value):
        return None
    if isinstance(value, str):
        try:
            value = value.replace("'", '"')
            return json.loads(value)
        except:
            try:
                return eval(value.replace('"', "'"))
            except:
                return None
    return value

def get_field_zone(x, y=None):
    """Determine field zone from coordinates"""
    if x is None:
        return "unknown area"
    
    # Horizontal zones (x-axis: 0-120)
    if x < 40:
        zone_h = "defensive third"
    elif x < 80:
        zone_h = "midfield"
    else:
        zone_h = "attacking third"
    
    # Vertical zones (y-axis: 0-80)
    if y is not None:
        if y < 26.67:
            zone_v = "right"
        elif y < 53.33:
            zone_v = "central"
        else:
            zone_v = "left"
        return f"{zone_v} {zone_h}"
    
    return zone_h

def describe_distance(distance):
    """Describe pass/carry distance"""
    if distance < 10:
        return "short"
    elif distance < 25:
        return "medium"
    else:
        return "long"

def generate_pass_commentary(event, next_event=None):
    """Generate commentary for a pass event"""
    player = event['player_name']
    pass_details = event['pass']
    
    if not pass_details:
        return f"{player} passes"
    
    recipient = pass_details.get('recipient', {}).get('name', 'teammate')
    length = pass_details.get('length', 0)
    height = pass_details.get('height', {}).get('name', '').lower()
    outcome = pass_details.get('outcome', {}).get('name', '')
    body_part = pass_details.get('body_part', {}).get('name', '')
    
    # Build commentary
    commentary = f"{player}"
    
    # Describe delivery
    distance_desc = describe_distance(length)
    if 'ground' in height.lower():
        delivery = f"{distance_desc} pass along the ground"
    elif 'high' in height.lower():
        delivery = f"{distance_desc} ball through the air"
    elif 'low' in height.lower():
        delivery = f"{distance_desc} low pass"
    else:
        delivery = f"{distance_desc} pass"
    
    # Add body part if header
    if 'head' in body_part.lower():
        commentary += f" heads it, {delivery}"
    else:
        commentary += f" plays {delivery}"
    
    # Add recipient
    commentary += f" to {recipient}"
    
    # Add location context
    zone = get_field_zone(event['location_x'], event['location_y'])
    commentary += f" in the {zone}"
    
    # Add outcome if incomplete
    if outcome and 'incomplete' in outcome.lower():
        commentary += ", but it's intercepted"
    elif outcome and 'out' in outcome.lower():
        commentary += ", but it goes out of play"
    
    return commentary

def generate_shot_commentary(event):
    """Generate commentary for a shot event"""
    player = event['player_name']
    shot_details = event['shot']
    
    if not shot_details:
        return f"{player} shoots!"
    
    outcome = shot_details.get('outcome', {}).get('name', '')
    body_part = shot_details.get('body_part', {}).get('name', '')
    xg = shot_details.get('statsbomb_xg', 0)
    technique = shot_details.get('technique', {}).get('name', '').lower()
    
    # Build commentary
    zone = get_field_zone(event['location_x'], event['location_y'])
    
    # Shot type
    if 'volley' in technique:
        shot_type = "volleys"
    elif 'overhead' in technique:
        shot_type = "attempts an overhead kick"
    else:
        shot_type = "shoots"
    
    commentary = f"{player} {shot_type}"
    
    # Add body part
    if 'head' in body_part.lower():
        commentary = f"{player} with a header"
    elif 'left foot' in body_part.lower():
        commentary += " with the left"
    elif 'right foot' in body_part.lower():
        commentary += " with the right"
    
    # Add location
    commentary += f" from the {zone}"
    
    # Add outcome with emotion
    if 'goal' in outcome.lower() and 'own goal' not in outcome.lower():
        commentary += " - IT'S A GOAL! What a finish!"
    elif 'saved' in outcome.lower():
        commentary += " - saved by the goalkeeper!"
    elif 'blocked' in outcome.lower():
        commentary += " - BLOCKED! Crucial defending"
    elif 'off target' in outcome.lower() or 'off t' in outcome.lower():
        commentary += " - just wide of the post"
    elif 'wayward' in outcome.lower():
        commentary += " - wayward, miles over the bar"
    elif 'post' in outcome.lower():
        commentary += " - HITS THE POST! So close!"
    
    # Add xG context if high
    if xg > 0.3:
        commentary += f" (xG: {xg:.2f} - great chance)"
    
    return commentary

def generate_dribble_commentary(event, opponent_event=None):
    """Generate commentary for a dribble event"""
    player = event['player_name']
    dribble_details = event['dribble']
    
    if not dribble_details:
        return f"{player} attempts to dribble"
    
    outcome = dribble_details.get('outcome', {}).get('name', '')
    nutmeg = dribble_details.get('nutmeg', False)
    overrun = dribble_details.get('overrun', False)
    
    # Find opponent if exists
    opponent_name = "the defender"
    if opponent_event and opponent_event.get('event_type') in ['Duel', 'Dribbled Past']:
        opponent_name = opponent_event.get('player_name', 'the defender')
    
    # Build commentary
    zone = get_field_zone(event['location_x'], event['location_y'])
    
    commentary = f"{player} takes on {opponent_name}"
    
    if nutmeg:
        commentary += " - NUTMEG! Through the legs"
    
    if 'complete' in outcome.lower():
        commentary += f", beats him and drives forward"
    elif 'incomplete' in outcome.lower():
        if overrun:
            commentary += f", but the ball gets away from him"
        else:
            commentary += f", but {opponent_name} stands firm"
    
    return commentary

def generate_carry_commentary(event):
    """Generate commentary for a carry event"""
    player = event['player_name']
    carry_details = event['carry']
    
    if not carry_details:
        return f"{player} carries forward"
    
    start_x = event['location_x']
    start_y = event['location_y']
    end_loc = carry_details.get('end_location', [])
    
    if not end_loc or len(end_loc) < 2:
        return f"{player} carries the ball forward"
    
    end_x, end_y = end_loc[0], end_loc[1]
    
    # Calculate distance
    if start_x and start_y:
        distance = math.sqrt((end_x - start_x)**2 + (end_y - start_y)**2)
    else:
        distance = 0
    
    # Determine direction
    start_zone = get_field_zone(start_x, start_y)
    end_zone = get_field_zone(end_x, end_y)
    
    commentary = f"{player}"
    
    if event.get('under_pressure'):
        commentary += " under pressure,"
    
    if distance > 15:
        commentary += f" drives forward with the ball"
    elif distance > 5:
        commentary += f" carries the ball"
    else:
        commentary += f" controls the ball"
    
    # Add progression context
    if end_x - (start_x or 0) > 10:
        commentary += ", pushing into the " + get_field_zone(end_x, end_y)
    
    return commentary

def generate_pressure_commentary(event, pressured_player=None):
    """Generate commentary for a pressure event"""
    player = event['player_name']
    
    commentary = f"{player} closes down"
    
    if pressured_player:
        target = pressured_player.get('player_name', 'the ball carrier')
        commentary = f"{player} presses {target}"
    
    zone = get_field_zone(event['location_x'], event['location_y'])
    commentary += f" in the {zone}"
    
    return commentary

def generate_sequence_commentary(df, sequence_id):
    """Generate full commentary for a sequence"""
    
    sequence = df[df['sequence_id'] == sequence_id].copy()
    sequence = sequence.sort_values('event_position')
    
    # Parse events
    events = []
    for _, row in sequence.iterrows():
        event_type = safe_parse_json(row['type'])
        player = safe_parse_json(row['player'])
        team = safe_parse_json(row['team'])
        location = safe_parse_json(row['location'])
        
        event = {
            'event_type': event_type.get('name') if event_type else None,
            'player_name': player.get('name') if player else None,
            'team_name': team.get('name') if team else None,
            'location_x': location[0] if location else None,
            'location_y': location[1] if location else None,
            'under_pressure': row['under_pressure'] if not pd.isna(row['under_pressure']) else False,
            'is_key_event': row['is_key_event'],
            'minute': row['minute'],
            'second': row['second'],
            'pass': safe_parse_json(row['pass']),
            'shot': safe_parse_json(row['shot']),
            'dribble': safe_parse_json(row['dribble']),
            'carry': safe_parse_json(row['carry']),
            'duel': safe_parse_json(row['duel']),
        }
        events.append(event)
    
    # Generate commentary for each event
    commentary_parts = []
    
    for i, event in enumerate(events):
        event_type = event['event_type']
        next_event = events[i+1] if i+1 < len(events) else None
        
        if event_type == 'Pass':
            comm = generate_pass_commentary(event, next_event)
        elif event_type == 'Shot':
            comm = generate_shot_commentary(event)
        elif event_type == 'Dribble':
            opponent = next_event if next_event and next_event['event_type'] in ['Duel', 'Dribbled Past'] else None
            comm = generate_dribble_commentary(event, opponent)
        elif event_type == 'Carry':
            comm = generate_carry_commentary(event)
        elif event_type == 'Pressure':
            # Find who is being pressured
            pressured = None
            if i > 0 and events[i-1]['team_name'] != event['team_name']:
                pressured = events[i-1]
            comm = generate_pressure_commentary(event, pressured)
        elif event_type == 'Ball Receipt*':
            comm = f"{event['player_name']} receives the ball"
        elif event_type == 'Block':
            comm = f"BLOCKED by {event['player_name']}!"
        elif event_type == 'Goal Keeper':
            comm = f"The goalkeeper deals with it"
        else:
            comm = f"{event['event_type']}"
        
        # Mark key event
        if event['is_key_event']:
            comm = "⭐ " + comm + " ⭐"
        
        commentary_parts.append(comm)
    
    # Combine into flowing commentary
    full_commentary = ". ".join(commentary_parts) + "."
    
    # Add time stamp
    first_event = events[0]
    time_stamp = f"[{first_event['minute']}:{first_event['second']:02d}] "
    
    return time_stamp + full_commentary

def main():
    """Generate commentary examples"""
    
    print("="*80)
    print("EVENT COMMENTARY GENERATION WITH FULL METADATA")
    print("="*80)
    
    # Load data
    csv_path = os.path.join(SCRIPT_DIR, 'commentator_training_data.csv')
    df = pd.read_csv(csv_path)
    
    print(f"\nLoaded {len(df)} events from {df['sequence_id'].nunique()} sequences\n")
    
    # Generate commentary for first 5 sequences
    print("="*80)
    print("GENERATED COMMENTARY EXAMPLES")
    print("="*80)
    
    for seq_id in range(1, 6):
        sequence = df[df['sequence_id'] == seq_id]
        if len(sequence) > 0:
            seq_type = sequence['sequence_type'].iloc[0]
            home_team = sequence['home_team_name'].iloc[0]
            away_team = sequence['away_team_name'].iloc[0]
            
            print(f"\n{'─'*80}")
            print(f"SEQUENCE {seq_id}: {seq_type}")
            print(f"Match: {home_team} vs {away_team}")
            print(f"{'─'*80}")
            
            commentary = generate_sequence_commentary(df, seq_id)
            print(f"\n{commentary}")
    
    print("\n" + "="*80)
    print("TEMPLATE SUMMARY")
    print("="*80)
    
    print("""
    📌 COMMENTARY TEMPLATES BY EVENT TYPE:
    
    1. PASS EVENT:
       "{Player} {verb} {distance} {delivery} to {Recipient} in the {zone}"
       
       Examples:
       - "Carvajal plays a short pass along the ground to Olmo in the central midfield"
       - "Kane heads it, long ball through the air to Saka in the left attacking third"
    
    2. SHOT EVENT:
       "{Player} {shot_type} from the {zone} - {outcome}"
       
       Examples:
       - "Williams shoots with the left from the central attacking third - BLOCKED!"
       - "Kane with a header from the right attacking third - saved by the goalkeeper!"
    
    3. DRIBBLE EVENT:
       "{Player} takes on {Opponent}, {outcome}"
       
       Examples:
       - "Shaw takes on Carvajal - NUTMEG! Through the legs"
       - "Rice takes on Fabián, beats him and drives forward"
    
    4. CARRY EVENT:
       "{Player} {pressure_context} {action} {progression}"
       
       Examples:
       - "Williams under pressure, drives forward with the ball"
       - "Stones carries the ball, pushing into the central midfield"
    
    5. PRESSURE EVENT:
       "{Player} {presses/closes down} {Target} in the {zone}"
       
       Examples:
       - "Bellingham presses Carvajal in the right defensive third"
       - "Rice closes down in the central midfield"
    
    6. SEQUENCE FLOW:
       Connect events with: ". " or ", " or " - " for dramatic effect
       
       Example Full Sequence:
       "[0:37] Carvajal receives the ball. Carvajal under pressure, carries the ball, 
       pushing into the central defensive third. ⭐ Bellingham presses Carvajal in the 
       right defensive third ⭐. Carvajal plays a short pass along the ground to Daniel 
       Olmo Carvajal in the right midfield. Rice closes down in the central midfield."
    """)
    
    print("\n" + "="*80)

if __name__ == "__main__":
    main()
