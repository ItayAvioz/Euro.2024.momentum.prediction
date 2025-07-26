import pandas as pd
import numpy as np
import ast

print("=== BALL CONTROL RATIOS vs GAME RESULTS ANALYSIS ===")
print("Analyzing if consecutive events, possessions, and turnover ratios predict match outcomes")
print("(Note: No real home/away advantage - Euro 2024 all in Germany)")

# Load the data
matches = pd.read_csv('../Data/matches_complete.csv')
events = pd.read_csv('../Data/events_complete.csv')

print(f"Total matches: {len(matches)}")
print(f"Total events: {len(events)}")

# Function to extract team name from dictionary string
def extract_team_name(team_dict_str):
    try:
        if pd.isna(team_dict_str):
            return None
        team_dict = ast.literal_eval(team_dict_str)
        return team_dict.get('name', None)
    except:
        return None

# Extract team names
events['team_name'] = events['team'].apply(extract_team_name)
events['possession_team_name'] = events['possession_team'].apply(extract_team_name)

# Create match-by-match analysis
ball_control_analysis = []

for _, match in matches.iterrows():
    match_id = match['match_id']
    team_a = match['home_team_name']  # Designated as "home"
    team_b = match['away_team_name']  # Designated as "away"
    stage = match['stage']
    
    # Get final scores
    team_a_score = int(match['home_score']) if pd.notna(match['home_score']) else 0
    team_b_score = int(match['away_score']) if pd.notna(match['away_score']) else 0
    
    # Get match events
    match_events = events[events['match_id'] == match_id].copy()
    match_events = match_events.dropna(subset=['possession'])
    
    if len(match_events) == 0:
        continue
    
    match_events = match_events.sort_values(['period', 'minute', 'second'])
    
    # Initialize period data storage
    period_data = {}
    
    # Analyze each period
    for period in [1, 2]:
        period_events = match_events[match_events['period'] == period]
        
        if len(period_events) == 0:
            continue
        
        # Calculate consecutive events per possession for each team
        possession_groups = period_events.groupby('possession')
        
        team_a_consecutive = []
        team_b_consecutive = []
        
        for possession_id, possession_events in possession_groups:
            team_counts = possession_events['team_name'].value_counts()
            
            for team, count in team_counts.items():
                if team == team_a:
                    team_a_consecutive.append(count)
                elif team == team_b:
                    team_b_consecutive.append(count)
        
        # Calculate turnovers for each team
        possession_team_events = period_events.dropna(subset=['possession_team_name'])
        team_a_turnovers = 0
        team_b_turnovers = 0
        
        if len(possession_team_events) > 0:
            prev_team = None
            for _, event in possession_team_events.iterrows():
                current_team = event['possession_team_name']
                if prev_team is not None and prev_team != current_team:
                    if prev_team == team_a:
                        team_a_turnovers += 1
                    elif prev_team == team_b:
                        team_b_turnovers += 1
                prev_team = current_team
        
        # Calculate statistics
        team_a_avg_consecutive = np.mean(team_a_consecutive) if team_a_consecutive else 0
        team_a_possessions = len(team_a_consecutive)
        
        team_b_avg_consecutive = np.mean(team_b_consecutive) if team_b_consecutive else 0
        team_b_possessions = len(team_b_consecutive)
        
        # Store period data
        period_data[period] = {
            'team_a_avg_consecutive': team_a_avg_consecutive,
            'team_a_possessions': team_a_possessions,
            'team_a_turnovers': team_a_turnovers,
            'team_b_avg_consecutive': team_b_avg_consecutive,
            'team_b_possessions': team_b_possessions,
            'team_b_turnovers': team_b_turnovers
        }
    
    # Calculate halftime goals (from first period only)
    if 1 in period_data:
        # Count goals in first half
        fh_shots = match_events[(match_events['period'] == 1) & (match_events['shot'].notna())]
        team_a_fh_goals = 0
        team_b_fh_goals = 0
        
        for _, shot_event in fh_shots.iterrows():
            try:
                shot_data = ast.literal_eval(shot_event['shot']) if isinstance(shot_event['shot'], str) else shot_event['shot']
                if isinstance(shot_data, dict) and shot_data.get('outcome', {}).get('name') == 'Goal':
                    if shot_event['team_name'] == team_a:
                        team_a_fh_goals += 1
                    elif shot_event['team_name'] == team_b:
                        team_b_fh_goals += 1
            except:
                continue
    else:
        team_a_fh_goals = team_b_fh_goals = 0
    
    # Calculate ratios and determine if they reflect results
    for period in [1, 2]:
        if period not in period_data:
            continue
        
        data = period_data[period]
        
        # Calculate ratios (avoid division by zero)
        consecutive_ratio = (data['team_a_avg_consecutive'] / data['team_b_avg_consecutive'] 
                           if data['team_b_avg_consecutive'] > 0 else float('inf'))
        
        possessions_ratio = (data['team_a_possessions'] / data['team_b_possessions'] 
                           if data['team_b_possessions'] > 0 else float('inf'))
        
        turnovers_ratio = (data['team_a_turnovers'] / data['team_b_turnovers'] 
                         if data['team_b_turnovers'] > 0 else float('inf'))
        
        # Determine results
        if period == 1:
            # Halftime result
            if team_a_fh_goals > team_b_fh_goals:
                period_result = f"{team_a_fh_goals}-{team_b_fh_goals} (A)"
                period_winner = "Team A"
            elif team_b_fh_goals > team_a_fh_goals:
                period_result = f"{team_a_fh_goals}-{team_b_fh_goals} (B)"
                period_winner = "Team B"
            else:
                period_result = f"{team_a_fh_goals}-{team_b_fh_goals} (D)"
                period_winner = "Draw"
        else:
            # Full-time result
            if team_a_score > team_b_score:
                period_result = f"{team_a_score}-{team_b_score} (A)"
                period_winner = "Team A"
            elif team_b_score > team_a_score:
                period_result = f"{team_a_score}-{team_b_score} (B)"
                period_winner = "Team B"
            else:
                period_result = f"{team_a_score}-{team_b_score} (D)"
                period_winner = "Draw"
        
        # Check if ratios reflect results
        # Consecutive events: higher = better control
        consecutive_reflects = (
            (consecutive_ratio > 1.0 and period_winner == "Team A") or
            (consecutive_ratio < 1.0 and period_winner == "Team B") or
            (0.9 <= consecutive_ratio <= 1.1 and period_winner == "Draw")
        )
        
        # Possessions: can be interpreted both ways, but generally more = more control
        possessions_reflects = (
            (possessions_ratio > 1.0 and period_winner == "Team A") or
            (possessions_ratio < 1.0 and period_winner == "Team B") or
            (0.9 <= possessions_ratio <= 1.1 and period_winner == "Draw")
        )
        
        # Turnovers: lower = better (fewer turnovers)
        turnovers_reflects = (
            (turnovers_ratio < 1.0 and period_winner == "Team A") or
            (turnovers_ratio > 1.0 and period_winner == "Team B") or
            (0.9 <= turnovers_ratio <= 1.1 and period_winner == "Draw")
        )
        
        ball_control_analysis.append({
            'match_id': match_id,
            'team_a': team_a,
            'team_b': team_b,
            'stage': stage,
            'period': period,
            'period_name': 'First Half' if period == 1 else 'Second Half',
            'period_result': period_result,
            'period_winner': period_winner,
            'consecutive_ratio': consecutive_ratio,
            'possessions_ratio': possessions_ratio,
            'turnovers_ratio': turnovers_ratio,
            'consecutive_reflects': consecutive_reflects,
            'possessions_reflects': possessions_reflects,
            'turnovers_reflects': turnovers_reflects,
            'team_a_consecutive': data['team_a_avg_consecutive'],
            'team_b_consecutive': data['team_b_avg_consecutive'],
            'team_a_possessions': data['team_a_possessions'],
            'team_b_possessions': data['team_b_possessions'],
            'team_a_turnovers': data['team_a_turnovers'],
            'team_b_turnovers': data['team_b_turnovers'],
            'match_date': match['match_date']
        })

