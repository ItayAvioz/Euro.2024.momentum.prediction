import pandas as pd
import ast

print("="*70)
print("GOALS vs MOMENTUM CHANGE - PREDICTION MINUTES (75-90)")
print("="*70)
print()
print("Checking if goals in minutes 75-90 follow the same pattern")
print("These are the minutes where we PREDICT momentum change!")
print()

# Load data
events = pd.read_csv('../../../Data/events_complete.csv', low_memory=False)
momentum_df = pd.read_csv('../outputs/momentum_by_period.csv')
predictions_df = pd.read_csv('../outputs/arimax_predictions_by_period.csv')

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

# Filter for goals in prediction minutes (75-90)
late_goals = goals_df[(goals_df['minute'] >= 75) & (goals_df['minute'] <= 95)]
print(f"Goals in minutes 75-90+: {len(late_goals)}")

# Analyze with CORRECT logic
results_real = []  # Using real momentum change
results_pred = []  # Using PREDICTED momentum change

for idx, goal in late_goals.iterrows():
    match_id = goal['match_id']
    goal_minute = int(goal['minute'])
    period = int(goal['period']) if pd.notna(goal.get('period')) else 2
    team = goal['team_name'] if pd.notna(goal.get('team_name')) else 'Unknown'
    
    # Check original minute = goal_minute - 5
    check_minute = goal_minute - 5
    
    # Get REAL momentum change
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
            real_change = mom_row['team_home_momentum_change']
            is_home = True
        else:
            real_change = mom_row['team_away_momentum_change']
            is_home = False
        
        if pd.notna(real_change):
            results_real.append({
                'match_id': match_id,
                'goal_minute': goal_minute,
                'check_minute': check_minute,
                'scoring_team': team,
                'real_change': real_change,
                'is_home': is_home
            })
    
    # Get PREDICTED momentum change
    pred_data = predictions_df[
        (predictions_df['match_id'] == match_id) & 
        (predictions_df['minute_start'] == check_minute)
    ]
    
    if len(pred_data) > 0:
        # Find the right team's prediction
        for _, pred_row in pred_data.iterrows():
            pred_team = pred_row['team']
            if pred_team == team:
                pred_change = pred_row['prediction_value']
                actual_change = pred_row['actual_value']
                
                if pd.notna(pred_change):
                    results_pred.append({
                        'match_id': match_id,
                        'goal_minute': goal_minute,
                        'check_minute': check_minute,
                        'scoring_team': team,
                        'predicted_change': pred_change,
                        'actual_change': actual_change
                    })

print()
print("="*70)
print("RESULTS - REAL MOMENTUM CHANGE (minutes 75-90)")
print("="*70)

if len(results_real) > 0:
    real_df = pd.DataFrame(results_real)
    pos_real = len(real_df[real_df['real_change'] > 0])
    neg_real = len(real_df[real_df['real_change'] < 0])
    total_real = len(real_df)
    
    print(f"\nGoals with valid REAL momentum data: {total_real}")
    print(f"\nScoring Team's REAL Momentum Change:")
    print(f"  POSITIVE (gaining momentum): {pos_real} ({pos_real/total_real*100:.1f}%)")
    print(f"  NEGATIVE (losing momentum):  {neg_real} ({neg_real/total_real*100:.1f}%)")

print()
print("="*70)
print("RESULTS - PREDICTED MOMENTUM CHANGE (minutes 75-90)")
print("="*70)

if len(results_pred) > 0:
    pred_df = pd.DataFrame(results_pred)
    pos_pred = len(pred_df[pred_df['predicted_change'] > 0])
    neg_pred = len(pred_df[pred_df['predicted_change'] < 0])
    total_pred = len(pred_df)
    
    print(f"\nGoals with valid PREDICTED momentum data: {total_pred}")
    print(f"\nScoring Team's PREDICTED Momentum Change:")
    print(f"  POSITIVE (gaining momentum): {pos_pred} ({pos_pred/total_pred*100:.1f}%)")
    print(f"  NEGATIVE (losing momentum):  {neg_pred} ({neg_pred/total_pred*100:.1f}%)")
    
    # Check actual values too
    pos_actual = len(pred_df[pred_df['actual_change'] > 0])
    neg_actual = len(pred_df[pred_df['actual_change'] < 0])
    na_actual = pred_df['actual_change'].isna().sum()
    
    print(f"\nScoring Team's ACTUAL Momentum Change (same goals):")
    print(f"  POSITIVE: {pos_actual} ({pos_actual/(total_pred-na_actual)*100:.1f}%)" if total_pred-na_actual > 0 else "  N/A")
    print(f"  NEGATIVE: {neg_actual} ({neg_actual/(total_pred-na_actual)*100:.1f}%)" if total_pred-na_actual > 0 else "  N/A")
    print(f"  NaN: {na_actual}")

