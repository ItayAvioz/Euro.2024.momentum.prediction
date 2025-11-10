"""
Generate Complete Match Commentary - Phase 2
============================================
ALL-IN-ONE script that:
1. Loads raw Euro 2024 data
2. Extracts and enriches match data with tournament statistics
3. Generates rich event-level and sequence-level commentary
4. Outputs final CSV with same structure as final/semi-finals

Usage:
    python generate_full_match_commentary.py <match_id>
    
Example:
    python generate_full_match_commentary.py 3930158  # Germany vs Scotland
"""

import pandas as pd
import numpy as np
import os
import sys
import json

# Global variables for team names (set in main())
TEAM_A_NAME = None
TEAM_B_NAME = None

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(SCRIPT_DIR))))
DATA_DIR = os.path.join(PROJECT_ROOT, 'Data')

# ============================================================================
# PART 1: DATA EXTRACTION AND ENRICHMENT
# ============================================================================

def load_data():
    """Load all required data"""
    print("Loading data...")
    
    events_path = os.path.join(DATA_DIR, 'euro_2024_complete_dataset.csv')
    matches_path = os.path.join(DATA_DIR, 'matches_complete.csv')
    
    events_df = pd.read_csv(events_path)
    matches_df = pd.read_csv(matches_path)
    
    print(f"  Loaded {len(events_df):,} events")
    print(f"  Loaded {len(matches_df):,} matches")
    
    return events_df, matches_df

def get_match_info(matches_df, match_id):
    """Get match details by ID"""
    match = matches_df[matches_df['match_id'] == int(match_id)]
    
    if len(match) == 0:
        print(f"ERROR: Match {match_id} not found!")
        return None
    
    match = match.iloc[0]
    print(f"\nMatch Found:")
    print(f"  Match ID: {match['match_id']}")
    print(f"  {match['home_team_name']} vs {match['away_team_name']}")
    print(f"  Score: {match['home_score']}-{match['away_score']}")
    print(f"  Date: {match['match_date']}")
    
    return match

def calculate_tournament_stats_before_match(matches_df, events_df, team_name, match_date):
    """Calculate team and player stats BEFORE this match"""
    
    # Get all matches before this match date
    matches_df['match_date'] = pd.to_datetime(matches_df['match_date'])
    previous_matches = matches_df[matches_df['match_date'] < pd.to_datetime(match_date)]
    
    # Filter matches where team played
    team_matches = previous_matches[
        (previous_matches['home_team_name'] == team_name) | 
        (previous_matches['away_team_name'] == team_name)
    ].copy()
    
    # Team stats
    wins = draws = losses = goals_scored = goals_conceded = 0
    
    for _, match in team_matches.iterrows():
        if match['home_team_name'] == team_name:
            goals_scored += match['home_score']
            goals_conceded += match['away_score']
            if match['home_score'] > match['away_score']:
                wins += 1
            elif match['home_score'] == match['away_score']:
                draws += 1
            else:
                losses += 1
        else:
            goals_scored += match['away_score']
            goals_conceded += match['home_score']
            if match['away_score'] > match['home_score']:
                wins += 1
            elif match['away_score'] == match['home_score']:
                draws += 1
            else:
                losses += 1
    
    team_stats = {
        'team_name': team_name,
        'matches_played': len(team_matches),
        'wins': wins,
        'draws': draws,
        'losses': losses,
        'goals_scored': goals_scored,
        'goals_conceded': goals_conceded,
        'goal_difference': goals_scored - goals_conceded
    }
    
    # Player stats - goals scored in tournament before this match
    team_match_ids = team_matches['match_id'].tolist()
    team_events = events_df[events_df['match_id'].isin(team_match_ids)]
    
    # Count goals by player (check shot_outcome for Goal)
    goal_events = team_events[
        (team_events['event_type'] == 'Shot') & 
        (team_events['shot_outcome'].str.contains('Goal', case=False, na=False)) &
        (team_events['team_name'] == team_name)
    ]
    
    player_goals = goal_events.groupby('player_name').size().to_dict()
    
    return team_stats, player_goals

