"""
Batch Commentary Generation - V6
Generates ESPN-style LLM commentary with:
- All V5 features (momentum agent, penalties, shootouts)
- NEW: Event sequence detection (Corner→Shot, Dribble→Shot, Free Kick→Goal)
- NEW: More variety in commentary
- NEW: Lower agent threshold (0.70)
- NEW: Clearer momentum vs momentum change

Author: Euro 2024 Momentum Project
Date: December 2024
"""

import os
import sys
import ast
import time
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Try to load API key
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Import V6 commentator
from gpt_commentator_v6 import GPTCommentatorV6

# =====================================
# PATHS
# =====================================
SCRIPT_DIR = Path(__file__).parent
BASE_DIR = SCRIPT_DIR.parent
PHASE7_DATA = BASE_DIR.parent / "07_all_games_commentary" / "data"
COMPLETE_DATA = Path("C:/Users/yonatanam/Desktop/Euro 2024 - momentum - DS-AI project/Data/euro_2024_complete_dataset.csv")
MATCHES_DATA = Path("C:/Users/yonatanam/Desktop/Euro 2024 - momentum - DS-AI project/Data/matches_complete.csv")
OUTPUT_DIR = BASE_DIR / "data" / "llm_commentary"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# =====================================
# IMPORT V3 HELPER FUNCTIONS (Same classification as V3!)
# =====================================
try:
    from v3_helpers import (
        get_location_description,
        get_distance_description,
        extract_xg_from_shot_column,
        get_foul_danger_context,
        extract_card_from_row,
        validate_player_team,
        calculate_shot_danger_score,
        analyze_multiple_shots,
        analyze_multiple_corners,
        analyze_multiple_fouls,
        analyze_multiple_substitutions,
        analyze_multiple_offsides,
        get_dominant_team_for_minute,
        check_domination_for_consecutive_generals,
        get_most_active_player,
        detect_all_important_events,
        detect_main_event,
        extract_event_specific_data,
        detect_event_chain,
    )
    HELPERS_AVAILABLE = True
    print("[OK] Using V3 classification (same as original)")
except ImportError as e:
    print(f"[ERROR] Could not import V3 helpers: {e}")
    print("[ERROR] V6 requires V3 helpers for consistent classification!")
    HELPERS_AVAILABLE = False

# V6: Import event sequence analyzer (graceful fallback)
# V6: analyze_event_sequence removed - using detect_event_chain instead


# =====================================
# SCORE COUNTING - FIX: Count goals from data, not broken columns
# =====================================
def build_running_score(df, home_team, away_team):
    """
    Build running score by counting goals (is_goal=True) AND own goals for each minute.
    Returns dict: {(minute, period): {'home': X, 'away': Y}}
    
    EXCLUDES period 5 (penalty shootout) - those are tracked separately.
    
    Own Goal Logic: When Team A scores an own goal, Team B gets +1
    """
    running_scores = {}
    home_goals = 0
    away_goals = 0
    
    # Get all shot goals in periods 1-4 (not shootout)
    goals = df[(df['is_goal'] == True) & (df['period'] <= 4)].copy()
    goals = goals.sort_values(['period', 'minute', 'second'] if 'second' in goals.columns else ['period', 'minute'])
    
    # Build set of goal (minute, period, team) for quick lookup
    goal_events = set()
    for _, row in goals.iterrows():
        goal_events.add((row['minute'], row['period'], row['team_name']))
    
    # Get own goals in periods 1-4
    # ONLY count "Own Goal For" - the team that BENEFITS from the own goal
    # (There are also "Own Goal Against" events but counting both would double-count)
    own_goals = df[
        (df['event_type'].str.contains('Own Goal For', case=False, na=False)) & 
        (df['period'] <= 4)
    ].copy()
    
    # Build set of own goals (minute, period, team_that_benefits)
    own_goal_events = set()
    for _, row in own_goals.iterrows():
        own_goal_events.add((row['minute'], row['period'], row['team_name']))
    
    # Process all minutes in order
    all_minutes = df.groupby(['minute', 'period']).size().reset_index()[['minute', 'period']]
    all_minutes = all_minutes.sort_values(['period', 'minute']).reset_index(drop=True)
    
    for _, row in all_minutes.iterrows():
        minute = row['minute']
        period = row['period']
        
        if period > 4:  # Skip shootout
            continue
        
        # Check if shot goal scored this minute
        if (minute, period, home_team) in goal_events:
            home_goals += 1
        if (minute, period, away_team) in goal_events:
            away_goals += 1
        
        # Check if own goal this minute (Own Goal For = team that BENEFITS gets the goal)
        if (minute, period, home_team) in own_goal_events:
            home_goals += 1  # Home team benefits from own goal
        if (minute, period, away_team) in own_goal_events:
            away_goals += 1  # Away team benefits from own goal
        
        running_scores[(minute, period)] = {'home': home_goals, 'away': away_goals}
    
    return running_scores


