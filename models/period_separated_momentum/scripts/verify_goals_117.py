import pandas as pd

print("="*70)
print("VERIFYING 117 GOALS")
print("="*70)

events = pd.read_csv('../../../Data/events_complete.csv', low_memory=False)

# Method 1: Shot with Goal outcome
shots = events[events['event_type'] == 'Shot'].copy()
goals_method1 = []
for idx, row in shots.iterrows():
    if pd.notna(row['shot']):
        shot_str = str(row['shot'])
        if "'outcome'" in shot_str and "'Goal'" in shot_str:
            goals_method1.append(row)

print(f"\nMethod 1 (Shot with Goal outcome): {len(goals_method1)} goals")

# Method 2: type_name == 'Shot' and shot_outcome_name == 'Goal'
if 'type_name' in events.columns and 'shot_outcome_name' in events.columns:
    goals_method2 = events[(events['type_name'] == 'Shot') & (events['shot_outcome_name'] == 'Goal')]
    print(f"Method 2 (type_name/shot_outcome_name): {len(goals_method2)} goals")

# Method 3: event_type == 'Goal'
if 'Goal' in events['event_type'].values:
    goals_method3 = events[events['event_type'] == 'Goal']
    print(f"Method 3 (event_type == 'Goal'): {len(goals_method3)} goals")

# Check for Own Goals
print("\n--- Own Goals Check ---")
own_goals = events[events['event_type'] == 'Own Goal Against']
print(f"Own Goal Against events: {len(own_goals)}")

# Total shots
print(f"\nTotal Shot events: {len(shots)}")

# Check unique matches
goals_df = pd.DataFrame(goals_method1)
print(f"\nUnique matches with goals: {goals_df['match_id'].nunique()}")
print(f"Total matches: {events['match_id'].nunique()}")

# Check for duplicates
print("\n--- Duplicate Check ---")
print(f"Duplicate goal rows: {goals_df.duplicated().sum()}")

# Goals per period
print("\n--- Goals by Period ---")
period_counts = goals_df['period'].value_counts().sort_index()
for period, count in period_counts.items():
    print(f"Period {period}: {count} goals")
print(f"Total: {period_counts.sum()}")

# Check periods 3 and 4 (extra time)
extra_time_goals = goals_df[goals_df['period'].isin([3, 4])]
print(f"\nExtra time goals (periods 3+4): {len(extra_time_goals)}")

# Regulation goals only
regulation_goals = goals_df[goals_df['period'].isin([1, 2])]
print(f"Regulation goals (periods 1+2): {len(regulation_goals)}")

# Check if 117 = regulation without own goals?
print("\n--- Final Check ---")
print(f"Shot goals (all periods): {len(goals_df)}")
print(f"Own goals: {len(own_goals)}")
print(f"Shot goals + Own goals: {len(goals_df) + len(own_goals)}")
print(f"Shot goals (regulation only): {len(regulation_goals)}")
print(f"Shot + Own (regulation): {len(regulation_goals) + len(own_goals[own_goals['period'].isin([1,2])])}")

# Let's see what's the actual count
print("\n" + "="*70)
print("ACTUAL 117 GOALS BREAKDOWN")
print("="*70)

# From the dashboard: 117 goals in 51 matches
# Let's count by match
goals_per_match = goals_df.groupby('match_id').size()
own_goals_per_match = own_goals.groupby('match_id').size() if len(own_goals) > 0 else pd.Series()

print(f"\nTotal shot goals: {goals_per_match.sum()}")
print(f"Total own goals: {own_goals_per_match.sum() if len(own_goals_per_match) > 0 else 0}")

# Combined
total_goals = goals_per_match.sum()
if len(own_goals_per_match) > 0:
    total_goals += own_goals_per_match.sum()
print(f"\nTotal (shot + own goals): {total_goals}")

# Check for penalty shootout goals
penalty_shootout = events[events['period'] == 5]  # Period 5 is usually penalty shootout
print(f"\nPenalty shootout events: {len(penalty_shootout)}")

