"""
Generate Rich Sports Commentary for Final Game
==============================================
Creates detailed, realistic commentary with context, stats, and excitement.
"""

import pandas as pd
import numpy as np
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

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

def calculate_field_zones(x, y):
    """Calculate field zones from coordinates"""
    # X: 0-120 (0=own goal, 120=opponent goal)
    # Y: 0-80 (width)
    
    if x is None or y is None:
        return "unknown", "unknown", "unknown"
    
    # Horizontal zones
    if x < 40:
        h_zone = "defensive third"
    elif x < 80:
        h_zone = "midfield"
    else:
        h_zone = "attacking third"
    
    # Vertical zones
    if y < 26.67:
        v_zone = "right"
    elif y < 53.33:
        v_zone = "central"
    else:
        v_zone = "left"
    
    combined = f"{v_zone} {h_zone}"
    
    return h_zone, v_zone, combined

def get_time_context(minute, second):
    """Get descriptive time context"""
    if minute >= 90:
        mins_into_added = minute - 90
        return f"in the {mins_into_added + 1}{get_ordinal_suffix(mins_into_added + 1)} minute of stoppage time"
    elif minute >= 88:
        return "in the dying moments"
    elif minute >= 85:
        return "late in the game"
    elif minute >= 80:
        return "with ten minutes to go"
    elif minute >= 75:
        return "with fifteen minutes remaining"
    else:
        return f"in the {minute}{get_ordinal_suffix(minute)} minute"

def get_ordinal_suffix(n):
    """Get ordinal suffix (st, nd, rd, th)"""
    if 10 <= n % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return suffix

def get_pass_distance_category(length):
    """Categorize pass distance"""
    if length is None or pd.isna(length):
        return "medium"
    if length < 15:
        return "short"
    elif length < 30:
        return "medium"
    else:
        return "long"

def get_pass_trajectory(height, angle, start_x, end_x):
    """Determine pass trajectory description"""
    if height == "Ground Pass":
        trajectory = "along the ground"
    elif height == "High Pass":
        trajectory = "through the air"
    elif height == "Low Pass":
        trajectory = ""
    else:
        trajectory = ""
    
    # Direction
    direction = ""
    if start_x and end_x:
        if end_x > start_x + 10:
            direction = "forward "
        elif end_x < start_x - 10:
            direction = "back "
    
    return f"{direction}{trajectory}".strip()

def get_score_context(spain_score, england_score, team_name):
    """Get score context"""
    if team_name == "Spain":
        if spain_score > england_score:
            lead = spain_score - england_score
            return f"Spain leading {spain_score}-{england_score}"
        elif spain_score < england_score:
            deficit = england_score - spain_score
            return f"Spain trailing {spain_score}-{england_score}"
        else:
            return f"level at {spain_score}-{spain_score}"
    else:  # England
        if england_score > spain_score:
            lead = england_score - spain_score
            return f"England leading {england_score}-{spain_score}"
        elif england_score < spain_score:
            deficit = spain_score - england_score
            return f"England trailing {england_score}-{spain_score}"
        else:
            return f"level at {spain_score}-{spain_score}"

