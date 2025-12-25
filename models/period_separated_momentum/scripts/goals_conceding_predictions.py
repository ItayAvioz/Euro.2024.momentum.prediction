import pandas as pd
import ast

print("="*70)
print("GOALS vs MOMENTUM - CONCEDING TEAM PREDICTIONS (75-90)")
print("="*70)
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

# Filter for goals in prediction minutes (75-90)
late_goals = goals_df[(goals_df['minute'] >= 75) & (goals_df['minute'] <= 95)]
print(f"Late goals (75-90+): {len(late_goals)}")

# Get team names for each match
match_teams = momentum_df.groupby('match_id').first()[['team_home', 'team_away']].to_dict('index')

# Analyze CONCEDING team predictions
results_scoring = []
results_conceding = []

for idx, goal in late_goals.iterrows():
    match_id = goal['match_id']
    goal_minute = int(goal['minute'])
    period = int(goal['period']) if pd.notna(goal.get('period')) else 2
    scoring_team = goal['team_name'] if pd.notna(goal.get('team_name')) else 'Unknown'
    
    # Find conceding team
    if match_id in match_teams:
        home = match_teams[match_id]['team_home']
        away = match_teams[match_id]['team_away']
        conceding_team = away if scoring_team == home else home
    else:
        continue
    
    # Check original minute = goal_minute - 5
    check_minute = goal_minute - 5
    
    # Get predictions for BOTH teams
    pred_data = predictions_df[
        (predictions_df['match_id'] == match_id) & 
        (predictions_df['minute_start'] == check_minute)
    ]
    
    for _, pred_row in pred_data.iterrows():
        pred_team = pred_row['team']
        pred_change = pred_row['prediction_value']
        actual_change = pred_row['actual_value']
        
        if pred_team == scoring_team and pd.notna(pred_change):
            results_scoring.append({
                'match_id': match_id,
                'goal_minute': goal_minute,
                'team': scoring_team,
                'role': 'SCORING',
                'predicted_change': pred_change,
                'actual_change': actual_change
            })
        elif pred_team == conceding_team and pd.notna(pred_change):
            results_conceding.append({
                'match_id': match_id,
                'goal_minute': goal_minute,
                'team': conceding_team,
                'role': 'CONCEDING',
                'predicted_change': pred_change,
                'actual_change': actual_change
            })

print()
print("="*70)
print("SCORING TEAM - PREDICTIONS")
print("="*70)

if len(results_scoring) > 0:
    score_df = pd.DataFrame(results_scoring)
    pos_pred = len(score_df[score_df['predicted_change'] > 0])
    neg_pred = len(score_df[score_df['predicted_change'] < 0])
    total = len(score_df)
    
    print(f"\nPredictions for SCORING team: {total}")
    print(f"  Predicted POSITIVE: {pos_pred} ({pos_pred/total*100:.1f}%)")
    print(f"  Predicted NEGATIVE: {neg_pred} ({neg_pred/total*100:.1f}%)")
    
    valid = score_df.dropna(subset=['actual_change'])
    pos_actual = len(valid[valid['actual_change'] > 0])
    neg_actual = len(valid[valid['actual_change'] < 0])
    
    print(f"\nActual for SCORING team: {len(valid)}")
    print(f"  Actual POSITIVE: {pos_actual} ({pos_actual/len(valid)*100:.1f}%)")
    print(f"  Actual NEGATIVE: {neg_actual} ({neg_actual/len(valid)*100:.1f}%)")

print()
print("="*70)
print("CONCEDING TEAM - PREDICTIONS")
print("="*70)

if len(results_conceding) > 0:
    conc_df = pd.DataFrame(results_conceding)
    pos_pred = len(conc_df[conc_df['predicted_change'] > 0])
    neg_pred = len(conc_df[conc_df['predicted_change'] < 0])
    total = len(conc_df)
    
    print(f"\nPredictions for CONCEDING team: {total}")
    print(f"  Predicted POSITIVE: {pos_pred} ({pos_pred/total*100:.1f}%)")
    print(f"  Predicted NEGATIVE: {neg_pred} ({neg_pred/total*100:.1f}%)")
    
    valid = conc_df.dropna(subset=['actual_change'])
    pos_actual = len(valid[valid['actual_change'] > 0])
    neg_actual = len(valid[valid['actual_change'] < 0])
    
    print(f"\nActual for CONCEDING team: {len(valid)}")
    print(f"  Actual POSITIVE: {pos_actual} ({pos_actual/len(valid)*100:.1f}%)")
    print(f"  Actual NEGATIVE: {neg_actual} ({neg_actual/len(valid)*100:.1f}%)")
    
    # Sign accuracy for conceding team
    conc_df['pred_sign'] = (conc_df['predicted_change'] > 0).astype(int)
    conc_df['actual_sign'] = (conc_df['actual_change'] > 0).astype(int)
    conc_df['sign_match'] = conc_df['pred_sign'] == conc_df['actual_sign']
    
    valid = conc_df.dropna(subset=['actual_change'])
    if len(valid) > 0:
        correct = valid['sign_match'].sum()
        print(f"\nSign accuracy for CONCEDING team: {correct}/{len(valid)} ({correct/len(valid)*100:.1f}%)")
        
        print(f"\nBreakdown (Conceding Team):")
        print(f"  Predicted POS, Actual POS: {len(valid[(valid['pred_sign']==1) & (valid['actual_sign']==1)])}")
        print(f"  Predicted NEG, Actual NEG: {len(valid[(valid['pred_sign']==0) & (valid['actual_sign']==0)])}")
        print(f"  Predicted POS, Actual NEG: {len(valid[(valid['pred_sign']==1) & (valid['actual_sign']==0)])}")
        print(f"  Predicted NEG, Actual POS: {len(valid[(valid['pred_sign']==0) & (valid['actual_sign']==1)])}")

