"""
Verify the new chain detection logic (V6.1) works correctly.
Tests the detect_event_chain function with the new 7-event lookback + change detection.
"""
import pandas as pd
from pathlib import Path
import sys
sys.stdout.reconfigure(encoding='utf-8')

def detect_event_chain(minute_df, detected_type, main_row, detection_info=None):
    """
    Detect related events that form a DIRECT chain for the MAIN event only.
    V6.1 Logic: Look back 7 events and detect CHANGES in play_pattern.
    """
    chain = {'has_chain': False, 'origin': '', 'related_events': []}
    
    player = main_row.get('player_name', '')
    main_idx = main_row.name if hasattr(main_row, 'name') else None
    
    if main_idx is None:
        return chain
    
    try:
        main_pos = minute_df.index.get_loc(main_idx)
    except:
        return chain
    
    # Get events before main event (up to 8 for change detection)
    events_before = minute_df.iloc[max(0, main_pos-8):main_pos]
    
    # For Shot/Goal: Check play_pattern changes in last 7 events
    if detected_type == 'Goal' or 'Shot' in detected_type:
        
        if len(events_before) >= 2:
            last_7 = events_before.tail(7)
            
            # Check for "From Corner" in last 7 play_patterns
            corner_in_7 = last_7[last_7['play_pattern'] == 'From Corner']
            if len(corner_in_7) > 0:
                if len(events_before) >= 8:
                    event_8 = events_before.iloc[0]
                    if event_8['play_pattern'] != 'From Corner':
                        chain['origin'] = 'From Corner'
                        chain['has_chain'] = True
            
            # Check for "From Free Kick" in last 7 play_patterns
            if not chain['origin']:
                fk_in_7 = last_7[last_7['play_pattern'] == 'From Free Kick']
                if len(fk_in_7) > 0:
                    if len(events_before) >= 8:
                        event_8 = events_before.iloc[0]
                        if event_8['play_pattern'] != 'From Free Kick':
                            chain['origin'] = 'From Free Kick'
                            chain['has_chain'] = True
            
            # Check for Dribble (Carry by same player in last 7)
            if not chain['origin'] and player:
                carries = last_7[
                    (last_7['event_type'] == 'Carry') & 
                    (last_7['player_name'] == player)
                ]
                if len(carries) > 0:
                    chain['origin'] = 'After Dribble'
                    chain['has_chain'] = True
    
    # For Corner: Check for blocked/saved shot before
    main_play_pattern = str(main_row.get('play_pattern', ''))
    if 'Corner' in main_play_pattern and main_pos > 0:
        last_7 = events_before.tail(7)
        shot_events = last_7[last_7['event_type'] == 'Shot']
        if len(shot_events) > 0:
            last_shot = shot_events.iloc[-1]
            outcome = str(last_shot.get('shot_outcome', ''))
            if outcome in ['Blocked', 'Saved']:
                chain['origin'] = f'After {outcome} Shot'
                chain['has_chain'] = True
    
    # Note: Assist handled by extract_event_specific_data() not here
    
    return chain

# Load Spain vs England match data
PHASE7_DATA = Path(__file__).parent.parent.parent / '07_all_games_commentary' / 'data'
match_df = pd.read_csv(PHASE7_DATA / 'match_3943043_rich_commentary.csv')

print('=' * 80)
print('VERIFYING NEW CHAIN DETECTION LOGIC (V6.1)')
print('=' * 80)
print()

# Test 1: Check all shots for chains
print('TEST 1: Checking all Shots for DIRECT chains')
print('-' * 80)

shots = match_df[match_df['event_type'] == 'Shot']
chains_found = []

for idx, row in shots.iterrows():
    minute = row['minute']
    minute_df = match_df[match_df['minute'] == minute].copy()
    
    # Use shot outcome to determine type
    outcome = row.get('shot_outcome', '')
    detected_type = 'Goal' if outcome == 'Goal' else f'Shot ({outcome})'
    chain = detect_event_chain(minute_df, detected_type, row, None)
    
    if chain['has_chain']:
        chains_found.append({
            'minute': minute,
            'player': str(row.get('player_name', ''))[:25],
            'outcome': row.get('shot_outcome', ''),
            'origin': chain.get('origin', ''),
            'related': chain.get('related_events', [])
        })

print(f'Chains found: {len(chains_found)}')
print()

for c in chains_found:
    related = f" + {c['related']}" if c['related'] else ""
    print(f"  Min {c['minute']:3d}: {c['player']:25s} ({c['outcome']:8s}) -> {c['origin']}{related}")

print()
print('Summary:')
origins = [c['origin'] for c in chains_found]
print(f"  From Corner:      {sum(1 for o in origins if 'Corner' in o)}")
print(f"  From Free Kick:   {sum(1 for o in origins if 'Free Kick' in o)}")
print(f"  After Dribble:    {sum(1 for o in origins if 'Dribble' in o)}")
print(f"  After Block/Save: {sum(1 for o in origins if 'Blocked' in o or 'Saved' in o)}")

# Test 2: Verify change detection works
print()
print('=' * 80)
print('TEST 2: Verify play_pattern CHANGE detection')
print('-' * 80)

# Check minute 12 (Le Normand shot with play_pattern="From Corner")
print('Checking Minute 12 (Le Normand shot - play_pattern says "From Corner"):')
min12 = match_df[match_df['minute'] == 12]
shot_row = min12[min12['event_type'] == 'Shot'].iloc[0] if len(min12[min12['event_type'] == 'Shot']) > 0 else None

if shot_row is not None:
    shot_idx = shot_row.name
    shot_pos = match_df.index.get_loc(shot_idx)
    
    # Show events before
    events_before = match_df.iloc[max(0, shot_pos-10):shot_pos]
    print(f"\nEvents before shot (showing play_pattern):")
    for i, (_, ev) in enumerate(events_before.iterrows()):
        marker = "<-- event -8" if i == len(events_before) - 8 else ""
        marker = "<-- event -7 (window start)" if i == len(events_before) - 7 else marker
        print(f"  {ev['event_type']:15s} | {ev['play_pattern']:15s} {marker}")
    print(f"  {'SHOT':15s} | {shot_row['play_pattern']:15s} <-- MAIN EVENT")
    
    # Run chain detection
    chain = detect_event_chain(min12, 'Shot (Off T)', shot_row, None)
    print(f"\nChain detected: {chain['has_chain']}")
    print(f"Origin: {chain.get('origin', 'None')}")
    
    if chain['has_chain']:
        print("Result: Corner chain detected")
    else:
        print("Result: No direct chain (corner started before 7-event window or no change)")

# Test 3: Goals with assists
print()
print('=' * 80)
print('TEST 3: Goals with Assists')
print('-' * 80)

goals = match_df[match_df['shot_outcome'] == 'Goal']
for idx, row in goals.iterrows():
    minute = row['minute']
    minute_df = match_df[match_df['minute'] == minute].copy()
    
    chain = detect_event_chain(minute_df, 'Goal', row, None)
    
    assists = [r for r in chain.get('related_events', []) if r.get('type') == 'Assist']
    assist_str = f" (Assist: {assists[0]['player'][:20]})" if assists else ""
    
    print(f"  Min {minute}: {row['player_name'][:25]:25s} -> {chain.get('origin', 'Regular Play'):15s}{assist_str}")

print()
print('=' * 80)
print('ALL TESTS COMPLETE')
print('=' * 80)

