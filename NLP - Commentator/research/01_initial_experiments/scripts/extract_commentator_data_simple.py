"""
Extract Event Sequences for NLP Commentator Training - Simplified
==================================================================
Extract 30 event sequences (3 games × 10 sequences) for commentator model development.
Focus on: Goals, Shots, Dribbles, Pressure, Carries with 2-5 consecutive events.
"""

import pandas as pd
import numpy as np
import json
import os

# Get project root directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
DATA_DIR = os.path.join(PROJECT_ROOT, 'Data')

def load_data():
    """Load the complete dataset"""
    print("Loading Euro 2024 dataset...")
    data_path = os.path.join(DATA_DIR, 'euro_2024_complete_dataset.csv')
    print(f"Loading from: {data_path}")
    df = pd.read_csv(data_path, low_memory=False)
    print(f"Loaded {len(df):,} events")
    return df

def select_exciting_games(df):
    """Select 3 exciting games for analysis"""
    # Get matches data
    matches_path = os.path.join(DATA_DIR, 'matches_complete.csv')
    matches = pd.read_csv(matches_path)
    
    # Select 3 dramatic/high-scoring games
    selected_matches = [
        3943043,  # Final: Spain 2-1 England (dramatic winner)
        3942226,  # QF: Spain 2-1 Germany (extra time thriller)
        3941017,  # R16: England 2-1 Slovakia (last-minute equalizer)
    ]
    
    match_info = matches[matches['match_id'].isin(selected_matches)][
        ['match_id', 'home_team_name', 'away_team_name', 'home_score', 'away_score', 'stage']
    ]
    
    print("\nSelected Games:")
    for _, match in match_info.iterrows():
        print(f"  {match['match_id']}: {match['home_team_name']} {match['home_score']}-{match['away_score']} {match['away_team_name']} ({match['stage']})")
    
    return selected_matches, match_info

def extract_key_events(df, match_id, num_events=10):
    """Extract key events from a match with their context"""
    match_events = df[df['match_id'] == match_id].copy()
    match_events = match_events.sort_values(['period', 'minute', 'second']).reset_index(drop=True)
    
    print(f"  Total events in match: {len(match_events)}")
    
    # Parse type column to get event names
    def get_event_name(type_value):
        """Extract event name from type column"""
        if pd.isna(type_value):
            return None
        if isinstance(type_value, str):
            try:
                # Try to parse as dict-like string
                type_dict = eval(type_value)
                return type_dict.get('name', None)
            except:
                return type_value
        return None
    
    match_events['event_name'] = match_events['type'].apply(get_event_name)
    
    sequences = []
    
    # 1. Find all shots (includes goals)
    shots = match_events[match_events['event_name'] == 'Shot']
    print(f"  Found {len(shots)} shots")
    for idx in shots.index[:4]:  # Top 4 shots
        start_idx = max(0, idx - 3)  # 3 events before
        end_idx = min(len(match_events), idx + 2)  # 1 event after
        sequences.append({
            'start_idx': start_idx,
            'end_idx': end_idx,
            'key_idx': idx,
            'type': 'shot_sequence',
            'key_event': 'Shot'
        })
    
    # 2. Find dribbles
    dribbles = match_events[match_events['event_name'] == 'Dribble']
    print(f"  Found {len(dribbles)} dribbles")
    for idx in dribbles.index[:2]:  # Top 2 dribbles
        start_idx = max(0, idx - 2)
        end_idx = min(len(match_events), idx + 3)
        sequences.append({
            'start_idx': start_idx,
            'end_idx': end_idx,
            'key_idx': idx,
            'type': 'dribble_sequence',
            'key_event': 'Dribble'
        })
    
    # 3. Find carries (attacking runs)
    carries = match_events[match_events['event_name'] == 'Carry']
    print(f"  Found {len(carries)} carries")
    for idx in carries.index[:2]:  # Top 2 carries
        start_idx = max(0, idx - 1)
        end_idx = min(len(match_events), idx + 3)
        sequences.append({
            'start_idx': start_idx,
            'end_idx': end_idx,
            'key_idx': idx,
            'type': 'carry_sequence',
            'key_event': 'Carry'
        })
    
    # 4. Find pressure moments
    pressure = match_events[match_events['event_name'] == 'Pressure']
    print(f"  Found {len(pressure)} pressure events")
    for idx in pressure.index[:2]:  # Top 2 pressure moments
        start_idx = max(0, idx - 2)
        end_idx = min(len(match_events), idx + 3)
        sequences.append({
            'start_idx': start_idx,
            'end_idx': end_idx,
            'key_idx': idx,
            'type': 'pressure_sequence',
            'key_event': 'Pressure'
        })
    
    # Sort by minute and limit to 10
    sequences.sort(key=lambda x: match_events.iloc[x['start_idx']]['minute'] if 'minute' in match_events.columns else 0)
    sequences = sequences[:10]
    
    print(f"  Selected {len(sequences)} sequences")
    
    return match_events, sequences

