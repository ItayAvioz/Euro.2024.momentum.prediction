"""
Test run for Spain vs England Final - V3

V3 ENHANCEMENTS:
- Progressive General events (1st basic, 2nd+ with domination streak)
- Multiple Shots (same team=pressure, different=end-to-end, most dangerous focus)
- Multiple Corners (count + same/different teams)
- Multiple Fouls (count context)
- Multiple Substitutions (double/triple)
- Multiple Offsides (same team vs wide-to-wide)
- xG extraction from shot column
- LLM has freedom of action

Key Logic:
- General: Check vs PREVIOUS minutes (domination)
- All others: Check within SAME minute
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

from gpt_commentator_v3 import GPTCommentator

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
possession_history = {}  # {(minute, period): {'dominant_team': 'Spain', 'pct': 65}}
last_event_type = None  # Track previous event type for consecutive generals
consecutive_general_count = 0  # Track consecutive general events
general_control_history = []  # Track control for consecutive generals (for same-team check)


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


def get_distance_description(distance_to_goal):
    """Convert distance to natural description."""
    if pd.isna(distance_to_goal):
        return None
    
    dist = float(distance_to_goal)
    
    if dist < 6:
        return "close range"
    elif dist < 12:
        return "inside the box"
    elif dist < 18:
        return "edge of the box"
    elif dist < 25:
        return "outside the box"
    else:
        return "long range"


def extract_xg_from_shot_column(shot_value):
    """
    Extract xG from the shot column.
    Shot column format: {'statsbomb_xg': 0.123, 'end_location': [...], ...}
    """
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


def extract_shot_outcome_from_column(shot_value):
    """Extract shot outcome from shot column (for penalty detection)."""
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


def check_for_penalty_in_minute(minute_df):
    """
    Check if there's a penalty in this minute (Period 1-4).
    
    Returns:
        dict with penalty info or None
    """
    # Check for shot with type='Penalty'
    shot_rows = minute_df[minute_df['event_type'] == 'Shot']
    for idx, row in shot_rows.iterrows():
        shot_data = row.get('shot', '')
        shot_type = extract_shot_type(shot_data)
        
        if shot_type == 'Penalty':
            outcome = extract_shot_outcome_from_column(shot_data) or row.get('shot_outcome', '')
            
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


def check_for_own_goal_in_minute(minute_df):
    """
    Check if there's an own goal in this minute.
    
    V6.2 FIX: Must match 'Own Goal Against' specifically (not 'Own Goal For').
    - 'Own Goal Against' has the player who scored in their own net
    - 'Own Goal For' has no player (just the team that received the goal)
    
    Returns:
        dict with own goal info or None
    """
    # V6.2 FIX: Match 'Own Goal Against' specifically to get the correct player
    og_rows = minute_df[
        minute_df['event_type'] == 'Own Goal Against'
    ]
    
    # Fallback to contains if exact match fails
    if len(og_rows) == 0:
        og_rows = minute_df[
            minute_df['event_type'].str.contains('Own Goal Against', case=False, na=False)
        ]
    
    if len(og_rows) > 0:
        row = og_rows.iloc[0]
        return {
            'has_own_goal': True,
            'player': row.get('player_name', ''),  # Player who scored own goal
            'team': row.get('team_name', ''),  # Team that conceded (scored against themselves)
            'row': row
        }
    
    return None


def get_foul_danger_context(location_x, location_y, is_danger_zone):
    """Get tactical context for fouls in dangerous areas."""
    if not is_danger_zone:
        return None
    
    if pd.isna(location_x) or pd.isna(location_y):
        return None
    
    x, y = float(location_x), float(location_y)
    is_wide = y < 25 or y > 55
    distance_from_goal = 120 - x
    
    if distance_from_goal < 20:
        if is_wide:
            return "good crossing position"
        else:
            return "dangerous free kick position"
    elif distance_from_goal < 30:
        if is_wide:
            return "free kick in a wide position"
        else:
            return "free kick on the edge of the box"
    
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


def validate_player_team(player, player_team, main_team, should_be_same_team):
    """Validate player attribution based on team."""
    if not player or pd.isna(player):
        return ''
    if not player_team or pd.isna(player_team):
        return ''
    if not main_team or pd.isna(main_team):
        return ''
    
    is_same_team = (str(player_team).strip() == str(main_team).strip())
    
    if should_be_same_team:
        return player if is_same_team else ''
    else:
        return player if not is_same_team else ''


# =====================================
# V3: MULTIPLE EVENTS DETECTION
# =====================================

def calculate_shot_danger_score(shot_info):
    """
    Calculate danger score for a shot.
    Higher = more dangerous.
    
    Formula: xG * 100 + (120 - distance) + outcome_bonus
    """
    score = 0
    
    # xG component (0-100)
    xg = shot_info.get('xg', 0)
    if xg and not pd.isna(xg):
        score += float(xg) * 100
    
    # Distance component (closer = higher)
    distance = shot_info.get('distance', 30)
    if distance and not pd.isna(distance):
        score += max(0, 120 - float(distance))
    
    # Outcome bonus
    outcome = shot_info.get('outcome', '')
    outcome_bonuses = {
        'Saved': 30,
        'Post': 25,
        'Blocked': 20,
        'Off T': 10,
        'Wayward': 5
    }
    for key, bonus in outcome_bonuses.items():
        if key in str(outcome):
            score += bonus
            break
    
    return score


def analyze_multiple_shots(minute_df):
    """
    Analyze multiple shots in the same minute.
    
    Returns:
        dict with has_multiple, count, scenario, shots_list, most_dangerous, team_counts
    """
    shot_rows = minute_df[minute_df['event_type'] == 'Shot'].copy()
    
    # Debug: Print shot count for verification
    shot_count = len(shot_rows)
    
    if shot_count < 2:
        return {'has_multiple': False, 'count': shot_count}
    
    # Build shots list with details
    shots_list = []
    for idx, row in shot_rows.iterrows():
        # Try to get xG from shot column (already merged into minute_df)
        xg = None
        if 'shot' in minute_df.columns:
            xg = extract_xg_from_shot_column(row.get('shot'))
        
        shot_info = {
            'player': row.get('player_name', ''),
            'team': row.get('team_name', ''),
            'outcome': row.get('shot_outcome', ''),
            'body_part': row.get('shot_body_part', ''),
            'location': get_location_description(row.get('location_x'), row.get('location_y')),
            'distance': row.get('distance_to_goal', 30),
            'xg': xg
        }
        shot_info['danger_score'] = calculate_shot_danger_score(shot_info)
        shots_list.append(shot_info)
    
    # Determine scenario
    teams = shot_rows['team_name'].unique()
    team_counts = shot_rows['team_name'].value_counts().to_dict()
    
    if len(teams) == 1:
        scenario = 'pressure'
    else:
        scenario = 'end_to_end'
    
    # Find most dangerous shot
    most_dangerous = max(shots_list, key=lambda x: x.get('danger_score', 0))
    
    return {
        'has_multiple': True,
        'count': len(shots_list),
        'scenario': scenario,
        'team_counts': team_counts,
        'shots_list': shots_list,
        'most_dangerous': most_dangerous
    }


def analyze_multiple_corners(minute_df):
    """Analyze multiple corners in the same minute."""
    corner_mask = minute_df['play_pattern'].str.contains('Corner', na=False)
    if 'pass_type' in minute_df.columns:
        corner_mask = corner_mask | minute_df['pass_type'].astype(str).str.contains('Corner', na=False)
    
    corner_rows = minute_df[corner_mask]
    
    if len(corner_rows) < 2:
        return {'has_multiple': False, 'count': len(corner_rows)}
    
    teams = corner_rows['team_name'].unique()
    team_counts = corner_rows['team_name'].value_counts().to_dict()
    
    if len(teams) == 1:
        scenario = 'pressure'
    else:
        scenario = 'open_game'
    
    return {
        'has_multiple': True,
        'count': len(corner_rows),
        'scenario': scenario,
        'team_counts': team_counts
    }


def analyze_multiple_fouls(minute_df):
    """Analyze multiple fouls in the same minute."""
    foul_rows = minute_df[minute_df['event_type'].isin(['Foul Committed', 'Foul Won'])]
    
    # Count unique foul incidents (Foul Committed + Foul Won = 1 incident)
    foul_committed = minute_df[minute_df['event_type'] == 'Foul Committed']
    foul_count = len(foul_committed)
    
    if foul_count < 3:
        return {'has_multiple': False, 'count': foul_count}
    
    return {
        'has_multiple': True,
        'count': foul_count
    }


def analyze_multiple_substitutions(minute_df):
    """Analyze multiple substitutions in the same minute."""
    import ast
    
    sub_rows = minute_df[minute_df['event_type'] == 'Substitution']
    
    if len(sub_rows) < 2:
        return {'has_multiple': False, 'count': len(sub_rows)}
    
    team_counts = sub_rows['team_name'].value_counts().to_dict()
    
    # Get players OFF and ON by team
    players_off_by_team = {}
    players_on_by_team = {}
    
    for team in team_counts:
        team_subs = sub_rows[sub_rows['team_name'] == team]
        players_off_by_team[team] = team_subs['player_name'].tolist()
        
        # FIX ISSUE 2: Extract replacement players from 'substitution' column
        replacements = []
        for _, row in team_subs.iterrows():
            sub_info = row.get('substitution', '')
            if pd.notna(sub_info) and sub_info:
                try:
                    # Parse the substitution dict string
                    if isinstance(sub_info, str):
                        sub_dict = ast.literal_eval(sub_info)
                    else:
                        sub_dict = sub_info
                    
                    if isinstance(sub_dict, dict) and 'replacement' in sub_dict:
                        replacement_name = sub_dict['replacement'].get('name', '')
                        if replacement_name:
                            replacements.append(replacement_name)
                except:
                    pass
        
        players_on_by_team[team] = replacements
    
    return {
        'has_multiple': True,
        'count': len(sub_rows),
        'team_counts': team_counts,
        'players_by_team': players_off_by_team,  # Backwards compatible (players OFF)
        'players_off_by_team': players_off_by_team,
        'players_on_by_team': players_on_by_team
    }


def analyze_multiple_offsides(minute_df):
    """Analyze multiple offsides in the same minute."""
    # Offsides are in pass_outcome or as separate events
    offside_mask = minute_df['event_type'] == 'Offside'
    if 'pass_outcome' in minute_df.columns:
        offside_mask = offside_mask | (minute_df['pass_outcome'] == 'Offside')
    
    offside_rows = minute_df[offside_mask]
    
    if len(offside_rows) < 2:
        return {'has_multiple': False, 'count': len(offside_rows)}
    
    teams = offside_rows['team_name'].dropna().unique()
    team_counts = offside_rows['team_name'].value_counts().to_dict()
    
    if len(teams) == 1:
        scenario = 'timing_issues'
    else:
        scenario = 'end_to_end'  # Both teams pushing forward = wide-to-wide
    
    return {
        'has_multiple': True,
        'count': len(offside_rows),
        'scenario': scenario,
        'team_counts': team_counts
    }


# =====================================
# V3: DOMINATION TRACKING
# =====================================

def get_dominant_team_for_minute(minute_df):
    """Calculate which team dominated possession this minute."""
    if 'possession_team' not in minute_df.columns:
        return None
    
    possession_counts = minute_df['possession_team'].value_counts()
    total_events = len(minute_df)
    
    if total_events == 0:
        return None
    
    dominant_team = possession_counts.index[0]
    dominant_count = possession_counts.iloc[0]
    pct = (dominant_count / total_events) * 100
    
    if pct > 55:
        return {
            'dominant_team': dominant_team,
            'pct': round(pct, 1)
        }
    
    return None


def check_domination_for_consecutive_generals(consecutive_count, current_control, control_history):
    """
    Check domination for consecutive General events.
    
    Logic:
    - Only applies to General events
    - Streak counts only if SAME team is in control
    - Resets if team changes or non-General event
    
    Args:
        consecutive_count: Number of consecutive General events (1, 2, 3, ...)
        current_control: Who's in control this minute (e.g., "Spain in control")
        control_history: List of control strings for consecutive generals
    
    Returns dict with has_domination, team, streak
    """
    if consecutive_count < 2 or not current_control:
        return {'has_domination': False}
    
    # Extract current team from control string
    current_team = current_control.split()[0] if current_control else ''
    if not current_team:
        return {'has_domination': False}
    
    # Check if same team has been in control for all consecutive generals
    same_team_streak = 0
    for ctrl in reversed(control_history):
        if ctrl and ctrl.split()[0] == current_team:
            same_team_streak += 1
        else:
            break  # Different team, stop counting
    
    if same_team_streak >= 2:
        return {
            'has_domination': True,
            'team': current_team,
            'streak': same_team_streak
        }
    
    return {'has_domination': False}


def get_most_active_player(minute_df):
    """Find the player with most events this minute."""
    if 'player_name' not in minute_df.columns:
        return None
    
    player_counts = minute_df['player_name'].dropna().value_counts()
    
    if len(player_counts) == 0:
        return None
    
    top_player = player_counts.index[0]
    count = player_counts.iloc[0]
    
    player_rows = minute_df[minute_df['player_name'] == top_player]
    team = player_rows['team_name'].iloc[0] if len(player_rows) > 0 else ''
    
    if count >= 5:
        return {
            'player': top_player,
            'team': team,
            'count': int(count)
        }
    
    return None


# =====================================
# EVENT DETECTION (from v2, with enhancements)
# =====================================

def detect_all_important_events(minute_df, detection_info):
    """Detect ALL important events that need separate commentary."""
    events = []
    used_indices = set()
    
    # 1. HALF START
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
    
    # 2. PENALTIES (Period 1-4) - TWO commentaries: Awarded + Result
    penalty_info = check_for_penalty_in_minute(minute_df)
    if penalty_info:
        penalty_row = penalty_info['row']
        
        # 2a. PENALTY AWARDED - Find the foul that led to penalty
        foul_won_rows = minute_df[minute_df['event_type'] == 'Foul Won']
        foul_committed_rows = minute_df[minute_df['event_type'] == 'Foul Committed']
        
        fouled_player = penalty_info.get('player', '')
        fouled_team = penalty_info.get('team', '')
        fouler = ''
        fouler_team = ''
        
        # Find foul in the box
        for _, foul_row in foul_committed_rows.iterrows():
            loc_x = foul_row.get('location_x', 0)
            if pd.notna(loc_x) and float(loc_x) > 102:  # In penalty area
                fouler = foul_row.get('player_name', '')
                fouler_team = foul_row.get('team_name', '')
                break
        
        if not fouler and len(foul_committed_rows) > 0:
            # Use last foul committed
            last_foul = foul_committed_rows.iloc[-1]
            fouler = last_foul.get('player_name', '')
            fouler_team = last_foul.get('team_name', '')
        
        awarded_info = {
            'team': penalty_info.get('team', ''),
            'fouled_player': fouled_player,
            'fouled_team': fouled_team,
            'fouler': fouler,
            'fouler_team': fouler_team,
            'location': 'in the box'
        }
        events.append(('Penalty Awarded', penalty_row, awarded_info))
        
        # 2b. PENALTY RESULT
        outcome = penalty_info.get('outcome', '')
        if outcome == 'Goal':
            event_type = 'Penalty Goal'
        elif outcome == 'Saved':
            event_type = 'Penalty Saved'
        else:
            event_type = 'Penalty Missed'
        
        result_info = {
            'penalty_info': penalty_info,
            'player': penalty_info.get('player', ''),
            'team': penalty_info.get('team', ''),
            'outcome': outcome,
            'goalkeeper': penalty_info.get('goalkeeper', ''),
            'goalkeeper_team': penalty_info.get('goalkeeper_team', '')
        }
        events.append((event_type, penalty_row, result_info))
        used_indices.add(penalty_row.name)
    
    # 3. OWN GOALS
    own_goal_info = check_for_own_goal_in_minute(minute_df)
    if own_goal_info:
        og_row = own_goal_info['row']
        if og_row.name not in used_indices:
            info = {
                'own_goal_info': own_goal_info,
                'scorer': own_goal_info.get('player', ''),
                'scoring_team': own_goal_info.get('team', '')
            }
            events.append(('Own Goal', og_row, info))
            used_indices.add(og_row.name)
    
    # 4. REGULAR GOALS (non-penalty, non-own-goal)
    goal_rows = minute_df[minute_df['shot_outcome'] == 'Goal']
    if len(goal_rows) == 0 and 'is_goal' in minute_df.columns:
        goal_rows = minute_df[minute_df['is_goal'] == True]
    
    for _, row in goal_rows.iterrows():
        if row.name not in used_indices:
            # Check it's not a penalty goal (already handled)
            shot_data = row.get('shot', '')
            shot_type = extract_shot_type(shot_data)
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
                closest_won = None
                min_dist = float('inf')
                for won_idx, won_row in foul_won_rows.iterrows():
                    dist = abs(won_idx - idx)
                    if dist < min_dist:
                        min_dist = dist
                        closest_won = won_row
                if closest_won is not None:
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
    
    # 8. If NO important events, detect main event
    if len(events) == 0:
        main_type, main_row, info = detect_main_event(minute_df)
        events.append((main_type, main_row, info))
    
    return events


def detect_main_event(minute_df):
    """Enhanced detection using multiple columns."""
    detection_info = {}
    
    # Check play patterns
    play_patterns = minute_df['play_pattern'].dropna().unique().tolist()
    detection_info['play_patterns'] = play_patterns
    
    has_corner_pattern = any('Corner' in str(p) for p in play_patterns)
    has_corner_pass_type = False
    if 'pass_type' in minute_df.columns:
        pass_types = minute_df['pass_type'].dropna().astype(str).tolist()
        has_corner_pass_type = any('Corner' in str(pt) for pt in pass_types)
    
    has_corner = has_corner_pattern or has_corner_pass_type
    has_free_kick = any('Free Kick' in str(p) for p in play_patterns)
    
    # Check for goals
    has_goal = minute_df['is_goal'].any() if 'is_goal' in minute_df.columns else False
    goal_rows = minute_df[minute_df['shot_outcome'] == 'Goal'] if 'shot_outcome' in minute_df.columns else pd.DataFrame()
    detection_info['has_goal'] = has_goal or len(goal_rows) > 0
    
    # Check for shots
    shot_rows = minute_df[minute_df['event_type'] == 'Shot']
    detection_info['has_shot'] = len(shot_rows) > 0
    
    # Check for cards
    card_rows = minute_df[minute_df['event_type'].isin(['Yellow Card', 'Red Card'])]
    detection_info['has_card'] = len(card_rows) > 0
    
    # Check for fouls
    foul_rows = minute_df[minute_df['event_type'].isin(['Foul Committed', 'Foul Won'])]
    detection_info['has_foul'] = len(foul_rows) > 0
    
    # Check danger zone
    danger_rows = minute_df[minute_df['is_danger_zone'] == True] if 'is_danger_zone' in minute_df.columns else pd.DataFrame()
    detection_info['has_danger_zone'] = len(danger_rows) > 0
    
    # Check substitutions
    sub_rows = minute_df[minute_df['event_type'] == 'Substitution']
    detection_info['has_substitution'] = len(sub_rows) > 0
    
    # Check Half Start
    half_start = minute_df[minute_df['event_type'] == 'Half Start']
    detection_info['has_half_start'] = len(half_start) > 0
    
    # Check Injury
    injury_rows = minute_df[minute_df['event_type'] == 'Injury Stoppage']
    detection_info['has_injury'] = len(injury_rows) > 0
    
    # PRIORITY-BASED DETECTION
    
    if detection_info['has_half_start']:
        main_row = half_start.iloc[0]
        period = main_row.get('period', 1)
        detection_info['period'] = period
        return 'Kick Off', main_row, detection_info
    
    # Check for PENALTY first (before regular goal check)
    penalty_info = check_for_penalty_in_minute(minute_df)
    if penalty_info:
        main_row = penalty_info['row']
        outcome = penalty_info.get('outcome', '')
        detection_info['penalty_info'] = penalty_info
        
        if outcome == 'Goal':
            return 'Penalty Goal', main_row, detection_info
        elif outcome == 'Saved':
            return 'Penalty Saved', main_row, detection_info
        elif outcome in ['Post', 'Off T', 'Wayward']:
            return 'Penalty Missed', main_row, detection_info
        else:
            return 'Penalty Goal', main_row, detection_info  # Default to goal if unclear
    
    # Check for OWN GOAL (before regular goal check)
    own_goal_info = check_for_own_goal_in_minute(minute_df)
    if own_goal_info:
        main_row = own_goal_info['row']
        detection_info['own_goal_info'] = own_goal_info
        return 'Own Goal', main_row, detection_info
    
    if detection_info['has_goal']:
        main_row = goal_rows.iloc[-1] if len(goal_rows) > 0 else minute_df[minute_df['is_goal'] == True].iloc[-1]
        return 'Goal', main_row, detection_info
    
    if detection_info['has_card']:
        main_row = card_rows.iloc[-1]
        return main_row['event_type'], main_row, detection_info
    
    if detection_info['has_shot']:
        main_row = shot_rows.iloc[-1]
        outcome = main_row.get('shot_outcome', '')
        return f"Shot ({outcome})" if outcome else "Shot", main_row, detection_info
    
    if detection_info['has_substitution']:
        main_row = sub_rows.iloc[-1]
        return 'Substitution', main_row, detection_info
    
    if has_corner:
        corner_rows = minute_df[minute_df['play_pattern'].str.contains('Corner', na=False)]
        if len(corner_rows) == 0 and 'pass_type' in minute_df.columns:
            corner_rows = minute_df[minute_df['pass_type'].astype(str).str.contains('Corner', na=False)]
        main_row = corner_rows.iloc[0] if len(corner_rows) > 0 else minute_df.iloc[-1]
        return 'Corner', main_row, detection_info
    
    if has_free_kick:
        fk_rows = minute_df[minute_df['play_pattern'].str.contains('Free Kick', na=False)]
        main_row = fk_rows.iloc[0] if len(fk_rows) > 0 else minute_df.iloc[-1]
        return 'Free Kick', main_row, detection_info
    
    if detection_info['has_foul']:
        main_row = foul_rows.iloc[-1]
        return 'Foul', main_row, detection_info
    
    if detection_info['has_injury']:
        main_row = injury_rows.iloc[-1]
        return 'Injury', main_row, detection_info
    
    # Default: General
    interesting_row = minute_df.iloc[-1]
    
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
    
    return 'General', interesting_row, detection_info


def extract_event_specific_data(detected_type, main_row, minute_df, detection_info):
    """Extract ALL relevant data for the detected event type."""
    data = {}
    
    data['player'] = main_row.get('player_name', '')
    data['team'] = main_row.get('team_name', '')
    data['location'] = get_location_description(
        main_row.get('location_x'), 
        main_row.get('location_y')
    )
    data['distance'] = get_distance_description(main_row.get('distance_to_goal'))
    
    if detected_type == 'Goal':
        data['scorer'] = main_row.get('player_name', '')
        data['body_part'] = main_row.get('shot_body_part', '')
        
        # Assist logic
        scorer = data['scorer']
        scorer_team = main_row.get('team_name', '')
        data['assisted_by'] = ''
        
        shot_rows = minute_df[minute_df['event_type'] == 'Shot']
        if len(shot_rows) > 0:
            shot_idx = shot_rows.index[-1]
            shot_row_position = minute_df.index.get_loc(shot_idx)
            start_pos = max(0, shot_row_position - 7)
            events_before_shot = minute_df.iloc[start_pos:shot_row_position]
            
            scorer_carries = events_before_shot[
                (events_before_shot['event_type'] == 'Carry') & 
                (events_before_shot['player_name'] == scorer)
            ]
            
            total_carry_distance = 0
            if len(scorer_carries) > 0 and 'carry_distance' in scorer_carries.columns:
                for _, carry in scorer_carries.iterrows():
                    dist = carry.get('carry_distance', 0)
                    if pd.notna(dist):
                        total_carry_distance += float(dist)
            
            if total_carry_distance <= 5.5:
                pass_events = events_before_shot[events_before_shot['event_type'] == 'Pass']
                for _, pass_row in pass_events.iloc[::-1].iterrows():
                    passer = pass_row.get('player_name', '')
                    passer_team = pass_row.get('team_name', '')
                    
                    if passer and passer != scorer:
                        validated_passer = validate_player_team(passer, passer_team, scorer_team, should_be_same_team=True)
                        if validated_passer:
                            recipient = pass_row.get('pass_recipient', '')
                            if recipient == scorer or not recipient:
                                data['assisted_by'] = validated_passer
                                break
    
    elif detected_type == 'Penalty Goal':
        data['outcome'] = 'Goal'
        data['body_part'] = main_row.get('shot_body_part', '')
        data['is_penalty'] = True
        penalty_info = detection_info.get('penalty_info', {})
        data['goalkeeper'] = penalty_info.get('goalkeeper', '')
    
    elif detected_type == 'Penalty Saved':
        data['outcome'] = 'Saved'
        data['is_penalty'] = True
        penalty_info = detection_info.get('penalty_info', {})
        data['saved_by'] = penalty_info.get('goalkeeper', '')
    
    elif detected_type == 'Penalty Missed':
        data['outcome'] = 'Missed'
        data['is_penalty'] = True
        penalty_info = detection_info.get('penalty_info', {})
        data['goalkeeper'] = penalty_info.get('goalkeeper', '')
    
    elif detected_type == 'Own Goal':
        own_goal_info = detection_info.get('own_goal_info', {})
        data['is_own_goal'] = True
        data['scorer'] = own_goal_info.get('player', main_row.get('player_name', ''))
        data['scoring_team'] = own_goal_info.get('team', main_row.get('team_name', ''))
    
    elif 'Shot' in detected_type:
        data['outcome'] = main_row.get('shot_outcome', '')
        data['body_part'] = main_row.get('shot_body_part', '')
        
        shooter_team = main_row.get('team_name', '')
        
        if main_row.get('shot_outcome') == 'Saved':
            gk_events = minute_df[minute_df['event_type'] == 'Goal Keeper']
            if len(gk_events) > 0:
                gk_row = gk_events.iloc[0]
                gk_player = gk_row.get('player_name', '')
                gk_team = gk_row.get('team_name', '')
                data['saved_by'] = validate_player_team(gk_player, gk_team, shooter_team, should_be_same_team=False)
        
        elif main_row.get('shot_outcome') == 'Blocked':
            next_player = main_row.get('next_player', '')
            next_team = main_row.get('next_team', '')
            data['blocked_by'] = validate_player_team(next_player, next_team, shooter_team, should_be_same_team=False)
    
    elif detected_type == 'Corner':
        data['delivered_by'] = main_row.get('player_name', '')
        corner_team = main_row.get('team_name', '')
        prev_player = main_row.get('previous_player', '')
        prev_team = main_row.get('previous_team', '')
        data['conceded_by'] = validate_player_team(prev_player, prev_team, corner_team, should_be_same_team=False)
    
    elif detected_type == 'Free Kick':
        foul_won_rows = minute_df[minute_df['event_type'] == 'Foul Won']
        foul_committed_rows = minute_df[minute_df['event_type'] == 'Foul Committed']
        
        if len(foul_won_rows) > 0:
            won_row = foul_won_rows.iloc[-1]
            data['fouled_player'] = won_row.get('player_name', '')
            data['fouled_team'] = won_row.get('team_name', '')
            
            if len(foul_committed_rows) > 0:
                won_team = data['fouled_team']
                opposite_fouls = foul_committed_rows[foul_committed_rows['team_name'] != won_team]
                if len(opposite_fouls) > 0:
                    comm_row = opposite_fouls.iloc[-1]
                    data['foul_committed_by'] = comm_row.get('player_name', '')
                    data['foul_committed_team'] = comm_row.get('team_name', '')
    
    elif detected_type == 'Foul':
        foul_won_rows = minute_df[minute_df['event_type'] == 'Foul Won']
        foul_committed_rows = minute_df[minute_df['event_type'] == 'Foul Committed']
        
        if len(foul_committed_rows) > 0:
            comm_row = foul_committed_rows.iloc[-1]
            data['committed_by'] = comm_row.get('player_name', '')
            data['committed_team'] = comm_row.get('team_name', '')
            
            if len(foul_won_rows) > 0:
                comm_team = data['committed_team']
                opposite_won = foul_won_rows[foul_won_rows['team_name'] != comm_team]
                if len(opposite_won) > 0:
                    won_row = opposite_won.iloc[-1]
                    data['fouled_player'] = won_row.get('player_name', '')
                    data['fouled_team'] = won_row.get('team_name', '')
    
    elif detected_type in ['Yellow Card', 'Red Card']:
        data['carded_player'] = main_row.get('player_name', '')
        data['carded_team'] = main_row.get('team_name', '')
    
    elif detected_type == 'Substitution':
        data['player_off'] = main_row.get('player_name', '')
        data['substitution_info'] = main_row.get('substitution', '')
    
    elif detected_type == 'Kick Off':
        period = main_row.get('period', 1)
        stage = detection_info.get('stage', '')
        
        if period == 1:
            phase = f'{stage} MATCH - First Half begins' if stage else 'First Half begins'
        elif period == 2:
            phase = 'Second Half begins'
        elif period == 3:
            phase = 'Extra Time First Half begins'
        elif period == 4:
            phase = 'Extra Time Second Half begins'
        else:
            phase = 'Play resumes'
        
        data['phase'] = phase
        data['period'] = period
        data['stage'] = stage
    
    elif detected_type == 'Injury':
        data['injured_player'] = main_row.get('player_name', '')
        data['injured_team'] = main_row.get('team_name', '')
    
    return data


def detect_event_chain(minute_df, detected_type, main_row, detection_info):
    """
    Detect related events that form a DIRECT chain for the MAIN event only.
    
    V6.1 Logic: Look back 7 events and detect CHANGES in play_pattern.
    - If play_pattern changes from something else to "From Corner" → DIRECT chain
    - If no change (same pattern continues from event -8) → NOT relevant
    
    Chains detected:
    1. Corner → Shot/Goal (play_pattern changed to 'From Corner' in last 7)
    2. Free Kick → Shot/Goal (play_pattern changed to 'From Free Kick' in last 7)
    3. Dribble → Shot (same player Carry in last 7 events)
    4. Blocked Shot → Corner (Shot with Blocked/Saved outcome before corner)
    
    Note: Assist detection handled separately by extract_event_specific_data()
    """
    chain = {'has_chain': False, 'origin': '', 'related_events': []}
    
    player = main_row.get('player_name', '')
    main_idx = main_row.name if hasattr(main_row, 'name') else None
    
    if main_idx is None:
        return chain
    
    try:
        main_pos = minute_df.index.get_loc(main_idx)
    except:
        return chain
    
    # Get events before main event (up to 8 for change detection)
    events_before = minute_df.iloc[max(0, main_pos-8):main_pos]
    
    # For Shot/Goal: Check play_pattern changes in last 7 events
    if detected_type == 'Goal' or 'Shot' in detected_type:
        
        if len(events_before) >= 2:
            # Get last 7 events (or fewer if not enough)
            last_7 = events_before.tail(7)
            
            # Check for "From Corner" in last 7 play_patterns
            corner_in_7 = last_7[last_7['play_pattern'] == 'From Corner']
            if len(corner_in_7) > 0:
                # Check if event -8 has DIFFERENT play_pattern (change detected)
                if len(events_before) >= 8:
                    event_8 = events_before.iloc[0]
                    if event_8['play_pattern'] != 'From Corner':
                        # Change detected! Corner started in our window
                        # Count passes between corner start and goal to determine direct/indirect
                        passes_in_chain = last_7[last_7['event_type'] == 'Pass']
                        if len(passes_in_chain) > 1:
                            # Indirect: goal after several passes from corner situation
                            chain['origin'] = 'From Corner (indirect)'
                        else:
                            # Direct: goal directly from corner (header/shot from delivery)
                            chain['origin'] = 'From Corner (direct)'
                chain['has_chain'] = True
                # If less than 8 events, not relevant (corner started before)
            
            # Check for "From Free Kick" in last 7 play_patterns
            if not chain['origin']:
                fk_in_7 = last_7[last_7['play_pattern'] == 'From Free Kick']
                if len(fk_in_7) > 0:
                    # Check if event -8 has DIFFERENT play_pattern
                    if len(events_before) >= 8:
                        event_8 = events_before.iloc[0]
                        if event_8['play_pattern'] != 'From Free Kick':
                            # Change detected! Free kick started in our window
                            # Count passes between free kick start and goal
                            passes_in_chain = last_7[last_7['event_type'] == 'Pass']
                            if len(passes_in_chain) > 1:
                                # Indirect: goal after several passes from free kick
                                chain['origin'] = 'From Free Kick (indirect)'
                            else:
                                # Direct: goal directly from free kick
                                chain['origin'] = 'From Free Kick (direct)'
                            chain['has_chain'] = True
                    # If less than 8 events, not relevant
            
            # Check for Dribble (Carry by same player in last 7)
            if not chain['origin'] and player:
                carries = last_7[
                    (last_7['event_type'] == 'Carry') & 
                    (last_7['player_name'] == player)
                ]
                if len(carries) > 0:
                    chain['origin'] = 'After Dribble'
                    chain['has_chain'] = True
    
    # For Corner: Check for blocked/saved shot before
    # Main event is first event with play_pattern="From Corner" in minute
    main_play_pattern = str(main_row.get('play_pattern', ''))
    if 'Corner' in main_play_pattern and main_pos > 0:
        # Look for Shot with Blocked/Saved outcome in last 7 events
        last_7 = events_before.tail(7)
        shot_events = last_7[last_7['event_type'] == 'Shot']
        if len(shot_events) > 0:
            last_shot = shot_events.iloc[-1]
            outcome = str(last_shot.get('shot_outcome', ''))
            if outcome in ['Blocked', 'Saved']:
                chain['origin'] = f'After {outcome} Shot'
                chain['has_chain'] = True
                blocker = last_shot.get('shot_blocked_by', '')
                if blocker:
                    chain['related_events'].append({
                        'type': 'Blocked By', 
                        'player': blocker
                    })
    
    # Note: Assist detection removed from chain - handled by extract_event_specific_data() 
    # which already looks back 7 events and populates event_data['assisted_by']
    
    return chain


def analyze_event_sequence(minute_df):
    """
    V6: Analyze event sequences in same minute.
    
    Detects related events that form a sequence based on:
    1. play_pattern column (e.g., 'From Corner', 'From Free Kick')
    2. Time proximity (same minute)
    3. Team relationship
    
    Supported sequences:
    - Corner → Shot (shot.play_pattern contains 'Corner')
    - Free Kick → Shot/Goal (shot.play_pattern contains 'Free Kick')
    - Dribble → Shot (carry followed by shot by same player)
    - Shot (Blocked/Saved) → Corner (corner after shot)
    
    Returns: {
        'has_sequence': bool,
        'sequence_type': str,
        'sequence_text': str,  # For LLM prompt
        'events': list
    }
    """
    result = {'has_sequence': False, 'sequence_type': '', 'sequence_text': '', 'events': []}
    
    if minute_df.empty:
        return result
    
    # Sort by second if available
    if 'second' in minute_df.columns:
        minute_df = minute_df.sort_values('second')
    
    # Get shots and their play patterns
    shot_rows = minute_df[minute_df['event_type'] == 'Shot']
    corner_rows = minute_df[minute_df['event_type'].str.contains('Corner', case=False, na=False) | 
                            minute_df['play_pattern'].str.contains('Corner', case=False, na=False)]
    goal_rows = minute_df[minute_df['is_goal'] == True] if 'is_goal' in minute_df.columns else pd.DataFrame()
    carry_rows = minute_df[minute_df['event_type'] == 'Carry']
    
    sequences = []
    
    # 1. Corner → Shot sequence
    for _, shot in shot_rows.iterrows():
        play_pattern = str(shot.get('play_pattern', ''))
        if 'Corner' in play_pattern:
            player = shot.get('player_name', '')
            team = shot.get('team_name', '')
            outcome = shot.get('shot_outcome', 'Unknown')
            sequences.append({
                'type': 'Corner Attack',
                'text': f"Corner → Shot ({player}, {outcome})",
                'events': ['Corner', 'Shot']
            })
    
    # 2. Free Kick → Shot/Goal sequence
    for _, shot in shot_rows.iterrows():
        play_pattern = str(shot.get('play_pattern', ''))
        if 'Free Kick' in play_pattern:
            player = shot.get('player_name', '')
            team = shot.get('team_name', '')
            is_goal = shot.get('is_goal', False) or shot.get('shot_outcome') == 'Goal'
            if is_goal:
                sequences.append({
                    'type': 'Free Kick Goal',
                    'text': f"Free Kick → GOAL ({player})",
                    'events': ['Free Kick', 'Goal']
                })
            else:
                outcome = shot.get('shot_outcome', 'Unknown')
                sequences.append({
                    'type': 'Free Kick Attack',
                    'text': f"Free Kick → Shot ({player}, {outcome})",
                    'events': ['Free Kick', 'Shot']
                })
    
    # 3. Dribble → Shot sequence (same player carries then shoots)
    for _, shot in shot_rows.iterrows():
        shot_player = shot.get('player_name', '')
        shot_second = shot.get('second', 999)
        
        # Check if same player had a carry event before this shot
        for _, carry in carry_rows.iterrows():
            carry_player = carry.get('player_name', '')
            carry_second = carry.get('second', 0)
            
            if carry_player == shot_player and carry_second < shot_second:
                outcome = shot.get('shot_outcome', 'Unknown')
                sequences.append({
                    'type': 'Dribble Attack',
                    'text': f"Dribble → Shot ({shot_player}, {outcome})",
                    'events': ['Dribble', 'Shot']
                })
                break  # One dribble->shot per shot
    
    # 4. Shot (Blocked/Saved) → Corner sequence
    for _, shot in shot_rows.iterrows():
        shot_outcome = str(shot.get('shot_outcome', ''))
        shot_team = shot.get('team_name', '')
        shot_second = shot.get('second', 0)
        
        if shot_outcome in ['Blocked', 'Saved']:
            # Check if corner for same team after this shot
            for _, corner in corner_rows.iterrows():
                corner_team = corner.get('team_name', corner.get('possession_team', ''))
                corner_second = corner.get('second', 999)
                
                if corner_team == shot_team and corner_second > shot_second:
                    blocker = shot.get('shot_blocked_by', '')
                    sequences.append({
                        'type': 'Shot to Corner',
                        'text': f"Shot ({shot_outcome}) → Corner ({shot_team})",
                        'events': ['Shot', 'Corner']
                    })
                    break
    
    # Return the most significant sequence (prioritize goals)
    if sequences:
        # Priority: Goal sequences first, then attacks
        goal_seqs = [s for s in sequences if 'Goal' in s['type']]
        if goal_seqs:
            best = goal_seqs[0]
        else:
            best = sequences[0]
        
        result['has_sequence'] = True
        result['sequence_type'] = best['type']
        result['sequence_text'] = best['text']
        result['events'] = best['events']
    
    return result


def main():
    global possession_history, last_event_type, consecutive_general_count, general_control_history
    
    print("=" * 60)
    print("LLM Commentary Test - V3 FINAL")
    print("Progressive General + Multi-Events + LLM Freedom")
    print("=" * 60)
    
    # Load match data
    match_id = 3943043
    csv_file = PHASE7_DATA / f"match_{match_id}_rich_commentary.csv"
    
    print(f"\n[LOAD] Loading: {csv_file}")
    df = pd.read_csv(csv_file)
    print(f"[OK] Loaded {len(df)} events")
    
    # Load complete dataset for xG and card columns
    complete_df = None
    print(f"\n[LOAD] Loading complete dataset...")
    try:
        complete_df = pd.read_csv(COMPLETE_DATA, low_memory=False)
        match_complete = complete_df[complete_df['match_id'] == match_id].copy().reset_index(drop=True)
        print(f"[OK] Loaded {len(match_complete)} events from complete dataset")
        
        if len(df) == len(match_complete):
            df['foul_committed'] = match_complete['foul_committed'].values
            df['bad_behaviour'] = match_complete['bad_behaviour'].values
            df['shot'] = match_complete['shot'].values
            print(f"[OK] Merged foul_committed, bad_behaviour, shot columns")
    except Exception as e:
        print(f"[WARN] Could not load complete dataset: {e}")
        match_complete = None
    
    # Initialize GPT V3
    print(f"\n[GPT] Initializing GPT Commentator V3...")
    commentator = GPTCommentator()
    print(f"[OK] Model: {commentator.model}")
    
    # Reset trackers
    possession_history = {}
    last_event_type = None
    consecutive_general_count = 0
    general_control_history = []
    
    # Group by (minute, period)
    df['minute_period'] = df['minute'].astype(str) + '_' + df['period'].astype(str)
    all_minute_periods = df.groupby(['minute', 'period']).size().reset_index()[['minute', 'period']]
    all_minute_periods = all_minute_periods.sort_values(['period', 'minute']).reset_index(drop=True)
    
    print(f"\n[FULL MATCH] Generating commentary for {len(all_minute_periods)} minute-period combinations")
    
    results = []
    total_items = len(all_minute_periods)
    event_counter = 0
    
    for idx, row in all_minute_periods.iterrows():
        minute = row['minute']
        period = row['period']
        
        minute_df = df[(df['minute'] == minute) & (df['period'] == period)].copy()
        
        # Track possession for domination
        dom_info = get_dominant_team_for_minute(minute_df)
        possession_history[(minute, period)] = dom_info
        
        # V3 FIX: Domination is now calculated per-event for consecutive General events only
        # (see inside the loop below)
        
        # Get most active player
        most_active = get_most_active_player(minute_df)
        
        # V3: Analyze multiple events in SAME minute
        multi_shots_info = analyze_multiple_shots(minute_df)
        multi_corners_info = analyze_multiple_corners(minute_df)
        multi_fouls_info = analyze_multiple_fouls(minute_df)
        multi_subs_info = analyze_multiple_substitutions(minute_df)
        multi_offsides_info = analyze_multiple_offsides(minute_df)
        
        # Base detection info
        base_detection_info = {
            'stage': 'Final',
            'full_df': df,
            'period': period
        }
        
        # Detect all important events
        all_events = detect_all_important_events(minute_df, base_detection_info)
        
        # V3 FIX: If multiple shots detected and main event is a shot, override to multi-shot
        if multi_shots_info.get('has_multiple') and len(all_events) == 1:
            detected_type, main_row, extra_info = all_events[0]
            if 'Shot' in detected_type and detected_type != 'Goal':
                # Change to multi-shot event type
                scenario = multi_shots_info.get('scenario', 'pressure')
                new_type = f"Shots ({scenario.title()})"
                all_events = [(new_type, main_row, extra_info)]
        
        # Summaries
        event_counts = minute_df['event_type'].value_counts().head(5).to_dict()
        event_summary = ', '.join([f"{k}({v})" for k, v in event_counts.items()])
        pattern_counts = minute_df['play_pattern'].value_counts().to_dict()
        pattern_summary = ', '.join([f"{k}({v})" for k, v in pattern_counts.items() if pd.notna(k)])
        
        score_row = minute_df.iloc[-1]
        
        progress_pct = (idx + 1) / total_items * 100
        period_label = f" (P{period})" if minute == 45 else ""
        
        for event_idx, (detected_type, main_row, extra_info) in enumerate(all_events):
            event_counter += 1
            
            # Get current control for this minute (needed for General tracking)
            current_control = ''
            if 'possession_team' in minute_df.columns:
                possession_counts = minute_df['possession_team'].value_counts()
                if len(possession_counts) > 0:
                    dominant_team = possession_counts.index[0]
                    dominant_pct = (possession_counts.iloc[0] / len(minute_df)) * 100
                    if dominant_pct > 55:
                        current_control = f"{dominant_team} in control"
            
            # V3: Track consecutive generals with control history
            if detected_type == 'General':
                if last_event_type == 'General':
                    consecutive_general_count += 1
                else:
                    consecutive_general_count = 1
                    general_control_history = []  # Reset history on new streak
                # Add current control to history
                general_control_history.append(current_control)
                # Calculate domination for consecutive generals
                domination_info = check_domination_for_consecutive_generals(
                    consecutive_general_count, 
                    current_control, 
                    general_control_history
                )
            else:
                consecutive_general_count = 0
                general_control_history = []  # Reset on non-General event
                domination_info = {'has_domination': False}
            
            last_event_type = detected_type
            
            # Merge detection info
            detection_info = base_detection_info.copy()
            detection_info.update(extra_info)
            
            # Extract event data
            event_data = extract_event_specific_data(detected_type, main_row, minute_df, detection_info)
            
            # For Card events
            if detected_type in ['Yellow Card', 'Red Card']:
                event_data['carded_player'] = extra_info.get('carded_player', event_data.get('player', ''))
                event_data['carded_team'] = extra_info.get('carded_team', event_data.get('team', ''))
                event_data['fouled_player'] = extra_info.get('fouled_player', '')
                event_data['fouled_team'] = extra_info.get('fouled_team', '')
            
            # Detect event chains
            event_chain = detect_event_chain(minute_df, detected_type, main_row, detection_info)
            
            # Get commentary
            rule_based = str(main_row.get('event_commentary', '')) if pd.notna(main_row.get('event_commentary')) else ''
            sequence = str(main_row.get('sequence_commentary', '')) if pd.notna(main_row.get('sequence_commentary')) else ''
            
            # V3 FIX: Calculate area for this minute
            area = ''
            if 'location_x' in minute_df.columns:
                avg_x = minute_df['location_x'].mean()
                if pd.notna(avg_x):
                    if avg_x < 40:
                        area = 'defensive third'
                    elif avg_x < 80:
                        area = 'midfield'
                    else:
                        area = 'attacking third'
            
            # Build context
            context = {
                'home_team': 'Spain',
                'away_team': 'England',
                'home_score': score_row.get('spain_score', 0),
                'away_score': score_row.get('england_score', 0),
                'stage': 'Final',
                'period': detection_info.get('period', 1),
                'detected_type': detected_type,
                'event_data': event_data,
                'event_chain': event_chain,
                'total_events': len(minute_df),
                'pattern_summary': pattern_summary,
                'control': detection_info.get('control', ''),
                'possession_stats': detection_info.get('possession_stats', {}),
                'area': area,  # V3 FIX: Add area
                # V3: New context
                'domination_info': domination_info,
                'consecutive_generals': consecutive_general_count,
                'most_active_player': most_active if most_active else {},
                'multi_shots_info': multi_shots_info,
                'multi_corners_info': multi_corners_info,
                'multi_fouls_info': multi_fouls_info,
                'multi_subs_info': multi_subs_info,
                'multi_offsides_info': multi_offsides_info,
            }
            
            is_key_event = detected_type not in ['General']
            
            # Print progress
            if is_key_event or (idx + 1) % 10 == 0:
                safe_player = str(event_data.get('player', event_data.get('carded_player', ''))).encode('ascii', 'replace').decode('ascii')
                print(f"\n[{event_counter}] Minute {minute}'{period_label} ({progress_pct:.0f}%)")
                print(f"  Event: [{detected_type}] {safe_player}")
                print(f"  Score: Spain {context['home_score']} - {context['away_score']} England")
                
                # V3 info
                if detected_type == 'General':
                    print(f"  V3: Consecutive general #{consecutive_general_count}")
                if domination_info.get('has_domination'):
                    print(f"  V3: {domination_info['team']} dominating for {domination_info['streak']} mins")
                if multi_shots_info.get('has_multiple'):
                    print(f"  V3: {multi_shots_info['count']} shots ({multi_shots_info['scenario']})")
                if multi_fouls_info.get('has_multiple'):
                    print(f"  V3: {multi_fouls_info['count']} fouls this minute")
            
            # Generate LLM commentary
            llm_commentary = commentator.generate_minute_commentary(
                minute=int(minute),
                events_data=[],
                rule_based_commentary=rule_based,
                sequence_commentary=sequence,
                match_context=context
            )
            
            if is_key_event:
                safe_commentary = llm_commentary[:80].encode('ascii', 'replace').decode('ascii')
                print(f"  LLM: {safe_commentary}...")
            
            # Save result
            result = {
                'match_id': match_id,
                'minute': minute,
                'period': period,
                'event_index': event_idx,
                'home_team': 'Spain',
                'away_team': 'England',
                'home_score': context['home_score'],
                'away_score': context['away_score'],
                'stage': 'Final',
                'detected_type': detected_type,
                'player': event_data.get('player', event_data.get('carded_player', '')),
                'team': event_data.get('team', event_data.get('carded_team', '')),
                'location': event_data.get('location', ''),
                'event_count': len(minute_df),
                'play_patterns': pattern_summary,
                'event_types': event_summary,
                'rule_based_commentary': rule_based[:500],
                'sequence_commentary': sequence[:500],
                'llm_commentary': llm_commentary,
                'model': commentator.model,
                'generated_at': datetime.now().isoformat(),
                # V3 columns
                'v3_consecutive_generals': consecutive_general_count if detected_type == 'General' else 0,
                'v3_domination_team': domination_info.get('team', '') if domination_info.get('has_domination') else '',
                'v3_domination_streak': domination_info.get('streak', 0) if domination_info.get('has_domination') else 0,
                'v3_multi_shots_count': multi_shots_info.get('count', 0) if multi_shots_info.get('has_multiple') else 0,
                'v3_multi_shots_scenario': multi_shots_info.get('scenario', '') if multi_shots_info.get('has_multiple') else '',
                'v3_multi_corners_count': multi_corners_info.get('count', 0) if multi_corners_info.get('has_multiple') else 0,
                'v3_multi_fouls_count': multi_fouls_info.get('count', 0) if multi_fouls_info.get('has_multiple') else 0,
                'v3_multi_subs_count': multi_subs_info.get('count', 0) if multi_subs_info.get('has_multiple') else 0,
                'v3_multi_offsides_count': multi_offsides_info.get('count', 0) if multi_offsides_info.get('has_multiple') else 0,
            }
            
            # Add event-specific fields
            for key, value in event_data.items():
                if key not in ['player', 'team', 'location']:
                    result[f'event_{key}'] = value
            
            result['has_chain'] = event_chain.get('has_chain', False)
            
            results.append(result)
    
    # Save to CSV
    results_df = pd.DataFrame(results)
    output_file = OUTPUT_DIR / f"match_{match_id}_V3_FINAL_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    results_df.to_csv(output_file, index=False)

    print(f"\n{'=' * 60}")
    print(f"[DONE] Generated {len(results)} commentaries!")
    print(f"[SAVED] {output_file}")
    print(f"{'=' * 60}")
    
    # Summary
    print(f"\n[EVENT BREAKDOWN]")
    print(results_df['detected_type'].value_counts().to_string())
    
    # V3 stats
    print(f"\n[V3 MULTI-EVENT STATS]")
    print(f"  Multi-shots minutes: {len(results_df[results_df['v3_multi_shots_count'] >= 2])}")
    print(f"  Multi-corners minutes: {len(results_df[results_df['v3_multi_corners_count'] >= 2])}")
    print(f"  Multi-fouls minutes: {len(results_df[results_df['v3_multi_fouls_count'] >= 3])}")
    print(f"  Domination streaks: {len(results_df[results_df['v3_domination_streak'] >= 2])}")
    
    print(f"\n[SAMPLE COMMENTARIES]")
    sample_df = results_df[['minute', 'detected_type', 'llm_commentary']].head(15)
    for _, row in sample_df.iterrows():
        safe_comm = str(row['llm_commentary'])[:70].encode('ascii', 'replace').decode('ascii')
        print(f"{row['minute']:3}' | {row['detected_type']:15} | {safe_comm}")


if __name__ == "__main__":
    main()

