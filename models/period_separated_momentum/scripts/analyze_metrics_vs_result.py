"""
Calculate all momentum metrics vs match results for period-separated data
Outputs the exact percentages needed for the Real Data Analysis dashboard page.
"""

import pandas as pd
import numpy as np
import json

print("=" * 70)
print("PERIOD-SEPARATED MOMENTUM METRICS vs MATCH RESULT ANALYSIS")
print("=" * 70)

# Load period-separated momentum data
momentum_df = pd.read_csv('../outputs/momentum_by_period.csv')

print(f"\nLoaded {len(momentum_df):,} momentum windows")
print(f"Games: {momentum_df['match_id'].nunique()}")

# Load match results to get final scores
events_df = pd.read_csv('../../../Data/euro_2024_complete_dataset.csv', low_memory=False)

# Get final scores for each match
match_results = {}
for match_id in momentum_df['match_id'].unique():
    match_events = events_df[events_df['match_id'] == match_id]
    if len(match_events) > 0:
        last_event = match_events.iloc[-1]
        home_score = last_event['home_score'] if pd.notna(last_event['home_score']) else 0
        away_score = last_event['away_score'] if pd.notna(last_event['away_score']) else 0
        
        home_team = momentum_df[momentum_df['match_id'] == match_id]['team_home'].iloc[0]
        away_team = momentum_df[momentum_df['match_id'] == match_id]['team_away'].iloc[0]
        
        match_results[match_id] = {
            'home_team': home_team,
            'away_team': away_team,
            'home_score': int(home_score),
            'away_score': int(away_score),
            'result': 'home_win' if home_score > away_score else ('away_win' if away_score > home_score else 'draw')
        }

print(f"Match results loaded: {len(match_results)} games")

# Combine Period 1 (min < 45) and Period 2 (min >= 45) - exclude overlap
df = momentum_df.copy()
p1 = df[(df['period'] == 1) & (df['minute'] < 45)]
p2 = df[(df['period'] == 2) & (df['minute'] >= 45)]
combined = pd.concat([p1, p2])

print(f"Combined windows (no overlap): {len(combined)}")

# Function to count sequences and longest sequence
def count_sequences_and_longest(changes):
    sequences = 0
    longest = 0
    current = 0
    for c in changes:
        if pd.notna(c) and c > 0:
            current += 1
            longest = max(longest, current)
        else:
            if current > 0:
                sequences += 1
            current = 0
    if current > 0:
        sequences += 1
    return sequences, longest

# Analyze each game
game_analysis = []

