"""
Combined Analysis: All metrics conditions and outcomes

WINNING METRICS (positive correlation with winning):
- Absolute Momentum Winner
- Number of Sequences Winner

CHASING METRICS (negative correlation - indicates losing team):
- Total Positive Momentum Changes Winner  
- Longest Sequence Winner

Analyze all combinations to see outcomes.
"""

import pandas as pd
import numpy as np

print("=" * 80)
print("COMBINED METRICS ANALYSIS: ALL CONDITIONS")
print("=" * 80)

# Load all previous analyses
momentum_df = pd.read_csv('momentum_vs_result_analysis.csv')
change_df = pd.read_csv('momentum_change_vs_result_analysis.csv')
sequence_df = pd.read_csv('momentum_sequence_vs_result_analysis.csv')

print(f"\nLoaded {len(momentum_df)} games")

# Merge all data
combined = momentum_df[['match_id', 'home_team', 'away_team', 'home_score', 'away_score', 
                        'match_result', 'momentum_winner']].copy()

# Add change winner
combined = combined.merge(
    change_df[['match_id', 'change_winner', 'home_positive_changes', 'away_positive_changes']], 
    on='match_id'
)

# Add sequence data
combined = combined.merge(
    sequence_df[['match_id', 'longest_winner', 'more_seq_winner', 
                 'home_longest_seq', 'away_longest_seq',
                 'home_num_sequences', 'away_num_sequences']], 
    on='match_id'
)

print(f"Combined data: {len(combined)} games")

# For each game, determine the "winner" of each metric (home or away perspective)
# And compare to match result

def get_team_outcome(row, metric_winner_col):
    """Get outcome for the team that won this metric"""
    winner = row[metric_winner_col]
    if winner == 'home':
        if row['match_result'] == 'home_win':
            return 'WIN'
        elif row['match_result'] == 'away_win':
            return 'LOSE'
        else:
            return 'DRAW'
    elif winner == 'away':
        if row['match_result'] == 'away_win':
            return 'WIN'
        elif row['match_result'] == 'home_win':
            return 'LOSE'
        else:
            return 'DRAW'
    else:
        return 'TIE'

# Add outcomes for each metric
combined['momentum_outcome'] = combined.apply(lambda r: get_team_outcome(r, 'momentum_winner'), axis=1)
combined['change_outcome'] = combined.apply(lambda r: get_team_outcome(r, 'change_winner'), axis=1)
combined['longest_outcome'] = combined.apply(lambda r: get_team_outcome(r, 'longest_winner'), axis=1)
combined['num_seq_outcome'] = combined.apply(lambda r: get_team_outcome(r, 'more_seq_winner'), axis=1)

print("\n" + "=" * 80)
print("PART 1: WINNING METRICS (Absolute Momentum + Number of Sequences)")
print("=" * 80)

# Check agreement between winning metrics
def check_agreement(row, col1, col2):
    """Check if both metrics point to same team"""
    if row[col1] == 'tie' or row[col2] == 'tie':
        return 'has_tie'
    elif row[col1] == row[col2]:
        return 'agree'
    else:
        return 'disagree'

combined['winning_metrics_agree'] = combined.apply(
    lambda r: check_agreement(r, 'momentum_winner', 'more_seq_winner'), axis=1
)

# When BOTH winning metrics agree
print("\n>>> When Absolute Momentum AND Number of Sequences point to SAME team:")
agree_df = combined[combined['winning_metrics_agree'] == 'agree']
print(f"    Total games: {len(agree_df)}")

agree_wins = len(agree_df[agree_df['momentum_outcome'] == 'WIN'])
agree_loses = len(agree_df[agree_df['momentum_outcome'] == 'LOSE'])
agree_draws = len(agree_df[agree_df['momentum_outcome'] == 'DRAW'])

print(f"    That team WON:  {agree_wins} ({agree_wins/len(agree_df)*100:.1f}%)")
print(f"    That team LOST: {agree_loses} ({agree_loses/len(agree_df)*100:.1f}%)")
print(f"    DRAW:           {agree_draws} ({agree_draws/len(agree_df)*100:.1f}%)")