def build_shootout_score(df, home_team, away_team):
    """
    Build penalty shootout score tracking.
    
    FIX: Process EACH SHOT ROW (not unique minutes) since multiple penalties
    can happen at the same minute.
    
    Alternation: First team in data starts, then alternates.
    
    Returns list: [{'minute': M, 'home': X, 'away': Y, 'penalty_num': N, 'team': T, 'player': P, 'scored': bool}, ...]
    """
    shootout_list = []
    home_scored = 0
    away_scored = 0
    
    # Get ALL shot rows in period 5, sorted by time
    sort_cols = ['minute', 'second'] if 'second' in df.columns else ['minute']
    shootout_shots = df[(df['period'] == 5) & (df['event_type'] == 'Shot')].sort_values(sort_cols).reset_index()
    
    if len(shootout_shots) == 0:
        return []
    
    # Determine first team from first penalty
    first_team = shootout_shots.iloc[0]['team_name']
    
    # Process each penalty
    for penalty_num, (_, shot_row) in enumerate(shootout_shots.iterrows(), start=1):
        minute = shot_row['minute']
        team = shot_row['team_name']
        player = shot_row.get('player_name', '')
        scored = shot_row.get('is_goal', False)
        
        # Update score
        if scored:
            if team == home_team:
                home_scored += 1
            else:
                away_scored += 1
        
        shootout_list.append({
            'minute': minute,
            'home': home_scored,
            'away': away_scored,
            'penalty_num': penalty_num,
            'team': team,
            'player': player,
            'scored': scored
        })
    
    return shootout_list


def load_all_matches():
    """Load match information for all 51 Euro 2024 games."""
    matches_df = pd.read_csv(MATCHES_DATA)
    
    matches = []
    for _, row in matches_df.iterrows():
        matches.append({
            'match_id': row['match_id'],
            'home_team': row['home_team_name'],
            'away_team': row['away_team_name'],
            'stage': row['stage'],
            'home_score': row['home_score'],
            'away_score': row['away_score'],
            'match_date': row.get('match_date', '')
        })
    
    return matches


def load_match_data(match_id):
    """Load event data for a specific match."""
    # Try rich commentary file first
    rich_file = PHASE7_DATA / f"match_{match_id}_rich_commentary.csv"
    if rich_file.exists():
        return pd.read_csv(rich_file)
    
    # Try detailed file
    detailed_file = PHASE7_DATA / f"match_{match_id}_detailed_commentary_data.csv"
    if detailed_file.exists():
        return pd.read_csv(detailed_file)
    
    return None


def load_complete_dataset():
    """Load the complete dataset for xG and card columns."""
    try:
        return pd.read_csv(COMPLETE_DATA, low_memory=False)
    except Exception as e:
        print(f"[WARN] Could not load complete dataset: {e}")
        return None


