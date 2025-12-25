import pandas as pd
import ast

print("="*70)
print("GOALS vs MOMENTUM CHANGE - NEW CORRECT LOGIC")
print("="*70)
print()
print("Logic: Goal at minute G → Check change at display minute G-2")
print("       Which is original minute G-5 in the data")
print("       Change compares (G-5,G-4,G-3) vs (G-2,G-1,G)")
print("       Goal at G is in the FUTURE window!")
print()

# Load data
events = pd.read_csv('../../../Data/events_complete.csv', low_memory=False)
momentum_df = pd.read_csv('../outputs/momentum_by_period.csv')

# Get actual goals
shots = events[events['event_type'] == 'Shot'].copy()
actual_goals = []
for idx, row in shots.iterrows():
    if pd.notna(row['shot']):
        shot_str = str(row['shot'])
        if "'outcome'" in shot_str and "'Goal'" in shot_str:
            actual_goals.append(row)

goals_df = pd.DataFrame(actual_goals)
print(f"Total tournament goals: {len(goals_df)}")

# NEW LOGIC: For goal at minute G, check change at original minute G-5
results_new = []
for idx, goal in goals_df.iterrows():
    match_id = goal['match_id']
    goal_minute = int(goal['minute'])
    period = int(goal['period'])
    team = goal['team_name'] if pd.notna(goal.get('team_name')) else 'Unknown'
    
    # NEW: Check original minute = goal_minute - 5
    # This gives us the change that has the goal in its FUTURE window
    check_minute = goal_minute - 5
    
    mom_data = momentum_df[
        (momentum_df['match_id'] == match_id) & 
        (momentum_df['period'] == period) &
        (momentum_df['minute'] == check_minute)
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
            results_new.append({
                'match_id': match_id,
                'goal_minute': goal_minute,
                'check_minute': check_minute,
                'display_minute': check_minute + 3,  # For reference
                'period': period,
                'scoring_team': team,
                'scoring_team_change': scoring_team_change,
                'conceding_team_change': conceding_team_change
            })

results_df = pd.DataFrame(results_new)
print(f"Goals with valid momentum data: {len(results_df)}")

print("\n" + "="*70)
print("RESULTS COMPARISON")
print("="*70)

# NEW LOGIC RESULTS
if len(results_df) > 0:
    pos_new = len(results_df[results_df['scoring_team_change'] > 0])
    neg_new = len(results_df[results_df['scoring_team_change'] < 0])
    total_new = len(results_df)
    
    print(f"\n--- NEW LOGIC: Check display minute G-2 ---")
    print(f"(Change shows momentum shift INTO the goal-scoring window)")
    print()
    print(f"Scoring Team's Momentum Change:")
    print(f"  POSITIVE (gaining momentum): {pos_new} ({pos_new/total_new*100:.1f}%)")
    print(f"  NEGATIVE (losing momentum):  {neg_new} ({neg_new/total_new*100:.1f}%)")
    
    pos_c_new = len(results_df[results_df['conceding_team_change'] > 0])
    neg_c_new = len(results_df[results_df['conceding_team_change'] < 0])
    
    print(f"\nConceding Team's Momentum Change:")
    print(f"  POSITIVE (gaining momentum): {pos_c_new} ({pos_c_new/total_new*100:.1f}%)")
    print(f"  NEGATIVE (losing momentum):  {neg_c_new} ({neg_c_new/total_new*100:.1f}%)")

# Compare with OLD LOGIC
print("\n" + "-"*70)
print("OLD LOGIC (for comparison): Check minute G-1")
print("-"*70)

results_old = []
for idx, goal in goals_df.iterrows():
    match_id = goal['match_id']
    goal_minute = int(goal['minute'])
    period = int(goal['period'])
    team = goal['team_name'] if pd.notna(goal.get('team_name')) else 'Unknown'
    
    # OLD: Check minute - 1
    check_minute = goal_minute - 1
    
    mom_data = momentum_df[
        (momentum_df['match_id'] == match_id) & 
        (momentum_df['period'] == period) &
        (momentum_df['minute'] == check_minute)
    ]
    
    if len(mom_data) > 0:
        mom_row = mom_data.iloc[0]
        home_team = mom_row['team_home']
        away_team = mom_row['team_away']
        
        if team == home_team:
            scoring_team_change = mom_row['team_home_momentum_change']
        else:
            scoring_team_change = mom_row['team_away_momentum_change']
        
        if pd.notna(scoring_team_change):
            results_old.append({'scoring_team_change': scoring_team_change})

results_old_df = pd.DataFrame(results_old)
if len(results_old_df) > 0:
    pos_old = len(results_old_df[results_old_df['scoring_team_change'] > 0])
    neg_old = len(results_old_df[results_old_df['scoring_team_change'] < 0])
    total_old = len(results_old_df)
    
    print(f"\nScoring Team's Momentum Change (OLD):")
    print(f"  POSITIVE: {pos_old} ({pos_old/total_old*100:.1f}%)")
    print(f"  NEGATIVE: {neg_old} ({neg_old/total_old*100:.1f}%)")

print("\n" + "="*70)
print("SUMMARY COMPARISON")
print("="*70)
print()
print("                          OLD LOGIC    NEW LOGIC")
print("                          ---------    ---------")
if len(results_old_df) > 0 and len(results_df) > 0:
    print(f"Scoring team POSITIVE:    {pos_old/total_old*100:5.1f}%       {pos_new/total_new*100:5.1f}%")
    print(f"Scoring team NEGATIVE:    {neg_old/total_old*100:5.1f}%       {neg_new/total_new*100:5.1f}%")
    print()
    print(f"Conceding team POSITIVE:    N/A         {pos_c_new/total_new*100:5.1f}%")
    print(f"Conceding team NEGATIVE:    N/A         {neg_c_new/total_new*100:5.1f}%")

print("\n" + "="*70)
print("INTERPRETATION")
print("="*70)
if len(results_df) > 0:
    if pos_new > neg_new:
        print("\n✓ NEW LOGIC shows: Teams with POSITIVE momentum change score more!")
        print("  → Teams build momentum and then score")
    else:
        print("\n✓ NEW LOGIC shows: Teams with NEGATIVE momentum change score more!")
        print("  → Counter-attacks are dominant in Euro 2024")