# When winning metrics DISAGREE
print("\n>>> When Absolute Momentum AND Number of Sequences point to DIFFERENT teams:")
disagree_df = combined[combined['winning_metrics_agree'] == 'disagree']
print(f"    Total games: {len(disagree_df)}")

if len(disagree_df) > 0:
    # Check who won more often - momentum winner or sequence winner
    mom_wins = len(disagree_df[disagree_df['momentum_outcome'] == 'WIN'])
    seq_wins = len(disagree_df[disagree_df['num_seq_outcome'] == 'WIN'])
    draws = len(disagree_df[disagree_df['match_result'] == 'draw'])
    
    print(f"    Momentum winner WON match:  {mom_wins} ({mom_wins/len(disagree_df)*100:.1f}%)")
    print(f"    Sequences winner WON match: {seq_wins} ({seq_wins/len(disagree_df)*100:.1f}%)")
    print(f"    DRAW:                       {draws} ({draws/len(disagree_df)*100:.1f}%)")

# Has ties
tie_df = combined[combined['winning_metrics_agree'] == 'has_tie']
print(f"\n>>> Games with at least one TIE in winning metrics: {len(tie_df)}")

print("\n" + "=" * 80)
print("PART 2: CHASING METRICS (Positive Changes + Longest Sequence)")
print("=" * 80)

combined['chasing_metrics_agree'] = combined.apply(
    lambda r: check_agreement(r, 'change_winner', 'longest_winner'), axis=1
)

# When BOTH chasing metrics agree
print("\n>>> When Positive Changes AND Longest Sequence point to SAME team:")
agree_chase = combined[combined['chasing_metrics_agree'] == 'agree']
print(f"    Total games: {len(agree_chase)}")

if len(agree_chase) > 0:
    chase_wins = len(agree_chase[agree_chase['change_outcome'] == 'WIN'])
    chase_loses = len(agree_chase[agree_chase['change_outcome'] == 'LOSE'])
    chase_draws = len(agree_chase[agree_chase['change_outcome'] == 'DRAW'])
    
    print(f"    That team WON:  {chase_wins} ({chase_wins/len(agree_chase)*100:.1f}%)")
    print(f"    That team LOST: {chase_loses} ({chase_loses/len(agree_chase)*100:.1f}%)")
    print(f"    DRAW:           {chase_draws} ({chase_draws/len(agree_chase)*100:.1f}%)")

# When chasing metrics DISAGREE
print("\n>>> When Positive Changes AND Longest Sequence point to DIFFERENT teams:")
disagree_chase = combined[combined['chasing_metrics_agree'] == 'disagree']
print(f"    Total games: {len(disagree_chase)}")

if len(disagree_chase) > 0:
    change_wins = len(disagree_chase[disagree_chase['change_outcome'] == 'WIN'])
    longest_wins = len(disagree_chase[disagree_chase['longest_outcome'] == 'WIN'])
    draws = len(disagree_chase[disagree_chase['match_result'] == 'draw'])
    
    print(f"    Positive Change winner WON:  {change_wins} ({change_wins/len(disagree_chase)*100:.1f}%)")
    print(f"    Longest Sequence winner WON: {longest_wins} ({longest_wins/len(disagree_chase)*100:.1f}%)")
    print(f"    DRAW:                        {draws} ({draws/len(disagree_chase)*100:.1f}%)")

tie_chase = combined[combined['chasing_metrics_agree'] == 'has_tie']
print(f"\n>>> Games with at least one TIE in chasing metrics: {len(tie_chase)}")

print("\n" + "=" * 80)
print("PART 3: CROSS ANALYSIS - Winning vs Chasing Metrics")
print("=" * 80)

