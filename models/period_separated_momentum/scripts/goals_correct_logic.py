import pandas as pd

print("="*70)
print("GOALS - CORRECT LOGIC")
print("="*70)
print()
print("POSITIVE seq = Scoring team gaining momentum BEFORE scoring")
print("NEGATIVE seq = Conceding team losing momentum BEFORE conceding")
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

# Get team names for each match
match_teams = momentum_df.groupby('match_id').first()[['team_home', 'team_away']].to_dict('index')

results = []

for idx, goal in goals_df.iterrows():
    match_id = goal['match_id']
    goal_minute = int(goal['minute'])
    period = int(goal['period']) if pd.notna(goal.get('period')) else 1
    scoring_team = goal['team_name'] if pd.notna(goal.get('team_name')) else 'Unknown'
    
    # Find conceding team
    if match_id not in match_teams:
        continue
    home = match_teams[match_id]['team_home']
    away = match_teams[match_id]['team_away']
    conceding_team = away if scoring_team == home else home
    
    match_mom = momentum_df[
        (momentum_df['match_id'] == match_id) & 
        (momentum_df['period'] == period)
    ].sort_values('minute')
    
    if len(match_mom) == 0:
        continue
    
    # Columns for scoring and conceding teams
    scoring_is_home = (scoring_team == home)
    scoring_change_col = 'team_home_momentum_change' if scoring_is_home else 'team_away_momentum_change'
    conceding_change_col = 'team_away_momentum_change' if scoring_is_home else 'team_home_momentum_change'
    
    goal_window_minute = goal_minute - 5
    before_window = match_mom[match_mom['minute'] < goal_window_minute].sort_values('minute', ascending=False)
    
    # SCORING TEAM: Count POSITIVE sequence
    pos_seq_scoring = 0
    pos_minutes_scoring = []
    for _, row in before_window.iterrows():
        change = row[scoring_change_col]
        if pd.notna(change) and change > 0:
            pos_seq_scoring += 1
            pos_minutes_scoring.append(int(row['minute']))
        else:
            break
    
    # CONCEDING TEAM: Count NEGATIVE sequence
    neg_seq_conceding = 0
    neg_minutes_conceding = []
    for _, row in before_window.iterrows():
        change = row[conceding_change_col]
        if pd.notna(change) and change < 0:
            neg_seq_conceding += 1
            neg_minutes_conceding.append(int(row['minute']))
        else:
            break
    
    # Get events for scoring team's positive sequence
    pos_events = []
    if pos_seq_scoring > 0 and len(pos_minutes_scoring) > 0:
        game_events = llm_df[llm_df['match_id'] == match_id]
        seen_minutes = set()
        for i, m in enumerate(pos_minutes_scoring[:5]):
            if i == 0:
                # First window: 3 events
                for em in [m, m+1, m+2]:
                    if em not in seen_minutes:
                        minute_events = game_events[
                            (game_events['period'] == period) &
                            (game_events['minute'] == em)
                        ]['detected_type'].value_counts()
                        if len(minute_events) > 0:
                            pos_events.append(f"{em}:{minute_events.index[0]}")
                        seen_minutes.add(em)
            else:
                # Additional windows: only 1 new event (m+2)
                em = m + 2
                if em not in seen_minutes:
                    minute_events = game_events[
                        (game_events['period'] == period) &
                        (game_events['minute'] == em)
                    ]['detected_type'].value_counts()
                    if len(minute_events) > 0:
                        pos_events.append(f"{em}:{minute_events.index[0]}")
                    seen_minutes.add(em)
    
    # Get events for conceding team's negative sequence
    neg_events = []
    if neg_seq_conceding > 0 and len(neg_minutes_conceding) > 0:
        game_events = llm_df[llm_df['match_id'] == match_id]
        seen_minutes = set()
        for i, m in enumerate(neg_minutes_conceding[:5]):
            if i == 0:
                # First window: 3 events
                for em in [m, m+1, m+2]:
                    if em not in seen_minutes:
                        minute_events = game_events[
                            (game_events['period'] == period) &
                            (game_events['minute'] == em)
                        ]['detected_type'].value_counts()
                        if len(minute_events) > 0:
                            neg_events.append(f"{em}:{minute_events.index[0]}")
                        seen_minutes.add(em)
            else:
                # Additional windows: only 1 new event
                em = m + 2
                if em not in seen_minutes:
                    minute_events = game_events[
                        (game_events['period'] == period) &
                        (game_events['minute'] == em)
                    ]['detected_type'].value_counts()
                    if len(minute_events) > 0:
                        neg_events.append(f"{em}:{minute_events.index[0]}")
                    seen_minutes.add(em)
    
    results.append({
        'goal_minute': goal_minute,
        'scoring_team': scoring_team,
        'conceding_team': conceding_team,
        'pos_seq_scoring': pos_seq_scoring,
        'neg_seq_conceding': neg_seq_conceding,
        'pos_events': pos_events,
        'neg_events': neg_events
    })