def format_pass_commentary(row, df, idx):
    """Generate detailed commentary for Pass events"""
    player = row['player_name']
    recipient = row['pass_recipient']
    team = row['team_name']
    length = row['pass_length']
    height = row['pass_height']
    outcome = row['pass_outcome']
    under_pressure = row['under_pressure']
    play_pattern = row['play_pattern']
    minute = row['minute']
    
    # NEW: Get enrichment data
    is_key_pass = row.get('is_key_pass', False)
    is_danger_zone = row.get('is_danger_zone', False)
    is_high_pressure = row.get('is_high_pressure', False)
    previous_player = row.get('previous_player')
    next_event_type = row.get('next_event_type')
    next_team = row.get('next_team')
    possession_retained = row.get('possession_retained')
    
    # Get zones
    _, _, start_zone = calculate_field_zones(row['location_x'], row['location_y'])
    _, _, end_zone = calculate_field_zones(row['pass_end_x'], row['pass_end_y'])
    
    # Build commentary
    distance = get_pass_distance_category(length)
    trajectory = get_pass_trajectory(height, row['pass_angle'], row['location_x'], row['pass_end_x'])
    
    # Base pass description with HIGH PRESSURE emphasis
    if is_high_pressure:
        pressure_text = "under MASSIVE pressure, "
    elif under_pressure:
        pressure_text = "under pressure, "
    else:
        pressure_text = ""
    
    # Pass type with KEY PASS emphasis
    if distance == "long" and "air" in trajectory:
        pass_type = "ball"
    else:
        pass_type = "pass"
    
    if is_key_pass:
        pass_descriptor = "BRILLIANT "
    elif is_danger_zone:
        pass_descriptor = "dangerous "
    else:
        pass_descriptor = ""
    
    # Build sentence
    commentary = f"{player} {pressure_text}"
    
    if recipient and pd.notna(recipient):
        commentary += f"plays a {pass_descriptor}{distance} {pass_type} {trajectory} to {recipient}"
    else:
        commentary += f"plays a {pass_descriptor}{distance} {pass_type} {trajectory}"
    
    # Add zone if significant progression
    if start_zone != end_zone and "attacking third" in end_zone:
        commentary += f" into the {end_zone}"
    elif is_danger_zone:
        commentary += " into the DANGER ZONE"
    
    # Add outcome with WHO GETS THE BALL
    if outcome and outcome != "Incomplete":
        if outcome == "Out":
            # Check who gets throw-in
            if next_event_type == "Throw In" and next_team:
                if next_team == team:
                    commentary += f", out of play. {team} throw-in"
                else:
                    commentary += f", out of play! {team} LOSES possession. {next_team} throw-in"
            else:
                commentary += ", but it goes out of play"
        elif outcome == "Offside":
            commentary += ", but the flag is up for offside!"
        elif outcome == "Injury Clearance":
            commentary += " for treatment"
    elif outcome == "Incomplete":
        if possession_retained == False:
            commentary += f", INTERCEPTED! {team} loses the ball"
        else:
            commentary += ", but the pass doesn't find its target"
    
    # Add what happens next for successful passes
    if not outcome or outcome not in ["Incomplete", "Out", "Offside"]:
        if next_event_type == "Shot":
            commentary += " - SHOT INCOMING!"
        elif next_event_type == "Clearance" and next_team != team:
            commentary += " - cleared away by the defense"
        elif next_event_type == "Corner" and next_team == team:
            commentary += " - corner kick!"
    
    # Add play pattern context
    if play_pattern and "Free Kick" in play_pattern:
        commentary = f"{commentary.replace('plays', 'delivers the free kick')}"
    elif play_pattern and "Corner" in play_pattern:
        commentary = f"{commentary.replace('plays', 'delivers the corner')}"
    elif play_pattern and "Goal Kick" in play_pattern:
        commentary = f"From the goal kick, {commentary}"
    
    return commentary

