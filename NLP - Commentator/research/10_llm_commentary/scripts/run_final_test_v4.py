"""
Test run for matches with penalties - V4

V4 ENHANCEMENTS (on top of V3):
- Period 5 (Penalty Shootout) handling
- Period 1-4 Penalty detection (Penalty Awarded, Penalty Goal/Saved/Missed)
- Goalkeeper info for saves
- Penalty count tracking for shootouts
- Shootout score tracking

Key Logic:
- Period 5: Skip Half Start, detect Shot events as penalties, track shootout score
- Period 1-4: Check shot.type.name='Penalty' for penalty kicks
- Penalty Awarded: Foul in box (location_x > 102) or play_pattern='From Penalty'
"""

import os
import sys
import ast
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gpt_commentator_v4 import GPTCommentator

# Paths
SCRIPT_DIR = Path(__file__).parent
BASE_DIR = SCRIPT_DIR.parent
PHASE7_DATA = BASE_DIR.parent / "07_all_games_commentary" / "data"
COMPLETE_DATA = Path("C:/Users/yonatanam/Desktop/Euro 2024 - momentum - DS-AI project/Data/euro_2024_complete_dataset.csv")
OUTPUT_DIR = BASE_DIR / "data" / "llm_commentary"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# =====================================
# GLOBAL TRACKERS
# =====================================
possession_history = {}
last_event_type = None
consecutive_general_count = 0
general_control_history = []

# V4: Shootout trackers
shootout_score = {'home': 0, 'away': 0}
penalty_count = 0


# =====================================
# HELPER FUNCTIONS
# =====================================

def get_location_description(location_x, location_y):
    """Convert x,y coordinates to natural location description."""
    if pd.isna(location_x) or pd.isna(location_y):
        return None
    
    x, y = float(location_x), float(location_y)
    
    if y < 26:
        side = "right"
    elif y > 54:
        side = "left"
    else:
        side = "centre"
    
    if x < 40:
        area = "defensive half"
    elif x < 60:
        area = "midfield"
    elif x < 80:
        area = f"{side} wing" if side != "centre" else "attacking third"
    elif x < 102:
        if side == "centre":
            area = "edge of the box"
        else:
            area = f"{side} side of the box"
    else:
        if x >= 114:
            area = "six yard box"
        elif side == "centre":
            area = "centre of the box"
        else:
            area = f"{side} side of the box"
    
    return area


def extract_xg_from_shot_column(shot_value):
    """Extract xG from the shot column."""
    if pd.isna(shot_value) or not shot_value:
        return None
    
    try:
        if isinstance(shot_value, str):
            data = ast.literal_eval(shot_value)
        else:
            data = shot_value
        
        if isinstance(data, dict):
            return data.get('statsbomb_xg', None)
    except (ValueError, SyntaxError):
        pass
    
    return None


def extract_shot_type(shot_value):
    """Extract shot type (Penalty, Open Play, etc.) from shot column."""
    if pd.isna(shot_value) or not shot_value:
        return None
    
    try:
        if isinstance(shot_value, str):
            data = ast.literal_eval(shot_value)
        else:
            data = shot_value
        
        if isinstance(data, dict):
            return data.get('type', {}).get('name', None)
    except (ValueError, SyntaxError):
        pass
    
    return None


def extract_shot_outcome(shot_value):
    """Extract shot outcome from shot column."""
    if pd.isna(shot_value) or not shot_value:
        return None
    
    try:
        if isinstance(shot_value, str):
            data = ast.literal_eval(shot_value)
        else:
            data = shot_value
        
        if isinstance(data, dict):
            return data.get('outcome', {}).get('name', None)
    except (ValueError, SyntaxError):
        pass
    
    return None


def extract_goalkeeper_info(gk_value):
    """Extract goalkeeper info from goalkeeper column."""
    if pd.isna(gk_value) or not gk_value:
        return None
    
    try:
        if isinstance(gk_value, str):
            data = ast.literal_eval(gk_value)
        else:
            data = gk_value
        
        if isinstance(data, dict):
            return {
                'type': data.get('type', {}).get('name', ''),
                'outcome': data.get('outcome', {}).get('name', '')
            }
    except (ValueError, SyntaxError):
        pass
    
    return None


