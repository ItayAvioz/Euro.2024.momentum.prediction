"""
Generate Commentary Examples for Top 11 Event Types
===================================================
This script extracts real examples from the training data and generates
commentary for each of the top 11 event types.
"""

import pandas as pd
import os

# Setup paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(SCRIPT_DIR, 'event_commentary_training_data.csv')

def format_pass_commentary(row):
    """Generate commentary for Pass events"""
    player = row['player_name']
    recipient = row['pass_recipient']
    length = row['pass_length']
    height = row['pass_height']
    
    # Determine pass distance
    if pd.notna(length):
        if length < 15:
            distance = "short"
        elif length < 30:
            distance = "medium"
        else:
            distance = "long"
    else:
        distance = "medium"
    
    # Determine pass trajectory
    if height == "Ground Pass":
        trajectory = "along the ground"
        template = f"{player} plays {distance} pass {trajectory} to {recipient}"
    elif height == "High Pass":
        template = f"{player} plays {distance} ball through the air to {recipient}"
    elif height == "Low Pass":
        template = f"{player} plays {distance} pass to {recipient}"
    else:
        trajectory = "along the ground"
        template = f"{player} plays {distance} pass {trajectory} to {recipient}"
    
    return template

def format_shot_commentary(row):
    """Generate commentary for Shot events"""
    player = row['player_name']
    outcome = row['shot_outcome']
    
    if outcome == "Blocked":
        return f"{player} shoots - BLOCKED!"
    elif outcome == "Saved":
        return f"{player} shoots - saved by the goalkeeper!"
    elif outcome in ["Off T", "Wayward"]:
        return f"{player} shoots - just wide!"
    elif outcome == "Goal":
        return f"{player} shoots - GOAL!"
    else:
        return f"{player} shoots!"

def format_carry_commentary(row):
    """Generate commentary for Carry events"""
    player = row['player_name']
    under_pressure = row['under_pressure']
    
    if under_pressure:
        return f"{player} under pressure, carries forward"
    else:
        return f"{player} carries the ball"

def format_pressure_commentary(row, df, idx):
    """Generate commentary for Pressure events"""
    player = row['player_name']
    
    # Try to find who is being pressed from context
    sequence_id = row['sequence_id']
    event_pos = row['event_position']
    
    # Look at previous/next events in same sequence
    sequence_events = df[df['sequence_id'] == sequence_id].sort_values('event_position')
    
    # Try to find the ball carrier (opposite team)
    target_player = None
    for _, event in sequence_events.iterrows():
        if event['event_position'] == event_pos - 1 or event['event_position'] == event_pos + 1:
            if event['team_name'] != row['team_name'] and event['event_type'] in ['Carry', 'Pass', 'Shot', 'Dribble']:
                target_player = event['player_name']
                break
    
    if target_player:
        return f"{player} presses {target_player}"
    else:
        return f"{player} presses the ball carrier"

def format_dribble_commentary(row, df, idx):
    """Generate commentary for Dribble events"""
    player = row['player_name']
    nutmeg = row['dribble_nutmeg']
    outcome = row['dribble_outcome']
    
    # Try to find defender from "Dribbled Past" event nearby
    sequence_id = row['sequence_id']
    event_pos = row['event_position']
    
    sequence_events = df[df['sequence_id'] == sequence_id].sort_values('event_position')
    defender = None
    
    for _, event in sequence_events.iterrows():
        if event['event_type'] == 'Dribbled Past' and abs(event['event_position'] - event_pos) <= 1:
            defender = event['player_name']
            break
    
    if nutmeg:
        if defender:
            return f"{player} takes on {defender} - NUTMEG!"
        else:
            return f"{player} takes on the defender - NUTMEG!"
    elif outcome == "Complete":
        if defender:
            return f"{player} beats {defender}"
        else:
            return f"{player} beats the defender"
    else:
        return f"{player} takes on the defender"