def create_commentator_dataset(df, selected_matches):
    """Create complete dataset for NLP commentator"""
    
    # Key columns for NLP commentator
    key_columns = [
        # Identifiers
        'match_id', 'id', 'index',
        
        # Temporal
        'minute', 'second', 'period', 'timestamp',
        
        # Event type
        'type', 'possession_team',
        
        # Location
        'location', 
        
        # Player & Team
        'player', 'player_id', 'team', 'position',
        
        # Event details (JSON fields)
        'shot', 'pass', 'dribble', 'carry', 'duel', 
        'interception', 'clearance', 'goalkeeper',
        
        # Context
        'under_pressure', 'counterpress', 'play_pattern',
        'duration',
        
        # Related events
        'related_events',
        
        # Match context
        'home_team_name', 'away_team_name'
    ]
    
    all_rows = []
    sequence_id = 1
    
    for match_id in selected_matches:
        print(f"\nProcessing Match {match_id}...")
        match_events, sequences = extract_key_events(df, match_id, num_events=10)
        
        for seq_info in sequences:
            # Extract events in sequence
            sequence_events = match_events.iloc[seq_info['start_idx']:seq_info['end_idx']]
            
            # Add each event with sequence metadata
            for pos, (idx, row) in enumerate(sequence_events.iterrows(), 1):
                event_row = {
                    'sequence_id': sequence_id,
                    'sequence_type': seq_info['type'],
                    'sequence_key_event': seq_info['key_event'],
                    'event_position': pos,
                    'sequence_length': len(sequence_events),
                    'is_key_event': (idx == seq_info['key_idx'])
                }
                
                # Add all available columns
                for col in key_columns:
                    if col in row.index:
                        value = row[col]
                        if pd.isna(value):
                            event_row[col] = None
                        elif col == 'location' and isinstance(value, str):
                            # Keep location as string for now
                            event_row[col] = value
                        else:
                            event_row[col] = value
                    else:
                        event_row[col] = None
                
                all_rows.append(event_row)
            
            sequence_id += 1
    
    return pd.DataFrame(all_rows)