def enrich_match_data(match_df, matches_df, events_df, match_info):
    """Enrich match data with tournament statistics"""
    print("\nEnriching match data with tournament statistics...")
    
    home_team = match_info['home_team_name']
    away_team = match_info['away_team_name']
    match_date = match_info['match_date']
    
    # Calculate stats for both teams
    home_team_stats, home_player_goals = calculate_tournament_stats_before_match(
        matches_df, events_df, home_team, match_date
    )
    away_team_stats, away_player_goals = calculate_tournament_stats_before_match(
        matches_df, events_df, away_team, match_date
    )
    
    print(f"\n{home_team} Tournament Stats (before this match):")
    print(f"  Record: {home_team_stats['wins']}W-{home_team_stats['draws']}D-{home_team_stats['losses']}L")
    print(f"  Goals: {home_team_stats['goals_scored']} scored, {home_team_stats['goals_conceded']} conceded")
    
    print(f"\n{away_team} Tournament Stats (before this match):")
    print(f"  Record: {away_team_stats['wins']}W-{away_team_stats['draws']}D-{away_team_stats['losses']}L")
    print(f"  Goals: {away_team_stats['goals_scored']} scored, {away_team_stats['goals_conceded']} conceded")
    
    # Add columns to match_df
    def add_team_stats(row):
        team = row['team_name']
        if team == home_team:
            stats = home_team_stats
            player_goals_dict = home_player_goals
        elif team == away_team:
            stats = away_team_stats
            player_goals_dict = away_player_goals
        else:
            stats = {'wins': 0, 'draws': 0, 'losses': 0, 'goals_scored': 0, 'goals_conceded': 0}
            player_goals_dict = {}
        
        row['team_tournament_wins'] = stats['wins']
        row['team_tournament_draws'] = stats['draws']
        row['team_tournament_losses'] = stats['losses']
        row['team_tournament_goals'] = stats['goals_scored']
        row['team_tournament_conceded'] = stats['goals_conceded']
        
        # Player tournament goals
        player_name = row['player_name']
        row['player_tournament_goals'] = player_goals_dict.get(player_name, 0) if pd.notna(player_name) else 0
        
        return row
    
    match_df = match_df.apply(add_team_stats, axis=1)
    
    # Create is_goal column from shot_outcome
    match_df['is_goal'] = (
        (match_df['event_type'] == 'Shot') & 
        (match_df['shot_outcome'].str.contains('Goal', case=False, na=False))
    )
    
    # Add in-match stats (goals scored BY THIS PLAYER in THIS MATCH so far)
    match_df['player_match_goals'] = 0
    
    player_match_goal_counts = {}
    for idx, row in match_df.iterrows():
        if row['is_goal'] == True and row['event_type'] == 'Shot':
            player = row['player_name']
            if pd.notna(player):
                player_match_goal_counts[player] = player_match_goal_counts.get(player, 0) + 1
        
        # Update current row with count BEFORE this goal
        if pd.notna(row['player_name']):
            match_df.at[idx, 'player_match_goals'] = player_match_goal_counts.get(row['player_name'], 0)
    
    return match_df

# ============================================================================
# PART 2: COMMENTARY GENERATION
# ============================================================================

def parse_json_field(value):
    """Safely parse JSON-like string fields"""
    if pd.isna(value):
        return None
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            return eval(value)
        except:
            return None
    return None

def format_shot_commentary(row):
    """Generate commentary for shots"""
    player = row['player_name']
    team = row['team_name']
    is_goal = row['is_goal']
    xg = row['shot_xg']
    body_part = row['shot_body_part']
    minute = int(row['minute'])
    
    # Get dynamic team names
    global TEAM_A_NAME, TEAM_B_NAME
    
    # Get scores (handle potential NaN)
    spain_score = int(row.get('spain_score', 0)) if pd.notna(row.get('spain_score')) else 0
    england_score = int(row.get('england_score', 0)) if pd.notna(row.get('england_score')) else 0
    
    if is_goal:
        # Goal commentary!
        commentary = f"⚽ GOAL! {player} scores for {team}! "
        
        # Update score
        if team == TEAM_A_NAME:
            new_spain = spain_score + 1
            new_england = england_score
        else:
            new_spain = spain_score
            new_england = england_score + 1
        
        # Score context
        if new_spain > new_england:
            commentary += f"{TEAM_A_NAME} now lead {new_spain}-{new_england}! "
        elif new_england > new_spain:
            commentary += f"{TEAM_B_NAME} now lead {new_england}-{new_spain}! "
        else:
            commentary += f"We're level at {new_spain}-{new_spain}! "
        
        # Player context
        player_tournament_goals = int(row.get('player_tournament_goals', 0))
        player_match_goals = int(row.get('player_match_goals', 0))
        
        total_goals = player_tournament_goals + player_match_goals
        if total_goals == 1:
            commentary += f"That's {player}'s first goal of the tournament! "
        elif player_match_goals >= 2:
            commentary += f"{player} with {player_match_goals} goals in this match! "
        
        return commentary.strip()
    else:
        # Shot attempt
        outcome = str(row.get('shot_outcome', 'missed')).lower()
        
        if 'saved' in outcome:
            return f"{player} ({team}) forces a save from the goalkeeper. xG: {xg:.2f}"
        elif 'blocked' in outcome:
            return f"{player} ({team}) shot blocked by the defense. xG: {xg:.2f}"
        elif 'post' in outcome or 'bar' in outcome:
            return f"🎯 {player} ({team}) hits the woodwork! So close! xG: {xg:.2f}"
        else:
            return f"{player} ({team}) shot goes wide. xG: {xg:.2f}"

