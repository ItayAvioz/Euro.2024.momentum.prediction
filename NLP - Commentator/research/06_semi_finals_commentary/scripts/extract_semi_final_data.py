"""
Extract Semi-Final Commentary Data - Generic script for any match
==================================================================
Adapted from the final game extraction script.
Can be used for Netherlands vs England or Spain vs France semi-finals.
"""

import pandas as pd
import numpy as np
import os
import json
import sys

# Setup paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(SCRIPT_DIR))))
DATA_DIR = os.path.join(PROJECT_ROOT, 'Data')

def load_data():
    """Load all required data"""
    print("Loading data...")
    
    events_path = os.path.join(DATA_DIR, 'euro_2024_complete_dataset.csv')
    matches_path = os.path.join(DATA_DIR, 'matches_complete.csv')
    
    events_df = pd.read_csv(events_path)
    matches_df = pd.read_csv(matches_path)
    
    print(f"Loaded {len(events_df):,} events")
    print(f"Loaded {len(matches_df):,} matches")
    
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
    
    # Parse team column
    def get_team_name_from_event(row):
        try:
            if pd.notna(row['team']):
                team_dict = eval(row['team'])
                return team_dict.get('name', None)
        except:
            pass
        return None
    
    team_events['team_name'] = team_events.apply(get_team_name_from_event, axis=1)
    team_events = team_events[team_events['team_name'] == team_name]
    
    # Get event type
    def get_event_type(row):
        try:
            if pd.notna(row['type']):
                type_dict = eval(row['type'])
                return type_dict.get('name', None)
        except:
            pass
        return None
    
    team_events['event_type'] = team_events.apply(get_event_type, axis=1)
    
    # Get player names
    def get_player_name(row):
        try:
            if pd.notna(row['player']):
                player_dict = eval(row['player'])
                return player_dict.get('name', None)
        except:
            pass
        return None
    
    team_events['player_name'] = team_events.apply(get_player_name, axis=1)
    
    # Count goals by player
    goals = team_events[team_events['event_type'] == 'Shot'].copy()
    
    def is_goal(row):
        try:
            if pd.notna(row['shot']):
                shot_dict = eval(row['shot'])
                outcome = shot_dict.get('outcome', {})
                if isinstance(outcome, dict):
                    return outcome.get('name') == 'Goal'
        except:
            pass
        return False
    
    goals['is_goal'] = goals.apply(is_goal, axis=1)
    player_goals = goals[goals['is_goal']].groupby('player_name').size().to_dict()
    
    return team_stats, player_goals

def extract_match_events(events_df, match_id):
    """Extract ALL events from the match"""
    
    match_events = events_df[events_df['match_id'] == int(match_id)].copy()
    match_events = match_events.sort_values(['period', 'minute', 'second'])
    
    print(f"\nExtracted {len(match_events)} events (FULL MATCH)")
    print(f"Periods: {sorted(match_events['period'].unique())}")
    print(f"Minutes: {match_events['minute'].min()}-{match_events['minute'].max()}")
    
    return match_events

def parse_json_field(value):
    """Safely parse JSON-like string fields"""
    if pd.isna(value):
        return None
    try:
        if isinstance(value, str):
            return eval(value)
        return value
    except:
        return None

