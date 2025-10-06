"""
Create Complete Training Data with Metadata & Commentary
========================================================
Generate comprehensive training dataset with:
1. All metadata extracted
2. Event-level commentary
3. Sequence-level commentary
4. Field zones and contextual information
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

def get_field_zone(x, y):
    """Determine field zone"""
    if x is None or y is None:
        return "unknown", "unknown", "unknown"
    
    # Horizontal zones
    if x < 40:
        zone_h = "defensive third"
    elif x < 80:
        zone_h = "midfield"
    else:
        zone_h = "attacking third"
    
    # Vertical zones
    if y < 26.67:
        zone_v = "right"
    elif y < 53.33:
        zone_v = "central"
    else:
        zone_v = "left"
    
    combined = f"{zone_v} {zone_h}"
    return zone_h, zone_v, combined

def describe_distance(distance):
    """Describe distance"""
    if distance < 10:
        return "short"
    elif distance < 25:
        return "medium"
    else:
        return "long"

def generate_event_commentary(event, prev_event, next_event):
    """Generate commentary for single event"""
    
    event_type = event['event_type']
    player = event['player_name']
    
    if event_type == 'Pass':
        pass_info = event['pass_details']
        if not pass_info:
            return f"{player} passes"
        
        recipient = pass_info.get('recipient', 'Unknown')
        length = pass_info.get('length', 0)
        height = pass_info.get('height', '').lower()
        distance_desc = describe_distance(length)
        
        if 'ground' in height:
            delivery = f"{distance_desc} pass along the ground"
        elif 'high' in height:
            delivery = f"{distance_desc} ball through the air"
        else:
            delivery = f"{distance_desc} pass"
        
        return f"{player} plays {delivery} to {recipient}"
    
    elif event_type == 'Shot':
        shot_info = event['shot_details']
        if not shot_info:
            return f"{player} shoots!"
        
        outcome = shot_info.get('outcome', '')
        xg = shot_info.get('xg', 0)
        
        if 'goal' in outcome.lower() and 'own' not in outcome.lower():
            return f"{player} SHOOTS - IT'S A GOAL!"
        elif 'saved' in outcome.lower():
            return f"{player} shoots - saved by the goalkeeper!"
        elif 'blocked' in outcome.lower():
            return f"{player} shoots - BLOCKED!"
        elif 'off' in outcome.lower():
            return f"{player} shoots - just wide!"
        else:
            return f"{player} shoots!"
    
    elif event_type == 'Dribble':
        dribble_info = event['dribble_details']
        outcome = dribble_info.get('outcome', '') if dribble_info else ''
        nutmeg = dribble_info.get('nutmeg', False) if dribble_info else False
        
        # Find opponent
        opponent = "the defender"
        if next_event and next_event['event_type'] in ['Duel', 'Dribbled Past']:
            opponent = next_event['player_name']
        
        if nutmeg:
            return f"{player} takes on {opponent} - NUTMEG!"
        elif 'complete' in outcome.lower():
            return f"{player} beats {opponent}"
        else:
            return f"{player} attempts to beat {opponent}"
    
    elif event_type == 'Carry':
        if event['under_pressure']:
            return f"{player} under pressure, carries forward"
        else:
            return f"{player} carries the ball"
    
    elif event_type == 'Pressure':
        target = "the ball carrier"
        if prev_event and prev_event['team_name'] != event['team_name']:
            target = prev_event['player_name']
        return f"{player} presses {target}"
    
    elif event_type == 'Ball Receipt*':
        return f"{player} receives"
    
    elif event_type == 'Block':
        return f"BLOCKED by {player}!"
    
    elif event_type == 'Goal Keeper':
        return "Goalkeeper deals with it"
    
    else:
        return f"{event_type}"

def create_enhanced_dataset():
    """Create enhanced dataset with all metadata"""
    
    # Load original data
    csv_path = os.path.join(SCRIPT_DIR, 'commentator_training_data.csv')
    df = pd.read_csv(csv_path)
    
    print(f"Processing {len(df)} events...")
    
    enhanced_rows = []
    
    # Group by sequence
    for seq_id in df['sequence_id'].unique():
        sequence = df[df['sequence_id'] == seq_id].copy()
        sequence = sequence.sort_values('event_position').reset_index(drop=True)
        
        # Generate sequence-level commentary
        sequence_commentary_parts = []
        
        for idx, row in sequence.iterrows():
            # Parse all JSON fields
            event_type = safe_parse_json(row['type'])
            player = safe_parse_json(row['player'])
            team = safe_parse_json(row['team'])
            possession_team = safe_parse_json(row['possession_team'])
            location = safe_parse_json(row['location'])
            position = safe_parse_json(row['position'])
            play_pattern = safe_parse_json(row['play_pattern'])
            
            shot = safe_parse_json(row['shot'])
            pass_data = safe_parse_json(row['pass'])
            dribble = safe_parse_json(row['dribble'])
            carry = safe_parse_json(row['carry'])
            duel = safe_parse_json(row['duel'])
            
            # Extract location info
            loc_x = location[0] if location and len(location) > 0 else None
            loc_y = location[1] if location and len(location) > 1 else None
            zone_h, zone_v, zone_combined = get_field_zone(loc_x, loc_y)
            
            # Extract pass details
            pass_recipient = None
            pass_length = None
            pass_height = None
            pass_outcome = None
            if pass_data:
                recipient_dict = pass_data.get('recipient', {})
                pass_recipient = recipient_dict.get('name') if isinstance(recipient_dict, dict) else None
                pass_length = pass_data.get('length')
                height_dict = pass_data.get('height', {})
                pass_height = height_dict.get('name') if isinstance(height_dict, dict) else None
                outcome_dict = pass_data.get('outcome', {})
                pass_outcome = outcome_dict.get('name') if isinstance(outcome_dict, dict) else None
            
            # Extract shot details
            shot_xg = None
            shot_outcome = None
            shot_body_part = None
            if shot:
                shot_xg = shot.get('statsbomb_xg')
                outcome_dict = shot.get('outcome', {})
                shot_outcome = outcome_dict.get('name') if isinstance(outcome_dict, dict) else None
                body_dict = shot.get('body_part', {})
                shot_body_part = body_dict.get('name') if isinstance(body_dict, dict) else None
            
            # Extract dribble details
            dribble_outcome = None
            dribble_nutmeg = False
            if dribble:
                outcome_dict = dribble.get('outcome', {})
                dribble_outcome = outcome_dict.get('name') if isinstance(outcome_dict, dict) else None
                dribble_nutmeg = dribble.get('nutmeg', False)
            
            # Extract carry details
            carry_end_x = None
            carry_end_y = None
            carry_distance = None
            if carry:
                end_loc = carry.get('end_location', [])
                if end_loc and len(end_loc) >= 2:
                    carry_end_x = end_loc[0]
                    carry_end_y = end_loc[1]
                    if loc_x and loc_y:
                        carry_distance = math.sqrt((carry_end_x - loc_x)**2 + (carry_end_y - loc_y)**2)
            
            # Create event object for commentary generation
            event_obj = {
                'event_type': event_type.get('name') if event_type else None,
                'player_name': player.get('name') if player else None,
                'team_name': team.get('name') if team else None,
                'under_pressure': row['under_pressure'] if not pd.isna(row['under_pressure']) else False,
                'pass_details': {
                    'recipient': pass_recipient,
                    'length': pass_length,
                    'height': pass_height,
                    'outcome': pass_outcome
                } if pass_data else None,
                'shot_details': {
                    'xg': shot_xg,
                    'outcome': shot_outcome,
                    'body_part': shot_body_part
                } if shot else None,
                'dribble_details': {
                    'outcome': dribble_outcome,
                    'nutmeg': dribble_nutmeg
                } if dribble else None
            }
            
            prev_event = None
            next_event = None
            if idx > 0:
                prev_row = sequence.iloc[idx-1]
                prev_type = safe_parse_json(prev_row['type'])
                prev_player = safe_parse_json(prev_row['player'])
                prev_team = safe_parse_json(prev_row['team'])
                prev_event = {
                    'event_type': prev_type.get('name') if prev_type else None,
                    'player_name': prev_player.get('name') if prev_player else None,
                    'team_name': prev_team.get('name') if prev_team else None
                }
            if idx < len(sequence) - 1:
                next_row = sequence.iloc[idx+1]
                next_type = safe_parse_json(next_row['type'])
                next_player = safe_parse_json(next_row['player'])
                next_team = safe_parse_json(next_row['team'])
                next_event = {
                    'event_type': next_type.get('name') if next_type else None,
                    'player_name': next_player.get('name') if next_player else None,
                    'team_name': next_team.get('name') if next_team else None
                }
            
            # Generate event commentary
            event_commentary = generate_event_commentary(event_obj, prev_event, next_event)
            sequence_commentary_parts.append(event_commentary)
            
            # Create enhanced row
            enhanced_row = {
                # Sequence metadata
                'sequence_id': row['sequence_id'],
                'sequence_type': row['sequence_type'],
                'sequence_key_event': row['sequence_key_event'],
                'sequence_length': row['sequence_length'],
                'event_position': row['event_position'],
                'is_key_event': row['is_key_event'],
                
                # Match metadata
                'match_id': row['match_id'],
                'home_team': row['home_team_name'],
                'away_team': row['away_team_name'],
                
                # Time metadata
                'minute': row['minute'],
                'second': row['second'],
                'period': row['period'],
                'timestamp': row['timestamp'],
                
                # Event metadata
                'event_type': event_type.get('name') if event_type else None,
                'player_name': player.get('name') if player else None,
                'player_position': position.get('name') if position else None,
                'team_name': team.get('name') if team else None,
                'possession_team': possession_team.get('name') if possession_team else None,
                
                # Location metadata
                'location_x': loc_x,
                'location_y': loc_y,
                'zone_horizontal': zone_h,
                'zone_vertical': zone_v,
                'zone_combined': zone_combined,
                
                # Context metadata
                'under_pressure': row['under_pressure'] if not pd.isna(row['under_pressure']) else False,
                'duration': row['duration'],
                'play_pattern': play_pattern.get('name') if play_pattern else None,
                
                # Pass metadata
                'pass_recipient': pass_recipient,
                'pass_length': pass_length,
                'pass_height': pass_height,
                'pass_outcome': pass_outcome,
                
                # Shot metadata
                'shot_xg': shot_xg,
                'shot_outcome': shot_outcome,
                'shot_body_part': shot_body_part,
                
                # Dribble metadata
                'dribble_outcome': dribble_outcome,
                'dribble_nutmeg': dribble_nutmeg,
                
                # Carry metadata
                'carry_end_x': carry_end_x,
                'carry_end_y': carry_end_y,
                'carry_distance': carry_distance,
                
                # Commentary
                'event_commentary': event_commentary,
                'sequence_commentary': ''  # Will be filled after loop
            }
            
            enhanced_rows.append(enhanced_row)
        
        # Add sequence commentary to all events in sequence
        sequence_commentary = ". ".join(sequence_commentary_parts) + "."
        time_stamp = f"[{sequence.iloc[0]['minute']}:{sequence.iloc[0]['second']:02d}] "
        full_sequence_commentary = time_stamp + sequence_commentary
        
        # Update all rows in this sequence
        start_idx = len(enhanced_rows) - len(sequence)
        for i in range(start_idx, len(enhanced_rows)):
            enhanced_rows[i]['sequence_commentary'] = full_sequence_commentary
    
    # Create DataFrame
    enhanced_df = pd.DataFrame(enhanced_rows)
    
    return enhanced_df

def main():
    """Main execution"""
    
    print("="*80)
    print("CREATING COMPLETE TRAINING DATA WITH METADATA & COMMENTARY")
    print("="*80)
    
    # Create enhanced dataset
    enhanced_df = create_enhanced_dataset()
    
    # Save to CSV
    output_file = os.path.join(SCRIPT_DIR, 'event_commentary_training_data.csv')
    enhanced_df.to_csv(output_file, index=False)
    
    print(f"\n✅ Complete training data created!")
    print(f"   File: {output_file}")
    print(f"   Total events: {len(enhanced_df)}")
    print(f"   Total sequences: {enhanced_df['sequence_id'].nunique()}")
    print(f"   Total columns: {len(enhanced_df.columns)}")
    
    print(f"\n📊 COLUMN CATEGORIES:")
    print(f"\n   Sequence Metadata ({6} columns):")
    print(f"      sequence_id, sequence_type, sequence_key_event,")
    print(f"      sequence_length, event_position, is_key_event")
    
    print(f"\n   Match Metadata ({5} columns):")
    print(f"      match_id, home_team, away_team, minute, second, period, timestamp")
    
    print(f"\n   Event Metadata ({7} columns):")
    print(f"      event_type, player_name, player_position, team_name,")
    print(f"      possession_team, under_pressure, duration, play_pattern")
    
    print(f"\n   Location Metadata ({5} columns):")
    print(f"      location_x, location_y, zone_horizontal,")
    print(f"      zone_vertical, zone_combined")
    
    print(f"\n   Pass Metadata ({4} columns):")
    print(f"      pass_recipient, pass_length, pass_height, pass_outcome")
    
    print(f"\n   Shot Metadata ({3} columns):")
    print(f"      shot_xg, shot_outcome, shot_body_part")
    
    print(f"\n   Dribble Metadata ({2} columns):")
    print(f"      dribble_outcome, dribble_nutmeg")
    
    print(f"\n   Carry Metadata ({3} columns):")
    print(f"      carry_end_x, carry_end_y, carry_distance")
    
    print(f"\n   Commentary ({2} columns):")
    print(f"      event_commentary, sequence_commentary")
    
    print(f"\n📋 EXAMPLE EVENT:")
    example = enhanced_df.iloc[10]
    print(f"\n   Event Type: {example['event_type']}")
    print(f"   Player: {example['player_name']} ({example['player_position']})")
    print(f"   Team: {example['team_name']}")
    print(f"   Time: {example['minute']}:{example['second']:02d}")
    print(f"   Location: {example['zone_combined']}")
    print(f"   Event Commentary: {example['event_commentary']}")
    
    print(f"\n📋 EXAMPLE SEQUENCE:")
    seq_example = enhanced_df[enhanced_df['sequence_id'] == 5].iloc[0]
    print(f"\n   Sequence Type: {seq_example['sequence_type']}")
    print(f"   Length: {seq_example['sequence_length']} events")
    print(f"   Full Commentary:")
    print(f"   {seq_example['sequence_commentary']}")
    
    print(f"\n" + "="*80)
    print("READY FOR NLP MODEL TRAINING!")
    print("="*80)
    
    print("""
    📌 HOW TO USE THIS DATA:
    
    1. EVENT-LEVEL TRAINING:
       Input: All metadata columns (sequence, match, event, location, pass/shot/dribble/carry)
       Output: event_commentary
       
    2. SEQUENCE-LEVEL TRAINING:
       Input: All events in a sequence (grouped by sequence_id)
       Output: sequence_commentary
       
    3. FEATURES AVAILABLE:
       - Temporal: minute, second, period
       - Spatial: location_x, location_y, zones
       - Player: player_name, player_position, team
       - Context: under_pressure, play_pattern
       - Event-specific: pass details, shot xG, dribble outcome, carry distance
       - Sequence: position in sequence, is_key_event
    
    4. TEMPLATES LEARNED:
       - Different templates for Pass, Shot, Dribble, Carry, Pressure
       - Context-aware (under pressure, field zone)
       - Outcome-based (goal, saved, blocked, complete, incomplete)
       - Sequential flow (connecting multiple events)
    """)
    
    print("="*80)

if __name__ == "__main__":
    main()