for match_id in combined['match_id'].unique():
    match_df = combined[combined['match_id'] == match_id]
    
    if match_id not in match_results:
        continue
    
    result = match_results[match_id]
    
    # 1. ABSOLUTE MOMENTUM (who wins more windows)
    home_momentum_wins = (match_df['team_home_momentum'] > match_df['team_away_momentum']).sum()
    away_momentum_wins = (match_df['team_away_momentum'] > match_df['team_home_momentum']).sum()
    
    if home_momentum_wins > away_momentum_wins:
        momentum_winner = 'home'
    elif away_momentum_wins > home_momentum_wins:
        momentum_winner = 'away'
    else:
        momentum_winner = 'tie'
    
    momentum_margin = abs(home_momentum_wins - away_momentum_wins)
    momentum_margin_pct = momentum_margin / len(match_df) * 100 if len(match_df) > 0 else 0
    
    # 2. POSITIVE CHANGES (who has more positive momentum changes)
    home_positive_changes = (match_df['team_home_momentum_change'] > 0).sum()
    away_positive_changes = (match_df['team_away_momentum_change'] > 0).sum()
    
    if home_positive_changes > away_positive_changes:
        change_winner = 'home'
    elif away_positive_changes > home_positive_changes:
        change_winner = 'away'
    else:
        change_winner = 'tie'
    
    change_margin = abs(home_positive_changes - away_positive_changes)
    change_margin_pct = change_margin / len(match_df) * 100 if len(match_df) > 0 else 0
    
    # 3. NUMBER OF SEQUENCES
    home_num_seq, home_longest = count_sequences_and_longest(match_df['team_home_momentum_change'].values)
    away_num_seq, away_longest = count_sequences_and_longest(match_df['team_away_momentum_change'].values)
    
    if home_num_seq > away_num_seq:
        num_seq_winner = 'home'
    elif away_num_seq > home_num_seq:
        num_seq_winner = 'away'
    else:
        num_seq_winner = 'tie'
    
    num_seq_margin = abs(home_num_seq - away_num_seq)
    
    # 4. LONGEST SEQUENCE
    if home_longest > away_longest:
        longest_winner = 'home'
    elif away_longest > home_longest:
        longest_winner = 'away'
    else:
        longest_winner = 'tie'
    
    longest_margin = abs(home_longest - away_longest)
    
    game_analysis.append({
        'match_id': match_id,
        'home_team': result['home_team'],
        'away_team': result['away_team'],
        'home_score': result['home_score'],
        'away_score': result['away_score'],
        'match_result': result['result'],
        'total_windows': len(match_df),
        # Momentum
        'home_momentum_wins': home_momentum_wins,
        'away_momentum_wins': away_momentum_wins,
        'momentum_winner': momentum_winner,
        'momentum_margin': momentum_margin,
        'momentum_margin_pct': momentum_margin_pct,
        # Change
        'home_positive_changes': home_positive_changes,
        'away_positive_changes': away_positive_changes,
        'change_winner': change_winner,
        'change_margin': change_margin,
        'change_margin_pct': change_margin_pct,
        # Sequences
        'home_num_seq': home_num_seq,
        'away_num_seq': away_num_seq,
        'num_seq_winner': num_seq_winner,
        'num_seq_margin': num_seq_margin,
        # Longest
        'home_longest': home_longest,
        'away_longest': away_longest,
        'longest_winner': longest_winner,
        'longest_margin': longest_margin
    })

results_df = pd.DataFrame(game_analysis)

# Function to calculate outcome for a winner
def get_outcome(row, winner_col):
    winner = row[winner_col]
    if winner == 'tie':
        return 'TIE'
    if winner == 'home':
        if row['match_result'] == 'home_win':
            return 'WIN'
        elif row['match_result'] == 'away_win':
            return 'LOSE'
        else:
            return 'DRAW'
    else:  # away
        if row['match_result'] == 'away_win':
            return 'WIN'
        elif row['match_result'] == 'home_win':
            return 'LOSE'
        else:
            return 'DRAW'

results_df['momentum_outcome'] = results_df.apply(lambda r: get_outcome(r, 'momentum_winner'), axis=1)
results_df['change_outcome'] = results_df.apply(lambda r: get_outcome(r, 'change_winner'), axis=1)
results_df['num_seq_outcome'] = results_df.apply(lambda r: get_outcome(r, 'num_seq_winner'), axis=1)
results_df['longest_outcome'] = results_df.apply(lambda r: get_outcome(r, 'longest_winner'), axis=1)

# Save full analysis
results_df.to_csv('../outputs/metrics_vs_result_analysis.csv', index=False)

# Calculate summary metrics for dashboard
def calc_metric_stats(df, winner_col, outcome_col):
    non_tie = df[df[winner_col] != 'tie']
    total = len(non_tie)
    wins = len(non_tie[non_tie[outcome_col] == 'WIN'])
    loses = len(non_tie[non_tie[outcome_col] == 'LOSE'])
    draws = len(non_tie[non_tie[outcome_col] == 'DRAW'])
    
    return {
        'games': total,
        'win': wins,
        'lose': loses,
        'draw': draws,
        'win_pct': round(wins/total*100, 1) if total > 0 else 0,
        'lose_pct': round(loses/total*100, 1) if total > 0 else 0,
        'draw_pct': round(draws/total*100, 1) if total > 0 else 0
    }

print("\n" + "=" * 70)
print("INDIVIDUAL METRICS vs MATCH OUTCOME")
print("=" * 70)

metrics = {}

# 1. Absolute Momentum
stats = calc_metric_stats(results_df, 'momentum_winner', 'momentum_outcome')
metrics['absolute_momentum'] = stats
print(f"\n1. ABSOLUTE MOMENTUM (Winning Metric):")
print(f"   Games: {stats['games']}")
print(f"   WIN: {stats['win_pct']}% | LOSE: {stats['lose_pct']}% | DRAW: {stats['draw_pct']}%")

