import pandas as pd

print("="*70)
print("CHECKING GOALS COUNT")
print("="*70)

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
print(f"\nTotal goals from events: {len(goals_df)}")

# Check why some are filtered out
match_teams = momentum_df.groupby('match_id').first()[['team_home', 'team_away']].to_dict('index')

analyzed = 0
not_in_momentum = 0
no_sequence_data = 0
early_goals = 0

for idx, goal in goals_df.iterrows():
    match_id = goal['match_id']
    goal_minute = int(goal['minute'])
    period = int(goal['period']) if pd.notna(goal.get('period')) else 1
    
    if match_id not in match_teams:
        not_in_momentum += 1
        continue
    
    # Goal window minute
    goal_window_minute = goal_minute - 5
    
    # Check if we have enough data before the goal
    match_mom = momentum_df[
        (momentum_df['match_id'] == match_id) & 
        (momentum_df['period'] == period)
    ].sort_values('minute')
    
    if len(match_mom) == 0:
        no_sequence_data += 1
        continue
    
    # Check if goal is too early (not enough minutes before)
    before_window = match_mom[match_mom['minute'] < goal_window_minute]
    if len(before_window) == 0:
        early_goals += 1
        print(f"  Early goal: minute {goal_minute}, period {period}, match {match_id}")
        continue
    
    analyzed += 1

print(f"\n--- Breakdown ---")
print(f"Analyzed: {analyzed}")
print(f"Not in momentum data: {not_in_momentum}")
print(f"No sequence data: {no_sequence_data}")
print(f"Early goals (< minute 6): {early_goals}")
print(f"Total: {analyzed + not_in_momentum + no_sequence_data + early_goals}")

# Count all momentum windows in the tournament
print("\n" + "="*70)
print("TOTAL MOMENTUM WINDOWS IN TOURNAMENT")
print("="*70)

total_windows = len(momentum_df)
print(f"\nTotal momentum windows: {total_windows}")
print(f"Total games: {momentum_df['match_id'].nunique()}")
print(f"Avg windows per game: {total_windows / momentum_df['match_id'].nunique():.1f}")

# Count sequences across ALL momentum windows (not just goals)
print("\n" + "="*70)
print("SEQUENCE DISTRIBUTION ACROSS ALL MOMENTUM WINDOWS")
print("="*70)

# For each window, count how many consecutive positive/negative changes it's part of
# This requires more complex calculation...

# Let's count how many windows have valid momentum change
valid_changes = momentum_df.dropna(subset=['team_home_momentum_change'])
print(f"\nWindows with valid momentum change: {len(valid_changes)}")