def format_pass_commentary(row):
    """Generate commentary for passes"""
    player = row['player_name']
    team = row['team_name']
    recipient = row.get('pass_recipient', '')
    outcome = row.get('pass_outcome', '')
    length = row.get('pass_length', 0)
    under_pressure = row.get('under_pressure', False)
    
    if pd.notna(recipient):
        if under_pressure:
            return f"{player} ({team}) plays under pressure to {recipient}"
        elif length and length > 30:
            return f"{player} ({team}) long ball to {recipient}"
        else:
            return f"{player} ({team}) passes to {recipient}"
    elif outcome and 'incomplete' in str(outcome).lower():
        return f"{player} ({team}) pass intercepted"
    else:
        return f"{player} ({team}) pass"

def format_carry_commentary(row):
    """Generate commentary for carries"""
    player = row['player_name']
    team = row['team_name']
    distance = row.get('carry_distance', 0)
    under_pressure = row.get('under_pressure', False)
    
    if distance and distance > 20:
        if under_pressure:
            return f"{player} ({team}) drives forward under pressure"
        else:
            return f"{player} ({team}) drives forward with the ball"
    else:
        return f"{player} ({team}) carries the ball"

def format_dribble_commentary(row):
    """Generate commentary for dribbles"""
    player = row['player_name']
    team = row['team_name']
    outcome = row.get('dribble_outcome', '')
    
    if outcome and 'complete' in str(outcome).lower():
        return f"✨ {player} ({team}) beats his marker with a skillful dribble!"
    else:
        return f"{player} ({team}) attempts to dribble"

def format_substitution_commentary(row):
    """Generate commentary for substitutions"""
    team = row['team_name']
    sub_data = parse_json_field(row.get('substitution', ''))
    
    if sub_data and isinstance(sub_data, dict):
        player_out = sub_data.get('replacement', {}).get('name', 'Unknown')
        player_in = sub_data.get('player', {}).get('name', 'Unknown')
        return f"🔄 {team} substitution: {player_in} comes on for {player_out}"
    else:
        return f"🔄 {team} substitution"

def format_foul_commentary(row):
    """Generate commentary for fouls"""
    player = row['player_name']
    team = row['team_name']
    foul_data = parse_json_field(row.get('foul_committed', ''))
    
    card = None
    if foul_data and isinstance(foul_data, dict):
        card = foul_data.get('card', {}).get('name', None) if 'card' in foul_data else None
    
    if card == 'Yellow Card':
        return f"🟨 {player} ({team}) is shown a yellow card for the foul"
    elif card == 'Red Card':
        return f"🟥 {player} ({team}) is sent off! Red card!"
    else:
        return f"{player} ({team}) commits a foul"

def format_clearance_commentary(row):
    """Generate commentary for clearances"""
    player = row['player_name']
    team = row['team_name']
    under_pressure = row.get('under_pressure', False)
    
    if under_pressure:
        return f"🛡️ {player} ({team}) clears the danger under pressure"
    else:
        return f"🛡️ {player} ({team}) clears the ball"

def format_generic_commentary(row):
    """Generate generic commentary for other event types"""
    player = row['player_name'] if pd.notna(row['player_name']) else row['team_name']
    team = row['team_name']
    event_type = row['event_type']
    
    return f"{player} ({team}) {event_type}"

