import pandas as pd
from pathlib import Path
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Load Spain vs England match data
PHASE7_DATA = Path(__file__).parent.parent.parent / '07_all_games_commentary' / 'data'
match_df = pd.read_csv(PHASE7_DATA / 'match_3943043_rich_commentary.csv')

print('=== NEW APPROACH: Look Back 7 Events ===')
print('=== Spain vs England - Finding DIRECT Chains ===\n')

# Get all shots and goals
shots_goals = match_df[match_df['event_type'].isin(['Shot', 'Goal'])]

chains_found = []

for idx, row in shots_goals.iterrows():
    minute = row['minute']
    event_type = row['event_type']
    player = row.get('player_name', '')
    shot_outcome = row.get('shot_outcome', '')
    
    # Get position in dataframe
    pos = match_df.index.get_loc(idx)
    
    # Look back 7 events
    start_pos = max(0, pos - 7)
    events_before = match_df.iloc[start_pos:pos]
    
    chain_type = None
    chain_detail = ''
    
    # Check for Corner in last 7 events
    corners = events_before[events_before['event_type'] == 'Corner']
    if len(corners) > 0:
        corner = corners.iloc[-1]
        events_between = pos - match_df.index.get_loc(corner.name) - 1
        chain_type = 'From Corner'
        chain_detail = f'{events_between} events between'
    
    # Check for Free Kick event type
    if not chain_type:
        free_kicks = events_before[events_before['event_type'].str.contains('Free Kick', na=False)]
        if len(free_kicks) > 0:
            fk = free_kicks.iloc[-1]
            events_between = pos - match_df.index.get_loc(fk.name) - 1
            chain_type = 'From Free Kick'
            chain_detail = f'{events_between} events between'
    
    # Check for Carry by same player (dribble)
    if not chain_type and player:
        carries = events_before[
            (events_before['event_type'] == 'Carry') & 
            (events_before['player_name'] == player)
        ]
        if len(carries) > 0:
            chain_type = 'After Dribble'
            chain_detail = f'{len(carries)} carries'
    
    if chain_type:
        outcome_str = f" ({shot_outcome})" if shot_outcome else ""
        chains_found.append({
            'minute': minute,
            'event': f"{event_type}{outcome_str}",
            'player': player,
            'chain': chain_type,
            'detail': chain_detail
        })

print(f'DIRECT Chains Found: {len(chains_found)}\n')
print('-' * 80)

for c in chains_found:
    print(f"Minute {c['minute']:3d}: [{c['event']:20s}] {c['player'][:25]:25s} | {c['chain']:15s} ({c['detail']})")

print('-' * 80)
print(f'\nSummary (NEW - 7 events lookback):')
chain_types = [c['chain'] for c in chains_found]
print(f"  From Corner:    {chain_types.count('From Corner')}")
print(f"  From Free Kick: {chain_types.count('From Free Kick')}")
print(f"  After Dribble:  {chain_types.count('After Dribble')}")

# Compare with play_pattern column
print('\n' + '=' * 80)
print('COMPARISON: What play_pattern column shows for Shots/Goals')
print('=' * 80)

play_patterns = shots_goals['play_pattern'].value_counts()
print(play_patterns)

# Show shots with "From Corner" play_pattern
corner_shots = shots_goals[shots_goals['play_pattern'].str.contains('Corner', na=False)]
print(f'\n--- Shots with play_pattern="From Corner" ({len(corner_shots)}) ---')
for idx, row in corner_shots.iterrows():
    minute = row['minute']
    pos = match_df.index.get_loc(idx)
    
    # Find corner in same minute
    minute_events = match_df[match_df['minute'] == minute]
    corners_in_min = minute_events[minute_events['event_type'] == 'Corner']
    
    if len(corners_in_min) > 0:
        corner_idx = corners_in_min.index[0]
        corner_pos = match_df.index.get_loc(corner_idx)
        events_between = pos - corner_pos - 1
        corner_info = f"Corner {events_between} events before"
    else:
        corner_info = "Corner NOT in same minute!"
    
    print(f"  Minute {minute}: {row['player_name'][:25]:25s} | {corner_info}")