def main():
    """Main execution"""
    print("=" * 70)
    print("NLP COMMENTATOR DATA EXTRACTION - SIMPLIFIED")
    print("=" * 70)
    
    # Load data
    df = load_data()
    
    # Select games
    selected_matches, match_info = select_exciting_games(df)
    
    # Create dataset
    print("\nExtracting event sequences...")
    commentator_df = create_commentator_dataset(df, selected_matches)
    
    # Save to CSV
    output_file = os.path.join(SCRIPT_DIR, 'commentator_training_data.csv')
    commentator_df.to_csv(output_file, index=False)
    
    print(f"\n✅ Dataset created successfully!")
    print(f"   File: {output_file}")
    print(f"   Total events: {len(commentator_df)}")
    print(f"   Total sequences: {commentator_df['sequence_id'].nunique()}")
    print(f"   Columns: {len(commentator_df.columns)}")
    
    # Display statistics
    print("\n📊 Sequence Type Distribution:")
    seq_types = commentator_df.groupby('sequence_type').size().sort_values(ascending=False)
    for seq_type, count in seq_types.items():
        print(f"   {seq_type}: {count} events ({count // commentator_df['sequence_length'].iloc[0]} sequences)")
    
    print("\n📊 Event Type Distribution:")
    event_types = commentator_df['type'].value_counts().head(10)
    for event_type, count in event_types.items():
        print(f"   {event_type}: {count}")
    
    print("\n📋 Sample Data (First 10 rows):")
    display_cols = ['sequence_id', 'sequence_type', 'event_position', 'minute', 'type', 'player', 'team']
    available_cols = [col for col in display_cols if col in commentator_df.columns]
    print(commentator_df[available_cols].head(10).to_string())
    
    print("\n" + "=" * 70)
    print("RECOMMENDED COLUMNS FOR NLP COMMENTATOR")
    print("=" * 70)
    print("""
PRIMARY COLUMNS (Essential for commentary):
-------------------------------------------
1.  minute, second, period     - Temporal context ("In the 67th minute...")
2.  type                       - Event type ("Shot", "Pass", "Dribble")
3.  player, team               - Who did what ("Yamal drives forward...")
4.  location                   - Field position ("[92.0, 38.0]" → "From the edge of the box...")
5.  shot, pass, dribble        - Event outcome details (JSON with detailed info)

CONTEXTUAL COLUMNS (Add richness):
----------------------------------
6.  under_pressure             - Pressure context ("Under pressure...")
7.  play_pattern               - Game phase ("From open play", "From corner")
8.  position                   - Player position ("The center forward...")
9.  duration                   - Event duration (important for carries)
10. related_events             - Event chains (to understand sequences)

MATCH CONTEXT:
--------------
11. home_team_name, away_team_name - Team names
12. possession_team                - Who has the ball
13. timestamp                      - Exact timing

SPECIAL COLUMNS (For specific events):
--------------------------------------
14. goalkeeper     - For saves ("Spectacular save by Pickford...")
15. duel           - For duels ("Wins the aerial duel...")
16. carry          - For runs ("Carries forward 15 meters...")
17. interception   - For interceptions ("Intercepts the through ball...")

SEQUENCE METADATA (For NLP training):
------------------------------------
18. sequence_id          - Unique sequence identifier
19. sequence_type        - Type of sequence (shot/dribble/pressure/carry)
20. sequence_key_event   - The main event in the sequence
21. event_position       - Position of event in sequence (1, 2, 3...)
22. sequence_length      - Total events in sequence
23. is_key_event         - True if this is the main event

USAGE NOTES:
-----------
- location: Parse "[x, y]" coordinates to natural language ("penalty area", "left wing", etc.)
- JSON fields (shot, pass, dribble): Parse to extract outcomes, distances, body parts used
- Build context by looking at previous events in same sequence (event_position - 1)
- Use is_key_event to identify the climax of each sequence for emphasis
    """)
    
    # Create a summary document
    summary_file = os.path.join(SCRIPT_DIR, 'data_extraction_summary.md')
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("# NLP Commentator Training Data - Extraction Summary\n\n")
        f.write(f"## Dataset Overview\n\n")
        f.write(f"- **Total Events**: {len(commentator_df)}\n")
        f.write(f"- **Total Sequences**: {commentator_df['sequence_id'].nunique()}\n")
        f.write(f"- **Matches**: {len(selected_matches)}\n\n")
        
        f.write("## Selected Matches\n\n")
        for _, match in match_info.iterrows():
            f.write(f"- **{match['match_id']}**: {match['home_team_name']} {match['home_score']}-{match['away_score']} {match['away_team_name']} ({match['stage']})\n")
        
        f.write("\n## Sequence Types\n\n")
        for seq_type, count in seq_types.items():
            f.write(f"- **{seq_type}**: {count} events\n")
        
        f.write("\n## Column Descriptions\n\n")
        for col in commentator_df.columns:
            non_null = commentator_df[col].notna().sum()
            f.write(f"- **{col}**: {non_null}/{len(commentator_df)} non-null values\n")
    
    print(f"\n📄 Summary document created: {summary_file}")
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
