import pandas as pd

# Load data
momentum_df = pd.read_csv('../outputs/momentum_by_period.csv')
events_df = pd.read_csv('../../../Data/events_complete.csv', low_memory=False)

# Get goals from events
goals = events_df[events_df['event_type'] == 'Shot'].copy()
# Check if it's a goal (shot outcome)
goals = goals[goals['shot'].notna()]
goals_only = []
for idx, row in goals.iterrows():
    if isinstance(row['shot'], str) and 'Goal' in row['shot']:
        goals_only.append(row)

goals_df = pd.DataFrame(goals_only)
print(f"Total goals found: {len(goals_df)}")
print(f"Columns: {goals_df.columns.tolist()[:10]}")

# For each goal, check the momentum change of the scoring team
print("\n" + "="*70)
print("ANALYSIS 1: Goals vs Momentum Change")
print("="*70)

results = []
for idx, goal in goals_df.iterrows():
    match_id = goal['match_id']
    minute = goal['minute']
    period = goal['period']
    team = goal['team_name'] if pd.notna(goal.get('team_name')) else 'Unknown'
    
    # Find momentum data for this minute
    mom_data = momentum_df[
        (momentum_df['match_id'] == match_id) & 
        (momentum_df['period'] == period) &
        (momentum_df['minute'] == minute)
    ]
    
    if len(mom_data) > 0:
        mom_row = mom_data.iloc[0]
        home_team = mom_row['team_home']
        away_team = mom_row['team_away']
        
        # Determine if scoring team is home or away
        if team == home_team:
            scoring_team_change = mom_row['team_home_momentum_change']
            conceding_team_change = mom_row['team_away_momentum_change']
        else:
            scoring_team_change = mom_row['team_away_momentum_change']
            conceding_team_change = mom_row['team_home_momentum_change']
        
        results.append({
            'match_id': match_id,
            'minute': minute,
            'period': period,
            'scoring_team': team,
            'scoring_team_change': scoring_team_change,
            'conceding_team_change': conceding_team_change
        })

results_df = pd.DataFrame(results)
print(f"\nGoals with momentum data: {len(results_df)}")

# Analyze
if len(results_df) > 0:
    pos_change_goals = len(results_df[results_df['scoring_team_change'] > 0])
    neg_change_goals = len(results_df[results_df['scoring_team_change'] < 0])
    zero_change_goals = len(results_df[results_df['scoring_team_change'] == 0])
    
    print(f"\n--- Scoring Team's Momentum Change at Goal ---")
    print(f"Goals with POSITIVE momentum change: {pos_change_goals} ({pos_change_goals/len(results_df)*100:.1f}%)")
    print(f"Goals with NEGATIVE momentum change: {neg_change_goals} ({neg_change_goals/len(results_df)*100:.1f}%)")
    print(f"Goals with ZERO momentum change: {zero_change_goals}")
    
    # Conceding team
    pos_concede = len(results_df[results_df['conceding_team_change'] > 0])
    neg_concede = len(results_df[results_df['conceding_team_change'] < 0])
    
    print(f"\n--- Conceding Team's Momentum Change at Goal ---")
    print(f"Goals against with POSITIVE momentum change: {pos_concede} ({pos_concede/len(results_df)*100:.1f}%)")
    print(f"Goals against with NEGATIVE momentum change: {neg_concede} ({neg_concede/len(results_df)*100:.1f}%)")
    
    print("\n--- Sample Goals ---")
    print(results_df[['minute', 'scoring_team', 'scoring_team_change', 'conceding_team_change']].head(10).to_string())