def extract_card_from_row(row):
    """Extract card information from foul_committed or bad_behaviour columns."""
    card = None
    
    fc = row.get('foul_committed', '')
    if pd.notna(fc) and fc and 'card' in str(fc).lower():
        try:
            data = ast.literal_eval(fc) if isinstance(fc, str) else fc
            if isinstance(data, dict) and 'card' in data:
                card_info = data['card']
                if isinstance(card_info, dict) and 'name' in card_info:
                    card = card_info['name']
        except (ValueError, SyntaxError):
            pass
    
    if card is None:
        bb = row.get('bad_behaviour', '')
        if pd.notna(bb) and bb and 'card' in str(bb).lower():
            try:
                data = ast.literal_eval(bb) if isinstance(bb, str) else bb
                if isinstance(data, dict) and 'card' in data:
                    card_info = data['card']
                    if isinstance(card_info, dict) and 'name' in card_info:
                        card = card_info['name']
            except (ValueError, SyntaxError):
                pass
    
    return card


def is_penalty_foul(row):
    """Check if a foul is in the penalty area (leads to penalty)."""
    location_x = row.get('location_x', 0)
    if pd.notna(location_x) and float(location_x) > 102:
        return True
    return False


def check_for_penalty_in_minute(minute_df):
    """
    Check if there's a penalty in this minute.
    
    Returns:
        dict with penalty info or None
    """
    # Check for shot with type='Penalty'
    for idx, row in minute_df[minute_df['event_type'] == 'Shot'].iterrows():
        shot_data = row.get('shot', '')
        shot_type = extract_shot_type(shot_data)
        
        if shot_type == 'Penalty':
            outcome = extract_shot_outcome(shot_data) or row.get('shot_outcome', '')
            
            # Find goalkeeper
            gk_name = ''
            gk_team = ''
            gk_events = minute_df[minute_df['event_type'] == 'Goal Keeper']
            if len(gk_events) > 0:
                gk_row = gk_events.iloc[0]
                gk_name = gk_row.get('player_name', '')
                gk_team = gk_row.get('team_name', '')
            
            return {
                'has_penalty': True,
                'player': row.get('player_name', ''),
                'team': row.get('team_name', ''),
                'outcome': outcome,
                'goalkeeper': gk_name,
                'goalkeeper_team': gk_team,
                'row': row
            }
    
    return None


def find_penalty_foul(minute_df, penalty_info):
    """
    Find the foul that led to the penalty.
    
    Returns:
        dict with fouler, fouled player, and location info
    """
    result = {
        'fouler': '',
        'fouler_team': '',
        'fouled_player': '',
        'fouled_team': '',
        'location': 'in the box'
    }
    
    # Look for Foul Committed and Foul Won events
    foul_committed = minute_df[minute_df['event_type'] == 'Foul Committed']
    foul_won = minute_df[minute_df['event_type'] == 'Foul Won']
    
    # Get the fouler (who committed the foul)
    if len(foul_committed) > 0:
        fc = foul_committed.iloc[-1]
        result['fouler'] = fc.get('player_name', '')
        result['fouler_team'] = fc.get('team_name', '')
        
        # Get location description
        loc_x = fc.get('location_x')
        loc_y = fc.get('location_y')
        if pd.notna(loc_x) and pd.notna(loc_y):
            loc_desc = get_location_description(loc_x, loc_y)
            if loc_desc:
                result['location'] = loc_desc
    
    # Get the fouled player (who won the foul / takes the penalty)
    if len(foul_won) > 0:
        fw = foul_won.iloc[-1]
        result['fouled_player'] = fw.get('player_name', '')
        result['fouled_team'] = fw.get('team_name', '')
    else:
        # Use penalty taker as the fouled player
        result['fouled_player'] = penalty_info.get('player', '')
        result['fouled_team'] = penalty_info.get('team', '')
    
    return result