# Convert to DataFrame
analysis_df = pd.DataFrame(ball_control_analysis)

print(f"\nSuccessfully analyzed {len(analysis_df)} period performances")

# ===== OVERALL REFLECTION STATISTICS =====
print("\n" + "="*80)
print("BALL CONTROL RATIOS REFLECTION OF RESULTS")
print("="*80)

consecutive_reflects = len(analysis_df[analysis_df['consecutive_reflects'] == True])
possessions_reflects = len(analysis_df[analysis_df['possessions_reflects'] == True])
turnovers_reflects = len(analysis_df[analysis_df['turnovers_reflects'] == True])

total_periods = len(analysis_df)

print(f"CONSECUTIVE EVENTS RATIO reflects result:")
print(f"  YES: {consecutive_reflects} periods ({(consecutive_reflects/total_periods)*100:.1f}%)")
print(f"  NO: {total_periods - consecutive_reflects} periods ({((total_periods - consecutive_reflects)/total_periods)*100:.1f}%)")

print(f"\nPOSSESSIONS RATIO reflects result:")
print(f"  YES: {possessions_reflects} periods ({(possessions_reflects/total_periods)*100:.1f}%)")
print(f"  NO: {total_periods - possessions_reflects} periods ({((total_periods - possessions_reflects)/total_periods)*100:.1f}%)")