def enrich_event_data(events_df, team_stats, player_goals, match_info, team1_name, team2_name):
    """Enrich each event with detailed metadata and stats"""
    
    enriched_events = []
    
    # Track in-match stats
    team1_goals_in_match = []
    team2_goals_in_match = []
    team1_score = 0
    team2_score = 0
    
    # Convert to list for context tracking
    events_list = list(events_df.iterrows())
    
    for event_idx, (idx, row) in enumerate(events_list):
        event = {}
        
        # Basic metadata
        event['event_id'] = idx
        event['match_id'] = row['match_id']
        event['period'] = row['period']
        event['minute'] = row['minute']
        event['second'] = row['second']
        event['timestamp'] = row['timestamp']
        
        # Parse event details
        type_dict = parse_json_field(row['type'])
        event['event_type'] = type_dict.get('name') if type_dict else None
        
        player_dict = parse_json_field(row['player'])
        event['player_name'] = player_dict.get('name') if player_dict else None
        
        team_dict = parse_json_field(row['team'])
        event['team_name'] = team_dict.get('name') if team_dict else None
        
        poss_team_dict = parse_json_field(row['possession_team'])
        event['possession_team'] = poss_team_dict.get('name') if poss_team_dict else None
        
        # Location
        location = parse_json_field(row['location'])
        if location and isinstance(location, list) and len(location) >= 2:
            event['location_x'] = location[0]
            event['location_y'] = location[1]
        else:
            event['location_x'] = None
            event['location_y'] = None
        
        # Pressure & duration
        event['under_pressure'] = row.get('under_pressure', False)
        event['duration'] = row.get('duration', None)
        
        # Play pattern
        play_pattern_dict = parse_json_field(row['play_pattern'])
        event['play_pattern'] = play_pattern_dict.get('name') if play_pattern_dict else None
        
        # Pass data
        pass_dict = parse_json_field(row.get('pass'))
        if pass_dict:
            recipient_dict = pass_dict.get('recipient', {})
            event['pass_recipient'] = recipient_dict.get('name') if isinstance(recipient_dict, dict) else None
            event['pass_length'] = pass_dict.get('length')
            height_dict = pass_dict.get('height', {})
            event['pass_height'] = height_dict.get('name') if isinstance(height_dict, dict) else None
            outcome_dict = pass_dict.get('outcome', {})
            event['pass_outcome'] = outcome_dict.get('name') if isinstance(outcome_dict, dict) else None
            event['pass_angle'] = pass_dict.get('angle')
            end_loc = pass_dict.get('end_location', [None, None])
            event['pass_end_x'] = end_loc[0] if end_loc else None
            event['pass_end_y'] = end_loc[1] if len(end_loc) > 1 else None
        else:
            event['pass_recipient'] = event['pass_length'] = event['pass_height'] = None
            event['pass_outcome'] = event['pass_angle'] = None
            event['pass_end_x'] = event['pass_end_y'] = None
        
        # Shot data
        shot_dict = parse_json_field(row.get('shot'))
        if shot_dict:
            outcome_dict = shot_dict.get('outcome', {})
            event['shot_outcome'] = outcome_dict.get('name') if isinstance(outcome_dict, dict) else None
            event['shot_xg'] = shot_dict.get('statsbomb_xg')
            body_part_dict = shot_dict.get('body_part', {})
            event['shot_body_part'] = body_part_dict.get('name') if isinstance(body_part_dict, dict) else None
            technique_dict = shot_dict.get('technique', {})
            event['shot_technique'] = technique_dict.get('name') if isinstance(technique_dict, dict) else None
            event['is_goal'] = event['shot_outcome'] == 'Goal'
        else:
            event['shot_outcome'] = event['shot_xg'] = event['shot_body_part'] = None
            event['shot_technique'] = None
            event['is_goal'] = False
        
        # Carry data
        carry_dict = parse_json_field(row.get('carry'))
        if carry_dict:
            end_loc = carry_dict.get('end_location', [None, None])
            event['carry_end_x'] = end_loc[0] if end_loc else None
            event['carry_end_y'] = end_loc[1] if len(end_loc) > 1 else None
            if event['location_x'] and event['carry_end_x']:
                event['carry_distance'] = np.sqrt(
                    (event['carry_end_x'] - event['location_x'])**2 + 
                    (event['carry_end_y'] - event['location_y'])**2
                )
            else:
                event['carry_distance'] = None
        else:
            event['carry_end_x'] = event['carry_end_y'] = event['carry_distance'] = None
        
        # Dribble data
        dribble_dict = parse_json_field(row.get('dribble'))
        if dribble_dict:
            outcome_dict = dribble_dict.get('outcome', {})
            event['dribble_outcome'] = outcome_dict.get('name') if isinstance(outcome_dict, dict) else None
            event['dribble_nutmeg'] = dribble_dict.get('nutmeg', False)
        else:
            event['dribble_outcome'] = None
            event['dribble_nutmeg'] = False
        
        # Other event data
        event['substitution'] = row.get('substitution')
        event['position'] = row.get('position')
        event['foul_committed'] = row.get('foul_committed')
        
        # Current score (BEFORE this event)
        event[f'{team1_name}_score'] = team1_score
        event[f'{team2_name}_score'] = team2_score
        event['score_diff'] = (team1_score - team2_score) if event['team_name'] == team1_name else (team2_score - team1_score)
        
        # Tournament stats
        if event['team_name'] in team_stats:
            event['team_tournament_wins'] = team_stats[event['team_name']]['wins']
            event['team_tournament_draws'] = team_stats[event['team_name']]['draws']
            event['team_tournament_losses'] = team_stats[event['team_name']]['losses']
            event['team_tournament_goals'] = team_stats[event['team_name']]['goals_scored']
            event['team_tournament_conceded'] = team_stats[event['team_name']]['goals_conceded']
        else:
            event['team_tournament_wins'] = event['team_tournament_draws'] = event['team_tournament_losses'] = None
            event['team_tournament_goals'] = event['team_tournament_conceded'] = None
        
        # Player tournament goals
        if event['player_name'] in player_goals.get(event['team_name'], {}):
            event['player_tournament_goals'] = player_goals[event['team_name']][event['player_name']]
        else:
            event['player_tournament_goals'] = 0
        
        # Player match goals (BEFORE this event)
        if event['team_name'] == team1_name:
            event['player_match_goals'] = sum(1 for g in team1_goals_in_match if g['player'] == event['player_name'])
        elif event['team_name'] == team2_name:
            event['player_match_goals'] = sum(1 for g in team2_goals_in_match if g['player'] == event['player_name'])
        else:
            event['player_match_goals'] = 0
        
        # Update scores AFTER recording (for next events)
        if event['is_goal']:
            if event['team_name'] == team1_name:
                team1_score += 1
                team1_goals_in_match.append({'player': event['player_name'], 'minute': event['minute'], 'second': event['second']})
            elif event['team_name'] == team2_name:
                team2_score += 1
                team2_goals_in_match.append({'player': event['player_name'], 'minute': event['minute'], 'second': event['second']})
        
        # Event context (previous/next events)
        if event_idx > 0:
            prev_idx, prev_row = events_list[event_idx - 1]
            prev_type_dict = parse_json_field(prev_row.get('type'))
            prev_player_dict = parse_json_field(prev_row.get('player'))
            prev_team_dict = parse_json_field(prev_row.get('team'))
            event['previous_event_type'] = prev_type_dict.get('name') if prev_type_dict else None
            event['previous_player'] = prev_player_dict.get('name') if prev_player_dict else None
            event['previous_team'] = prev_team_dict.get('name') if prev_team_dict else None
            event['previous_minute'] = prev_row.get('minute')
            event['previous_second'] = prev_row.get('second')
        else:
            event['previous_event_type'] = event['previous_player'] = event['previous_team'] = None
            event['previous_minute'] = event['previous_second'] = None
        
        if event_idx < len(events_list) - 1:
            next_idx, next_row = events_list[event_idx + 1]
            next_type_dict = parse_json_field(next_row.get('type'))
            next_player_dict = parse_json_field(next_row.get('player'))
            next_team_dict = parse_json_field(next_row.get('team'))
            event['next_event_type'] = next_type_dict.get('name') if next_type_dict else None
            event['next_player'] = next_player_dict.get('name') if next_player_dict else None
            event['next_team'] = next_team_dict.get('name') if next_team_dict else None
        else:
            event['next_event_type'] = event['next_player'] = event['next_team'] = None
        
        # Derived fields
        event['possession_retained'] = (event['team_name'] == event['next_team']) if event['next_team'] else None
        event['distance_to_goal'] = abs(120 - event['location_x']) if event['location_x'] else None
        event['is_key_pass'] = (event['event_type'] == 'Pass' and event['next_event_type'] == 'Shot' and event['team_name'] == event['next_team'])
        event['is_danger_zone'] = (event['location_x'] and 95 <= event['location_x'] <= 120)
        
        # High pressure detection
        event['is_high_pressure'] = False
        if event_idx > 0:
            prev_idx, prev_row = events_list[event_idx - 1]
            prev_type_dict = parse_json_field(prev_row.get('type'))
            if prev_type_dict and prev_type_dict.get('name') == 'Pressure':
                time_diff = abs(event['second'] - prev_row.get('second', 0))
                event['is_high_pressure'] = time_diff < 1.5
        
        enriched_events.append(event)
    
    return pd.DataFrame(enriched_events)