def extract_recent_events(minute_df, minute, home_team, away_team, lookback=5):
    """Extract recent events for momentum agent context."""
    events = []
    
    for _, row in minute_df.iterrows():
        event_type = row.get('event_type', 'Unknown')
        team = row.get('team', row.get('possession_team', ''))
        player = row.get('player', '')
        
        # Map to simplified event types
        if event_type in ['Shot', 'Goal']:
            detail = row.get('shot_outcome', '')
        elif event_type == 'Foul Committed':
            detail = 'Foul'
            event_type = 'Foul'
        elif event_type == 'Pass':
            if 'key' in str(row.get('pass_type', '')).lower():
                detail = 'Key pass'
            else:
                continue  # Skip regular passes
        elif event_type == 'Carry':
            detail = 'Dribble'
        elif event_type == 'Corner':
            detail = ''
        else:
            continue  # Skip other event types
        
        events.append({
            'minute': int(row.get('minute', minute)),
            'team': team,
            'event_type': event_type,
            'detail': detail,
            'player': player
        })
    
    return events[-10:]  # Last 10 events max


def generate_match_commentary_v6(match_info, df, complete_df, commentator):
    """Generate V6 commentary for a single match with momentum agent and event sequences."""
    match_id = match_info['match_id']
    home_team = match_info['home_team']
    away_team = match_info['away_team']
    stage = match_info['stage']
    
    # Reset trackers
    last_event_type = None
    consecutive_general_count = 0
    general_control_history = []
    recent_events_cache = []
    
    # Merge columns from complete dataset
    if complete_df is not None:
        match_complete = complete_df[complete_df['match_id'] == match_id].copy().reset_index(drop=True)
        if len(df) == len(match_complete):
            for col in ['foul_committed', 'bad_behaviour', 'shot']:
                if col in match_complete.columns:
                    df[col] = match_complete[col].values
    
    # FIX: Build running score by COUNTING GOALS, not using broken columns
    running_scores = build_running_score(df, home_team, away_team)
    shootout_list = build_shootout_score(df, home_team, away_team)  # Now returns a list
    
    results = []
    
    # FIX: Group by (minute, period) not just minute - for PERIODS 1-4 only
    df['minute_period'] = df['minute'].astype(str) + '_' + df['period'].astype(str)
    minute_periods = df[df['period'] <= 4].groupby(['minute', 'period']).size().reset_index()[['minute', 'period']]
    minute_periods = minute_periods.sort_values(['period', 'minute']).reset_index(drop=True)
    
    for _, mp_row in minute_periods.iterrows():
        minute = mp_row['minute']
        period = mp_row['period']
        
        minute_df = df[(df['minute'] == minute) & (df['period'] == period)].copy()
        if minute_df.empty:
            continue
        
        # Normal detection for periods 1-4
        if HELPERS_AVAILABLE:
            base_detection_info = {
                'home_team': home_team,
                'away_team': away_team,
                'period': period,
            }
            
            all_events = detect_all_important_events(minute_df, base_detection_info)
            if not all_events:
                detected_type, main_row, extra_info = detect_main_event(minute_df, base_detection_info)
                all_events = [(detected_type, main_row, extra_info)]
            
            # Multi-event analysis (V3 function signatures)
            multi_shots_info = analyze_multiple_shots(minute_df)
            multi_corners_info = analyze_multiple_corners(minute_df)
            multi_fouls_info = analyze_multiple_fouls(minute_df)
            multi_subs_info = analyze_multiple_substitutions(minute_df)
            multi_offsides_info = analyze_multiple_offsides(minute_df)
            most_active = get_most_active_player(minute_df)
            
            # V6: Event sequence removed - now using chain detection instead
        else:
            # Simplified detection
            event_type = minute_df.iloc[0].get('event_type', 'General')
            detected_type = event_type if event_type in ['Goal', 'Shot', 'Foul Committed'] else 'General'
            all_events = [(detected_type, minute_df.iloc[0], {})]
            multi_shots_info = {'has_multiple': False}
            multi_corners_info = {'has_multiple': False}
            multi_fouls_info = {'has_multiple': False}
            multi_subs_info = {'has_multiple': False}
            multi_offsides_info = {'has_multiple': False}
            most_active = {}
            event_sequence_info = {'has_sequence': False}
        
        # FIX: Get scores from running score (counted from goals)
        # Regular play - use running score
        score_info = running_scores.get((minute, period), {'home': 0, 'away': 0})
        home_score = score_info['home']
        away_score = score_info['away']
        penalty_num = 0
        
        # Extract recent events for momentum agent
        recent_events = extract_recent_events(minute_df, minute, home_team, away_team)
        recent_events_cache.extend(recent_events)
        recent_events_cache = recent_events_cache[-20:]  # Keep last 20
        
        # Track which teams have been processed for multi-subs this minute
        # FIX: Generate SEPARATE commentary for each team when both teams sub in same minute
        multi_subs_teams_processed = set()
        
        for event_idx, (detected_type, main_row, extra_info) in enumerate(all_events):
            # FIX POINT 1: Handle multi-subs PER TEAM
            # Generate one commentary per team, not one combined for all teams
            # Reset current_sub_team for each event (only set when processing multi-subs)
            current_sub_team = None
            if detected_type == 'Substitution' and multi_subs_info.get('has_multiple', False):
                # Get the team for this substitution event
                sub_team = main_row.get('team_name', main_row.get('team', ''))
                
                if sub_team in multi_subs_teams_processed:
                    # Skip - already generated commentary for this team's subs
                    continue
                multi_subs_teams_processed.add(sub_team)
                current_sub_team = sub_team  # Pass this to context for filtering
            # Get current control
            current_control = ''
            if 'possession_team' in minute_df.columns:
                possession_counts = minute_df['possession_team'].value_counts()
                if len(possession_counts) > 0:
                    dominant_team = possession_counts.index[0]
                    dominant_pct = (possession_counts.iloc[0] / len(minute_df)) * 100
                    if dominant_pct > 60:
                        current_control = f"{dominant_team} in control"
            
            # Track consecutive generals
            if detected_type == 'General':
                # FIX ISSUE 1: Reset count when TEAM CHANGES, not just event type
                # Extract current controlling team
                current_team = current_control.split()[0] if current_control and current_control.strip() else ''
                last_control = general_control_history[-1] if general_control_history else ''
                last_team = last_control.split()[0] if last_control and last_control.strip() else ''
                
                if last_event_type == 'General' and current_team == last_team:
                    # Same team still in control - increment
                    consecutive_general_count += 1
                else:
                    # Different team OR first general - reset to 1
                    consecutive_general_count = 1
                    general_control_history = []
                
                general_control_history.append(current_control)
                if HELPERS_AVAILABLE:
                    domination_info = check_domination_for_consecutive_generals(
                        consecutive_general_count, 
                        current_control, 
                        general_control_history
                    )
                else:
                    domination_info = {'has_domination': False}
            else:
                consecutive_general_count = 0
                general_control_history = []
                domination_info = {'has_domination': False}
            
            last_event_type = detected_type
            
            # Extract event data
            if HELPERS_AVAILABLE:
                detection_info = {'home_team': home_team, 'away_team': away_team, 'period': period}
                detection_info.update(extra_info)
                event_data = extract_event_specific_data(detected_type, main_row, minute_df, detection_info)
            else:
                event_data = {
                    'player': main_row.get('player', ''),
                    'team': main_row.get('team', main_row.get('possession_team', '')),
                    'scorer': main_row.get('player', ''),
                }
            
            # FIX POINT 2: Add fouled_player/fouled_team for Card events (from V3 lines 1017-1021)
            # This enables commentary like "for a foul on X" instead of generic "late challenge"
            if detected_type in ['Yellow Card', 'Red Card']:
                event_data['carded_player'] = extra_info.get('carded_player', event_data.get('player', ''))
                event_data['carded_team'] = extra_info.get('carded_team', event_data.get('team', ''))
                event_data['fouled_player'] = extra_info.get('fouled_player', '')
                event_data['fouled_team'] = extra_info.get('fouled_team', '')
            
            # V6: Detect event chain (origin + related events for main event)
            event_chain = {'has_chain': False, 'origin': '', 'related_events': []}
            if HELPERS_AVAILABLE:
                event_chain = detect_event_chain(minute_df, detected_type, main_row, detection_info)
            
            # Calculate area - V6.2 FIX: Add team context (whose third)
            # X=0 is home goal, X=120 is away goal (StatsBomb convention)
            area = ''
            if 'location_x' in minute_df.columns:
                avg_x = minute_df['location_x'].mean()
                if pd.notna(avg_x):
                    if avg_x < 40:
                        area = f"{home_team}'s defensive third"  # Near home goal
                    elif avg_x < 80:
                        area = 'midfield'
                    else:
                        area = f"{away_team}'s defensive third"  # Near away goal
            
            # Note: Period 5 is handled separately after main loop
            
            # V6 FIX: Calculate possession stats for General events
            possession_stats = {}
            if detected_type == 'General' and 'possession_team' in minute_df.columns:
                poss_counts = minute_df['possession_team'].value_counts()
                total = len(minute_df)
                for team_name, count in poss_counts.items():
                    pct = int((count / total) * 100)
                    possession_stats[team_name] = pct
            
            # Build context - V6: Added event_chain, most_active_player, possession_stats
            context = {
                'match_id': match_id,
                'home_team': home_team,
                'away_team': away_team,
                'home_score': home_score,
                'away_score': away_score,
                'stage': stage,
                'period': period,
                'detected_type': detected_type,
                'event_data': event_data,
                'control': current_control,
                'area': area,
                'domination_info': domination_info,
                'consecutive_generals': consecutive_general_count,
                'multi_shots_info': multi_shots_info,
                'multi_corners_info': multi_corners_info,
                'multi_fouls_info': multi_fouls_info,
                'multi_subs_info': multi_subs_info,
                'multi_offsides_info': multi_offsides_info,
                'current_sub_team': current_sub_team,  # For filtering multi-subs per team
                'event_chain': event_chain,  # V6: Chain detection (origin + related)
                'most_active_player': most_active,  # V6 FIX: Pass most active player
                'possession_stats': possession_stats,  # V6 FIX: Pass possession stats
            }
            
            # Generate commentary with V6 (includes momentum agent + sequences)
            llm_commentary = commentator.generate_minute_commentary(
                minute=int(minute),
                events_data=[],
                rule_based_commentary='',
                sequence_commentary='',
                match_context=context,
                recent_events=recent_events_cache[-10:]  # Pass recent events to momentum agent
            )
            
            # Save result
            result = {
                'match_id': match_id,
                'minute': minute,
                'period': period,
                'home_team': home_team,
                'away_team': away_team,
                'home_score': home_score,
                'away_score': away_score,
                'stage': stage,
                'detected_type': detected_type,
                'player': event_data.get('player', event_data.get('scorer', event_data.get('carded_player', ''))),
                'team': event_data.get('team', event_data.get('carded_team', '')),
                'llm_commentary': llm_commentary,
                'model': commentator.model,
                'agent_model': commentator.agent_model,
                'momentum_used': 'momentum_context' in context,
                'chain_used': event_chain.get('has_chain', False),  # V6: Chain detection
                'generated_at': datetime.now().isoformat(),
            }
            
            results.append(result)
    
    # ========================================================================
    # PERIOD 5 (PENALTY SHOOTOUT) - Process each penalty individually
    # ========================================================================
    if shootout_list:
        print(f"  Processing {len(shootout_list)} penalties in shootout...")
        
        for shootout_info in shootout_list:
            minute = shootout_info['minute']
            penalty_num = shootout_info['penalty_num']
            home_score = shootout_info['home']
            away_score = shootout_info['away']
            team = shootout_info['team']
            player = shootout_info['player']
            scored = shootout_info['scored']
            
            detected_type = f'Penalty {penalty_num}'
            
            # Build event data
            event_data = {
                'penalty_number': penalty_num,
                'shootout_score': {'home': home_score, 'away': away_score},
                'scored': scored,
                'outcome': 'Goal' if scored else 'Missed/Saved',
                'team': team,
                'player': player,
            }
            
            # Build context for shootout
            context = {
                'match_id': match_id,
                'home_team': home_team,
                'away_team': away_team,
                'home_score': home_score,
                'away_score': away_score,
                'stage': stage,
                'period': 5,
                'detected_type': detected_type,
                'event_data': event_data,
                'control': '',
                'area': '',
                'domination_info': {'has_domination': False},
                'consecutive_generals': 0,
                'multi_shots_info': {'has_multiple': False},
                'multi_corners_info': {'has_multiple': False},
                'multi_fouls_info': {'has_multiple': False},
                'multi_subs_info': {'has_multiple': False},
                'multi_offsides_info': {'has_multiple': False},
                'event_sequence_info': {'has_sequence': False},  # V6
            }
            
            # Generate commentary
            llm_commentary = commentator.generate_minute_commentary(
                minute=int(minute),
                events_data=[],
                rule_based_commentary='',
                sequence_commentary='',
                match_context=context,
                recent_events=[]  # No recent events for shootout
            )
            
            # Save result
            result = {
                'match_id': match_id,
                'minute': minute,
                'period': 5,
                'home_team': home_team,
                'away_team': away_team,
                'home_score': home_score,
                'away_score': away_score,
                'stage': stage,
                'detected_type': detected_type,
                'player': player,
                'team': team,
                'llm_commentary': llm_commentary,
                'model': commentator.model,
                'agent_model': commentator.agent_model,
                'momentum_used': False,
                'chain_used': False,
                'generated_at': datetime.now().isoformat(),
            }
            
            results.append(result)
    
    return results