# =====================================
# V4: PENALTY SHOOTOUT DETECTION
# =====================================

def detect_shootout_penalties(minute_df, home_team, away_team, current_shootout_score):
    """
    Detect penalties in Period 5 (shootout).
    
    Returns:
        list of penalty events with shootout context
    """
    global penalty_count
    
    events = []
    shot_rows = minute_df[minute_df['event_type'] == 'Shot']
    
    for idx, row in shot_rows.iterrows():
        penalty_count += 1
        
        shot_data = row.get('shot', '')
        outcome = extract_shot_outcome(shot_data) or row.get('shot_outcome', '')
        
        player = row.get('player_name', '')
        team = row.get('team_name', '')
        
        # Find goalkeeper
        gk_name = ''
        gk_team = ''
        gk_events = minute_df[minute_df['event_type'] == 'Goal Keeper']
        if len(gk_events) > 0:
            gk_row = gk_events.iloc[0]
            gk_name = gk_row.get('player_name', '')
            gk_team = gk_row.get('team_name', '')
        
        # Determine event type based on outcome
        if outcome == 'Goal':
            event_type = 'Penalty Goal'
            # Update shootout score
            if team == home_team:
                current_shootout_score['home'] += 1
            else:
                current_shootout_score['away'] += 1
        elif outcome == 'Saved':
            event_type = 'Penalty Saved'
        else:  # Post, Off T, Wayward
            event_type = 'Penalty Missed'
        
        info = {
            'penalty_number': penalty_count,
            'player': player,
            'team': team,
            'outcome': outcome,
            'goalkeeper': gk_name,
            'goalkeeper_team': gk_team,
            'shootout_score': current_shootout_score.copy(),
            'is_shootout': True
        }
        
        events.append((f'Penalty {penalty_count}', row, info))
    
    return events


# =====================================
# V4: ENHANCED EVENT DETECTION
# =====================================

