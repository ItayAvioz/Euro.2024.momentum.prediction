"""
Starting Game Commentary Examples
===================================
Analyze starting events and create natural language commentary templates.

Takes 3 diverse matches and shows:
1. Metadata (match context)
2. Extracted Data (team stats, lineups)
3. Template Format (commentary structure)
4. Generated Commentary (natural language)
"""

import pandas as pd
import os

# Get project root directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
DATA_DIR = os.path.join(PROJECT_ROOT, 'Data')

def load_starting_events():
    """Load the starting events dataset"""
    csv_path = os.path.join(SCRIPT_DIR, 'starting_events_with_team_stats.csv')
    df = pd.read_csv(csv_path)
    return df

def select_3_diverse_matches(df):
    """Select 3 diverse match examples"""
    # Select interesting matches:
    # 1. Opening match (Germany vs Scotland) - No previous form
    # 2. Group stage with form (Denmark vs England) - Both teams played 1 game
    # 3. Final (Spain vs England) - Both teams with full tournament history
    
    selected_match_ids = [
        3930158,  # Opening: Germany 5-1 Scotland
        3930171,  # Group Stage: Denmark 1-1 England
        3943043,  # Final: Spain 2-1 England
    ]
    
    return selected_match_ids

def get_match_data(df, match_id):
    """Extract all data for a specific match"""
    match_df = df[df['match_id'] == match_id].iloc[0]  # Get first row (all rows have same match info)
    
    return {
        # Match Context
        'match_id': match_df['match_id'],
        'match_date': match_df['match_date'],
        'stage': match_df['stage'],
        'kick_off_time': match_df['kick_off_time'],
        'stadium': match_df['stadium'],
        'referee': match_df['referee'],
        
        # Teams
        'team_a': match_df['team_a'],
        'team_b': match_df['team_b'],
        'team_a_score': match_df['team_a_score'],
        'team_b_score': match_df['team_b_score'],
        
        # Team A Stats
        'team_a_stats': {
            'matches_played': match_df['team_a_matches_played'],
            'wins': match_df['team_a_wins'],
            'draws': match_df['team_a_draws'],
            'losses': match_df['team_a_losses'],
            'goals_scored': match_df['team_a_goals_scored'],
            'goals_conceded': match_df['team_a_goals_conceded'],
            'goal_difference': match_df['team_a_goal_difference'],
            'last_result': match_df['team_a_last_result'],
            'last_score': match_df['team_a_last_score'],
            'last_opponent': match_df['team_a_last_opponent'],
        },
        
        # Team B Stats
        'team_b_stats': {
            'matches_played': match_df['team_b_matches_played'],
            'wins': match_df['team_b_wins'],
            'draws': match_df['team_b_draws'],
            'losses': match_df['team_b_losses'],
            'goals_scored': match_df['team_b_goals_scored'],
            'goals_conceded': match_df['team_b_goals_conceded'],
            'goal_difference': match_df['team_b_goal_difference'],
            'last_result': match_df['team_b_last_result'],
            'last_score': match_df['team_b_last_score'],
            'last_opponent': match_df['team_b_last_opponent'],
        },
        
        # Lineups
        'team_a_lineup': match_df['team_a_lineup'],
        'team_b_lineup': match_df['team_b_lineup'],
    }

def create_commentary_template():
    """Define commentary template structure"""
    template = """
[OPENING - Match Introduction]
Template: "Welcome to {stadium} for this {stage} match between {team_a} and {team_b}. 
{referee} is the referee for today's match."

[TEAM A FORM - Conditional based on matches_played]
IF matches_played > 0:
    Template: "{team_a} come into this match with {record_summary}. 
    {form_details}. Last time out, they {last_result_detail}."
ELSE:
    Template: "{team_a} are making their tournament debut today."

[TEAM B FORM - Conditional based on matches_played]
IF matches_played > 0:
    Template: "{team_b} have {record_summary}. 
    {form_details}. Their last match saw them {last_result_detail}."
ELSE:
    Template: "{team_b} are also starting their tournament campaign."

[STARTING LINEUPS]
Template: "For {team_a}, key players include {key_players_a}.
And for {team_b}, we have {key_players_b}."

[KICK-OFF]
Template: "The match is about to begin here at {stadium}. 
This promises to be an exciting encounter!"
"""
    return template

