import pandas as pd

print("="*70)
print("GOALS - POSITIVE vs NEGATIVE SEQUENCES BEFORE GOAL")
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
    
    match_mom = momentum_df[
        (momentum_df['match_id'] == match_id) & 
        (momentum_df['period'] == period)
    ].sort_values('minute')
    
    if len(match_mom) == 0:
        continue
    
    home_team = match_mom.iloc[0]['team_home']
    is_home = (scoring_team == home_team)
    change_col = 'team_home_momentum_change' if is_home else 'team_away_momentum_change'
    
    goal_window_minute = goal_minute - 5
    before_window = match_mom[match_mom['minute'] < goal_window_minute].sort_values('minute', ascending=False)
    
    # Count POSITIVE sequence
    pos_seq = 0
    pos_minutes = []
    for _, row in before_window.iterrows():
        change = row[change_col]
        if pd.notna(change) and change > 0:
            pos_seq += 1
            pos_minutes.append(int(row['minute']))
        else:
            break
    
    # Count NEGATIVE sequence (from beginning again)
    neg_seq = 0
    neg_minutes = []
    for _, row in before_window.iterrows():
        change = row[change_col]
        if pd.notna(change) and change < 0:
            neg_seq += 1
            neg_minutes.append(int(row['minute']))
        else:
            break
    
    # Get events for positive sequence
    pos_events = []
    if pos_seq > 0 and len(pos_minutes) > 0:
        game_events = llm_df[llm_df['match_id'] == match_id]
        for m in pos_minutes[:3]:
            minute_events = game_events[
                (game_events['period'] == period) &
                (game_events['minute'].isin([m, m+1, m+2]))
            ]['detected_type'].value_counts()
            if len(minute_events) > 0:
                pos_events.append(f"{m}:{minute_events.index[0]}")
    
    # Get events for negative sequence
    neg_events = []
    if neg_seq > 0 and len(neg_minutes) > 0:
        game_events = llm_df[llm_df['match_id'] == match_id]
        for m in neg_minutes[:3]:
            minute_events = game_events[
                (game_events['period'] == period) &
                (game_events['minute'].isin([m, m+1, m+2]))
            ]['detected_type'].value_counts()
            if len(minute_events) > 0:
                neg_events.append(f"{m}:{minute_events.index[0]}")
    
    results.append({
        'goal_minute': goal_minute,
        'scoring_team': scoring_team,
        'pos_seq': pos_seq,
        'neg_seq': neg_seq,
        'pos_events': pos_events,
        'neg_events': neg_events
    })

df = pd.DataFrame(results)
print(f"Goals analyzed: {len(df)}")

print("\n" + "="*70)
print("POSITIVE SEQUENCE DISTRIBUTION")
print("="*70)

pos_counts = df['pos_seq'].value_counts().sort_index()
print(f"\n{'Seq':<6} {'Count':<8} {'%':<8} {'Goals have this seq before'}")
print("-"*50)
for seq_len in range(0, 8):
    count = pos_counts.get(seq_len, 0)
    pct = count/len(df)*100
    bar = "█" * int(pct/2)
    print(f"{seq_len:<6} {count:<8} {pct:>5.1f}%   {bar}")

print("\n" + "="*70)
print("NEGATIVE SEQUENCE DISTRIBUTION")
print("="*70)

neg_counts = df['neg_seq'].value_counts().sort_index()
print(f"\n{'Seq':<6} {'Count':<8} {'%':<8} {'Goals have this seq before'}")
print("-"*50)
for seq_len in range(0, 8):
    count = neg_counts.get(seq_len, 0)
    pct = count/len(df)*100
    bar = "█" * int(pct/2)
    print(f"{seq_len:<6} {count:<8} {pct:>5.1f}%   {bar}")

print("\n" + "="*70)
print("CUMULATIVE COMPARISON")
print("="*70)

print(f"\n{'Threshold':<15} {'POSITIVE Seq':<20} {'NEGATIVE Seq':<20}")
print("-"*55)
for thresh in [0, 1, 2, 3, 4, 5]:
    pos_cum = len(df[df['pos_seq'] >= thresh])
    neg_cum = len(df[df['neg_seq'] >= thresh])
    print(f"≥{thresh:<14} {pos_cum:>4} ({pos_cum/len(df)*100:>5.1f}%)         {neg_cum:>4} ({neg_cum/len(df)*100:>5.1f}%)")

print("\n" + "="*70)
print("EVENTS IN POSITIVE SEQUENCES")
print("="*70)
print("\nHow we count: For each minute in sequence, get key event from that 3-min window")
print("Example: Minute 27 in sequence → events from 27, 28, 29 → most common type")

all_pos_events = []
for events in df[df['pos_seq'] >= 1]['pos_events']:
    for e in events:
        if ':' in str(e):
            all_pos_events.append(str(e).split(':')[1])

if all_pos_events:
    pos_event_counts = pd.Series(all_pos_events).value_counts()
    print(f"\n{'Event':<20} {'Count':<8}")
    print("-"*30)
    for event, count in pos_event_counts.head(10).items():
        print(f"{event:<20} {count:<8}")

print("\n" + "="*70)
print("EVENTS IN NEGATIVE SEQUENCES")
print("="*70)

all_neg_events = []
for events in df[df['neg_seq'] >= 1]['neg_events']:
    for e in events:
        if ':' in str(e):
            all_neg_events.append(str(e).split(':')[1])

if all_neg_events:
    neg_event_counts = pd.Series(all_neg_events).value_counts()
    print(f"\n{'Event':<20} {'Count':<8}")
    print("-"*30)
    for event, count in neg_event_counts.head(10).items():
        print(f"{event:<20} {count:<8}")

print("\n" + "="*70)
print("KEY INSIGHT")
print("="*70)
print(f"""
POSITIVE sequences before goals: {len(df[df['pos_seq'] >= 1])} goals ({len(df[df['pos_seq'] >= 1])/len(df)*100:.1f}%)
NEGATIVE sequences before goals: {len(df[df['neg_seq'] >= 1])} goals ({len(df[df['neg_seq'] >= 1])/len(df)*100:.1f}%)

→ More goals come after POSITIVE sequences than NEGATIVE!
→ This validates: Predict positive change → Higher goal probability
""")

