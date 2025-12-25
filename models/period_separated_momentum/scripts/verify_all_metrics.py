import pandas as pd
import numpy as np

# Load period-separated momentum data
df = pd.read_csv('../outputs/momentum_by_period.csv')

# Filter for period 1 and 2 only
df = df[df['period'].isin([1, 2])].copy()

print('='*70)
print('PERIOD-SEPARATED DATA - ALL METRICS')
print('='*70)
print(f'Total matches: {df["match_id"].nunique()}')

# Calculate minute from minute_range
df['minute'] = df['minute_range'].str.split('-').str[0].astype(int)

# Filter from minute 3 onwards
df = df[df['minute'] >= 3].copy()

results = []
for match_id in df['match_id'].unique():
    game = df[df['match_id'] == match_id]
    home = game['team_home'].iloc[0]
    away = game['team_away'].iloc[0]
    
    # 1. Absolute Momentum - who won more windows
    home_mom_wins = (game['team_home_momentum'] > game['team_away_momentum']).sum()
    away_mom_wins = (game['team_away_momentum'] > game['team_home_momentum']).sum()
    
    # 2. Positive Changes - who had more positive momentum changes
    home_pos_changes = (game['team_home_momentum_change'] > 0).sum()
    away_pos_changes = (game['team_away_momentum_change'] > 0).sum()
    
    # 3. Number of Sequences - count consecutive positive change streaks
    def count_sequences(changes):
        seq_count = 0
        in_seq = False
        for c in changes:
            if c > 0:
                if not in_seq:
                    seq_count += 1
                    in_seq = True
            else:
                in_seq = False
        return seq_count
    
    home_num_seq = count_sequences(game['team_home_momentum_change'].values)
    away_num_seq = count_sequences(game['team_away_momentum_change'].values)
    
    # 4. Longest Sequence
    def longest_sequence(changes):
        max_len = 0
        curr_len = 0
        for c in changes:
            if c > 0:
                curr_len += 1
                max_len = max(max_len, curr_len)
            else:
                curr_len = 0
        return max_len
    
    home_longest = longest_sequence(game['team_home_momentum_change'].values)
    away_longest = longest_sequence(game['team_away_momentum_change'].values)
    
    results.append({
        'match_id': match_id,
        'home': home,
        'away': away,
        'home_mom_wins': home_mom_wins,
        'away_mom_wins': away_mom_wins,
        'abs_mom_winner': 'HOME' if home_mom_wins > away_mom_wins else ('AWAY' if away_mom_wins > home_mom_wins else 'TIE'),
        'home_pos_changes': home_pos_changes,
        'away_pos_changes': away_pos_changes,
        'pos_change_winner': 'HOME' if home_pos_changes > away_pos_changes else ('AWAY' if away_pos_changes > home_pos_changes else 'TIE'),
        'home_num_seq': home_num_seq,
        'away_num_seq': away_num_seq,
        'num_seq_winner': 'HOME' if home_num_seq > away_num_seq else ('AWAY' if away_num_seq > home_num_seq else 'TIE'),
        'home_longest': home_longest,
        'away_longest': away_longest,
        'longest_winner': 'HOME' if home_longest > away_longest else ('AWAY' if away_longest > home_longest else 'TIE')
    })

results_df = pd.DataFrame(results)

# Count winners for each metric
print('\n1. ABSOLUTE MOMENTUM:')
abs_mom = results_df['abs_mom_winner'].value_counts()
print(f'   HOME dominant: {abs_mom.get("HOME", 0)}')
print(f'   AWAY dominant: {abs_mom.get("AWAY", 0)}')
print(f'   TIE: {abs_mom.get("TIE", 0)}')
print(f'   Games with dominance: {abs_mom.get("HOME", 0) + abs_mom.get("AWAY", 0)}')

print('\n2. POSITIVE CHANGES:')
pos_ch = results_df['pos_change_winner'].value_counts()
print(f'   HOME more: {pos_ch.get("HOME", 0)}')
print(f'   AWAY more: {pos_ch.get("AWAY", 0)}')
print(f'   TIE: {pos_ch.get("TIE", 0)}')
print(f'   Games with winner: {pos_ch.get("HOME", 0) + pos_ch.get("AWAY", 0)}')

print('\n3. NUMBER OF SEQUENCES:')
num_seq = results_df['num_seq_winner'].value_counts()
print(f'   HOME more: {num_seq.get("HOME", 0)}')
print(f'   AWAY more: {num_seq.get("AWAY", 0)}')
print(f'   TIE: {num_seq.get("TIE", 0)}')
print(f'   Games with winner: {num_seq.get("HOME", 0) + num_seq.get("AWAY", 0)}')

print('\n4. LONGEST SEQUENCE:')
longest = results_df['longest_winner'].value_counts()
print(f'   HOME longer: {longest.get("HOME", 0)}')
print(f'   AWAY longer: {longest.get("AWAY", 0)}')
print(f'   TIE: {longest.get("TIE", 0)}')
print(f'   Games with winner: {longest.get("HOME", 0) + longest.get("AWAY", 0)}')

# Show ties for each metric
print('\n' + '='*70)
print('TIE GAMES BY METRIC:')
print('='*70)

for metric in ['abs_mom_winner', 'pos_change_winner', 'num_seq_winner', 'longest_winner']:
    ties = results_df[results_df[metric] == 'TIE']
    if len(ties) > 0:
        print(f'\n{metric}:')
        for _, row in ties.iterrows():
            print(f'  {row["home"]} vs {row["away"]}')