def format_shot_commentary(row, df, idx):
    """Generate EXCITED commentary for Shot events"""
    player = row['player_name']
    team = row['team_name']
    outcome = row['shot_outcome']
    xg = row['shot_xg']
    body_part = row['shot_body_part']
    under_pressure = row['under_pressure']
    minute = row['minute']
    spain_score = row['spain_score']
    england_score = row['england_score']
    is_goal = row['is_goal']
    
    # NEW: Get enrichment data
    previous_player = row.get('previous_player')
    previous_event_type = row.get('previous_event_type')
    previous_team = row.get('previous_team')
    next_event_type = row.get('next_event_type')
    next_team = row.get('next_team')
    distance_to_goal = row.get('distance_to_goal')
    is_danger_zone = row.get('is_danger_zone', False)
    is_high_pressure = row.get('is_high_pressure', False)
    
    _, _, zone = calculate_field_zones(row['location_x'], row['location_y'])
    time_context = get_time_context(minute, row['second'])
    
    # GOAL - Maximum excitement!
    if is_goal:
        # Get assist if available
        assist_text = ""
        if previous_event_type == 'Pass' and previous_player and previous_team == team:
            assist_text = f", assisted by {previous_player}"
        
        # Calculate new score - FIX THE SCORE CALCULATION!
        if team == "Spain":
            new_spain = spain_score + 1
            new_england = england_score
        else:
            new_spain = spain_score
            new_england = england_score + 1
        
        # Check if this is player's first/second goal  
        # player_match_goals = goals scored BEFORE this one
        player_match_goals_before = row['player_match_goals']
        player_match_goals_now = player_match_goals_before + 1  # Add this goal
        
        player_tournament_goals_before = row['player_tournament_goals']
        player_tournament_goals_now = player_tournament_goals_before + 1  # Add this goal
        
        # Build EXCITED commentary
        commentary = f"⚽ GOOOAL! {player} scores{assist_text}! "
        
        # Add context about the goal with distance
        if distance_to_goal and distance_to_goal < 10:
            distance_desc = f"from close range ({distance_to_goal:.0f}m)"
        elif distance_to_goal and distance_to_goal > 25:
            distance_desc = f"from distance ({distance_to_goal:.0f}m out)"
        else:
            distance_desc = ""
        
        if body_part == "Head":
            commentary += f"A brilliant header {distance_desc}! " if distance_desc else f"A brilliant header from {player}! "
        elif body_part == "Right Foot":
            commentary += f"What a strike with the right foot {distance_desc}! " if distance_desc else f"What a strike with the right foot! "
        elif body_part == "Left Foot":
            commentary += f"A superb left-footed finish {distance_desc}! " if distance_desc else f"A superb left-footed finish! "
        
        # Add score - SHOW BOTH SCORES CORRECTLY
        if new_spain > new_england:
            commentary += f"Spain now lead {new_spain}-{new_england}! "
        elif new_england > new_spain:
            commentary += f"England now lead {new_england}-{new_spain}! "
        else:
            commentary += f"We're level at {new_spain}-{new_spain}! "
        
        # Add player milestone - ONLY if this is their 2nd+ goal in THIS match
        if player_match_goals_now == 2:
            commentary += f"That's {player}'s second goal of the match! A brace in the final! "
        elif player_match_goals_now == 3:
            commentary += f"That's {player}'s THIRD goal of the match! A hat-trick in the final! "
        elif player_match_goals_now >= 4:
            commentary += f"That's {player}'s {player_match_goals_now}{get_ordinal_suffix(player_match_goals_now)} goal of the match! Incredible! "
        
        # Tournament goals
        if player_tournament_goals_now == 1:
            commentary += f"His first goal of the tournament {time_context}! "
        elif player_tournament_goals_now == 2:
            commentary += f"His 2nd goal of the tournament {time_context}! "
        else:
            commentary += f"His {player_tournament_goals_now}{get_ordinal_suffix(player_tournament_goals_now)} goal of the tournament {time_context}! "
        
        # Add dramatic context based on score
        score_diff = abs(new_spain - new_england)
        if score_diff == 2:
            commentary += "A crucial two-goal lead in the final! "
        elif score_diff == 1 and minute >= 80:
            commentary += "A vital goal in the closing stages! "
        elif time_context and "stoppage" in time_context:
            commentary += "What drama in stoppage time! "
        
        return commentary
    
    # Non-goal shots
    else:
        # Build-up context
        buildup_text = ""
        if previous_event_type == 'Pass' and previous_player and previous_team == team:
            buildup_text = f"Receiving from {previous_player}, "
        elif previous_event_type == 'Carry' and previous_team == team:
            buildup_text = "After carrying forward, "
        
        # Pressure context with HIGH PRESSURE emphasis
        if is_high_pressure:
            pressure_text = "under MASSIVE pressure, "
        elif under_pressure:
            pressure_text = "under pressure, "
        else:
            pressure_text = ""
        
        # Danger zone emphasis
        if is_danger_zone:
            zone_text = "from a DANGEROUS position"
        else:
            zone_text = f"from the {zone}"
        
        # Distance to goal
        distance_desc = ""
        if distance_to_goal and distance_to_goal < 15:
            distance_desc = f" ({distance_to_goal:.0f}m out!)"
        elif distance_to_goal and distance_to_goal > 30:
            distance_desc = f" from long range ({distance_to_goal:.0f}m)"
        
        commentary = f"{buildup_text}{player} {pressure_text}shoots"
        
        if body_part:
            commentary += f" with the {body_part.lower()}"
        
        commentary += f" {zone_text}{distance_desc}"
        
        # Outcome with what happens next
        if outcome == "Blocked":
            commentary += " - BLOCKED!"
            if next_event_type == "Corner" and next_team == team:
                commentary += " Corner kick!"
        elif outcome == "Saved":
            commentary += " - SAVED by the goalkeeper!"
            # What happens to the save?
            if next_event_type == "Corner" and next_team == team:
                commentary += " Corner to {team}!"
            elif next_event_type == "Ball Recovery" and next_team != team:
                commentary += " Goalkeeper claims it."
            else:
                commentary += " Parried away!"
            if xg and xg > 0.3:
                commentary += " Great chance wasted!"
        elif outcome == "Off T":
            commentary += " - just wide!"
            if xg and xg > 0.25:
                commentary += " Should have scored!"
        elif outcome == "Wayward":
            commentary += " - well wide!"
        elif outcome == "Post":
            commentary += " - HITS THE POST! SO CLOSE!"
            if next_event_type == "Corner" and next_team == team:
                commentary += " Corner kick!"
        
        # Add xG context for big chances
        if xg and xg > 0.4:
            commentary += f" [xG: {xg:.2f}]"
        
        return commentary