def generate_commentary(match_data):
    """Generate natural language commentary from match data"""
    
    team_a = match_data['team_a']
    team_b = match_data['team_b']
    team_a_stats = match_data['team_a_stats']
    team_b_stats = match_data['team_b_stats']
    
    # Opening
    opening = f"Welcome to {match_data['stadium']} for this {match_data['stage']} clash between {team_a} and {team_b}. "
    opening += f"{match_data['referee']} will be taking charge of today's match."
    
    # Team A Form
    if team_a_stats['matches_played'] > 0:
        # Create record summary
        w, d, l = team_a_stats['wins'], team_a_stats['draws'], team_a_stats['losses']
        record = f"{w} win{'s' if w != 1 else ''}, {d} draw{'s' if d != 1 else ''}, and {l} loss{'es' if l != 1 else ''}"
        
        team_a_form = f"{team_a} come into this match having recorded {record} in the tournament so far. "
        
        # Goals summary
        gs, gc = team_a_stats['goals_scored'], team_a_stats['goals_conceded']
        team_a_form += f"They've scored {gs} goal{'s' if gs != 1 else ''} while conceding {gc}. "
        
        # Last match
        last_result = team_a_stats['last_result']
        last_score = team_a_stats['last_score']
        last_opp = team_a_stats['last_opponent']
        
        if last_result == 'Win':
            team_a_form += f"Last time out, they secured a {last_score} victory over {last_opp}."
        elif last_result == 'Draw':
            team_a_form += f"Their previous match ended in a {last_score} draw against {last_opp}."
        else:
            team_a_form += f"They'll be looking to bounce back from a {last_score} defeat to {last_opp}."
    else:
        team_a_form = f"{team_a} are making their tournament debut in front of their home fans tonight."
    
    # Team B Form
    if team_b_stats['matches_played'] > 0:
        w, d, l = team_b_stats['wins'], team_b_stats['draws'], team_b_stats['losses']
        record = f"{w} win{'s' if w != 1 else ''}, {d} draw{'s' if d != 1 else ''}, and {l} loss{'es' if l != 1 else ''}"
        
        team_b_form = f"{team_b} have managed {record} so far in Euro 2024. "
        
        gs, gc = team_b_stats['goals_scored'], team_b_stats['goals_conceded']
        team_b_form += f"With {gs} goal{'s' if gs != 1 else ''} scored and {gc} conceded, "
        
        last_result = team_b_stats['last_result']
        last_score = team_b_stats['last_score']
        last_opp = team_b_stats['last_opponent']
        
        if last_result == 'Win':
            team_b_form += f"they come in confident after beating {last_opp} {last_score}."
        elif last_result == 'Draw':
            team_b_form += f"they drew {last_score} with {last_opp} last time."
        else:
            team_b_form += f"they'll want to recover from that {last_score} loss to {last_opp}."
    else:
        team_b_form = f"{team_b} are also starting their Euro 2024 journey this evening."
    
    # Lineups (extract first 3 players from each lineup)
    lineup_a = match_data['team_a_lineup']
    lineup_b = match_data['team_b_lineup']
    
    # Parse lineups to get key players
    players_a = lineup_a.split('|')[:3] if '|' in lineup_a else ['the starting eleven']
    players_b = lineup_b.split('|')[:3] if '|' in lineup_b else ['the starting eleven']
    
    if len(players_a) > 1 and 'the starting' not in players_a[0]:
        key_players_a = ', '.join([p.split('.')[-1].strip() for p in players_a])
        lineup_text = f"For {team_a}, we have {key_players_a} in the starting lineup. "
    else:
        lineup_text = f"The teams have been announced. "
    
    if len(players_b) > 1 and 'the starting' not in players_b[0]:
        key_players_b = ', '.join([p.split('.')[-1].strip() for p in players_b])
        lineup_text += f"And {team_b} field {key_players_b} among others."
    else:
        lineup_text += f"Both sides are ready."
    
    # Kick-off
    kickoff = f"We're all set for kick-off here at {match_data['stadium']}. This {match_data['stage']} encounter promises to be fascinating!"
    
    # Combine all parts
    full_commentary = f"{opening}\n\n{team_a_form}\n\n{team_b_form}\n\n{lineup_text}\n\n{kickoff}"
    
    return full_commentary