def detect_all_important_events_v4(minute_df, detection_info, home_team, away_team):
    """
    Detect ALL important events including penalties.
    
    V4 adds:
    - Period 5 (shootout) penalty detection
    - Period 1-4 penalty awarded detection
    - Period 1-4 penalty taken detection
    """
    global shootout_score, penalty_count
    
    events = []
    used_indices = set()
    period = detection_info.get('period', 1)
    
    # ========== PERIOD 5: PENALTY SHOOTOUT ==========
    if period == 5:
        # Skip Half Start events in shootout
        # Only detect penalties
        shootout_events = detect_shootout_penalties(
            minute_df, home_team, away_team, shootout_score
        )
        return shootout_events
    
    # ========== PERIODS 1-4: REGULAR PLAY ==========
    
    # 1. HALF START (Kick Off)
    half_start = minute_df[minute_df['event_type'] == 'Half Start']
    if len(half_start) > 0:
        row = half_start.iloc[0]
        period = row.get('period', 1)
        info = {
            'period': period,
            'is_period_start': True,
            'stage': detection_info.get('stage', '')
        }
        events.append(('Kick Off', row, info))
        used_indices.add(row.name)
    
    # 2. PENALTIES (Period 1-4): Always create 2 events - Awarded + Result
    penalty_info = check_for_penalty_in_minute(minute_df)
    if penalty_info:
        # 2a. PENALTY AWARDED - First commentary
        # Find the foul that led to the penalty
        foul_info = find_penalty_foul(minute_df, penalty_info)
        
        awarded_info = {
            'team': penalty_info.get('team', ''),
            'fouled_player': foul_info.get('fouled_player', penalty_info.get('player', '')),
            'fouled_team': foul_info.get('fouled_team', penalty_info.get('team', '')),
            'fouler': foul_info.get('fouler', ''),
            'fouler_team': foul_info.get('fouler_team', ''),
            'location': foul_info.get('location', 'in the box'),
        }
        events.append(('Penalty Awarded', penalty_info['row'], awarded_info))
        
        # 2b. PENALTY RESULT - Second commentary
        outcome = penalty_info.get('outcome', '')
        if outcome == 'Goal':
            event_type = 'Penalty Goal'
        elif outcome == 'Saved':
            event_type = 'Penalty Saved'
        else:
            event_type = 'Penalty Missed'
        
        events.append((event_type, penalty_info['row'], penalty_info))
        used_indices.add(penalty_info['row'].name)
    
    # 4. REGULAR GOALS (non-penalty)
    goal_rows = minute_df[minute_df['shot_outcome'] == 'Goal']
    if len(goal_rows) == 0 and 'is_goal' in minute_df.columns:
        goal_rows = minute_df[minute_df['is_goal'] == True]
    
    for _, row in goal_rows.iterrows():
        if row.name not in used_indices:
            # Check if this is a penalty goal (already handled above)
            shot_type = extract_shot_type(row.get('shot', ''))
            if shot_type != 'Penalty':
                events.append(('Goal', row, {}))
                used_indices.add(row.name)
    
    # 5. CARDS
    for idx, row in minute_df.iterrows():
        if idx in used_indices:
            continue
        card_type = extract_card_from_row(row)
        if card_type:
            foul_won_rows = minute_df[minute_df['event_type'] == 'Foul Won']
            fouled_player = ''
            fouled_team = ''
            if len(foul_won_rows) > 0:
                closest_won = foul_won_rows.iloc[-1]
                fouled_player = closest_won.get('player_name', '')
                fouled_team = closest_won.get('team_name', '')
            
            info = {
                'card_type': card_type,
                'carded_player': row.get('player_name', ''),
                'carded_team': row.get('team_name', ''),
                'fouled_player': fouled_player,
                'fouled_team': fouled_team
            }
            events.append((card_type, row, info))
            used_indices.add(idx)
    
    # 6. SUBSTITUTIONS
    sub_rows = minute_df[minute_df['event_type'] == 'Substitution']
    for _, row in sub_rows.iterrows():
        if row.name not in used_indices:
            events.append(('Substitution', row, {}))
            used_indices.add(row.name)
    
    # 7. INJURIES
    injury_rows = minute_df[minute_df['event_type'] == 'Injury Stoppage']
    for _, row in injury_rows.iterrows():
        if row.name not in used_indices:
            events.append(('Injury', row, {}))
            used_indices.add(row.name)
    
    # 8. If NO important events, detect main event (from V3)
    if len(events) == 0:
        main_type, main_row, info = detect_main_event_v4(minute_df)
        events.append((main_type, main_row, info))
    
    return events


def detect_main_event_v4(minute_df):
    """Enhanced detection using multiple columns (V4 version)."""
    detection_info = {}
    
    # Check play patterns
    play_patterns = minute_df['play_pattern'].dropna().unique().tolist()
    detection_info['play_patterns'] = play_patterns
    
    has_corner = any('Corner' in str(p) for p in play_patterns)
    has_free_kick = any('Free Kick' in str(p) for p in play_patterns)
    
    # Check for shots
    shot_rows = minute_df[minute_df['event_type'] == 'Shot']
    if len(shot_rows) > 0:
        main_row = shot_rows.iloc[-1]
        outcome = main_row.get('shot_outcome', '')
        return f"Shot ({outcome})" if outcome else "Shot", main_row, detection_info
    
    # Check for corners
    if has_corner:
        corner_rows = minute_df[minute_df['play_pattern'].str.contains('Corner', na=False)]
        main_row = corner_rows.iloc[0] if len(corner_rows) > 0 else minute_df.iloc[-1]
        return 'Corner', main_row, detection_info
    
    # Check for free kicks
    if has_free_kick:
        fk_rows = minute_df[minute_df['play_pattern'].str.contains('Free Kick', na=False)]
        main_row = fk_rows.iloc[0] if len(fk_rows) > 0 else minute_df.iloc[-1]
        return 'Free Kick', main_row, detection_info
    
    # Check for fouls
    foul_rows = minute_df[minute_df['event_type'].isin(['Foul Committed', 'Foul Won'])]
    if len(foul_rows) > 0:
        main_row = foul_rows.iloc[-1]
        return 'Foul', main_row, detection_info
    
    # Default: General
    main_row = minute_df.iloc[-1]
    
    # Calculate possession stats
    if 'possession_team' in minute_df.columns:
        possession_counts = minute_df['possession_team'].value_counts()
        total_events = len(minute_df)
        possession_pcts = {team: round(count/total_events*100, 1) 
                          for team, count in possession_counts.items()}
        detection_info['possession_stats'] = possession_pcts
        
        if len(possession_pcts) > 0:
            dominant_team = max(possession_pcts, key=possession_pcts.get)
            dominant_pct = possession_pcts[dominant_team]
            if dominant_pct > 70:
                detection_info['control'] = f"{dominant_team} dominant"
            elif dominant_pct > 55:
                detection_info['control'] = f"{dominant_team} in control"
            else:
                detection_info['control'] = "Even"
    
    return 'General', main_row, detection_info