# Create combined state
def get_combined_state(row):
    """Compare winning metrics team vs chasing metrics team"""
    # Get winning metrics winner (use momentum as primary)
    if row['winning_metrics_agree'] == 'agree':
        winning_team = row['momentum_winner']
    elif row['winning_metrics_agree'] == 'disagree':
        winning_team = 'mixed'
    else:
        winning_team = 'tie'
    
    # Get chasing metrics winner (use change as primary)
    if row['chasing_metrics_agree'] == 'agree':
        chasing_team = row['change_winner']
    elif row['chasing_metrics_agree'] == 'disagree':
        chasing_team = 'mixed'
    else:
        chasing_team = 'tie'
    
    return winning_team, chasing_team

# Analyze: When winning metrics say Team A AND chasing metrics say Team A (same team)
print("\n>>> SAME team wins BOTH winning AND chasing metrics:")
same_team = combined[(combined['winning_metrics_agree'] == 'agree') & 
                     (combined['chasing_metrics_agree'] == 'agree') &
                     (combined['momentum_winner'] == combined['change_winner'])]
print(f"    Total games: {len(same_team)}")

if len(same_team) > 0:
    same_wins = len(same_team[same_team['momentum_outcome'] == 'WIN'])
    same_loses = len(same_team[same_team['momentum_outcome'] == 'LOSE'])
    same_draws = len(same_team[same_team['momentum_outcome'] == 'DRAW'])
    
    print(f"    That team WON:  {same_wins} ({same_wins/len(same_team)*100:.1f}%)")
    print(f"    That team LOST: {same_loses} ({same_loses/len(same_team)*100:.1f}%)")
    print(f"    DRAW:           {same_draws} ({same_draws/len(same_team)*100:.1f}%)")

# Different teams win winning vs chasing
print("\n>>> DIFFERENT teams win winning metrics vs chasing metrics:")
diff_team = combined[(combined['winning_metrics_agree'] == 'agree') & 
                     (combined['chasing_metrics_agree'] == 'agree') &
                     (combined['momentum_winner'] != combined['change_winner'])]
print(f"    Total games: {len(diff_team)}")

if len(diff_team) > 0:
    # Winning metrics team won
    winning_won = len(diff_team[diff_team['momentum_outcome'] == 'WIN'])
    # Chasing metrics team won (which means chasing metrics winner LOST momentum battle but WON match)
    chasing_won = len(diff_team[diff_team['change_outcome'] == 'WIN'])
    draws = len(diff_team[diff_team['match_result'] == 'draw'])
    
    print(f"    WINNING metrics team WON match:  {winning_won} ({winning_won/len(diff_team)*100:.1f}%)")
    print(f"    CHASING metrics team WON match:  {chasing_won} ({chasing_won/len(diff_team)*100:.1f}%)")
    print(f"    DRAW:                            {draws} ({draws/len(diff_team)*100:.1f}%)")

print("\n" + "=" * 80)
print("PART 4: FULL COMBINATION TABLE")
print("=" * 80)

# All 4 metrics combinations
print("\n>>> All possible metric combinations and outcomes:")
print()

# Group by all 4 metric winners
combinations = combined.groupby(['momentum_winner', 'more_seq_winner', 'change_winner', 'longest_winner']).agg({
    'match_id': 'count',
    'match_result': lambda x: x.value_counts().to_dict()
}).reset_index()

combinations.columns = ['Momentum', 'Num_Seq', 'Pos_Change', 'Longest_Seq', 'Games', 'Results']

print(f"{'Momentum':<10} {'Num_Seq':<10} {'Pos_Chg':<10} {'Longest':<10} {'Games':>6}  Results")
print("-" * 75)

for _, row in combinations.sort_values('Games', ascending=False).head(20).iterrows():
    results_str = str(row['Results']).replace("'", "").replace("{", "").replace("}", "")
    print(f"{row['Momentum']:<10} {row['Num_Seq']:<10} {row['Pos_Change']:<10} {row['Longest_Seq']:<10} {row['Games']:>6}  {results_str}")

print("\n" + "=" * 80)
print("SUMMARY TABLE: Key Combinations")
print("=" * 80)

print("""
+----------------------------------+-------+--------+--------+--------+
| CONDITION                        | Games |  WIN   |  LOSE  |  DRAW  |
+----------------------------------+-------+--------+--------+--------+""")