print()
print("="*70)
print("PREDICTION ACCURACY FOR GOAL-SCORING MOMENTS")
print("="*70)

if len(results_pred) > 0:
    pred_df = pd.DataFrame(results_pred)
    
    # Check if prediction sign matches actual sign
    pred_df['pred_sign'] = (pred_df['predicted_change'] > 0).astype(int)
    pred_df['actual_sign'] = (pred_df['actual_change'] > 0).astype(int)
    pred_df['sign_match'] = pred_df['pred_sign'] == pred_df['actual_sign']
    
    valid = pred_df.dropna(subset=['actual_change'])
    if len(valid) > 0:
        correct = valid['sign_match'].sum()
        total = len(valid)
        print(f"\nSign accuracy for goal-scoring moments: {correct}/{total} ({correct/total*100:.1f}%)")
        
        print(f"\nBreakdown:")
        print(f"  Predicted POS, Actual POS: {len(valid[(valid['pred_sign']==1) & (valid['actual_sign']==1)])}")
        print(f"  Predicted NEG, Actual NEG: {len(valid[(valid['pred_sign']==0) & (valid['actual_sign']==0)])}")
        print(f"  Predicted POS, Actual NEG: {len(valid[(valid['pred_sign']==1) & (valid['actual_sign']==0)])}")
        print(f"  Predicted NEG, Actual POS: {len(valid[(valid['pred_sign']==0) & (valid['actual_sign']==1)])}")

print()
print("="*70)
print("COMPARISON: ALL GOALS vs LATE GOALS (75-90)")
print("="*70)

# Load all goals analysis
all_goals_results = []
for idx, goal in goals_df.iterrows():
    match_id = goal['match_id']
    goal_minute = int(goal['minute'])
    period = int(goal['period']) if pd.notna(goal.get('period')) else 1
    team = goal['team_name'] if pd.notna(goal.get('team_name')) else 'Unknown'
    
    check_minute = goal_minute - 5
    
    mom_data = momentum_df[
        (momentum_df['match_id'] == match_id) & 
        (momentum_df['period'] == period) &
        (momentum_df['minute'] == check_minute)
    ]
    
    if len(mom_data) > 0:
        mom_row = mom_data.iloc[0]
        home_team = mom_row['team_home']
        
        if team == home_team:
            real_change = mom_row['team_home_momentum_change']
        else:
            real_change = mom_row['team_away_momentum_change']
        
        if pd.notna(real_change):
            all_goals_results.append({'real_change': real_change, 'minute': goal_minute})

all_df = pd.DataFrame(all_goals_results)
early_df = all_df[all_df['minute'] < 75]
late_df = all_df[all_df['minute'] >= 75]

print(f"\n{'Category':<25} {'Positive %':<15} {'Negative %':<15} {'Count':<10}")
print("-"*65)

if len(early_df) > 0:
    pos_e = len(early_df[early_df['real_change'] > 0])
    neg_e = len(early_df[early_df['real_change'] < 0])
    print(f"{'Early Goals (0-74)':<25} {pos_e/len(early_df)*100:>10.1f}%    {neg_e/len(early_df)*100:>10.1f}%    {len(early_df)}")

if len(late_df) > 0:
    pos_l = len(late_df[late_df['real_change'] > 0])
    neg_l = len(late_df[late_df['real_change'] < 0])
    print(f"{'Late Goals (75-90+)':<25} {pos_l/len(late_df)*100:>10.1f}%    {neg_l/len(late_df)*100:>10.1f}%    {len(late_df)}")

if len(all_df) > 0:
    pos_a = len(all_df[all_df['real_change'] > 0])
    neg_a = len(all_df[all_df['real_change'] < 0])
    print(f"{'ALL Goals':<25} {pos_a/len(all_df)*100:>10.1f}%    {neg_a/len(all_df)*100:>10.1f}%    {len(all_df)}")

print()
print("="*70)
print("SAMPLE: LATE GOALS WITH PREDICTIONS")
print("="*70)
if len(results_pred) > 0:
    pred_df = pd.DataFrame(results_pred)
    print(f"\n{'Min':<5} {'Team':<20} {'Predicted':<12} {'Actual':<12} {'Match?'}")
    print("-"*55)
    for _, row in pred_df.head(15).iterrows():
        pred = row['predicted_change']
        actual = row['actual_change']
        match = "✓" if (pd.notna(actual) and (pred > 0) == (actual > 0)) else "✗" if pd.notna(actual) else "N/A"
        actual_str = f"{actual:.3f}" if pd.notna(actual) else "NaN"
        print(f"{int(row['goal_minute']):<5} {row['scoring_team'][:18]:<20} {pred:>10.3f}   {actual_str:>10}   {match}")