def format_carry_commentary(row, df, idx):
    """Generate commentary for Carry events"""
    player = row['player_name']
    under_pressure = row['under_pressure']
    distance = row['carry_distance']
    
    # NEW: Get enrichment data
    is_danger_zone = row.get('is_danger_zone', False)
    is_high_pressure = row.get('is_high_pressure', False)
    possession_retained = row.get('possession_retained')
    
    _, _, start_zone = calculate_field_zones(row['location_x'], row['location_y'])
    _, _, end_zone = calculate_field_zones(row['carry_end_x'], row['carry_end_y'])
    
    # Long dribbling runs
    if distance and distance > 25:
        if is_danger_zone:
            action = "BURSTS into the DANGER ZONE with an amazing run"
        elif is_high_pressure:
            action = "breaks away under MASSIVE pressure with a brilliant run"
        else:
            action = "surges forward on a BRILLIANT run"
    elif distance and distance > 15:
        if is_high_pressure:
            action = "under MASSIVE pressure, drives forward with the ball"
        elif under_pressure:
            action = "under pressure, drives forward with the ball"
        else:
            action = "drives forward with the ball"
    else:
        if is_high_pressure:
            action = "under MASSIVE pressure, carries the ball"
        elif under_pressure:
            action = "under pressure, carries the ball"
        else:
            action = "carries the ball"
    
    commentary = f"{player} {action}"
    
    # Add zone progression
    if start_zone != end_zone:
        if is_danger_zone:
            commentary += " - NOW IN THE DANGER ZONE!"
        else:
            commentary += f" from the {start_zone} into the {end_zone}"
    
    # Loss of possession
    if possession_retained == False:
        commentary += " - BUT LOSES IT!"
    
    return commentary

def format_pressure_commentary(row, df, idx):
    """Generate commentary for Pressure events"""
    player = row['player_name']
    team = row['team_name']
    
    # Try to find who is being pressed
    target = "the ball carrier"
    if idx > 0:
        prev = df.iloc[idx - 1]
        if prev['team_name'] != team and prev['player_name']:
            target = prev['player_name']
    
    commentary = f"{player} closes down {target}"
    
    return commentary

def format_ball_receipt_commentary(row, df, idx):
    """Generate commentary for Ball Receipt events"""
    player = row['player_name']
    under_pressure = row['under_pressure']
    _, _, zone = calculate_field_zones(row['location_x'], row['location_y'])
    
    if under_pressure and "attacking third" in zone:
        commentary = f"{player} receives under pressure in the {zone}"
    elif "attacking third" in zone or "penalty" in zone.lower():
        commentary = f"{player} receives in the {zone}"
    else:
        commentary = f"{player} receives"
    
    return commentary

def format_substitution_commentary(row):
    """Generate detailed substitution commentary"""
    player_off = row['player_name']
    team = row['team_name']
    
    # Try to parse substitution data
    sub_dict = parse_json_field(row.get('substitution'))
    position_dict = parse_json_field(row.get('position'))
    
    if not sub_dict:
        return f"⚔️ Substitution for {team}"
    
    # Get replacement player
    replacement = sub_dict.get('replacement', {})
    player_on = replacement.get('name', 'Unknown') if isinstance(replacement, dict) else str(replacement)
    
    # Get position
    position_off = position_dict.get('name') if position_dict else None
    
    # Base commentary
    commentary = f"⚔️ SUBSTITUTION for {team}: {player_off} comes off"
    
    if player_on and player_on != 'Unknown':
        commentary += f", replaced by {player_on}"
    
    # Add position if available
    if position_off:
        commentary += f". {player_off} was playing as {position_off}"
    
    return commentary