# 2. Number of Sequences
stats = calc_metric_stats(results_df, 'num_seq_winner', 'num_seq_outcome')
metrics['num_sequences'] = stats
print(f"\n2. NUMBER OF SEQUENCES (Winning Metric):")
print(f"   Games: {stats['games']}")
print(f"   WIN: {stats['win_pct']}% | LOSE: {stats['lose_pct']}% | DRAW: {stats['draw_pct']}%")

# 3. Positive Changes
stats = calc_metric_stats(results_df, 'change_winner', 'change_outcome')
metrics['positive_changes'] = stats
print(f"\n3. POSITIVE CHANGES (Chasing Metric):")
print(f"   Games: {stats['games']}")
print(f"   WIN: {stats['win_pct']}% | LOSE: {stats['lose_pct']}% | DRAW: {stats['draw_pct']}%")

# 4. Longest Sequence
stats = calc_metric_stats(results_df, 'longest_winner', 'longest_outcome')
metrics['longest_sequence'] = stats
print(f"\n4. LONGEST SEQUENCE (Chasing Metric):")
print(f"   Games: {stats['games']}")
print(f"   WIN: {stats['win_pct']}% | LOSE: {stats['lose_pct']}% | DRAW: {stats['draw_pct']}%")

# Cumulative margin analysis
print("\n" + "=" * 70)
print("CUMULATIVE MARGIN ANALYSIS")
print("=" * 70)

# Absolute Momentum Margins
print("\nABSOLUTE MOMENTUM CUMULATIVE MARGINS:")
momentum_margins = {}
for min_margin in [0, 5, 10, 15, 20, 25]:
    subset = results_df[(results_df['momentum_margin_pct'] >= min_margin) & (results_df['momentum_winner'] != 'tie')]
    total = len(subset)
    if total > 0:
        wins = len(subset[subset['momentum_outcome'] == 'WIN'])
        loses = len(subset[subset['momentum_outcome'] == 'LOSE'])
        draws = len(subset[subset['momentum_outcome'] == 'DRAW'])
        momentum_margins[str(min_margin)] = {
            'games': total,
            'win_pct': round(wins/total*100, 1),
            'lose_pct': round(loses/total*100, 1),
            'draw_pct': round(draws/total*100, 1)
        }
        print(f"  {min_margin}%+: Games={total}, WIN={wins/total*100:.1f}%, LOSE={loses/total*100:.1f}%")

metrics['momentum_margins'] = momentum_margins

# Number of Sequences Margins
print("\nNUMBER OF SEQUENCES CUMULATIVE MARGINS:")
num_seq_margins = {}
for min_margin in [0, 1, 2, 3, 4, 5]:
    subset = results_df[(results_df['num_seq_margin'] >= min_margin) & (results_df['num_seq_winner'] != 'tie')]
    total = len(subset)
    if total > 0:
        wins = len(subset[subset['num_seq_outcome'] == 'WIN'])
        loses = len(subset[subset['num_seq_outcome'] == 'LOSE'])
        draws = len(subset[subset['num_seq_outcome'] == 'DRAW'])
        num_seq_margins[str(min_margin)] = {
            'games': total,
            'win_pct': round(wins/total*100, 1),
            'lose_pct': round(loses/total*100, 1),
            'draw_pct': round(draws/total*100, 1)
        }
        print(f"  {min_margin}+ seq: Games={total}, WIN={wins/total*100:.1f}%, LOSE={loses/total*100:.1f}%")

metrics['num_seq_margins'] = num_seq_margins

