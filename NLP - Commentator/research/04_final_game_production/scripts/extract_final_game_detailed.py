"""
Extract Final Game Commentary Data - Spain vs England (75+ minutes)
====================================================================
This script extracts detailed event data from the Euro 2024 final,
enriched with tournament and in-match statistics for realistic commentary.
"""

import pandas as pd
import numpy as np
import os
import json
from datetime import datetime

# Setup paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
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

def get_final_match_info(matches_df):
    """Get Spain vs England final match details"""
    # The final is Spain vs England
    final = matches_df[
        (matches_df['home_team_name'] == 'Spain') & 
        (matches_df['away_team_name'] == 'England')
    ]
    
    if len(final) == 0:
        # Try reverse
        final = matches_df[
            (matches_df['home_team_name'] == 'England') & 
            (matches_df['away_team_name'] == 'Spain')
        ]
    
    if len(final) == 0:
        print("ERROR: Final match not found!")
        return None
    
    final = final.iloc[0]
    print(f"\nFinal Match Found:")
    print(f"  Match ID: {final['match_id']}")
    print(f"  {final['home_team_name']} vs {final['away_team_name']}")
    print(f"  Score: {final['home_score']}-{final['away_score']}")
    print(f"  Date: {final['match_date']}")
    
    return final

def calculate_tournament_stats_before_final(matches_df, events_df, team_name, final_date):
    """Calculate team and player stats BEFORE the final"""
    
    # Get all matches before final date
    matches_df['match_date'] = pd.to_datetime(matches_df['match_date'])
    previous_matches = matches_df[matches_df['match_date'] < pd.to_datetime(final_date)]
    
    # Filter matches where team played
    team_matches = previous_matches[
        (previous_matches['home_team_name'] == team_name) | 
        (previous_matches['away_team_name'] == team_name)
    ].copy()
    
    # Team stats
    wins = 0
    draws = 0
    losses = 0
    goals_scored = 0
    goals_conceded = 0
    
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
    
    # Player stats - goals scored in tournament before final
    team_match_ids = team_matches['match_id'].tolist()
    team_events = events_df[events_df['match_id'].isin(team_match_ids)]
    
    # Parse team column to get team name
    def get_team_name(row):
        try:
            if pd.notna(row['team']):
                team_dict = eval(row['team'])
                return team_dict.get('name', None)
        except:
            pass
        return None
    
    team_events['team_name'] = team_events.apply(get_team_name, axis=1)
    team_events = team_events[team_events['team_name'] == team_name]
    
    # Get goals
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

def extract_final_events(events_df, match_id, start_minute=0):
    """Extract ALL events from the match (all periods)"""
    
    # Filter by match
    match_events = events_df[events_df['match_id'] == match_id].copy()
    
    # Sort by timestamp
    match_events = match_events.sort_values(['period', 'minute', 'second'])
    
    print(f"\nExtracted {len(match_events)} events (FULL MATCH)")
    print(f"Periods covered: {sorted(match_events['period'].unique())}")
    print(f"Minute range: {match_events['minute'].min()}-{match_events['minute'].max()}")
    
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