def format_foul_committed_commentary(row):
    """Generate foul commentary with card tracking"""
    player = row['player_name']
    team = row['team_name']
    
    # Try to parse foul data
    foul_dict = parse_json_field(row.get('foul_committed'))
    
    # Get location
    _, _, zone = calculate_field_zones(row.get('location_x'), row.get('location_y'))
    
    # Base commentary
    commentary = f"⚠️ FOUL by {player}"
    
    if zone and zone != "unknown":
        commentary += f" in the {zone}"
    
    # Check for card
    if foul_dict:
        card_info = foul_dict.get('card', {})
        if isinstance(card_info, dict):
            card = card_info.get('name')
            if card == 'Yellow Card':
                commentary += f" - YELLOW CARD for {player}!"
            elif card == 'Red Card':
                commentary += f" - RED CARD! {player} is SENT OFF! {team} down to 10 men!"
        
        # Check for penalty
        if foul_dict.get('penalty'):
            commentary += " PENALTY!"
    
    return commentary

def format_injury_stoppage_commentary(row):
    """Generate injury stoppage commentary"""
    player = row['player_name']
    team = row['team_name']
    
    if pd.notna(player):
        return f"⏸️ PLAY STOPPED - {player} ({team}) is down injured"
    else:
        return f"⏸️ INJURY STOPPAGE - Play halted for treatment"

def format_dispossessed_commentary(row):
    """Generate dispossessed commentary"""
    player = row['player_name']
    next_player = row.get('next_player')
    next_team = row.get('next_team')
    team = row['team_name']
    
    if next_player and next_team != team and pd.notna(next_player):
        return f"{player} is dispossessed by {next_player}!"
    else:
        return f"{player} loses the ball!"

def format_miscontrol_commentary(row):
    """Generate miscontrol commentary"""
    player = row['player_name']
    under_pressure = row.get('under_pressure', False)
    possession_retained = row.get('possession_retained', True)
    
    if under_pressure and not possession_retained:
        return f"{player} loses control under pressure!"
    elif under_pressure:
        return f"{player} struggles to control under pressure"
    elif not possession_retained:
        return f"Poor touch from {player} - loses possession!"
    else:
        return f"Heavy touch from {player}"

def format_dribbled_past_commentary(row):
    """Generate dribbled past commentary"""
    player = row['player_name']
    prev_player = row.get('previous_player')
    
    if prev_player and pd.notna(prev_player):
        return f"{player} is beaten by {prev_player}!"
    else:
        return f"{player} is beaten!"

def format_50_50_commentary(row):
    """Generate 50/50 commentary"""
    player = row['player_name']
    next_team = row.get('next_team')
    team = row['team_name']
    
    if next_team == team:
        return f"{player} wins the 50/50!"
    else:
        return f"{player} loses the 50/50 challenge"

def format_tactical_shift_commentary(row):
    """Generate tactical shift commentary"""
    team = row['team_name']
    minute = row['minute']
    
    if pd.notna(team):
        return f"📋 TACTICAL CHANGE - {team} adjusts formation ({minute}')"
    else:
        return f"📋 TACTICAL CHANGE at the {minute}' mark"

def format_simple_commentary(row, event_type):
    """Generate commentary for simple events"""
    player = row['player_name']
    
    templates = {
        'Block': f"Crucial block by {player}!",
        'Clearance': f"{player} clears the danger",
        'Interception': f"{player} intercepts!",
        'Ball Recovery': f"{player} wins the ball back",
        'Goal Keeper': "The goalkeeper deals with it",
        'Foul Won': f"{player} is fouled",
        'Duel': f"{player} in the duel",
        'Dribble': f"{player} takes on the defender",
        'Shield': f"{player} shields the ball",
        'Error': f"Error by {player}",
        'Referee Ball-Drop': "Referee drops the ball",
        'Half Start': f"Half Start",
        'Half End': f"Half End",
        'Starting XI': f"Starting XI"
    }
    
    return templates.get(event_type, f"{event_type} - {player}")