print(f"\nTURNOVERS RATIO reflects result:")
print(f"  YES: {turnovers_reflects} periods ({(turnovers_reflects/total_periods)*100:.1f}%)")
print(f"  NO: {total_periods - turnovers_reflects} periods ({((total_periods - turnovers_reflects)/total_periods)*100:.1f}%)")

# ===== PERIOD COMPARISON =====
print("\n" + "="*80)
print("REFLECTION ACCURACY BY PERIOD")
print("="*80)

for period in [1, 2]:
    period_data = analysis_df[analysis_df['period'] == period]
    period_name = "First Half" if period == 1 else "Second Half"
    
    cons_reflects = len(period_data[period_data['consecutive_reflects'] == True])
    poss_reflects = len(period_data[period_data['possessions_reflects'] == True])
    turn_reflects = len(period_data[period_data['turnovers_reflects'] == True])
    total = len(period_data)
    
    print(f"\n{period_name} ({total} periods):")
    print(f"  Consecutive Events: {cons_reflects}/{total} ({(cons_reflects/total)*100:.1f}%)")
    print(f"  Possessions: {poss_reflects}/{total} ({(poss_reflects/total)*100:.1f}%)")
    print(f"  Turnovers: {turn_reflects}/{total} ({(turn_reflects/total)*100:.1f}%)")

# ===== STAGE ANALYSIS =====
print("\n" + "="*80)
print("REFLECTION ACCURACY BY STAGE")
print("="*80)

for stage in analysis_df['stage'].unique():
    stage_data = analysis_df[analysis_df['stage'] == stage]
    
    cons_reflects = len(stage_data[stage_data['consecutive_reflects'] == True])
    poss_reflects = len(stage_data[stage_data['possessions_reflects'] == True])
    turn_reflects = len(stage_data[stage_data['turnovers_reflects'] == True])
    total = len(stage_data)
    
    print(f"\n{stage.upper()} ({total} periods):")
    print(f"  Consecutive Events: {cons_reflects}/{total} ({(cons_reflects/total)*100:.1f}%)")
    print(f"  Possessions: {poss_reflects}/{total} ({(poss_reflects/total)*100:.1f}%)")
    print(f"  Turnovers: {turn_reflects}/{total} ({(turn_reflects/total)*100:.1f}%)")