df = pd.DataFrame(results)
print(f"Goals analyzed: {len(df)}")

print("\n" + "="*70)
print("🟢 POSITIVE SEQUENCES (Scoring Team)")
print("="*70)
print("\nScoring team had X consecutive POSITIVE changes BEFORE scoring:")

pos_counts = df['pos_seq_scoring'].value_counts().sort_index()
total = len(df)
print(f"\n{'Seq':<6} {'Goals':<10}")
print("-"*20)
for seq_len in range(8):
    count = pos_counts.get(seq_len, 0)
    print(f"{seq_len:<6} {count:<10}")
print("-"*20)
print(f"{'Total':<6} {total:<10}")

print("\n" + "="*70)
print("🔴 NEGATIVE SEQUENCES (Conceding Team)")
print("="*70)
print("\nConceding team had X consecutive NEGATIVE changes BEFORE conceding:")

neg_counts = df['neg_seq_conceding'].value_counts().sort_index()
print(f"\n{'Seq':<6} {'Goals':<10}")
print("-"*20)
for seq_len in range(8):
    count = neg_counts.get(seq_len, 0)
    print(f"{seq_len:<6} {count:<10}")
print("-"*20)
print(f"{'Total':<6} {total:<10}")

print("\n" + "="*70)
print("EVENTS IN SEQUENCES")
print("="*70)
print("\nLogic: First window = 3 events (23,24,25)")
print("       Each additional seq = +1 new event (26, 27, ...)")
print("       Total events for Seq N = 3 + (N-1) = N + 2")

print("\n🟢 Events in POSITIVE Sequences (Scoring Team):")
all_pos_events = []
for events in df[df['pos_seq_scoring'] >= 1]['pos_events']:
    for e in events:
        if ':' in str(e):
            all_pos_events.append(str(e).split(':')[1])

if all_pos_events:
    pos_ev_counts = pd.Series(all_pos_events).value_counts()
    print(f"\n{'Event':<20} {'Count':<8}")
    print("-"*30)
    for event, count in pos_ev_counts.head(10).items():
        print(f"{event:<20} {count:<8}")

print("\n🔴 Events in NEGATIVE Sequences (Conceding Team):")
all_neg_events = []
for events in df[df['neg_seq_conceding'] >= 1]['neg_events']:
    for e in events:
        if ':' in str(e):
            all_neg_events.append(str(e).split(':')[1])

if all_neg_events:
    neg_ev_counts = pd.Series(all_neg_events).value_counts()
    print(f"\n{'Event':<20} {'Count':<8}")
    print("-"*30)
    for event, count in neg_ev_counts.head(10).items():
        print(f"{event:<20} {count:<8}")

print("\n" + "="*70)
print("KEY INSIGHT")
print("="*70)
pos_1_plus = len(df[df['pos_seq_scoring'] >= 1])
neg_1_plus = len(df[df['neg_seq_conceding'] >= 1])
print(f"""
Goals where SCORING team had ≥1 positive seq: {pos_1_plus} ({pos_1_plus/total*100:.1f}%)
Goals where CONCEDING team had ≥1 negative seq: {neg_1_plus} ({neg_1_plus/total*100:.1f}%)

Interpretation:
- {pos_1_plus/total*100:.1f}% of goals: Scorer was building momentum
- {neg_1_plus/total*100:.1f}% of goals: Conceder was losing momentum
""")