# Longest Sequence Margins
print("\nLONGEST SEQUENCE CUMULATIVE MARGINS:")
longest_margins = {}
for min_margin in [0, 1, 2, 3, 4, 5]:
    subset = results_df[(results_df['longest_margin'] >= min_margin) & (results_df['longest_winner'] != 'tie')]
    total = len(subset)
    if total > 0:
        wins = len(subset[subset['longest_outcome'] == 'WIN'])
        loses = len(subset[subset['longest_outcome'] == 'LOSE'])
        draws = len(subset[subset['longest_outcome'] == 'DRAW'])
        longest_margins[str(min_margin)] = {
            'games': total,
            'win_pct': round(wins/total*100, 1),
            'lose_pct': round(loses/total*100, 1),
            'draw_pct': round(draws/total*100, 1)
        }
        print(f"  {min_margin}+ windows: Games={total}, WIN={wins/total*100:.1f}%, LOSE={loses/total*100:.1f}%")

metrics['longest_margins'] = longest_margins

# Combined Metrics Analysis
print("\n" + "=" * 70)
print("COMBINED METRICS ANALYSIS")
print("=" * 70)

# Determine winning metrics winner (momentum + num_seq)
results_df['winning_metrics_team'] = 'none'
for idx, row in results_df.iterrows():
    mom_winner = row['momentum_winner']
    seq_winner = row['num_seq_winner']
    if mom_winner == seq_winner and mom_winner != 'tie':
        results_df.loc[idx, 'winning_metrics_team'] = mom_winner

# Determine chasing metrics winner (positive_changes + longest_seq)
results_df['chasing_metrics_team'] = 'none'
for idx, row in results_df.iterrows():
    change_winner = row['change_winner']
    longest_winner = row['longest_winner']
    if change_winner == longest_winner and change_winner != 'tie':
        results_df.loc[idx, 'chasing_metrics_team'] = change_winner

# Combined outcomes
combined_analysis = {}

# Winning metrics agree
winning_agree = results_df[results_df['winning_metrics_team'] != 'none'].copy()
winning_agree['combined_outcome'] = winning_agree.apply(
    lambda r: 'WIN' if (r['winning_metrics_team'] == 'home' and r['match_result'] == 'home_win') or 
                       (r['winning_metrics_team'] == 'away' and r['match_result'] == 'away_win')
    else ('LOSE' if (r['winning_metrics_team'] == 'home' and r['match_result'] == 'away_win') or
                    (r['winning_metrics_team'] == 'away' and r['match_result'] == 'home_win')
          else 'DRAW'), axis=1)

total_wa = len(winning_agree)
wa_wins = len(winning_agree[winning_agree['combined_outcome'] == 'WIN'])
wa_loses = len(winning_agree[winning_agree['combined_outcome'] == 'LOSE'])
wa_draws = len(winning_agree[winning_agree['combined_outcome'] == 'DRAW'])

combined_analysis['winning_agree'] = {
    'games': total_wa,
    'win': wa_wins,
    'lose': wa_loses,
    'draw': wa_draws,
    'win_pct': round(wa_wins/total_wa*100, 1) if total_wa > 0 else 0,
    'lose_pct': round(wa_loses/total_wa*100, 1) if total_wa > 0 else 0,
    'draw_pct': round(wa_draws/total_wa*100, 1) if total_wa > 0 else 0
}

print(f"\nWINNING Metrics AGREE (Momentum + Num Seq → same team):")
print(f"   Games: {total_wa}")
print(f"   WIN: {wa_wins/total_wa*100:.1f}% | LOSE: {wa_loses/total_wa*100:.1f}% | DRAW: {wa_draws/total_wa*100:.1f}%")

# Chasing metrics agree
chasing_agree = results_df[results_df['chasing_metrics_team'] != 'none'].copy()
chasing_agree['combined_outcome'] = chasing_agree.apply(
    lambda r: 'WIN' if (r['chasing_metrics_team'] == 'home' and r['match_result'] == 'home_win') or 
                       (r['chasing_metrics_team'] == 'away' and r['match_result'] == 'away_win')
    else ('LOSE' if (r['chasing_metrics_team'] == 'home' and r['match_result'] == 'away_win') or
                    (r['chasing_metrics_team'] == 'away' and r['match_result'] == 'home_win')
          else 'DRAW'), axis=1)

total_ca = len(chasing_agree)
ca_wins = len(chasing_agree[chasing_agree['combined_outcome'] == 'WIN'])
ca_loses = len(chasing_agree[chasing_agree['combined_outcome'] == 'LOSE'])
ca_draws = len(chasing_agree[chasing_agree['combined_outcome'] == 'DRAW'])

