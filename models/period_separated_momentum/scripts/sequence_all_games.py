import pandas as pd

print("="*70)
print("SEQUENCE DISTRIBUTION - ALL GAMES")
print("="*70)

momentum_df = pd.read_csv('../outputs/momentum_by_period.csv')

print(f"\nTotal momentum windows: {len(momentum_df)}")
print(f"Total games: {momentum_df['match_id'].nunique()}")

# For each momentum window, calculate the sequence length
# Sequence = consecutive same-sign changes

def calculate_sequences(df):
    """Calculate positive and negative sequence lengths for each window"""
    results = []
    
    for match_id in df['match_id'].unique():
        match_df = df[df['match_id'] == match_id]
        
        for period in match_df['period'].unique():
            period_df = match_df[match_df['period'] == period].sort_values('minute')
            
            home_changes = period_df['team_home_momentum_change'].values
            away_changes = period_df['team_away_momentum_change'].values
            minutes = period_df['minute'].values
            
            for i in range(len(period_df)):
                # Count positive sequence for home team (going backwards)
                pos_seq_home = 0
                for j in range(i-1, -1, -1):
                    if pd.notna(home_changes[j]) and home_changes[j] > 0:
                        pos_seq_home += 1
                    else:
                        break
                
                # Count negative sequence for home team (going backwards)
                neg_seq_home = 0
                for j in range(i-1, -1, -1):
                    if pd.notna(home_changes[j]) and home_changes[j] < 0:
                        neg_seq_home += 1
                    else:
                        break
                
                # Same for away team
                pos_seq_away = 0
                for j in range(i-1, -1, -1):
                    if pd.notna(away_changes[j]) and away_changes[j] > 0:
                        pos_seq_away += 1
                    else:
                        break
                
                neg_seq_away = 0
                for j in range(i-1, -1, -1):
                    if pd.notna(away_changes[j]) and away_changes[j] < 0:
                        neg_seq_away += 1
                    else:
                        break
                
                results.append({
                    'match_id': match_id,
                    'period': period,
                    'minute': minutes[i],
                    'pos_seq_home': pos_seq_home,
                    'neg_seq_home': neg_seq_home,
                    'pos_seq_away': pos_seq_away,
                    'neg_seq_away': neg_seq_away
                })
    
    return pd.DataFrame(results)

print("\nCalculating sequences for all windows...")
seq_df = calculate_sequences(momentum_df)

# Combine home and away (each window counted twice, once per team)
all_pos_seqs = list(seq_df['pos_seq_home']) + list(seq_df['pos_seq_away'])
all_neg_seqs = list(seq_df['neg_seq_home']) + list(seq_df['neg_seq_away'])

print("\n" + "="*70)
print("POSITIVE SEQUENCE DISTRIBUTION (All Team-Windows)")
print("="*70)

pos_counts = pd.Series(all_pos_seqs).value_counts().sort_index()
total_pos = len(all_pos_seqs)

print(f"\n{'Seq':<6} {'Count':<10} {'%':<10}")
print("-"*30)
for seq_len in range(10):
    count = pos_counts.get(seq_len, 0)
    pct = count/total_pos*100
    print(f"{seq_len:<6} {count:<10} {pct:.1f}%")
print("-"*30)
print(f"{'Total':<6} {total_pos:<10}")

print("\n" + "="*70)
print("NEGATIVE SEQUENCE DISTRIBUTION (All Team-Windows)")
print("="*70)

neg_counts = pd.Series(all_neg_seqs).value_counts().sort_index()
total_neg = len(all_neg_seqs)

print(f"\n{'Seq':<6} {'Count':<10} {'%':<10}")
print("-"*30)
for seq_len in range(10):
    count = neg_counts.get(seq_len, 0)
    pct = count/total_neg*100
    print(f"{seq_len:<6} {count:<10} {pct:.1f}%")
print("-"*30)
print(f"{'Total':<6} {total_neg:<10}")

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print(f"""
Total momentum windows: {len(momentum_df)}
Total team-windows (home + away): {total_pos}

Each window is a potential "moment" where a goal could happen.
We count how many consecutive same-sign changes came BEFORE that window.

This gives us the "baseline" distribution to compare against goals.
""")

# Compare goal distribution vs all windows distribution
print("\n" + "="*70)
print("COMPARISON: GOALS vs ALL WINDOWS")
print("="*70)

# Goal data (hardcoded from previous analysis)
goal_pos = {0: 54, 1: 16, 2: 6, 3: 14, 4: 9, 5: 4, 6: 1, 7: 1}
goal_neg = {0: 57, 1: 19, 2: 10, 3: 12, 4: 5, 5: 1, 6: 2, 7: 1}
total_goals = 107

print(f"\n{'Seq':<6} {'All Windows %':<15} {'Goals %':<15} {'Lift':<10}")
print("-"*50)
print("POSITIVE (Scoring Team):")
for seq_len in range(6):
    all_pct = pos_counts.get(seq_len, 0)/total_pos*100
    goal_pct = goal_pos.get(seq_len, 0)/total_goals*100
    lift = goal_pct / all_pct if all_pct > 0 else 0
    print(f"{seq_len:<6} {all_pct:>10.1f}%     {goal_pct:>10.1f}%     {lift:.2f}x")