def enrich_event_data(events_df, team_stats, player_goals, match_info):
    """Enrich each event with detailed metadata and stats"""
    
    enriched_events = []
    
    # Track in-match stats
    spain_goals_in_match = []
    england_goals_in_match = []
    spain_score = 0
    england_score = 0
    
    
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
        
        # Parse type
        type_dict = parse_json_field(row['type'])
        event['event_type'] = type_dict.get('name') if type_dict else None
        
        # Parse player
        player_dict = parse_json_field(row['player'])
        event['player_name'] = player_dict.get('name') if player_dict else None
        
        # Parse team
        team_dict = parse_json_field(row['team'])
        event['team_name'] = team_dict.get('name') if team_dict else None
        
        # Parse possession team
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
        
        # Under pressure
        event['under_pressure'] = row.get('under_pressure', False)
        
        # Duration
        event['duration'] = row.get('duration', None)
        
        # Play pattern
        play_pattern_dict = parse_json_field(row['play_pattern'])
        event['play_pattern'] = play_pattern_dict.get('name') if play_pattern_dict else None
        
        # Event-specific data
        # Pass
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
            event['pass_end_x'] = pass_dict.get('end_location', [None, None])[0] if pass_dict.get('end_location') else None
            event['pass_end_y'] = pass_dict.get('end_location', [None, None])[1] if pass_dict.get('end_location') else None
        else:
            event['pass_recipient'] = None
            event['pass_length'] = None
            event['pass_height'] = None
            event['pass_outcome'] = None
            event['pass_angle'] = None
            event['pass_end_x'] = None
            event['pass_end_y'] = None
        
        # Shot
        shot_dict = parse_json_field(row.get('shot'))
        if shot_dict:
            outcome_dict = shot_dict.get('outcome', {})
            event['shot_outcome'] = outcome_dict.get('name') if isinstance(outcome_dict, dict) else None
            event['shot_xg'] = shot_dict.get('statsbomb_xg')
            
            body_part_dict = shot_dict.get('body_part', {})
            event['shot_body_part'] = body_part_dict.get('name') if isinstance(body_part_dict, dict) else None
            
            technique_dict = shot_dict.get('technique', {})
            event['shot_technique'] = technique_dict.get('name') if isinstance(technique_dict, dict) else None
            
            # Check if goal
            is_goal = event['shot_outcome'] == 'Goal'
            event['is_goal'] = is_goal
        else:
            event['shot_outcome'] = None
            event['shot_xg'] = None
            event['shot_body_part'] = None
            event['shot_technique'] = None
            event['is_goal'] = False
        
        # Carry
        carry_dict = parse_json_field(row.get('carry'))
        if carry_dict:
            end_loc = carry_dict.get('end_location', [None, None])
            event['carry_end_x'] = end_loc[0] if end_loc else None
            event['carry_end_y'] = end_loc[1] if end_loc else None
        else:
            event['carry_end_x'] = None
            event['carry_end_y'] = None
        
        # Calculate carry distance
        if event['location_x'] and event['carry_end_x']:
            event['carry_distance'] = np.sqrt(
                (event['carry_end_x'] - event['location_x'])**2 + 
                (event['carry_end_y'] - event['location_y'])**2
            )
        else:
            event['carry_distance'] = None
        
        # Dribble
        dribble_dict = parse_json_field(row.get('dribble'))
        if dribble_dict:
            outcome_dict = dribble_dict.get('outcome', {})
            event['dribble_outcome'] = outcome_dict.get('name') if isinstance(outcome_dict, dict) else None
            event['dribble_nutmeg'] = dribble_dict.get('nutmeg', False)
        else:
            event['dribble_outcome'] = None
            event['dribble_nutmeg'] = False
        
        # Substitution (for template)
        event['substitution'] = row.get('substitution')
        event['position'] = row.get('position')
        
        # Foul Committed (for card tracking)
        event['foul_committed'] = row.get('foul_committed')
        
        # Current score at this event (BEFORE this event's outcome)
        event['spain_score'] = spain_score
        event['england_score'] = england_score
        event['score_diff'] = spain_score - england_score if event['team_name'] == 'Spain' else england_score - spain_score
        
        # Tournament stats for player's team
        if event['team_name'] in team_stats:
            event['team_tournament_wins'] = team_stats[event['team_name']]['wins']
            event['team_tournament_draws'] = team_stats[event['team_name']]['draws']
            event['team_tournament_losses'] = team_stats[event['team_name']]['losses']
            event['team_tournament_goals'] = team_stats[event['team_name']]['goals_scored']
            event['team_tournament_conceded'] = team_stats[event['team_name']]['goals_conceded']
        else:
            event['team_tournament_wins'] = None
            event['team_tournament_draws'] = None
            event['team_tournament_losses'] = None
            event['team_tournament_goals'] = None
            event['team_tournament_conceded'] = None
        
        # Player tournament goals (before this match)
        if event['player_name'] in player_goals.get(event['team_name'], {}):
            event['player_tournament_goals'] = player_goals[event['team_name']][event['player_name']]
        else:
            event['player_tournament_goals'] = 0
        
        # Player goals in this match (before this event)
        if event['team_name'] == 'Spain':
            event['player_match_goals'] = sum(1 for g in spain_goals_in_match if g['player'] == event['player_name'])
        elif event['team_name'] == 'England':
            event['player_match_goals'] = sum(1 for g in england_goals_in_match if g['player'] == event['player_name'])
        else:
            event['player_match_goals'] = 0
        
        # Update scores AFTER recording player_match_goals (for next events)
        if event['is_goal']:
            if event['team_name'] == 'Spain':
                spain_score += 1
                spain_goals_in_match.append({
                    'player': event['player_name'],
                    'minute': event['minute'],
                    'second': event['second']
                })
            elif event['team_name'] == 'England':
                england_score += 1
                england_goals_in_match.append({
                    'player': event['player_name'],
                    'minute': event['minute'],
                    'second': event['second']
                })
        
        # === EVENT CONTEXT: Previous & Next Events ===
        
        # Get previous event (who passed to this player, etc.)
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
            event['previous_event_type'] = None
            event['previous_player'] = None
            event['previous_team'] = None
            event['previous_minute'] = None
            event['previous_second'] = None
        
        # Get next event (what happens after - corner, throw-in, etc.)
        if event_idx < len(events_list) - 1:
            next_idx, next_row = events_list[event_idx + 1]
            next_type_dict = parse_json_field(next_row.get('type'))
            next_player_dict = parse_json_field(next_row.get('player'))
            next_team_dict = parse_json_field(next_row.get('team'))
            
            event['next_event_type'] = next_type_dict.get('name') if next_type_dict else None
            event['next_player'] = next_player_dict.get('name') if next_player_dict else None
            event['next_team'] = next_team_dict.get('name') if next_team_dict else None
        else:
            event['next_event_type'] = None
            event['next_player'] = None
            event['next_team'] = None
        
        # Possession outcome (does team keep ball?)
        if event['next_team']:
            event['possession_retained'] = (event['team_name'] == event['next_team'])
        else:
            event['possession_retained'] = None
        
        # Distance to goal (for shots)
        if event['location_x']:
            # Goal is at x=120 for attacking team
            event['distance_to_goal'] = abs(120 - event['location_x'])
        else:
            event['distance_to_goal'] = None
        
        # Key pass detection (pass followed by shot from same team)
        event['is_key_pass'] = (
            event['event_type'] == 'Pass' and 
            event['next_event_type'] == 'Shot' and 
            event['team_name'] == event['next_team']
        )
        
        # Danger zone detection (attacking third within 25m of goal)
        event['is_danger_zone'] = (
            event['location_x'] and event['location_x'] >= 95 and event['location_x'] <= 120
        )
        
        # High pressure situation (Pressure event within recent time)
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
    
    # Load data
    events_df, matches_df = load_data()
    
    # Get final match info
    final_match = get_final_match_info(matches_df)
    if final_match is None:
        return
    
    match_id = final_match['match_id']
    final_date = final_match['match_date']
    
    # Calculate tournament stats for both teams (BEFORE final)
    print("\nCalculating tournament stats (before final)...")
    spain_stats, spain_player_goals = calculate_tournament_stats_before_final(
        matches_df, events_df, 'Spain', final_date
    )
    england_stats, england_player_goals = calculate_tournament_stats_before_final(
        matches_df, events_df, 'England', final_date
    )
    
    print(f"\nSpain Tournament Stats (before final):")
    print(f"  Record: {spain_stats['wins']}-{spain_stats['draws']}-{spain_stats['losses']}")
    print(f"  Goals: {spain_stats['goals_scored']} scored, {spain_stats['goals_conceded']} conceded")
    print(f"  Top Scorers: {len(spain_player_goals)} players")
    
    print(f"\nEngland Tournament Stats (before final):")
    print(f"  Record: {england_stats['wins']}-{england_stats['draws']}-{england_stats['losses']}")
    print(f"  Goals: {england_stats['goals_scored']} scored, {england_stats['goals_conceded']} conceded")
    print(f"  Top Scorers: {len(england_player_goals)} players")
    
    # Extract ALL events from the final
    final_events = extract_final_events(events_df, match_id, start_minute=0)
    
    # Enrich events
    print("\nEnriching events with stats and metadata...")
    team_stats = {
        'Spain': spain_stats,
        'England': england_stats
    }
    player_goals = {
        'Spain': spain_player_goals,
        'England': england_player_goals
    }
    
    enriched_df = enrich_event_data(final_events, team_stats, player_goals, final_match)
    
    # Save to CSV
    output_file = os.path.join(SCRIPT_DIR, 'final_game_detailed_commentary_data.csv')
    enriched_df.to_csv(output_file, index=False)
    
    print(f"\n✅ Enriched data saved to: {output_file}")
    print(f"   Total events: {len(enriched_df)}")
    print(f"   Columns: {len(enriched_df.columns)}")
    print(f"\nEvent type distribution:")
    print(enriched_df['event_type'].value_counts().head(10))

if __name__ == "__main__":
    main()

