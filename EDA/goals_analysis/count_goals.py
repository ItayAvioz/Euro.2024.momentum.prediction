import pandas as pd

# Load the data
df = pd.read_csv('../Data/final/euro_2024_events.csv')

# Count goals by type
goal_events = df[df['type'].str.contains('Goal', na=False)]
print('Goal event types and counts:')
print(goal_events['type'].value_counts())
print(f'\nTotal goal events: {len(goal_events)}')

# Check shot outcome goals
shot_goals = df[df['shot_outcome'] == 'Goal']
print(f'\nShot outcome goals: {len(shot_goals)}')

# Check for any other goal indicators
if 'goal' in df.columns:
    other_goals = df[df['goal'] == True]
    print(f'Goal column goals: {len(other_goals)}')

# Check period distribution
print('\nGoals by period:')
print(goal_events['period'].value_counts().sort_index())

# Check if there are any extra time goals
if 'minute' in df.columns:
    extra_time_goals = goal_events[goal_events['minute'] > 90]
    print(f'\nExtra time goals (minute > 90): {len(extra_time_goals)}')
    if len(extra_time_goals) > 0:
        print('Extra time goal details:')
        print(extra_time_goals[['minute', 'second', 'period', 'match_id']].head(10))

# Check specific periods for extra time
period_3_goals = goal_events[goal_events['period'] == 3]
period_4_goals = goal_events[goal_events['period'] == 4]
period_5_goals = goal_events[goal_events['period'] == 5]

print(f'\nPeriod 3 goals (First extra time): {len(period_3_goals)}')
print(f'Period 4 goals (Second extra time): {len(period_4_goals)}')
print(f'Period 5 goals (Penalty shootout): {len(period_5_goals)}')

print(f'\nTotal goals in regulation (periods 1-2): {len(goal_events[goal_events["period"].isin([1, 2])])}')
print(f'Total goals in extra time (periods 3-4): {len(goal_events[goal_events["period"].isin([3, 4])])}')
print(f'Total goals including extra time: {len(goal_events[goal_events["period"].isin([1, 2, 3, 4])])}') 