def add_period_commentary(row):
    """Add special commentary for period starts"""
    minute = int(row['minute'])
    period = int(row['period'])
    event_type = row['event_type']
    play_pattern = str(row.get('play_pattern', ''))
    
    global TEAM_A_NAME, TEAM_B_NAME
    
    # Get scores
    spain_score = int(row.get('spain_score', 0)) if pd.notna(row.get('spain_score')) else 0
    england_score = int(row.get('england_score', 0)) if pd.notna(row.get('england_score')) else 0
    
    # Game start
    if minute == 0 and period == 1 and event_type == 'Pass' and 'Kick Off' in str(play_pattern):
        return f"🏆 THE MATCH IS UNDERWAY! Welcome for this clash between {TEAM_A_NAME} and {TEAM_B_NAME}! "
    
    # Second half start
    elif minute == 45 and period == 2 and event_type in ['Pass', 'Carry', 'Ball Receipt*']:
        if spain_score > england_score:
            return f"⚽ THE SECOND HALF IS UNDERWAY! {TEAM_A_NAME} lead {spain_score}-{england_score} at the break. "
        elif england_score > spain_score:
            return f"⚽ THE SECOND HALF IS UNDERWAY! {TEAM_B_NAME} lead {england_score}-{spain_score} at the break. "
        else:
            return f"⚽ THE SECOND HALF IS UNDERWAY! Still level at {spain_score}-{spain_score} after the first half. "
    
    # Stoppage time
    elif minute >= 90 and period == 2:
        return f"⏱️ Into stoppage time! "
    
    return ""

def generate_event_commentary(df):
    """Generate commentary for each event"""
    print("\nGenerating event commentary...")
    
    commentary_list = []
    
    for idx, row in df.iterrows():
        event_type = row['event_type']
        
        # Period commentary first
        period_comm = add_period_commentary(row)
        
        # Event-specific commentary
        if event_type == 'Shot':
            event_comm = format_shot_commentary(row)
        elif event_type == 'Pass':
            event_comm = format_pass_commentary(row)
        elif event_type == 'Carry':
            event_comm = format_carry_commentary(row)
        elif event_type == 'Dribble':
            event_comm = format_dribble_commentary(row)
        elif event_type == 'Substitution':
            event_comm = format_substitution_commentary(row)
        elif event_type == 'Foul Committed':
            event_comm = format_foul_commentary(row)
        elif event_type == 'Clearance':
            event_comm = format_clearance_commentary(row)
        else:
            event_comm = format_generic_commentary(row)
        
        # Combine
        full_commentary = period_comm + event_comm
        commentary_list.append(full_commentary)
    
    return commentary_list

def create_sequences(df):
    """Group related events into sequences"""
    print("\nCreating event sequences...")
    
    sequences = []
    current_sequence = []
    last_team = None
    last_minute = None
    
    for idx, row in df.iterrows():
        team = row['team_name']
        minute = row['minute']
        event_type = row['event_type']
        
        # Start new sequence if:
        # 1. Team changes
        # 2. More than 10 seconds gap
        # 3. Goal scored
        # 4. Key event (shot, substitution, etc.)
        
        start_new = False
        
        if last_team is None:
            start_new = False  # First event
        elif team != last_team:
            start_new = True  # Possession change
        elif event_type in ['Shot', 'Goal', 'Substitution', 'Foul Committed']:
            start_new = True  # Key event
        elif len(current_sequence) >= 10:
            start_new = True  # Sequence too long
        
        if start_new and current_sequence:
            sequences.append(current_sequence)
            current_sequence = []
        
        current_sequence.append(idx)
        last_team = team
        last_minute = minute
    
    # Add final sequence
    if current_sequence:
        sequences.append(current_sequence)
    
    return sequences

def generate_sequence_commentary(df, sequences):
    """Generate sequence-level commentary"""
    print("\nGenerating sequence commentary...")
    
    sequence_map = {}
    
    for seq_id, event_indices in enumerate(sequences, 1):
        # Get key event (usually the last one, or a goal if present)
        key_idx = event_indices[-1]
        
        # Check if there's a goal in this sequence
        for idx in event_indices:
            if df.iloc[idx]['is_goal'] == True:
                key_idx = idx
                break
        
        key_event = df.iloc[key_idx]
        
        # Build sequence commentary from event commentaries
        event_comms = [df.iloc[idx]['event_commentary'] for idx in event_indices]
        event_comms = [c for c in event_comms if c and len(c.strip()) > 0]
        
        # Format: [minute:second] event1. event2. event3
        minute = int(key_event['minute'])
        second = int(key_event['second'])
        
        sequence_text = f"[{minute}:{second:02d}] " + " ".join(event_comms[:5])  # Limit to 5 events
        
        # Store for all events in sequence
        for idx in event_indices:
            sequence_map[idx] = {
                'sequence_id': seq_id,
                'sequence_commentary': sequence_text,
                'sequence_length': len(event_indices)
            }
    
    return sequence_map

# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main(match_id):
    """Main function
    
    Args:
        match_id (int): The match_id to generate commentary for
    """
    
    print("="*80)
    print(f"PHASE 2: GENERATING COMPLETE COMMENTARY FOR MATCH {match_id}")
    print("="*80)
    
    # Step 1: Load data
    events_df, matches_df = load_data()
    
    # Step 2: Get match info
    match_info = get_match_info(matches_df, match_id)
    if match_info is None:
        return
    
    # Step 3: Filter events for this match
    print(f"\nFiltering events for match {match_id}...")
    match_df = events_df[events_df['match_id'] == match_id].copy()
    print(f"  Found {len(match_df)} events for this match")
    
    if len(match_df) == 0:
        print(f"ERROR: No events found for match {match_id}")
        return
    
    # Step 4: Enrich with tournament statistics
    match_df = enrich_match_data(match_df, matches_df, events_df, match_info)
    
    # Step 5: Setup team names for templates
    unique_teams = sorted(match_df['team_name'].unique())
    if len(unique_teams) == 2:
        team_a_name, team_b_name = unique_teams
        print(f"\n  Teams: {team_a_name} vs {team_b_name}")
    else:
        print(f"  WARNING: Expected 2 teams, found {len(unique_teams)}: {unique_teams}")
        team_a_name = match_info['home_team_name']
        team_b_name = match_info['away_team_name']
    
    global TEAM_A_NAME, TEAM_B_NAME
    TEAM_A_NAME = team_a_name
    TEAM_B_NAME = team_b_name
    
    # Normalize score columns to generic names (for template compatibility)
    score_cols = [c for c in match_df.columns if '_score' in c and c not in ['score_diff']]
    if len(score_cols) == 2:
        rename_map = {
            score_cols[0]: 'spain_score',
            score_cols[1]: 'england_score'
        }
        match_df = match_df.rename(columns=rename_map)
        print(f"  Normalized score columns for templates")
    
    # Step 6: Generate event commentary
    match_df['event_commentary'] = generate_event_commentary(match_df)
    
    # Step 7: Create sequences
    sequences = create_sequences(match_df)
    print(f"  Created {len(sequences)} sequences")
    
    # Step 8: Generate sequence commentary
    sequence_map = generate_sequence_commentary(match_df, sequences)
    
    # Step 9: Add sequence info to dataframe
    match_df['sequence_id'] = match_df.index.map(lambda x: sequence_map.get(x, {}).get('sequence_id'))
    match_df['sequence_commentary'] = match_df.index.map(lambda x: sequence_map.get(x, {}).get('sequence_commentary'))
    match_df['sequence_length'] = match_df.index.map(lambda x: sequence_map.get(x, {}).get('sequence_length'))
    
    # Step 10: Save output
    output_file = os.path.join(SCRIPT_DIR, '..', 'data', f'match_{match_id}_rich_commentary.csv')
    match_df.to_csv(output_file, index=False)
    
    print(f"\n{'='*80}")
    print(f"✅ SUCCESS! Rich commentary saved to:")
    print(f"   {output_file}")
    print(f"{'='*80}")
    print(f"   Total events: {len(match_df):,}")
    print(f"   Total sequences: {len(sequences)}")
    print(f"   Columns: {len(match_df.columns)}")
    print(f"   File size: {os.path.getsize(output_file):,} bytes")
    
    # Show sample commentary
    print(f"\n{'='*80}")
    print("SAMPLE COMMENTARY (First 10 events):")
    print("="*80)
    
    for i in range(min(10, len(match_df))):
        row = match_df.iloc[i]
        print(f"\n[{row['minute']}:{row['second']:02d}] {row['event_type']}")
        print(f"  Player: {row['player_name']} ({row['team_name']})")
        print(f"  Event: {row['event_commentary']}")
        if pd.notna(row['sequence_commentary']):
            print(f"  Sequence: {row['sequence_commentary'][:100]}...")
    
    print(f"\n{'='*80}")
    print(f"✅ PHASE 2 COMPLETE FOR MATCH {match_id}")
    print(f"   {team_a_name} vs {team_b_name}")
    print(f"   Final Score: {match_info['home_score']}-{match_info['away_score']}")
    print("="*80)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        match_id = int(sys.argv[1])
        main(match_id)
    else:
        print("="*80)
        print("PHASE 2: Euro 2024 Commentary Generator")
        print("="*80)
        print("\nUsage: python generate_full_match_commentary.py <match_id>")
        print("\nExamples:")
        print("  python generate_full_match_commentary.py 3930158  # Germany vs Scotland")
        print("  python generate_full_match_commentary.py 3943043  # Spain vs England (Final)")
        print("\nTo find match_ids, check Data/matches_complete.csv")
        sys.exit(1)

