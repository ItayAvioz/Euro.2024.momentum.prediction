"""
Extract Starting Events (First 4) with Team Statistics
=======================================================
Extract first 4 events from 10 games with:
- Team statistics (wins, draws, goals scored/conceded)
- Last match result
- Match context (stadium, referee, stage)
- Lineup information
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
    """Load datasets"""
    print("Loading Euro 2024 datasets...")
    
    # Load events
    events_path = os.path.join(DATA_DIR, 'euro_2024_complete_dataset.csv')
    events_df = pd.read_csv(events_path, low_memory=False)
    
    # Load matches
    matches_path = os.path.join(DATA_DIR, 'matches_complete.csv')
    matches_df = pd.read_csv(matches_path)
    
    # Load lineups
    lineups_path = os.path.join(DATA_DIR, 'lineups_complete.csv')
    lineups_df = pd.read_csv(lineups_path)
    
    print(f"Loaded {len(events_df):,} events from {matches_df['match_id'].nunique()} matches")
    
    return events_df, matches_df, lineups_df

def select_10_games(matches_df):
    """Select 10 diverse and exciting games across all stages"""
    
    # Select games from different stages and with different characteristics
    selected_matches = [
        3930158,  # Group Stage MD1: Germany 5-1 Scotland (opening match, high scoring)
        3930171,  # Group Stage MD2: Denmark 1-1 England (competitive draw)
        3942226,  # Quarter-final: Spain 2-1 Germany (extra time thriller)
        3943043,  # Final: Spain 2-1 England (dramatic final)
        3941017,  # R16: England 2-1 Slovakia (comeback)
        3942382,  # Quarter-final: Netherlands 2-1 Turkey (exciting)
        3930180,  # Group Stage MD3: Netherlands 2-3 Austria (upset)
        3941021,  # R16: Romania 0-3 Netherlands (dominant)
        3942752,  # Semi-final: Spain 2-1 France (high quality)
        3942819,  # Semi-final: Netherlands 1-2 England (late drama)
    ]
    
    match_info = matches_df[matches_df['match_id'].isin(selected_matches)].copy()
    
    # Parse match_date
    match_info['match_date'] = pd.to_datetime(match_info['match_date'])
    match_info = match_info.sort_values('match_date')
    
    print("\nSelected 10 Games:")
    for _, match in match_info.iterrows():
        print(f"  {match['match_id']}: {match['home_team_name']} {match['home_score']}-{match['away_score']} {match['away_team_name']} ({match['stage']})")
    
    return match_info

def calculate_team_stats_before_match(matches_df, team_name, current_match_date):
    """Calculate team statistics before the current match"""
    
    # Get all matches before current date for this team
    matches_df['match_date'] = pd.to_datetime(matches_df['match_date'])
    previous_matches = matches_df[matches_df['match_date'] < current_match_date]
    
    # Filter matches where team played
    team_matches = previous_matches[
        (previous_matches['home_team_name'] == team_name) | 
        (previous_matches['away_team_name'] == team_name)
    ].copy()
    
    if len(team_matches) == 0:
        return {
            'matches_played': 0,
            'wins': 0,
            'draws': 0,
            'losses': 0,
            'goals_scored': 0,
            'goals_conceded': 0,
            'goal_difference': 0,
            'last_result': 'No previous match',
            'last_score': 'N/A'
        }
    
    # Calculate stats
    wins = 0
    draws = 0
    losses = 0
    goals_scored = 0
    goals_conceded = 0
    
    for _, match in team_matches.iterrows():
        if match['home_team_name'] == team_name:
            # Team is home
            goals_scored += match['home_score']
            goals_conceded += match['away_score']
            if match['home_score'] > match['away_score']:
                wins += 1
            elif match['home_score'] == match['away_score']:
                draws += 1
            else:
                losses += 1
        else:
            # Team is away
            goals_scored += match['away_score']
            goals_conceded += match['home_score']
            if match['away_score'] > match['home_score']:
                wins += 1
            elif match['away_score'] == match['home_score']:
                draws += 1
            else:
                losses += 1
    
    # Get last match result
    last_match = team_matches.iloc[-1]
    if last_match['home_team_name'] == team_name:
        last_score = f"{last_match['home_score']}-{last_match['away_score']}"
        if last_match['home_score'] > last_match['away_score']:
            last_result = 'Win'
        elif last_match['home_score'] == last_match['away_score']:
            last_result = 'Draw'
        else:
            last_result = 'Loss'
        last_opponent = last_match['away_team_name']
    else:
        last_score = f"{last_match['away_score']}-{last_match['home_score']}"
        if last_match['away_score'] > last_match['home_score']:
            last_result = 'Win'
        elif last_match['away_score'] == last_match['home_score']:
            last_result = 'Draw'
        else:
            last_result = 'Loss'
        last_opponent = last_match['home_team_name']
    
    return {
        'matches_played': len(team_matches),
        'wins': wins,
        'draws': draws,
        'losses': losses,
        'goals_scored': goals_scored,
        'goals_conceded': goals_conceded,
        'goal_difference': goals_scored - goals_conceded,
        'last_result': last_result,
        'last_score': last_score,
        'last_opponent': last_opponent
    }

def get_lineup_string(lineups_df, match_id, team_name):
    """Get lineup as formatted string"""
    lineup = lineups_df[
        (lineups_df['match_id'] == match_id) & 
        (lineups_df['team_name'] == team_name)
    ]
    
    if len(lineup) == 0:
        return "Lineup not available"
    
    # Get players
    players = lineup.sort_values('jersey_number')
    player_names = []
    for _, player in players.iterrows():
        name = player['player_name']
        number = player['jersey_number']
        player_names.append(f"{number}.{name}")
    
    return " | ".join(player_names[:11])  # Starting 11

def extract_first_4_events(events_df, match_id):
    """Extract first 4 events from match (kickoff sequence)"""
    
    match_events = events_df[events_df['match_id'] == match_id].copy()
    match_events = match_events.sort_values(['period', 'minute', 'second', 'index']).reset_index(drop=True)
    
    # Get first 4 events
    first_4 = match_events.head(4)
    
    return first_4

def parse_json_field(value):
    """Safely parse JSON-like string field"""
    if pd.isna(value):
        return None
    if isinstance(value, str):
        try:
            return eval(value)
        except:
            return value
    return value

def create_starting_events_dataset(events_df, matches_df, lineups_df, selected_matches):
    """Create dataset with first 4 events and team statistics"""
    
    all_rows = []
    
    for _, match in selected_matches.iterrows():
        match_id = match['match_id']
        match_date = match['match_date']
        home_team = match['home_team_name']
        away_team = match['away_team_name']
        
        print(f"\nProcessing Match {match_id}: {home_team} vs {away_team}")
        
        # Get team statistics before this match
        home_stats = calculate_team_stats_before_match(matches_df, home_team, match_date)
        away_stats = calculate_team_stats_before_match(matches_df, away_team, match_date)
        
        print(f"  {home_team}: {home_stats['wins']}W {home_stats['draws']}D {home_stats['losses']}L | Last: {home_stats['last_result']}")
        print(f"  {away_team}: {away_stats['wins']}W {away_stats['draws']}D {away_stats['losses']}L | Last: {away_stats['last_result']}")
        
        # Get lineups
        home_lineup = get_lineup_string(lineups_df, match_id, home_team)
        away_lineup = get_lineup_string(lineups_df, match_id, away_team)
        
        # Parse stadium, referee, stage from match data
        stadium = parse_json_field(match.get('stadium', {}))
        stadium_name = stadium.get('name', 'Unknown') if isinstance(stadium, dict) else 'Unknown'
        
        referee = parse_json_field(match.get('referee', {}))
        referee_name = referee.get('name', 'Unknown') if isinstance(referee, dict) else 'Unknown'
        
        stage = match.get('stage', 'Unknown')
        kick_off = match.get('kick_off', 'Unknown')
        
        # Extract first 4 events
        first_4_events = extract_first_4_events(events_df, match_id)
        
        print(f"  Extracted {len(first_4_events)} starting events")
        
        # Create rows with all information
        for idx, (_, event) in enumerate(first_4_events.iterrows(), 1):
            
            # Parse event type
            event_type_dict = parse_json_field(event.get('type', {}))
            event_type = event_type_dict.get('name', 'Unknown') if isinstance(event_type_dict, dict) else str(event_type_dict)
            
            # Parse player
            player_dict = parse_json_field(event.get('player', {}))
            player_name = player_dict.get('name', 'Unknown') if isinstance(player_dict, dict) else str(player_dict)
            
            # Parse team
            team_dict = parse_json_field(event.get('team', {}))
            team_name = team_dict.get('name', 'Unknown') if isinstance(team_dict, dict) else str(team_dict)
            
            # Parse position
            position_dict = parse_json_field(event.get('position', {}))
            position_name = position_dict.get('name', 'Unknown') if isinstance(position_dict, dict) else 'Unknown'
            
            # Determine if this is team_a or team_b event
            is_team_a_event = (team_name == home_team)
            
            row = {
                # Match Information
                'match_id': match_id,
                'match_date': match_date.strftime('%Y-%m-%d'),
                'stage': stage,
                'kick_off_time': kick_off,
                'stadium': stadium_name,
                'referee': referee_name,
                
                # Teams
                'team_a': home_team,
                'team_b': away_team,
                'team_a_score': match['home_score'],
                'team_b_score': match['away_score'],
                
                # Team A Statistics (before match)
                'team_a_matches_played': home_stats['matches_played'],
                'team_a_wins': home_stats['wins'],
                'team_a_draws': home_stats['draws'],
                'team_a_losses': home_stats['losses'],
                'team_a_goals_scored': home_stats['goals_scored'],
                'team_a_goals_conceded': home_stats['goals_conceded'],
                'team_a_goal_difference': home_stats['goal_difference'],
                'team_a_last_result': home_stats['last_result'],
                'team_a_last_score': home_stats['last_score'],
                'team_a_last_opponent': home_stats.get('last_opponent', 'N/A'),
                
                # Team B Statistics (before match)
                'team_b_matches_played': away_stats['matches_played'],
                'team_b_wins': away_stats['wins'],
                'team_b_draws': away_stats['draws'],
                'team_b_losses': away_stats['losses'],
                'team_b_goals_scored': away_stats['goals_scored'],
                'team_b_goals_conceded': away_stats['goals_conceded'],
                'team_b_goal_difference': away_stats['goal_difference'],
                'team_b_last_result': away_stats['last_result'],
                'team_b_last_score': away_stats['last_score'],
                'team_b_last_opponent': away_stats.get('last_opponent', 'N/A'),
                
                # Lineups
                'team_a_lineup': home_lineup,
                'team_b_lineup': away_lineup,
                
                # Event Information
                'event_number': idx,
                'event_id': event.get('id', ''),
                'minute': event.get('minute', 0),
                'second': event.get('second', 0),
                'period': event.get('period', 1),
                'timestamp': event.get('timestamp', ''),
                'event_type': event_type,
                'event_team': team_name,
                'is_team_a_event': is_team_a_event,
                'player_name': player_name,
                'player_position': position_name,
                'location': event.get('location', ''),
                'under_pressure': event.get('under_pressure', False),
                'duration': event.get('duration', ''),
                
                # Event details (keep as JSON for reference)
                'pass_details': event.get('pass', ''),
                'carry_details': event.get('carry', ''),
                'shot_details': event.get('shot', ''),
            }
            
            all_rows.append(row)
    
    return pd.DataFrame(all_rows)

def main():
    """Main execution"""
    print("=" * 70)
    print("STARTING EVENTS EXTRACTION WITH TEAM STATISTICS")
    print("=" * 70)
    
    # Load data
    events_df, matches_df, lineups_df = load_data()
    
    # Select 10 games
    selected_matches = select_10_games(matches_df)
    
    # Create dataset
    print("\nExtracting first 4 events from each match with team statistics...")
    starting_events_df = create_starting_events_dataset(
        events_df, matches_df, lineups_df, selected_matches
    )
    
    # Save to CSV
    output_file = os.path.join(SCRIPT_DIR, 'starting_events_with_team_stats.csv')
    starting_events_df.to_csv(output_file, index=False)
    
    print(f"\n✅ Dataset created successfully!")
    print(f"   File: {output_file}")
    print(f"   Total events: {len(starting_events_df)} (4 events × 10 matches)")
    print(f"   Total columns: {len(starting_events_df.columns)}")
    
    # Display statistics
    print("\n📊 Dataset Overview:")
    print(f"   Matches: {starting_events_df['match_id'].nunique()}")
    print(f"   Events per match: {len(starting_events_df) / starting_events_df['match_id'].nunique():.0f}")
    print(f"   Stages: {starting_events_df['stage'].unique()}")
    
    print("\n📊 Event Types in Starting Sequences:")
    event_counts = starting_events_df['event_type'].value_counts()
    for event_type, count in event_counts.items():
        print(f"   {event_type}: {count}")
    
    print("\n📋 Sample Data (First 5 rows):")
    display_cols = [
        'match_id', 'team_a', 'team_b', 'event_number', 
        'event_type', 'player_name', 'team_a_wins', 'team_b_wins'
    ]
    available_cols = [col for col in display_cols if col in starting_events_df.columns]
    print(starting_events_df[available_cols].head(5).to_string())
    
    print("\n📋 Column List:")
    print("=" * 70)
    for i, col in enumerate(starting_events_df.columns, 1):
        print(f"{i:2d}. {col}")
    
    print("\n" + "=" * 70)
    print("KEY FEATURES OF THIS DATASET")
    print("=" * 70)
    print("""
    ✅ MATCH CONTEXT:
       - Stadium, Referee, Stage, Kick-off time
       - Final score (team_a_score, team_b_score)
       
    ✅ TEAM STATISTICS (Before this match):
       TEAM A:
       - Matches played, Wins, Draws, Losses
       - Goals scored, Goals conceded, Goal difference
       - Last result, Last score, Last opponent
       
       TEAM B:
       - Matches played, Wins, Draws, Losses
       - Goals scored, Goals conceded, Goal difference
       - Last result, Last score, Last opponent
    
    ✅ LINEUPS:
       - Complete starting 11 for both teams
    
    ✅ STARTING EVENTS (First 4):
       - Event number (1-4)
       - Event type (Pass, Carry, Ball Receipt, etc.)
       - Player name and position
       - Location coordinates
       - Event details (pass/carry/shot details)
       - Timestamp and period information
    
    ✅ USE CASES:
       - Pre-match commentary with team form
       - "Team X comes in with 2 wins and 1 draw..."
       - "Last time out, they beat Team Y 2-1..."
       - Opening sequence analysis with context
       - Statistical context for match predictions
    """)
    
    # Create summary document
    summary_file = os.path.join(SCRIPT_DIR, 'starting_events_summary.md')
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("# Starting Events with Team Statistics - Summary\n\n")
        f.write(f"## Dataset Overview\n\n")
        f.write(f"- **Total Events**: {len(starting_events_df)}\n")
        f.write(f"- **Matches**: {starting_events_df['match_id'].nunique()}\n")
        f.write(f"- **Events per Match**: 4 (kick-off sequence)\n")
        f.write(f"- **Total Columns**: {len(starting_events_df.columns)}\n\n")
        
        f.write("## Selected Matches\n\n")
        for _, match in selected_matches.iterrows():
            f.write(f"- **{match['match_id']}** ({match['match_date'].strftime('%Y-%m-%d')}): ")
            f.write(f"{match['home_team_name']} {match['home_score']}-{match['away_score']} ")
            f.write(f"{match['away_team_name']} ({match['stage']})\n")
        
        f.write("\n## Column Categories\n\n")
        f.write("### Match Context (6 columns)\n")
        f.write("- match_id, match_date, stage, kick_off_time, stadium, referee\n\n")
        
        f.write("### Team Information (4 columns)\n")
        f.write("- team_a, team_b, team_a_score, team_b_score\n\n")
        
        f.write("### Team A Statistics (10 columns)\n")
        f.write("- matches_played, wins, draws, losses\n")
        f.write("- goals_scored, goals_conceded, goal_difference\n")
        f.write("- last_result, last_score, last_opponent\n\n")
        
        f.write("### Team B Statistics (10 columns)\n")
        f.write("- Same structure as Team A stats\n\n")
        
        f.write("### Lineups (2 columns)\n")
        f.write("- team_a_lineup, team_b_lineup\n\n")
        
        f.write("### Event Details (14 columns)\n")
        f.write("- event_number (1-4), event_id, timestamp, minute, second, period\n")
        f.write("- event_type, event_team, is_team_a_event\n")
        f.write("- player_name, player_position, location\n")
        f.write("- pass_details, carry_details, shot_details\n\n")
    
    print(f"\n📄 Summary document: {summary_file}")
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
