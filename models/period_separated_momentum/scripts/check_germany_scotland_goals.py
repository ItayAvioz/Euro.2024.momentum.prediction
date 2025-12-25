import pandas as pd

# Load events
events = pd.read_csv('../../../Data/events_complete.csv', low_memory=False)

# Find Germany vs Scotland match
matches = events[['match_id', 'team_name']].drop_duplicates()
print("Looking for Germany vs Scotland...")

# Get events for this match
germany_events = events[events['team_name'] == 'Germany']
scotland_events = events[events['team_name'] == 'Scotland']

# Find common match
germany_matches = set(germany_events['match_id'].unique())
scotland_matches = set(scotland_events['match_id'].unique())
common = germany_matches.intersection(scotland_matches)
print(f"Common match IDs: {common}")

match_id = list(common)[0]
match_events = events[events['match_id'] == match_id]

print(f"\nMatch ID: {match_id}")

# Find all goals (shots with Goal outcome)
shots = match_events[match_events['event_type'] == 'Shot']
goals = []
for idx, row in shots.iterrows():
    if pd.notna(row.get('shot')):
        shot_str = str(row['shot'])
        if "'outcome'" in shot_str and "'Goal'" in shot_str:
            goals.append({
                'minute': row['minute'],
                'period': row['period'],
                'team': row['team_name'],
                'type': 'Shot Goal'
            })

# Find own goals
own_goals = match_events[match_events['event_type'] == 'Own Goal Against']
for idx, row in own_goals.iterrows():
    goals.append({
        'minute': row['minute'],
        'period': row['period'],
        'team': row['team_name'],  # Team that conceded
        'type': 'Own Goal'
    })

# Sort by minute
goals_df = pd.DataFrame(goals).sort_values(['period', 'minute'])

print("\n=== ALL GOALS IN GERMANY vs SCOTLAND ===")
print(goals_df.to_string(index=False))

print(f"\nTotal goals: {len(goals_df)}")

# Count by team
print("\nGoals by team (scoring):")
for team in goals_df['team'].unique():
    team_goals = goals_df[goals_df['team'] == team]
    shot_goals = len(team_goals[team_goals['type'] == 'Shot Goal'])
    own_goals_count = len(team_goals[team_goals['type'] == 'Own Goal'])
    print(f"  {team}: {shot_goals} shot goals, {own_goals_count} own goals (against)")

# Check LLM commentary for Goal events
print("\n=== LLM COMMENTARY - Goal events ===")
llm = pd.read_csv('../../../NLP - Commentator/research/10_llm_commentary/data/llm_commentary/all_matches_V3_20251209_193514.csv')
llm_match = llm[llm['match_id'] == match_id]
goal_events = llm_match[llm_match['detected_type'] == 'Goal']
print(goal_events[['minute', 'period', 'detected_type']].to_string(index=False))