def extract_event_specific_data_v4(detected_type, main_row, minute_df, detection_info, home_team, away_team):
    """Extract event-specific data including penalty information."""
    data = {}
    
    data['player'] = main_row.get('player_name', '')
    data['team'] = main_row.get('team_name', '')
    data['location'] = get_location_description(
        main_row.get('location_x'), 
        main_row.get('location_y')
    )
    
    if detected_type == 'Goal':
        data['scorer'] = main_row.get('player_name', '')
        data['body_part'] = main_row.get('shot_body_part', '')
        # Assist logic (from V3)
        data['assisted_by'] = ''
    
    elif detected_type == 'Penalty Goal':
        data['player'] = detection_info.get('player', main_row.get('player_name', ''))
        data['team'] = detection_info.get('team', main_row.get('team_name', ''))
        data['goalkeeper'] = detection_info.get('goalkeeper', '')
        data['goalkeeper_team'] = detection_info.get('goalkeeper_team', '')
    
    elif detected_type == 'Penalty Saved':
        data['player'] = detection_info.get('player', main_row.get('player_name', ''))
        data['team'] = detection_info.get('team', main_row.get('team_name', ''))
        data['goalkeeper'] = detection_info.get('goalkeeper', '')
        data['goalkeeper_team'] = detection_info.get('goalkeeper_team', '')
    
    elif detected_type == 'Penalty Missed':
        data['player'] = detection_info.get('player', main_row.get('player_name', ''))
        data['team'] = detection_info.get('team', main_row.get('team_name', ''))
        data['outcome'] = detection_info.get('outcome', 'Missed')
    
    elif detected_type == 'Penalty Awarded':
        data['team'] = detection_info.get('team', '')
        data['fouled_player'] = detection_info.get('fouled_player', '')
        data['fouled_team'] = detection_info.get('fouled_team', '')
        data['fouler'] = detection_info.get('fouler', '')
        data['fouler_team'] = detection_info.get('fouler_team', '')
    
    elif detected_type.startswith('Penalty') and detection_info.get('is_shootout'):
        # Penalty shootout
        data['penalty_number'] = detection_info.get('penalty_number', 0)
        data['player'] = detection_info.get('player', '')
        data['team'] = detection_info.get('team', '')
        data['outcome'] = detection_info.get('outcome', '')
        data['goalkeeper'] = detection_info.get('goalkeeper', '')
        data['goalkeeper_team'] = detection_info.get('goalkeeper_team', '')
        data['shootout_score'] = detection_info.get('shootout_score', {'home': 0, 'away': 0})
    
    elif 'Shot' in detected_type:
        data['outcome'] = main_row.get('shot_outcome', '')
        data['body_part'] = main_row.get('shot_body_part', '')
        
        if main_row.get('shot_outcome') == 'Saved':
            gk_events = minute_df[minute_df['event_type'] == 'Goal Keeper']
            if len(gk_events) > 0:
                data['saved_by'] = gk_events.iloc[0].get('player_name', '')
    
    elif detected_type == 'Corner':
        data['delivered_by'] = main_row.get('player_name', '')
        data['conceded_by'] = main_row.get('previous_player', '')
    
    elif detected_type in ['Foul', 'Free Kick']:
        foul_committed = minute_df[minute_df['event_type'] == 'Foul Committed']
        foul_won = minute_df[minute_df['event_type'] == 'Foul Won']
        
        if len(foul_committed) > 0:
            data['committed_by'] = foul_committed.iloc[-1].get('player_name', '')
            data['committed_team'] = foul_committed.iloc[-1].get('team_name', '')
        
        if len(foul_won) > 0:
            data['fouled_player'] = foul_won.iloc[-1].get('player_name', '')
            data['fouled_team'] = foul_won.iloc[-1].get('team_name', '')
    
    elif detected_type in ['Yellow Card', 'Red Card']:
        data['carded_player'] = detection_info.get('carded_player', main_row.get('player_name', ''))
        data['carded_team'] = detection_info.get('carded_team', main_row.get('team_name', ''))
        data['fouled_player'] = detection_info.get('fouled_player', '')
        data['fouled_team'] = detection_info.get('fouled_team', '')
    
    elif detected_type == 'Substitution':
        data['player_off'] = main_row.get('player_name', '')
        data['substitution_info'] = main_row.get('substitution', '')
    
    elif detected_type == 'Kick Off':
        period = main_row.get('period', 1)
        stage = detection_info.get('stage', '')
        
        if period == 1:
            phase = f'{stage} - First Half begins' if stage else 'First Half begins'
        elif period == 2:
            phase = 'Second Half begins'
        elif period == 3:
            phase = 'Extra Time First Half begins'
        elif period == 4:
            phase = 'Extra Time Second Half begins'
        elif period == 5:
            phase = 'Penalty Shootout begins'
        else:
            phase = 'Play resumes'
        
        data['phase'] = phase
        data['period'] = period
        data['stage'] = stage
    
    elif detected_type == 'Injury':
        data['injured_player'] = main_row.get('player_name', '')
        data['injured_team'] = main_row.get('team_name', '')
    
    return data


