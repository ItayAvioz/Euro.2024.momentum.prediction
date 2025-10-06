"""
Extract Event Sequences for NLP Commentator Training
=====================================================
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
    df = pd.read_csv(data_path)
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
        3941017,  # R16: England 2-1 Slovakia (last-minute equalizer + extra time)
    ]
    
    match_info = matches[matches['match_id'].isin(selected_matches)][
        ['match_id', 'home_team_name', 'away_team_name', 'home_score', 'away_score', 'stage']
    ]
    
    print("\nSelected Games:")
    for _, match in match_info.iterrows():
        print(f"  {match['match_id']}: {match['home_team_name']} {match['home_score']}-{match['away_score']} {match['away_team_name']} ({match['stage']})")
    
    return selected_matches, match_info

def extract_event_sequences(df, match_id, num_sequences=10):
    """Extract 10 meaningful event sequences from a match"""
    match_events = df[df['match_id'] == match_id].copy()
    match_events = match_events.sort_values(['period', 'minute', 'second']).reset_index(drop=True)
    
    # Target event types
    target_types = ['Shot', 'Dribble', 'Pressure', 'Carry', 'Pass']  # Include Pass for context
    
    sequences = []
    
    # 1. Extract all goals and their build-up (2-5 events before)
    goals = match_events[match_events['shot'].str.contains('"outcome".*"Goal"', na=False, regex=True)]
    for idx in goals.index:
        start_idx = max(0, idx - 4)  # 4 events before goal
        end_idx = min(len(match_events), idx + 1)  # Include goal
        sequence = match_events.iloc[start_idx:end_idx]
        sequences.append({
            'type': 'goal_buildup',
            'events': sequence,
            'key_event_idx': len(sequence) - 1,
            'minute': sequence.iloc[-1]['minute']
        })
    
    # 2. Extract dangerous shots and their build-up
    dangerous_shots = match_events[
        (match_events['type'] == 'Shot') & 
        (match_events['shot'].str.contains('"outcome".*"Saved"|"Post"', na=False, regex=True))
    ]
    for idx in dangerous_shots.index[:3]:  # Top 3 dangerous shots
        start_idx = max(0, idx - 3)
        end_idx = min(len(match_events), idx + 1)
        sequence = match_events.iloc[start_idx:end_idx]
        sequences.append({
            'type': 'shot_sequence',
            'events': sequence,
            'key_event_idx': len(sequence) - 1,
            'minute': sequence.iloc[-1]['minute']
        })
    
    # 3. Extract successful dribble sequences
    successful_dribbles = match_events[
        (match_events['type'] == 'Dribble') & 
        (match_events['dribble'].str.contains('"outcome".*"Complete"', na=False, regex=True))
    ]
    for idx in successful_dribbles.index[:2]:  # Top 2 dribbles
        start_idx = max(0, idx - 2)
        end_idx = min(len(match_events), idx + 3)  # Include aftermath
        sequence = match_events.iloc[start_idx:end_idx]
        sequences.append({
            'type': 'dribble_sequence',
            'events': sequence,
            'key_event_idx': 2 if len(sequence) >= 3 else len(sequence) - 1,
            'minute': sequence.iloc[0]['minute']
        })
    
    # 4. Extract high-pressure sequences
    pressure_events = match_events[match_events['type'] == 'Pressure']
    # Find clusters of pressure (3+ pressure events in short succession)
    pressure_clusters = []
    for idx in pressure_events.index:
        nearby = match_events.loc[max(0, idx-5):min(len(match_events), idx+5)]
        if len(nearby[nearby['type'] == 'Pressure']) >= 2:
            pressure_clusters.append(idx)
    
    for idx in pressure_clusters[:2]:  # Top 2 pressure sequences
        start_idx = max(0, idx - 2)
        end_idx = min(len(match_events), idx + 3)
        sequence = match_events.iloc[start_idx:end_idx]
        sequences.append({
            'type': 'pressure_sequence',
            'events': sequence,
            'key_event_idx': 2,
            'minute': sequence.iloc[0]['minute']
        })
    
    # 5. Extract carry sequences (attacking runs)
    carries = match_events[match_events['type'] == 'Carry']
    # Find carries with significant forward movement
    for idx in carries.index[:2]:  # Top 2 carries
        start_idx = max(0, idx - 1)
        end_idx = min(len(match_events), idx + 3)
        sequence = match_events.iloc[start_idx:end_idx]
        sequences.append({
            'type': 'carry_sequence',
            'events': sequence,
            'key_event_idx': 1,
            'minute': sequence.iloc[0]['minute']
        })
    
    # Sort by minute and select top 10 diverse sequences
    sequences.sort(key=lambda x: x['minute'])
    
    # Ensure diversity - max 3 of same type
    type_counts = {}
    final_sequences = []
    for seq in sequences:
        seq_type = seq['type']
        if type_counts.get(seq_type, 0) < 3:
            final_sequences.append(seq)
            type_counts[seq_type] = type_counts.get(seq_type, 0) + 1
        if len(final_sequences) >= num_sequences:
            break
    
    return final_sequences

def create_commentator_dataset(df, selected_matches):
    """Create complete dataset for NLP commentator"""
    
    # Recommended columns for commentator
    columns_to_extract = [
        # Identifiers
        'match_id', 'id', 'index',
        
        # Temporal
        'minute', 'second', 'period', 'timestamp',
        
        # Event type
        'type', 'possession_team',
        
        # Location
        'location', 'location_x', 'location_y',
        
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
        
        # Tactics
        'tactics',
        
        # Match context
        'home_team_name', 'away_team_name'
    ]
    
    all_sequences = []
    sequence_id = 1
    
    for match_id in selected_matches:
        print(f"\nProcessing Match {match_id}...")
        sequences = extract_event_sequences(df, match_id, num_sequences=10)
        
        for seq in sequences:
            events_df = seq['events']
            
            # Add sequence metadata
            for idx, row in events_df.iterrows():
                event_data = {}
                
                # Basic identifiers
                event_data['sequence_id'] = sequence_id
                event_data['sequence_type'] = seq['type']
                event_data['is_key_event'] = (events_df.index.get_loc(idx) == seq['key_event_idx'])
                event_data['event_position_in_sequence'] = events_df.index.get_loc(idx) + 1
                event_data['sequence_length'] = len(events_df)
                
                # Extract all relevant columns
                for col in columns_to_extract:
                    if col in row.index:
                        value = row[col]
                        # Handle NaN and complex types
                        if pd.isna(value):
                            event_data[col] = None
                        elif isinstance(value, (dict, list)):
                            event_data[col] = json.dumps(value)
                        else:
                            event_data[col] = value
                    else:
                        event_data[col] = None
                
                all_sequences.append(event_data)
            
            sequence_id += 1
            
        print(f"  Extracted {len(sequences)} sequences")
    
    return pd.DataFrame(all_sequences)

def main():
    """Main execution"""
    print("=" * 60)
    print("NLP COMMENTATOR DATA EXTRACTION")
    print("=" * 60)
    
    # Load data
    df = load_data()
    
    # Select games
    selected_matches, match_info = select_exciting_games(df)
    
    # Create dataset
    print("\nExtracting event sequences...")
    commentator_df = create_commentator_dataset(df, selected_matches)
    
    # Save to CSV
    output_file = 'commentator_training_data.csv'
    commentator_df.to_csv(output_file, index=False)
    
    print(f"\n✅ Dataset created successfully!")
    print(f"   File: {output_file}")
    print(f"   Total events: {len(commentator_df)}")
    print(f"   Total sequences: {commentator_df['sequence_id'].nunique()}")
    print(f"   Columns: {len(commentator_df.columns)}")
    
    # Display statistics
    print("\n📊 Sequence Type Distribution:")
    print(commentator_df.groupby('sequence_type')['sequence_id'].nunique())
    
    print("\n📊 Event Type Distribution:")
    print(commentator_df['type'].value_counts().head(10))
    
    print("\n📋 Sample Data (First 5 rows):")
    print(commentator_df[['sequence_id', 'sequence_type', 'minute', 'type', 'player', 'location']].head(10))
    
    print("\n" + "=" * 60)
    print("RECOMMENDED COLUMNS FOR NLP COMMENTATOR")
    print("=" * 60)
    print("""
    PRIMARY COLUMNS (Essential for commentary):
    -------------------------------------------
    1. minute, second, period - Temporal context ("In the 67th minute...")
    2. type - Event type ("Shot", "Pass", "Dribble", etc.)
    3. player, team - Who did what ("Yamal drives forward...")
    4. location - Field position ("From outside the box...", "In the penalty area...")
    5. shot, pass, dribble - Event outcome details ("Saved by Pickford...", "Complete pass...")
    
    CONTEXTUAL COLUMNS (Add richness):
    ----------------------------------
    6. under_pressure - Pressure context ("Under pressure from...")
    7. play_pattern - Game phase ("From open play", "From corner")
    8. position - Player position ("The center forward...")
    9. duration - Event duration (for carries/dribbles)
    10. related_events - Event chains (understand sequences)
    
    MATCH CONTEXT COLUMNS:
    ---------------------
    11. home_team_name, away_team_name - Team names
    12. possession_team - Who has the ball
    13. tactics - Formation/tactical context
    
    SPECIAL COLUMNS (For specific events):
    -------------------------------------
    14. goalkeeper - For saves ("Spectacular save...")
    15. duel - For duels ("Wins the aerial duel...")
    16. carry - For runs ("Carries the ball forward...")
    17. interception - For interceptions ("Intercepts the pass...")
    """)

if __name__ == "__main__":
    main()