def add_period_commentary(row):
    """Add special commentary for match periods (game start, 2nd half, overtime)"""
    minute = row['minute']
    period = row['period']
    event_type = row['event_type']
    play_pattern = row.get('play_pattern', '')
    
    # GAME START - Use template with CORRECT SEMI-FINAL results
    if minute == 0 and period == 1 and event_type == 'Pass' and 'Kick Off' in str(play_pattern):
        return "🏆 THE EURO 2024 FINAL IS UNDERWAY! Welcome to Olympiastadion Berlin for this Final clash between Spain and England. François Letexier will be taking charge of today's match. Spain come into this match having recorded 6 wins, 0 draws, and 0 losses in the tournament so far. They've scored 13 goals while conceding 3. Last time out, they secured a 2-1 victory over France in the semi-final. England have managed 3 wins, 3 draws, and 0 losses so far in Euro 2024. With 7 goals scored and 4 conceded, they come in confident after beating Netherlands 2-1 in the semi-final. We're all set for kick-off here at Olympiastadion Berlin. "
    
    # SECOND HALF START
    elif minute == 45 and period == 2 and event_type in ['Pass', 'Carry', 'Ball Receipt*']:
        spain_score = row.get('spain_score', 0)
        england_score = row.get('england_score', 0)
        if spain_score > england_score:
            return f"⚽ THE SECOND HALF IS UNDERWAY! Spain lead {spain_score}-{england_score} at the break. Can England find a way back into this final? 45 minutes to decide the champion of Europe! "
        elif england_score > spain_score:
            return f"⚽ THE SECOND HALF IS UNDERWAY! England lead {england_score}-{spain_score} at the break. Can Spain respond in the second half? Everything to play for! "
        else:
            return f"⚽ THE SECOND HALF IS UNDERWAY! Still level at {spain_score}-{spain_score} after an intense first half. Everything to play for in the final 45 minutes! "
    
    # STOPPAGE TIME
    elif minute >= 90 and minute < 91 and event_type in ['Pass', 'Shot', 'Carry']:
        spain_score = row.get('spain_score', 0)
        england_score = row.get('england_score', 0)
        if spain_score != england_score:
            return f"⏱️ WE'RE INTO STOPPAGE TIME! Seconds remaining in this Euro 2024 final! "
        else:
            return f"⏱️ INTO STOPPAGE TIME! Still all square! We could be heading to extra time! "
    
    return ""

def generate_event_commentary(df):
    """Generate commentary for each event"""
    
    commentaries = []
    
    for idx, row in df.iterrows():
        event_type = row['event_type']
        
        # Check for special period commentary (game start, 2nd half, etc.)
        period_comment = add_period_commentary(row)
        
        # Generate main event commentary
        if event_type == 'Pass':
            commentary = format_pass_commentary(row, df, idx)
        elif event_type == 'Shot':
            commentary = format_shot_commentary(row, df, idx)
        elif event_type == 'Carry':
            commentary = format_carry_commentary(row, df, idx)
        elif event_type == 'Pressure':
            commentary = format_pressure_commentary(row, df, idx)
        elif event_type == 'Ball Receipt*':
            commentary = format_ball_receipt_commentary(row, df, idx)
        elif event_type == 'Substitution':
            commentary = format_substitution_commentary(row)
        elif event_type == 'Foul Committed':
            commentary = format_foul_committed_commentary(row)
        elif event_type == 'Injury Stoppage':
            commentary = format_injury_stoppage_commentary(row)
        elif event_type == 'Dispossessed':
            commentary = format_dispossessed_commentary(row)
        elif event_type == 'Miscontrol':
            commentary = format_miscontrol_commentary(row)
        elif event_type == 'Dribbled Past':
            commentary = format_dribbled_past_commentary(row)
        elif event_type == '50/50':
            commentary = format_50_50_commentary(row)
        elif event_type == 'Tactical Shift':
            commentary = format_tactical_shift_commentary(row)
        else:
            commentary = format_simple_commentary(row, event_type)
        
        # Combine period commentary with event commentary
        if period_comment:
            commentary = period_comment + commentary
        
        commentaries.append(commentary)
    
    return commentaries

def create_sequences(df):
    """Create event sequences (groups of related events)"""
    
    sequences = []
    current_sequence = []
    current_possession_team = None
    sequence_id = 1
    
    for idx, row in df.iterrows():
        possession_team = row['possession_team']
        
        # Start new sequence if possession changes or sequence gets too long
        if possession_team != current_possession_team or len(current_sequence) >= 10:
            if current_sequence:
                sequences.append({
                    'sequence_id': sequence_id,
                    'events': current_sequence.copy()
                })
                sequence_id += 1
            current_sequence = []
            current_possession_team = possession_team
        
        current_sequence.append(idx)
    
    # Add last sequence
    if current_sequence:
        sequences.append({
            'sequence_id': sequence_id,
            'events': current_sequence
        })
    
    return sequences