# ===== DETAILED EXAMPLES =====
print("\n" + "="*80)
print("SAMPLE ANALYSIS RESULTS")
print("="*80)

print("Format: Team A vs Team B | Period | Result | Consecutive Ratio | Possessions Ratio | Turnovers Ratio")
print("-" * 100)

for _, game in analysis_df.head(10).iterrows():
    cons_str = f"{game['consecutive_ratio']:.2f}" if game['consecutive_ratio'] != float('inf') else "∞"
    poss_str = f"{game['possessions_ratio']:.2f}" if game['possessions_ratio'] != float('inf') else "∞"
    turn_str = f"{game['turnovers_ratio']:.2f}" if game['turnovers_ratio'] != float('inf') else "∞"
    
    print(f"{game['team_a']} vs {game['team_b']} | {game['period_name']} | {game['period_result']}")
    print(f"  Ratios: Consecutive {cons_str} | Possessions {poss_str} | Turnovers {turn_str}")
    print(f"  Reflects: Consecutive {game['consecutive_reflects']} | Possessions {game['possessions_reflects']} | Turnovers {game['turnovers_reflects']}")
    print("-" * 100)

# ===== BEST PREDICTORS =====
print("\n" + "="*80)
print("BEST BALL CONTROL PREDICTORS")
print("="*80)

predictor_accuracy = {
    'Consecutive Events': (consecutive_reflects/total_periods)*100,
    'Possessions': (possessions_reflects/total_periods)*100,
    'Turnovers': (turnovers_reflects/total_periods)*100
}

sorted_predictors = sorted(predictor_accuracy.items(), key=lambda x: x[1], reverse=True)

print("RANKING BY PREDICTION ACCURACY:")
for i, (predictor, accuracy) in enumerate(sorted_predictors, 1):
    print(f"{i}. {predictor}: {accuracy:.1f}%")

# ===== EXTREME RATIOS =====
print("\n" + "="*80)
print("EXTREME BALL CONTROL RATIOS")
print("="*80)

# Filter out infinite values for analysis
finite_data = analysis_df[
    (analysis_df['consecutive_ratio'] != float('inf')) & 
    (analysis_df['possessions_ratio'] != float('inf')) & 
    (analysis_df['turnovers_ratio'] != float('inf'))
]

print("HIGHEST CONSECUTIVE EVENTS DOMINANCE:")
top_consecutive = finite_data.nlargest(5, 'consecutive_ratio')
for _, row in top_consecutive.iterrows():
    print(f"  {row['team_a']} vs {row['team_b']} ({row['stage']}, {row['period_name']}): {row['consecutive_ratio']:.2f}")

print("\nHIGHEST POSSESSION DOMINANCE:")
top_possessions = finite_data.nlargest(5, 'possessions_ratio')
for _, row in top_possessions.iterrows():
    print(f"  {row['team_a']} vs {row['team_b']} ({row['stage']}, {row['period_name']}): {row['possessions_ratio']:.2f}")

print("\nLOWEST TURNOVER RATIOS (Best Ball Security):")
top_turnovers = finite_data.nsmallest(5, 'turnovers_ratio')
for _, row in top_turnovers.iterrows():
    print(f"  {row['team_a']} vs {row['team_b']} ({row['stage']}, {row['period_name']}): {row['turnovers_ratio']:.2f}")

# ===== SAVE RESULTS =====
print("\n" + "="*80)
print("SAVING RESULTS")
print("="*80)

analysis_df.to_csv('ball_control_ratios_vs_results.csv', index=False)
print("File saved: ball_control_ratios_vs_results.csv")

print(f"\n=== BALL CONTROL RATIOS vs RESULTS ANALYSIS COMPLETE ===")
best_predictor, best_accuracy = sorted_predictors[0]
print(f"Best Predictor: {best_predictor} ({best_accuracy:.1f}% accuracy)")
print(f"Overall Finding: Ball control ratios have varying predictive power for match results") 