print()
print("="*70)
print("SIDE BY SIDE COMPARISON")
print("="*70)

print(f"\n{'Metric':<35} {'SCORING':<15} {'CONCEDING':<15}")
print("-"*65)

if len(results_scoring) > 0 and len(results_conceding) > 0:
    score_df = pd.DataFrame(results_scoring)
    conc_df = pd.DataFrame(results_conceding)
    
    # Predicted
    s_pos = len(score_df[score_df['predicted_change'] > 0])
    s_neg = len(score_df[score_df['predicted_change'] < 0])
    c_pos = len(conc_df[conc_df['predicted_change'] > 0])
    c_neg = len(conc_df[conc_df['predicted_change'] < 0])
    
    print(f"{'Predicted POSITIVE':<35} {s_pos/len(score_df)*100:>10.1f}%    {c_pos/len(conc_df)*100:>10.1f}%")
    print(f"{'Predicted NEGATIVE':<35} {s_neg/len(score_df)*100:>10.1f}%    {c_neg/len(conc_df)*100:>10.1f}%")
    
    # Actual
    sv = score_df.dropna(subset=['actual_change'])
    cv = conc_df.dropna(subset=['actual_change'])
    
    sa_pos = len(sv[sv['actual_change'] > 0])
    sa_neg = len(sv[sv['actual_change'] < 0])
    ca_pos = len(cv[cv['actual_change'] > 0])
    ca_neg = len(cv[cv['actual_change'] < 0])
    
    print(f"{'Actual POSITIVE':<35} {sa_pos/len(sv)*100:>10.1f}%    {ca_pos/len(cv)*100:>10.1f}%")
    print(f"{'Actual NEGATIVE':<35} {sa_neg/len(sv)*100:>10.1f}%    {ca_neg/len(cv)*100:>10.1f}%")

print()
print("="*70)
print("SAMPLE: BOTH TEAMS AT GOAL MOMENTS")
print("="*70)

# Merge scoring and conceding for same goals
if len(results_scoring) > 0 and len(results_conceding) > 0:
    score_df = pd.DataFrame(results_scoring)
    conc_df = pd.DataFrame(results_conceding)
    
    merged = pd.merge(
        score_df[['match_id', 'goal_minute', 'team', 'predicted_change', 'actual_change']],
        conc_df[['match_id', 'goal_minute', 'team', 'predicted_change', 'actual_change']],
        on=['match_id', 'goal_minute'],
        suffixes=('_scorer', '_conceder')
    )
    
    print(f"\n{'Min':<5} {'Scorer':<12} {'Pred':<8} {'Act':<8} | {'Conceder':<12} {'Pred':<8} {'Act':<8}")
    print("-"*75)
    
    for _, row in merged.head(12).iterrows():
        sp = f"{row['predicted_change_scorer']:.2f}"
        sa = f"{row['actual_change_scorer']:.2f}" if pd.notna(row['actual_change_scorer']) else "NaN"
        cp = f"{row['predicted_change_conceder']:.2f}"
        ca = f"{row['actual_change_conceder']:.2f}" if pd.notna(row['actual_change_conceder']) else "NaN"
        
        print(f"{int(row['goal_minute']):<5} {row['team_scorer'][:10]:<12} {sp:<8} {sa:<8} | {row['team_conceder'][:10]:<12} {cp:<8} {ca:<8}")

print()
print("="*70)
print("KEY INSIGHT")
print("="*70)
print("""
EXPECTED PATTERN (if model is good):
- Scoring team:   Predicted POSITIVE, Actual POSITIVE
- Conceding team: Predicted NEGATIVE, Actual NEGATIVE

REALITY CHECK:
- Does the model predict opposite signs for scorer vs conceder?
- Does actual show opposite signs (scorer gaining, conceder losing)?
""")