def format_simple_commentary(row, event_type):
    """Generate commentary for simple event types"""
    player = row['player_name']
    
    templates = {
        'Ball Receipt*': f"{player} receives",
        'Block': f"BLOCKED by {player}!",
        'Goal Keeper': "Goalkeeper deals with it",
        'Dribbled Past': "Dribbled Past",
        'Ball Recovery': "Ball Recovery",
        'Duel': "Duel"
    }
    
    return templates.get(event_type, f"{event_type} by {player}")

def display_event_examples(df, event_type, num_examples=3):
    """Display examples for a specific event type"""
    events = df[df['event_type'] == event_type].head(num_examples)
    
    print(f"\n{'='*80}")
    print(f"EVENT TYPE: {event_type.upper()}")
    print(f"{'='*80}\n")
    
    for idx, (_, row) in enumerate(events.iterrows(), 1):
        print(f"EXAMPLE {idx}:")
        print(f"  Match: {row['home_team']} vs {row['away_team']}")
        print(f"  Time: {row['minute']}:{row['second']:02d}")
        print(f"  Player: {row['player_name']} ({row['team_name']})")
        print(f"  Zone: {row['zone_combined']}")
        
        # Event-specific details
        if event_type == "Pass":
            print(f"  Recipient: {row['pass_recipient']}")
            print(f"  Length: {row['pass_length']:.1f}m" if pd.notna(row['pass_length']) else "  Length: N/A")
            print(f"  Height: {row['pass_height']}")
            print(f"  Outcome: {row['pass_outcome'] if pd.notna(row['pass_outcome']) else 'Success'}")
            commentary = format_pass_commentary(row)
            
        elif event_type == "Shot":
            print(f"  xG: {row['shot_xg']:.3f}" if pd.notna(row['shot_xg']) else "  xG: N/A")
            print(f"  Outcome: {row['shot_outcome']}")
            print(f"  Body Part: {row['shot_body_part']}")
            commentary = format_shot_commentary(row)
            
        elif event_type == "Carry":
            print(f"  Distance: {row['carry_distance']:.2f}m" if pd.notna(row['carry_distance']) else "  Distance: N/A")
            print(f"  Under Pressure: {row['under_pressure']}")
            print(f"  Duration: {row['duration']:.2f}s" if pd.notna(row['duration']) else "  Duration: N/A")
            commentary = format_carry_commentary(row)
            
        elif event_type == "Pressure":
            print(f"  Duration: {row['duration']:.2f}s" if pd.notna(row['duration']) else "  Duration: N/A")
            commentary = format_pressure_commentary(row, df, idx)
            
        elif event_type == "Dribble":
            print(f"  Outcome: {row['dribble_outcome']}")
            print(f"  Nutmeg: {row['dribble_nutmeg']}")
            print(f"  Under Pressure: {row['under_pressure']}")
            commentary = format_dribble_commentary(row, df, idx)
            
        else:
            commentary = format_simple_commentary(row, event_type)
        
        print(f"\n  Generated Commentary: \"{commentary}\"")
        print(f"  Original Commentary: \"{row['event_commentary']}\"")
        print()

def main():
    """Main function"""
    print("Loading data...")
    df = pd.read_csv(DATA_FILE)
    print(f"Loaded {len(df)} events from {df['sequence_id'].nunique()} sequences\n")
    
    # Top 11 event types
    top_11_events = [
        'Ball Receipt*',
        'Carry',
        'Pressure',
        'Pass',
        'Shot',
        'Dribble',
        'Block',
        'Goal Keeper',
        'Dribbled Past',
        'Ball Recovery',
        'Duel'
    ]
    
    # Display distribution
    print("EVENT TYPE DISTRIBUTION:")
    print("-" * 40)
    for event_type in top_11_events:
        count = len(df[df['event_type'] == event_type])
        print(f"  {event_type:<20} {count:>3} occurrences")
    print()
    
    # Generate examples for each event type
    for event_type in top_11_events:
        display_event_examples(df, event_type, num_examples=2)
    
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"Total Events: {len(df)}")
    print(f"Total Sequences: {df['sequence_id'].nunique()}")
    print(f"Total Matches: {df['match_id'].nunique()}")
    print(f"Event Types Covered: {len(top_11_events)}")
    print()

if __name__ == "__main__":
    main()