def main():
    """Main execution"""
    
    if len(sys.argv) < 2:
        print("Usage: python extract_semi_final_data.py <match_id>")
        print("  3942819 = Netherlands vs England")
        print("  3942752 = Spain vs France")
        sys.exit(1)
    
    match_id = sys.argv[1]
    
    # Load data
    events_df, matches_df = load_data()
    
    # Get match info
    match = get_match_info(matches_df, match_id)
    if match is None:
        return
    
    match_date = match['match_date']
    team1_name = match['home_team_name']
    team2_name = match['away_team_name']
    
    # Calculate tournament stats for both teams (BEFORE this match)
    print(f"\nCalculating tournament stats (before {team1_name} vs {team2_name})...")
    team1_stats, team1_player_goals = calculate_tournament_stats_before_match(
        matches_df, events_df, team1_name, match_date
    )
    team2_stats, team2_player_goals = calculate_tournament_stats_before_match(
        matches_df, events_df, team2_name, match_date
    )
    
    print(f"\n{team1_name} Tournament Stats:")
    print(f"  Record: {team1_stats['wins']}-{team1_stats['draws']}-{team1_stats['losses']}")
    print(f"  Goals: {team1_stats['goals_scored']} scored, {team1_stats['goals_conceded']} conceded")
    print(f"  Top Scorers: {len(team1_player_goals)} players")
    
    print(f"\n{team2_name} Tournament Stats:")
    print(f"  Record: {team2_stats['wins']}-{team2_stats['draws']}-{team2_stats['losses']}")
    print(f"  Goals: {team2_stats['goals_scored']} scored, {team2_stats['goals_conceded']} conceded")
    print(f"  Top Scorers: {len(team2_player_goals)} players")
    
    # Extract ALL events from the match
    match_events = extract_match_events(events_df, match_id)
    
    # Enrich events
    print("\nEnriching events with stats and metadata...")
    team_stats = {team1_name: team1_stats, team2_name: team2_stats}
    player_goals = {team1_name: team1_player_goals, team2_name: team2_player_goals}
    
    enriched_df = enrich_event_data(match_events, team_stats, player_goals, match, team1_name, team2_name)
    
    # Save to CSV
    output_file = os.path.join(SCRIPT_DIR, f'match_{match_id}_detailed_commentary_data.csv')
    enriched_df.to_csv(output_file, index=False)
    
    print(f"\n✅ Enriched data saved to: {output_file}")
    print(f"   Total events: {len(enriched_df)}")
    print(f"   Columns: {len(enriched_df.columns)}")
    print(f"\nEvent type distribution:")
    print(enriched_df['event_type'].value_counts().head(10))

if __name__ == "__main__":
    main()

