import pandas as pd
import ast

print("="*70)
print("GOALS vs MOMENTUM SEQUENCE ANALYSIS")
print("="*70)
print()
print("Question: Do goals come after a SEQUENCE of positive momentum changes?")
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

# For each goal, check the momentum sequence before it
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
    
    # Get momentum changes leading up to the goal
    # Check display minute G-2 (original minute G-5) where goal is in future window
    # Also check the sequence before that
    
    # Original minute for goal window: G-5 (so change covers G-5 to G-2 vs G-2 to G)
    check_minute = goal_minute - 5
    
    # Get the last 5 momentum changes before the goal
    before_goal = match_mom[match_mom['minute'] <= check_minute].tail(5)
    
    if len(before_goal) == 0:
        continue
    
    # Count consecutive positive changes (sequence)
    changes = before_goal[change_col].dropna().tolist()
    
    # Check if the immediate change (at check_minute) is positive
    immediate_change = None
    immediate_row = match_mom[match_mom['minute'] == check_minute]
    if len(immediate_row) > 0:
        immediate_change = immediate_row.iloc[0][change_col]
    
    # Count sequence of positive changes before goal
    positive_seq = 0
    for c in reversed(changes):
        if c > 0:
            positive_seq += 1
        else:
            break
    
    # Get events during the momentum sequence
    seq_events = []
    if positive_seq > 0:
        # Get minutes covered by the sequence
        seq_minutes = before_goal.tail(positive_seq)['minute'].tolist()
        for m in seq_minutes:
            # Each minute m in momentum covers events m, m+1, m+2
            game_events = llm_df[
                (llm_df['match_id'] == match_id) &
                (llm_df['period'] == period) &
                (llm_df['minute'].isin([m, m+1, m+2]))
            ]['detected_type'].value_counts()
            if len(game_events) > 0:
                seq_events.extend(game_events.head(2).index.tolist())
    
    results.append({
        'match_id': match_id,
        'goal_minute': goal_minute,
        'period': period,
        'scoring_team': scoring_team,
        'immediate_change': immediate_change,
        'positive_seq_length': positive_seq,
        'last_5_changes': changes[-5:] if len(changes) >= 5 else changes,
        'seq_events': list(set(seq_events))[:5] if seq_events else []
    })

results_df = pd.DataFrame(results)
print(f"Goals analyzed: {len(results_df)}")

# Analysis
print("\n" + "="*70)
print("IMMEDIATE MOMENTUM CHANGE BEFORE GOAL")
print("="*70)

valid = results_df.dropna(subset=['immediate_change'])
pos_immediate = len(valid[valid['immediate_change'] > 0])
neg_immediate = len(valid[valid['immediate_change'] < 0])

print(f"\nGoals with POSITIVE immediate change: {pos_immediate} ({pos_immediate/len(valid)*100:.1f}%)")
print(f"Goals with NEGATIVE immediate change: {neg_immediate} ({neg_immediate/len(valid)*100:.1f}%)")

print("\n" + "="*70)
print("POSITIVE SEQUENCE LENGTH BEFORE GOAL")
print("="*70)

seq_counts = results_df['positive_seq_length'].value_counts().sort_index()
print(f"\nDistribution of positive sequence length before goals:")
for seq_len, count in seq_counts.items():
    pct = count/len(results_df)*100
    bar = "█" * int(pct/2)
    print(f"  Seq {seq_len}: {count:3d} ({pct:5.1f}%) {bar}")

# Goals with sequence >= 2
seq_2_plus = len(results_df[results_df['positive_seq_length'] >= 2])
seq_3_plus = len(results_df[results_df['positive_seq_length'] >= 3])
print(f"\nGoals with sequence ≥2: {seq_2_plus} ({seq_2_plus/len(results_df)*100:.1f}%)")
print(f"Goals with sequence ≥3: {seq_3_plus} ({seq_3_plus/len(results_df)*100:.1f}%)")

print("\n" + "="*70)
print("EVENTS IN POSITIVE MOMENTUM SEQUENCES")
print("="*70)

# Collect all events from sequences
all_seq_events = []
for events in results_df[results_df['positive_seq_length'] >= 2]['seq_events']:
    all_seq_events.extend(events)

if all_seq_events:
    event_counts = pd.Series(all_seq_events).value_counts()
    print(f"\nTop events in positive sequences leading to goals:")
    for event, count in event_counts.head(10).items():
        print(f"  {event}: {count}")

print("\n" + "="*70)
print("SAMPLE: GOALS WITH POSITIVE SEQUENCES")
print("="*70)

seq_goals = results_df[results_df['positive_seq_length'] >= 2].head(10)
print(f"\n{'Min':<5} {'Team':<15} {'Seq':<5} {'Imm.Chg':<10} {'Events'}")
print("-"*70)
for _, row in seq_goals.iterrows():
    imm = f"{row['immediate_change']:.2f}" if pd.notna(row['immediate_change']) else "N/A"
    events = ', '.join(row['seq_events'][:3]) if row['seq_events'] else '-'
    print(f"{row['goal_minute']:<5} {row['scoring_team'][:13]:<15} {row['positive_seq_length']:<5} {imm:<10} {events}")

print("\n" + "="*70)
print("SAMPLE: GOALS WITHOUT POSITIVE SEQUENCES (Counter-attacks?)")
print("="*70)

no_seq_goals = results_df[results_df['positive_seq_length'] == 0].head(10)
print(f"\n{'Min':<5} {'Team':<15} {'Imm.Chg':<10} {'Last 3 Changes'}")
print("-"*70)
for _, row in no_seq_goals.iterrows():
    imm = f"{row['immediate_change']:.2f}" if pd.notna(row['immediate_change']) else "N/A"
    changes = [f"{c:.1f}" for c in row['last_5_changes'][-3:]] if row['last_5_changes'] else []
    print(f"{row['goal_minute']:<5} {row['scoring_team'][:13]:<15} {imm:<10} {changes}")

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print(f"""
Total Goals: {len(results_df)}

Immediate Change (at goal window):
  - Positive: {pos_immediate} ({pos_immediate/len(valid)*100:.1f}%)
  - Negative: {neg_immediate} ({neg_immediate/len(valid)*100:.1f}%)

Sequence Before Goal:
  - No sequence (0): {len(results_df[results_df['positive_seq_length']==0])} goals
  - Sequence 1:      {len(results_df[results_df['positive_seq_length']==1])} goals
  - Sequence 2+:     {seq_2_plus} goals ({seq_2_plus/len(results_df)*100:.1f}%)
  - Sequence 3+:     {seq_3_plus} goals ({seq_3_plus/len(results_df)*100:.1f}%)

Key Insight:
  Goals with positive sequence = Buildup play
  Goals without sequence = Counter-attack / Set piece
""")