# =====================================
# MAIN FUNCTION
# =====================================

def main():
    global possession_history, last_event_type, consecutive_general_count
    global general_control_history, shootout_score, penalty_count
    
    print("=" * 60)
    print("LLM Commentary Test - V4")
    print("Penalty Handling (Period 1-4 + Period 5 Shootout)")
    print("=" * 60)
    
    # Test with Portugal vs France (has penalty shootout)
    match_id = 3942349  # Portugal vs France Quarter-final
    home_team = 'Portugal'
    away_team = 'France'
    stage = 'Quarter-finals'
    
    csv_file = PHASE7_DATA / f"match_{match_id}_rich_commentary.csv"
    
    print(f"\n[LOAD] Loading: {csv_file}")
    df = pd.read_csv(csv_file)
    print(f"[OK] Loaded {len(df)} events")
    
    # Load complete dataset for shot, goalkeeper columns
    print(f"\n[LOAD] Loading complete dataset...")
    try:
        complete_df = pd.read_csv(COMPLETE_DATA, low_memory=False)
        match_complete = complete_df[complete_df['match_id'] == match_id].copy().reset_index(drop=True)
        print(f"[OK] Loaded {len(match_complete)} events from complete dataset")
        
        if len(df) == len(match_complete):
            df['foul_committed'] = match_complete['foul_committed'].values
            df['bad_behaviour'] = match_complete['bad_behaviour'].values
            df['shot'] = match_complete['shot'].values
            df['goalkeeper'] = match_complete['goalkeeper'].values
            print(f"[OK] Merged foul_committed, bad_behaviour, shot, goalkeeper columns")
    except Exception as e:
        print(f"[WARN] Could not load complete dataset: {e}")
    
    # Check for Period 5
    periods = df['period'].unique()
    print(f"\n[INFO] Periods in match: {sorted(periods)}")
    if 5 in periods:
        print("[INFO] ⚽ PENALTY SHOOTOUT DETECTED (Period 5)")
    
    # Initialize GPT V4
    print(f"\n[GPT] Initializing GPT Commentator V4...")
    commentator = GPTCommentator()
    print(f"[OK] Model: {commentator.model}")
    
    # Reset trackers
    possession_history = {}
    last_event_type = None
    consecutive_general_count = 0
    general_control_history = []
    shootout_score = {'home': 0, 'away': 0}
    penalty_count = 0
    
    # Group by (minute, period)
    df['minute_period'] = df['minute'].astype(str) + '_' + df['period'].astype(str)
    all_minute_periods = df.groupby(['minute', 'period']).size().reset_index()[['minute', 'period']]
    all_minute_periods = all_minute_periods.sort_values(['period', 'minute']).reset_index(drop=True)
    
    print(f"\n[FULL MATCH] Generating commentary for {len(all_minute_periods)} minute-period combinations")
    
    results = []
    total_items = len(all_minute_periods)
    
    for idx, row in all_minute_periods.iterrows():
        minute = row['minute']
        period = row['period']
        
        minute_df = df[(df['minute'] == minute) & (df['period'] == period)].copy()
        
        # Base detection info
        base_detection_info = {
            'stage': stage,
            'period': period
        }
        
        # V4: Detect all events including penalties
        all_events = detect_all_important_events_v4(minute_df, base_detection_info, home_team, away_team)
        
        score_row = minute_df.iloc[-1]
        
        # Get scores (use portugal_score/france_score or home_score/away_score)
        home_score = score_row.get('portugal_score', score_row.get('home_score', 0))
        away_score = score_row.get('france_score', score_row.get('away_score', 0))
        
        for event_idx, (detected_type, main_row, extra_info) in enumerate(all_events):
            # Extract event data
            event_data = extract_event_specific_data_v4(
                detected_type, main_row, minute_df, extra_info, home_team, away_team
            )
            
            # Build context
            context = {
                'home_team': home_team,
                'away_team': away_team,
                'home_score': home_score,
                'away_score': away_score,
                'stage': stage,
                'period': period,
                'detected_type': detected_type,
                'event_data': event_data,
            }
            
            # Print progress
            period_label = f" (P{period})" if period >= 3 else ""
            print(f"\n[{idx+1}/{total_items}] Minute {minute}'{period_label}")
            print(f"  Event: [{detected_type}] {event_data.get('player', '')}")
            
            if period == 5:
                ss = event_data.get('shootout_score', {})
                print(f"  Shootout: {home_team} {ss.get('home', 0)} - {ss.get('away', 0)} {away_team}")
            
            # Generate LLM commentary
            llm_commentary = commentator.generate_minute_commentary(
                minute=int(minute),
                events_data=[],
                match_context=context
            )
            
            safe_commentary = llm_commentary[:80].encode('ascii', 'replace').decode('ascii')
            print(f"  LLM: {safe_commentary}...")
            
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
                'player': event_data.get('player', ''),
                'team': event_data.get('team', ''),
                'llm_commentary': llm_commentary,
                'is_penalty': 'Penalty' in detected_type,
                'is_shootout': period == 5,
                'penalty_number': event_data.get('penalty_number', 0),
                'model': commentator.model,
                'generated_at': datetime.now().isoformat(),
            }
            
            results.append(result)
    
    # Save to CSV
    results_df = pd.DataFrame(results)
    output_file = OUTPUT_DIR / f"match_{match_id}_V4_PENALTY_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    results_df.to_csv(output_file, index=False)
    
    print(f"\n{'=' * 60}")
    print(f"[DONE] Generated {len(results)} commentaries!")
    print(f"[SAVED] {output_file}")
    print(f"{'=' * 60}")
    
    # Summary
    print(f"\n[EVENT BREAKDOWN]")
    print(results_df['detected_type'].value_counts().to_string())
    
    # Penalty summary
    penalties = results_df[results_df['is_penalty'] == True]
    print(f"\n[PENALTIES]")
    print(f"  Total: {len(penalties)}")
    print(f"  Period 1-4: {len(penalties[penalties['is_shootout'] == False])}")
    print(f"  Shootout (P5): {len(penalties[penalties['is_shootout'] == True])}")


if __name__ == "__main__":
    main()

