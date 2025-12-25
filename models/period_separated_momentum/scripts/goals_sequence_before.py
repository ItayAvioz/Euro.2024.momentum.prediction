import pandas as pd

print("="*70)
print("GOALS - SEQUENCE BEFORE GOAL (Excluding Goal Window)")
print("="*70)
print()

# Load data
events = pd.read_csv('../../../Data/events_complete.csv', low_memory=False)
momentum_df = pd.read_csv('../outputs/momentum_by_period.csv')
llm_df = pd.read_csv('../../../NLP - Commentator/research/10_llm_commentary/data/llm_commentary/all_matches_V3_20251209_193514.csv')

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

results = []

for idx, goal in goals_df.iterrows():
    match_id = goal['match_id']
    goal_minute = int(goal['minute'])
    period = int(goal['period']) if pd.notna(goal.get('period')) else 1
    scoring_team = goal['team_name'] if pd.notna(goal.get('team_name')) else 'Unknown'
    
    # Get momentum data for this match and period
    match_mom = momentum_df[
        (momentum_df['match_id'] == match_id) & 
        (momentum_df['period'] == period)
    ].sort_values('minute')
    
    if len(match_mom) == 0:
        continue
    
    # Determine if scoring team is home or away
    home_team = match_mom.iloc[0]['team_home']
    is_home = (scoring_team == home_team)
    change_col = 'team_home_momentum_change' if is_home else 'team_away_momentum_change'
    
    # Goal window is at original minute G-5
    # BEFORE goal starts at original minute G-6, G-7, G-8...
    goal_window_minute = goal_minute - 5
    
    # Get sequence BEFORE the goal window (starting from G-6)
    before_window = match_mom[match_mom['minute'] < goal_window_minute].sort_values('minute', ascending=False)
    
    # Count consecutive positive changes BEFORE the goal
    sequence_length = 0
    sequence_changes = []
    sequence_minutes = []
    
    for _, row in before_window.iterrows():
        change = row[change_col]
        if pd.notna(change) and change > 0:
            sequence_length += 1
            sequence_changes.append(change)
            sequence_minutes.append(int(row['minute']))
        else:
            break  # Stop at first non-positive
    
    # Get events in the sequence
    seq_events = []
    if sequence_length > 0 and len(sequence_minutes) > 0:
        game_events = llm_df[llm_df['match_id'] == match_id]
        for m in sequence_minutes[:3]:  # First 3 minutes of sequence
            minute_events = game_events[
                (game_events['period'] == period) &
                (game_events['minute'].isin([m, m+1, m+2]))
            ]['detected_type'].value_counts()
            if len(minute_events) > 0:
                seq_events.append(f"{m}:{minute_events.index[0]}")
    
    results.append({
        'match_id': match_id,
        'goal_minute': goal_minute,
        'period': period,
        'scoring_team': scoring_team,
        'seq_before_length': sequence_length,
        'seq_changes': sequence_changes[:5],
        'seq_events': seq_events
    })

results_df = pd.DataFrame(results)
print(f"Goals analyzed: {len(results_df)}")

print("\n" + "="*70)
print("SEQUENCE BEFORE GOAL (Excluding Goal Window)")
print("="*70)

seq_counts = results_df['seq_before_length'].value_counts().sort_index()
print(f"\nDistribution of positive sequence BEFORE goal:")
for seq_len, count in seq_counts.head(8).items():
    pct = count/len(results_df)*100
    bar = "█" * int(pct/2)
    print(f"  Seq {seq_len}: {count:3d} ({pct:5.1f}%) {bar}")

seq_1_plus = len(results_df[results_df['seq_before_length'] >= 1])
seq_2_plus = len(results_df[results_df['seq_before_length'] >= 2])
seq_3_plus = len(results_df[results_df['seq_before_length'] >= 3])

print(f"\nGoals with sequence ≥1 BEFORE: {seq_1_plus} ({seq_1_plus/len(results_df)*100:.1f}%)")
print(f"Goals with sequence ≥2 BEFORE: {seq_2_plus} ({seq_2_plus/len(results_df)*100:.1f}%)")
print(f"Goals with sequence ≥3 BEFORE: {seq_3_plus} ({seq_3_plus/len(results_df)*100:.1f}%)")

print("\n" + "="*70)
print("EVENTS IN SEQUENCES BEFORE GOALS")
print("="*70)

all_seq_events = []
for events in results_df[results_df['seq_before_length'] >= 1]['seq_events']:
    for e in events:
        if ':' in e:
            all_seq_events.append(e.split(':')[1])

if all_seq_events:
    event_counts = pd.Series(all_seq_events).value_counts()
    print(f"\nTop events in sequences BEFORE goals:")
    for event, count in event_counts.head(10).items():
        print(f"  {event}: {count}")

print("\n" + "="*70)
print("SAMPLE: GOALS WITH POSITIVE SEQUENCE BEFORE")
print("="*70)

seq_goals = results_df[results_df['seq_before_length'] >= 2].head(10)
print(f"\n{'GoalMin':<8} {'Team':<15} {'SeqBefore':<10} {'Events Before Goal'}")
print("-"*70)
for _, row in seq_goals.iterrows():
    events = ', '.join(row['seq_events'][:3]) if row['seq_events'] else '-'
    print(f"{row['goal_minute']:<8} {row['scoring_team'][:13]:<15} {row['seq_before_length']:<10} {events}")

print("\n" + "="*70)
print("SAMPLE: GOALS WITHOUT SEQUENCE BEFORE (Counter-attacks)")
print("="*70)

no_seq = results_df[results_df['seq_before_length'] == 0].head(10)
print(f"\n{'GoalMin':<8} {'Team':<15} {'SeqBefore':<10}")
print("-"*50)
for _, row in no_seq.iterrows():
    print(f"{row['goal_minute']:<8} {row['scoring_team'][:13]:<15} {row['seq_before_length']:<10}")

print("\n" + "="*70)
print("KEY INSIGHT FOR PREDICTION")
print("="*70)
print(f"""
If model predicts POSITIVE momentum change:
  → 76.8% chance of goal (immediate window)
  
If model predicts SEQUENCE of positive changes:
  → {seq_1_plus/len(results_df)*100:.1f}% of goals had ≥1 positive BEFORE
  → {seq_2_plus/len(results_df)*100:.1f}% of goals had ≥2 positive BEFORE
  → {seq_3_plus/len(results_df)*100:.1f}% of goals had ≥3 positive BEFORE

PRACTICAL USE:
  1. Model predicts +0.3 at minute 30 → Check previous predictions
  2. If minute 29 was also +positive → Sequence building!
  3. Sequence = Higher goal probability
""")