# Condition 1: Winning metrics agree
agree_w = combined[combined['winning_metrics_agree'] == 'agree']
w1 = len(agree_w[agree_w['momentum_outcome'] == 'WIN'])
l1 = len(agree_w[agree_w['momentum_outcome'] == 'LOSE'])
d1 = len(agree_w[agree_w['momentum_outcome'] == 'DRAW'])
t1 = len(agree_w)
print(f"| Winning metrics AGREE            | {t1:>5} | {w1/t1*100:>5.1f}% | {l1/t1*100:>5.1f}% | {d1/t1*100:>5.1f}% |")

# Condition 2: Winning metrics disagree
disagree_w = combined[combined['winning_metrics_agree'] == 'disagree']
if len(disagree_w) > 0:
    t2 = len(disagree_w)
    # When they disagree, check who wins more often
    mom_w = len(disagree_w[disagree_w['momentum_outcome'] == 'WIN'])
    seq_w = len(disagree_w[disagree_w['num_seq_outcome'] == 'WIN'])
    d2 = len(disagree_w[disagree_w['match_result'] == 'draw'])
    print(f"| Winning metrics DISAGREE         | {t2:>5} | Mom:{mom_w/t2*100:.0f}% | Seq:{seq_w/t2*100:.0f}% | {d2/t2*100:>5.1f}% |")

# Condition 3: Chasing metrics agree
agree_c = combined[combined['chasing_metrics_agree'] == 'agree']
if len(agree_c) > 0:
    w3 = len(agree_c[agree_c['change_outcome'] == 'WIN'])
    l3 = len(agree_c[agree_c['change_outcome'] == 'LOSE'])
    d3 = len(agree_c[agree_c['change_outcome'] == 'DRAW'])
    t3 = len(agree_c)
    print(f"| Chasing metrics AGREE            | {t3:>5} | {w3/t3*100:>5.1f}% | {l3/t3*100:>5.1f}% | {d3/t3*100:>5.1f}% |")

# Condition 4: Chasing metrics disagree
disagree_c = combined[combined['chasing_metrics_agree'] == 'disagree']
if len(disagree_c) > 0:
    t4 = len(disagree_c)
    chg_w = len(disagree_c[disagree_c['change_outcome'] == 'WIN'])
    lng_w = len(disagree_c[disagree_c['longest_outcome'] == 'WIN'])
    d4 = len(disagree_c[disagree_c['match_result'] == 'draw'])
    print(f"| Chasing metrics DISAGREE         | {t4:>5} | Chg:{chg_w/t4*100:.0f}% | Lng:{lng_w/t4*100:.0f}% | {d4/t4*100:>5.1f}% |")

# Condition 5: Same team wins both
if len(same_team) > 0:
    w5 = len(same_team[same_team['momentum_outcome'] == 'WIN'])
    l5 = len(same_team[same_team['momentum_outcome'] == 'LOSE'])
    d5 = len(same_team[same_team['momentum_outcome'] == 'DRAW'])
    t5 = len(same_team)
    print(f"| SAME team: Winning + Chasing     | {t5:>5} | {w5/t5*100:>5.1f}% | {l5/t5*100:>5.1f}% | {d5/t5*100:>5.1f}% |")

# Condition 6: Different teams win
if len(diff_team) > 0:
    t6 = len(diff_team)
    win_won = len(diff_team[diff_team['momentum_outcome'] == 'WIN'])
    chase_won = len(diff_team[diff_team['change_outcome'] == 'WIN'])
    d6 = len(diff_team[diff_team['match_result'] == 'draw'])
    print(f"| DIFF team: Winning vs Chasing    | {t6:>5} | W:{win_won/t6*100:.0f}%  | C:{chase_won/t6*100:.0f}%  | {d6/t6*100:>5.1f}% |")

print("+----------------------------------+-------+--------+--------+--------+")

# Save combined data
combined.to_csv('combined_metrics_analysis.csv', index=False)
print(f"\n✅ Detailed results saved to: combined_metrics_analysis.csv")

