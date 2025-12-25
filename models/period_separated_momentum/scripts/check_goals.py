import pandas as pd
import ast

events = pd.read_csv('../../../Data/events_complete.csv', low_memory=False)
shots = events[events['event_type'] == 'Shot'].copy()

print("Checking shot outcomes...")

# Parse shot column to find actual goals
actual_goals = []
for idx, row in shots.iterrows():
    if pd.notna(row['shot']):
        shot_str = str(row['shot'])
        if "'outcome'" in shot_str and "'Goal'" in shot_str:
            actual_goals.append(row)

goals_df = pd.DataFrame(actual_goals)
print(f"Actual tournament goals: {len(goals_df)}")

# Now analyze with proper goals
momentum_df = pd.read_csv('../outputs/momentum_by_period.csv')

results = []
for idx, goal in goals_df.iterrows():
    match_id = goal['match_id']
    minute = int(goal['minute'])
    period = int(goal['period'])
    team = goal['team_name'] if pd.notna(goal.get('team_name')) else 'Unknown'
    
    # Find momentum data for the minute BEFORE the goal (to avoid contamination)
    mom_data = momentum_df[
        (momentum_df['match_id'] == match_id) & 
        (momentum_df['period'] == period) &
        (momentum_df['minute'] == minute - 1)  # Check minute before
    ]
    
    if len(mom_data) > 0:
        mom_row = mom_data.iloc[0]
        home_team = mom_row['team_home']
        away_team = mom_row['team_away']
        
        if team == home_team:
            scoring_team_change = mom_row['team_home_momentum_change']
            conceding_team_change = mom_row['team_away_momentum_change']
        else:
            scoring_team_change = mom_row['team_away_momentum_change']
            conceding_team_change = mom_row['team_home_momentum_change']
        
        if pd.notna(scoring_team_change):
            results.append({
                'match_id': match_id,
                'minute': minute,
                'period': period,
                'scoring_team': team,
                'scoring_team_change': scoring_team_change,
                'conceding_team_change': conceding_team_change
            })

results_df = pd.DataFrame(results)
print(f"Goals with momentum data (minute before): {len(results_df)}")

if len(results_df) > 0:
    pos = len(results_df[results_df['scoring_team_change'] > 0])
    neg = len(results_df[results_df['scoring_team_change'] < 0])
    total = len(results_df)
    
    print(f"\n--- Scoring Team's Momentum Change BEFORE Goal ---")
    print(f"POSITIVE change (team gaining momentum): {pos} ({pos/total*100:.1f}%)")
    print(f"NEGATIVE change (team losing momentum): {neg} ({neg/total*100:.1f}%)")
    
    # Conceding team
    pos_c = len(results_df[results_df['conceding_team_change'] > 0])
    neg_c = len(results_df[results_df['conceding_team_change'] < 0])
    
    print(f"\n--- Conceding Team's Momentum Change BEFORE Goal ---")
    print(f"POSITIVE change: {pos_c} ({pos_c/total*100:.1f}%)")
    print(f"NEGATIVE change: {neg_c} ({neg_c/total*100:.1f}%)")