def run_single_match(match_id=None, home_team=None, away_team=None):
    """Run V6 commentary for a single match."""
    print("=" * 70)
    print("BATCH COMMENTARY GENERATION - V6 (Enhanced Variety)")
    print("With Momentum Agent + Event Sequences + More Variety")
    print("=" * 70)
    
    # Load matches
    print("\n[1/5] Loading match information...")
    matches = load_all_matches()
    
    # Find the match
    match_info = None
    for m in matches:
        if match_id and m['match_id'] == match_id:
            match_info = m
            break
        if home_team and away_team:
            if (home_team.lower() in m['home_team'].lower() and 
                away_team.lower() in m['away_team'].lower()):
                match_info = m
                break
            if (away_team.lower() in m['home_team'].lower() and 
                home_team.lower() in m['away_team'].lower()):
                match_info = m
                break
    
    if not match_info:
        print(f"[ERROR] Match not found!")
        return None
    
    print(f"      Found: {match_info['home_team']} vs {match_info['away_team']}")
    print(f"      Match ID: {match_info['match_id']}")
    print(f"      Stage: {match_info['stage']}")
    
    # Load complete dataset
    print("\n[2/5] Loading complete dataset...")
    complete_df = load_complete_dataset()
    if complete_df is not None:
        print(f"      Loaded {len(complete_df)} events")
    
    # Load match data
    print("\n[3/5] Loading match event data...")
    df = load_match_data(match_info['match_id'])
    if df is None:
        print(f"[ERROR] No data found for match {match_info['match_id']}")
        return None
    print(f"      Loaded {len(df)} events")
    
    # Initialize V6 commentator
    print("\n[4/5] Initializing V6 Commentator...")
    
    # Get API key from environment or command line
    api_key = os.getenv('OPENAI_API_KEY')
    
    # Try to load from root .env if not in environment
    if not api_key:
        # Search parent directories for .env
        current = Path(__file__).resolve().parent
        for _ in range(6):  # Up to 6 levels
            env_path = current / '.env'
            if env_path.exists():
                # Try different encodings (UTF-16, UTF-8, etc.)
                for encoding in ['utf-16', 'utf-8', 'utf-8-sig', 'latin-1']:
                    try:
                        with open(env_path, 'r', encoding=encoding) as f:
                            for line in f:
                                line = line.strip()
                                if 'OPENAI_API_KEY' in line and '=' in line:
                                    # Handle formats like: OPENAI_API_KEY= sk-xxx or OPENAI_API_KEY=sk-xxx
                                    key = line.split('=', 1)[1].strip()
                                    if key.startswith('sk-'):
                                        api_key = key
                                        print(f"      API key loaded from {env_path}")
                                        break
                        if api_key:
                            break
                    except Exception:
                        continue
                if api_key:
                    break
            current = current.parent
    
    if not api_key:
        print("[ERROR] No API key found!")
        print("        Set OPENAI_API_KEY environment variable or use --api-key argument")
        print("")
        print("        Usage: python batch_generate_v6.py --api-key sk-your-key-here")
        return None
    
    try:
        commentator = GPTCommentatorV6(
            api_key=api_key,
            model="gpt-4o-mini",      # Commentary
            agent_model="gpt-4o",     # Momentum agent
            enable_momentum=True
        )
        print(f"      Commentary model: {commentator.model}")
        print(f"      Agent model: {commentator.agent_model}")
        print(f"      Momentum agent: {'Enabled' if commentator.momentum_agent else 'Disabled'}")
        print(f"      Chain detection: Enabled")
    except Exception as e:
        print(f"[ERROR] Failed to initialize commentator: {e}")
        return None
    
    # Generate commentary
    print("\n[5/5] Generating V6 commentary...")
    print("-" * 70)
    
    start_time = time.time()
    
    try:
        results = generate_match_commentary_v6(match_info, df, complete_df, commentator)
        
        if results:
            # Create DataFrame
            results_df = pd.DataFrame(results)
            
            # Save CSV
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_home = match_info['home_team'].replace(' ', '_')
            safe_away = match_info['away_team'].replace(' ', '_')
            output_file = OUTPUT_DIR / f"match_{match_info['match_id']}_{safe_home}_vs_{safe_away}_V6_{timestamp}.csv"
            results_df.to_csv(output_file, index=False)
            
            elapsed = time.time() - start_time
            
            print(f"\n[OK] Generated {len(results)} commentaries in {elapsed:.1f}s")
            print(f"[OK] Saved: {output_file}")
            
            # Stats
            chain_count = results_df['chain_used'].sum() if 'chain_used' in results_df.columns else 0
            print(f"[OK] Chains detected: {chain_count}")
            
            # Show sample
            print("\n" + "=" * 70)
            print("SAMPLE COMMENTARIES:")
            print("=" * 70)
            for _, row in results_df.head(10).iterrows():
                chain_mark = " [CHAIN]" if row.get('chain_used', False) else ""
                print(f"\n{row['minute']}' [{row['detected_type']}]{chain_mark}")
                print(f"   {row['llm_commentary']}")
            
            return output_file
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='V6 Commentary Generator')
    parser.add_argument('--api-key', type=str, help='OpenAI API key')
    parser.add_argument('--home', type=str, default='England', help='Home team name')
    parser.add_argument('--away', type=str, default='Switzerland', help='Away team name')
    parser.add_argument('--match-id', type=int, help='Match ID (optional)')
    args = parser.parse_args()
    
    # Set API key if provided
    if args.api_key:
        os.environ['OPENAI_API_KEY'] = args.api_key
    
    # Run the match
    output = run_single_match(
        match_id=args.match_id,
        home_team=args.home,
        away_team=args.away
    )
    
    if output:
        print(f"\n[SUCCESS] Output saved to: {output}")
    else:
        print(f"\n[FAILED] No output generated")


if __name__ == "__main__":
    main()