def create_narrative_flow(df, event_indices):
    """Create flowing narrative from sequence of events (no player name repetition)"""
    
    if len(event_indices) == 0:
        return ""
    
    narrative_parts = []
    last_player = None
    last_team = None
    
    for i, idx in enumerate(event_indices[:5]):  # Limit to 5 events
        try:
            event = df.loc[idx]
            player = event['player_name']
            team = event['team_name']
            event_type = event['event_type']
            commentary = event['event_commentary']
            
            if pd.isna(commentary) or not commentary:
                continue
            
            # Skip special period commentary (game start, etc.)
            if '🏆 THE EURO 2024 FINAL' in str(commentary) or '⚽ THE SECOND HALF' in str(commentary):
                continue
            
            # First event: Full commentary
            if i == 0:
                narrative_parts.append(commentary)
                last_player = player
                last_team = team
            else:
                # Same player, same team: Remove redundant player name
                if player == last_player and pd.notna(player) and team == last_team:
                    # Remove player name from start of commentary
                    if pd.notna(player) and commentary.startswith(str(player)):
                        # Remove "{player} " or "{player}, "
                        action = commentary[len(str(player)):].lstrip(' ,')
                        if action:
                            narrative_parts.append(action)
                        else:
                            narrative_parts.append(commentary)
                    else:
                        narrative_parts.append(commentary)
                
                # Different player, same team
                elif team == last_team and pd.notna(team):
                    narrative_parts.append(commentary)
                
                # Opponent team - new sentence
                else:
                    narrative_parts.append(". " + commentary)
                    last_team = team
                
                last_player = player
        except Exception as e:
            # Skip problematic events
            continue
    
    # Join parts with space, clean up
    result = ' '.join(narrative_parts)
    # Clean up double spaces and extra periods
    result = result.replace('  ', ' ').replace('..', '.').strip()
    return result

def generate_sequence_commentary(df, sequences):
    """Generate sequence-level commentary with narrative flow"""
    
    sequence_map = {}
    
    for seq in sequences:
        seq_id = seq['sequence_id']
        event_indices = seq['events']
        
        # Build narrative sequence commentary
        narrative = create_narrative_flow(df, event_indices)
        
        # Add time context for first event
        try:
            first_event = df.loc[event_indices[0]]
            time_context = f"[{first_event['minute']}:{first_event['second']:02d}]"
            sequence_commentary = f"{time_context} {narrative}"
        except:
            sequence_commentary = narrative
        
        # Map to all events in sequence
        for idx in event_indices:
            sequence_map[idx] = {
                'sequence_id': seq_id,
                'sequence_commentary': sequence_commentary,
                'sequence_length': len(event_indices)
            }
    
    return sequence_map

def main():
    """Main execution"""
    
    # Load enriched data
    input_file = os.path.join(SCRIPT_DIR, 'final_game_detailed_commentary_data.csv')
    df = pd.read_csv(input_file)
    
    print(f"Loaded {len(df)} events")
    print(f"Generating detailed commentary...")
    
    # Generate event-level commentary
    df['event_commentary'] = generate_event_commentary(df)
    
    # Create sequences
    sequences = create_sequences(df)
    print(f"Created {len(sequences)} sequences")
    
    # Generate sequence commentary
    sequence_map = generate_sequence_commentary(df, sequences)
    
    # Add sequence info to dataframe
    df['sequence_id'] = df.index.map(lambda x: sequence_map.get(x, {}).get('sequence_id'))
    df['sequence_commentary'] = df.index.map(lambda x: sequence_map.get(x, {}).get('sequence_commentary'))
    df['sequence_length'] = df.index.map(lambda x: sequence_map.get(x, {}).get('sequence_length'))
    
    # Save
    output_file = os.path.join(SCRIPT_DIR, 'final_game_rich_commentary.csv')
    df.to_csv(output_file, index=False)
    
    print(f"\n✅ Rich commentary saved to: {output_file}")
    print(f"   Total events: {len(df)}")
    print(f"   Total sequences: {len(sequences)}")
    print(f"   Columns: {len(df.columns)}")
    
    # Show some examples
    print("\n" + "="*80)
    print("SAMPLE COMMENTARY:")
    print("="*80)
    
    for i in range(min(10, len(df))):
        row = df.iloc[i]
        print(f"\n[{row['minute']}:{row['second']:02d}] {row['event_type']}")
        print(f"  Player: {row['player_name']} ({row['team_name']})")
        print(f"  Commentary: {row['event_commentary']}")

if __name__ == "__main__":
    main()