def print_match_analysis(match_data, example_num):
    """Print comprehensive analysis for one match"""
    
    print(f"\n{'='*80}")
    print(f"EXAMPLE {example_num}: {match_data['team_a']} vs {match_data['team_b']}")
    print(f"{'='*80}")
    
    # 1. METADATA
    print("\n" + "─"*80)
    print("1. METADATA (Match Context)")
    print("─"*80)
    print(f"Match ID:      {match_data['match_id']}")
    print(f"Date:          {match_data['match_date']}")
    print(f"Stage:         {match_data['stage']}")
    print(f"Kick-off:      {match_data['kick_off_time']}")
    print(f"Stadium:       {match_data['stadium']}")
    print(f"Referee:       {match_data['referee']}")
    print(f"Final Score:   {match_data['team_a']} {int(match_data['team_a_score'])}-{int(match_data['team_b_score'])} {match_data['team_b']}")
    
    # 2. EXTRACTED DATA
    print("\n" + "─"*80)
    print("2. EXTRACTED DATA (Team Statistics & Form)")
    print("─"*80)
    
    print(f"\n{match_data['team_a'].upper()} (Team A):")
    stats_a = match_data['team_a_stats']
    if stats_a['matches_played'] > 0:
        print(f"  • Tournament Record: {stats_a['wins']}W - {stats_a['draws']}D - {stats_a['losses']}L")
        print(f"  • Goals: {stats_a['goals_scored']} scored, {stats_a['goals_conceded']} conceded (GD: {stats_a['goal_difference']:+d})")
        print(f"  • Last Result: {stats_a['last_result']} ({stats_a['last_score']} vs {stats_a['last_opponent']})")
    else:
        print(f"  • No previous matches (Tournament opener)")
    
    print(f"\n{match_data['team_b'].upper()} (Team B):")
    stats_b = match_data['team_b_stats']
    if stats_b['matches_played'] > 0:
        print(f"  • Tournament Record: {stats_b['wins']}W - {stats_b['draws']}D - {stats_b['losses']}L")
        print(f"  • Goals: {stats_b['goals_scored']} scored, {stats_b['goals_conceded']} conceded (GD: {stats_b['goal_difference']:+d})")
        print(f"  • Last Result: {stats_b['last_result']} ({stats_b['last_score']} vs {stats_b['last_opponent']})")
    else:
        print(f"  • No previous matches (Tournament opener)")
    
    print(f"\nStarting Lineups:")
    print(f"  {match_data['team_a']}: {match_data['team_a_lineup'][:80]}...")
    print(f"  {match_data['team_b']}: {match_data['team_b_lineup'][:80]}...")
    
    # 3. TEMPLATE FORMAT
    print("\n" + "─"*80)
    print("3. TEMPLATE FORMAT (Commentary Structure)")
    print("─"*80)
    
    print("""
[SECTION 1: OPENING]
├─ Stadium + Stage + Teams + Referee
└─ Welcoming tone, set the scene

[SECTION 2: TEAM A FORM]
├─ IF matches_played > 0:
│  ├─ Record summary (W-D-L)
│  ├─ Goals scored/conceded
│  └─ Last match result and opponent
└─ ELSE: Tournament debut statement

[SECTION 3: TEAM B FORM]  
├─ IF matches_played > 0:
│  ├─ Record summary (W-D-L)
│  ├─ Goals scored/conceded  
│  └─ Last match result and opponent
└─ ELSE: Tournament debut statement

[SECTION 4: LINEUPS]
├─ Key players from Team A lineup
└─ Key players from Team B lineup

[SECTION 5: KICK-OFF]
└─ Anticipation, excitement, match is starting
    """)
    
    # 4. GENERATED COMMENTARY
    print("\n" + "─"*80)
    print("4. GENERATED COMMENTARY (Natural Language)")
    print("─"*80)
    print()
    
    commentary = generate_commentary(match_data)
    print(commentary)
    
    print("\n" + "="*80 + "\n")

def main():
    """Main execution"""
    print("\n" + "="*80)
    print("STARTING GAME COMMENTARY - 3 EXAMPLES")
    print("="*80)
    print("\nShowing how to convert structured data into natural commentary format")
    
    # Load data
    df = load_starting_events()
    
    # Select 3 matches
    match_ids = select_3_diverse_matches(df)
    
    print(f"\nSelected Matches:")
    print(f"  1. Opening Match (No form data)")
    print(f"  2. Group Stage (Some form data)")
    print(f"  3. Final (Full tournament history)")
    
    # Analyze each match
    for i, match_id in enumerate(match_ids, 1):
        match_data = get_match_data(df, match_id)
        print_match_analysis(match_data, i)
    
    # Summary
    print("="*80)
    print("SUMMARY: Commentary Generation Process")
    print("="*80)
    print("""
KEY INSIGHTS:

1. CONDITIONAL LOGIC IS ESSENTIAL
   - Check if teams have previous matches
   - Adjust narrative based on tournament stage
   - Different templates for debuts vs experienced teams

2. DATA POINTS USED:
   ✓ Match context (stadium, stage, referee)
   ✓ Team records (wins, draws, losses)
   ✓ Goal statistics (scored, conceded, difference)
   ✓ Recent form (last result and opponent)
   ✓ Player lineups (key players)

3. COMMENTARY STRUCTURE:
   ① Opening: Set the scene
   ② Team A Form: Build context and narrative
   ③ Team B Form: Balance the story
   ④ Lineups: Introduce key players
   ⑤ Kick-off: Generate excitement

4. NATURAL LANGUAGE TECHNIQUES:
   - Vary sentence structure
   - Use transitional phrases
   - Include excitement/anticipation
   - Adapt tone to match importance (group stage vs final)
   - Incorporate statistics naturally

5. TEMPLATE FLEXIBILITY:
   - Opening match: Emphasis on debut, excitement
   - Mid-tournament: Focus on form and momentum
   - Final: Full context, high stakes narrative
    """)
    
    print("\n" + "="*80)
    print("✅ Analysis complete! Ready for NLP model training.")
    print("="*80)

if __name__ == "__main__":
    main()