combined_analysis['chasing_agree'] = {
    'games': total_ca,
    'win': ca_wins,
    'lose': ca_loses,
    'draw': ca_draws,
    'win_pct': round(ca_wins/total_ca*100, 1) if total_ca > 0 else 0,
    'lose_pct': round(ca_loses/total_ca*100, 1) if total_ca > 0 else 0,
    'draw_pct': round(ca_draws/total_ca*100, 1) if total_ca > 0 else 0
}

print(f"\nCHASING Metrics AGREE (Pos Change + Longest → same team):")
print(f"   Games: {total_ca}")
print(f"   WIN: {ca_wins/total_ca*100:.1f}% | LOSE: {ca_loses/total_ca*100:.1f}% | DRAW: {ca_draws/total_ca*100:.1f}%")

# DIFFERENT teams (Winning → A, Chasing → B)
diff_teams = results_df[
    (results_df['winning_metrics_team'] != 'none') & 
    (results_df['chasing_metrics_team'] != 'none') &
    (results_df['winning_metrics_team'] != results_df['chasing_metrics_team'])
].copy()

diff_teams['combined_outcome'] = diff_teams.apply(
    lambda r: 'WIN' if (r['winning_metrics_team'] == 'home' and r['match_result'] == 'home_win') or 
                       (r['winning_metrics_team'] == 'away' and r['match_result'] == 'away_win')
    else ('LOSE' if (r['winning_metrics_team'] == 'home' and r['match_result'] == 'away_win') or
                    (r['winning_metrics_team'] == 'away' and r['match_result'] == 'home_win')
          else 'DRAW'), axis=1)

total_diff = len(diff_teams)
diff_wins = len(diff_teams[diff_teams['combined_outcome'] == 'WIN'])
diff_loses = len(diff_teams[diff_teams['combined_outcome'] == 'LOSE'])
diff_draws = len(diff_teams[diff_teams['combined_outcome'] == 'DRAW'])

combined_analysis['different_teams'] = {
    'games': total_diff,
    'win': diff_wins,
    'lose': diff_loses,
    'draw': diff_draws,
    'win_pct': round(diff_wins/total_diff*100, 1) if total_diff > 0 else 0,
    'lose_pct': round(diff_loses/total_diff*100, 1) if total_diff > 0 else 0,
    'draw_pct': round(diff_draws/total_diff*100, 1) if total_diff > 0 else 0
}

print(f"\n🔥 DIFFERENT Teams (Winning → A, Chasing → B):")
print(f"   Games: {total_diff}")
print(f"   WIN: {diff_wins/total_diff*100:.1f}% | LOSE: {diff_loses/total_diff*100:.1f}% | DRAW: {diff_draws/total_diff*100:.1f}%")

metrics['combined'] = combined_analysis

# Example games for the "different teams" scenario
if total_diff > 0:
    print(f"\n   Example games:")
    for _, row in diff_teams.head(5).iterrows():
        winning_team = row['home_team'] if row['winning_metrics_team'] == 'home' else row['away_team']
        chasing_team = row['home_team'] if row['chasing_metrics_team'] == 'home' else row['away_team']
        print(f"   {row['home_team']} {row['home_score']}-{row['away_score']} {row['away_team']}")
        print(f"      Winning metrics → {winning_team}, Chasing metrics → {chasing_team}")

# Summary stats
total_games = len(results_df)
total_windows = combined['match_id'].count()
avg_windows = results_df['total_windows'].mean()

metrics['summary'] = {
    'total_games': int(total_games),
    'total_windows': int(total_windows),
    'avg_windows_per_game': round(avg_windows, 1)
}

# Save metrics JSON for dashboard
with open('../outputs/dashboard_metrics.json', 'w') as f:
    json.dump(metrics, f, indent=2)

print("\n" + "=" * 70)
print("OUTPUT FILES CREATED")
print("=" * 70)
print("\n✅ metrics_vs_result_analysis.csv - Full game-by-game analysis")
print("✅ dashboard_metrics.json - Summary metrics for dashboard")
print("=" * 70)

