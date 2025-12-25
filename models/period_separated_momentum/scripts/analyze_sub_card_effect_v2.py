"""
Analyze Substitution and Card Effect on Momentum Change
Using correct logic: Before = X-1, After = X+1 (event happens AT X)
With 3-window trend analysis before and after
"""
import pandas as pd
import numpy as np

print("="*70)
print("SUBSTITUTION & CARD EFFECT ON MOMENTUM (CORRECTED)")
print("="*70)

# Load data
momentum_df = pd.read_csv('../outputs/momentum_by_period.csv')
events_df = pd.read_csv('../../../Data/events_complete.csv', low_memory=False)

# Get team names per match
match_teams = momentum_df.groupby('match_id').first()[['team_home', 'team_away']].to_dict('index')

def get_momentum_change(match_id, period, minute, team_col):
    """Get momentum change at specific minute"""
    row = momentum_df[
        (momentum_df['match_id'] == match_id) & 
        (momentum_df['period'] == period) & 
        (momentum_df['minute'] == minute)
    ]
    if len(row) > 0:
        val = row[team_col].values[0]
        return val if pd.notna(val) else None
    return None

def analyze_event_with_windows(events, event_name, windows_before=3, windows_after=3):
    """
    Analyze event with multiple windows before/after
    
    For event at minute X:
    - The event happens AT minute X
    - Before windows: X-3, X-2, X-1 (BEFORE event)
    - After windows: X+1, X+2, X+3 (AFTER event, event included in momentum)
    """
    print(f"\n{'='*70}")
    print(f"ANALYZING {event_name.upper()} EFFECT")
    print(f"Total events: {len(events)}")
    print(f"{'='*70}")
    
    results = []
    for idx, event in events.iterrows():
        match_id = event['match_id']
        minute = int(event['minute'])
        period = int(event['period']) if pd.notna(event.get('period')) else 1
        team = event.get('team_name', '')
        
        if match_id not in match_teams:
            continue
        
        home = match_teams[match_id]['team_home']
        away = match_teams[match_id]['team_away']
        
        is_home = (team == home)
        team_col = 'team_home_momentum_change' if is_home else 'team_away_momentum_change'
        opp_col = 'team_away_momentum_change' if is_home else 'team_home_momentum_change'
        
        # Get windows before event (X-3, X-2, X-1)
        team_before = [get_momentum_change(match_id, period, minute - i, team_col) for i in range(windows_before, 0, -1)]
        opp_before = [get_momentum_change(match_id, period, minute - i, opp_col) for i in range(windows_before, 0, -1)]
        
        # Get windows after event (X+1, X+2, X+3)
        team_after = [get_momentum_change(match_id, period, minute + i, team_col) for i in range(1, windows_after + 1)]
        opp_after = [get_momentum_change(match_id, period, minute + i, opp_col) for i in range(1, windows_after + 1)]
        
        # Only include if we have at least 1 before and 1 after
        if team_before[-1] is not None and team_after[0] is not None:
            results.append({
                'match_id': match_id,
                'minute': minute,
                'period': period,
                'team': team,
                'team_b3': team_before[0],
                'team_b2': team_before[1],
                'team_b1': team_before[2],  # Immediately before
                'team_a1': team_after[0],   # Immediately after
                'team_a2': team_after[1],
                'team_a3': team_after[2],
                'opp_b3': opp_before[0],
                'opp_b2': opp_before[1],
                'opp_b1': opp_before[2],
                'opp_a1': opp_after[0],
                'opp_a2': opp_after[1],
                'opp_a3': opp_after[2],
            })
    
    if not results:
        print("No valid results")
        return None
    
    df = pd.DataFrame(results)
    print(f"\nAnalyzed {len(df)} events with valid data")
    
    # Calculate averages for each window
    print(f"\n--- TEAM THAT HAD {event_name.upper()} ---")
    print("Window averages (B = Before, A = After event):")
    
    team_avgs = {
        'B-3': df['team_b3'].dropna().mean(),
        'B-2': df['team_b2'].dropna().mean(),
        'B-1': df['team_b1'].dropna().mean(),
        'A+1': df['team_a1'].dropna().mean(),
        'A+2': df['team_a2'].dropna().mean(),
        'A+3': df['team_a3'].dropna().mean(),
    }
    for k, v in team_avgs.items():
        print(f"  {k}: {v:.3f}" if v is not None and not np.isnan(v) else f"  {k}: N/A")
    
    # Immediate impact (B-1 vs A+1)
    valid = df.dropna(subset=['team_b1', 'team_a1'])
    improved = (valid['team_a1'] > valid['team_b1']).sum()
    worsened = (valid['team_a1'] < valid['team_b1']).sum()
    same = (valid['team_a1'] == valid['team_b1']).sum()
    
    print(f"\nImmediate impact (B-1 → A+1): {len(valid)} events")
    print(f"  IMPROVED: {improved} ({improved/len(valid)*100:.1f}%)")
    print(f"  WORSENED: {worsened} ({worsened/len(valid)*100:.1f}%)")
    print(f"  SAME: {same} ({same/len(valid)*100:.1f}%)")
    
    # Trend analysis: Was momentum declining before?
    valid_trend = df.dropna(subset=['team_b3', 'team_b2', 'team_b1'])
    declining_before = ((valid_trend['team_b2'] < valid_trend['team_b3']) & 
                        (valid_trend['team_b1'] < valid_trend['team_b2'])).sum()
    rising_before = ((valid_trend['team_b2'] > valid_trend['team_b3']) & 
                     (valid_trend['team_b1'] > valid_trend['team_b2'])).sum()
    
    print(f"\nTrend BEFORE event:")
    print(f"  Declining (B3→B2→B1): {declining_before} ({declining_before/len(valid_trend)*100:.1f}%)")
    print(f"  Rising (B3→B2→B1): {rising_before} ({rising_before/len(valid_trend)*100:.1f}%)")
    
    # Did event reverse the trend?
    valid_all = df.dropna(subset=['team_b1', 'team_a1', 'team_a2'])
    was_declining = valid_all['team_b1'] < valid_all['team_b2']
    reversed_to_rising = was_declining & (valid_all['team_a1'] > valid_all['team_b1']) & (valid_all['team_a2'] > valid_all['team_a1'])
    
    print(f"\nTrend reversal after event:")
    print(f"  Was declining, reversed to rising: {reversed_to_rising.sum()} ({reversed_to_rising.sum()/len(valid_all)*100:.1f}%)")
    
    # Opponent analysis
    print(f"\n--- OPPONENT TEAM ---")
    print("Window averages:")
    
    opp_avgs = {
        'B-3': df['opp_b3'].dropna().mean(),
        'B-2': df['opp_b2'].dropna().mean(),
        'B-1': df['opp_b1'].dropna().mean(),
        'A+1': df['opp_a1'].dropna().mean(),
        'A+2': df['opp_a2'].dropna().mean(),
        'A+3': df['opp_a3'].dropna().mean(),
    }
    for k, v in opp_avgs.items():
        print(f"  {k}: {v:.3f}" if v is not None and not np.isnan(v) else f"  {k}: N/A")
    
    valid_opp = df.dropna(subset=['opp_b1', 'opp_a1'])
    opp_improved = (valid_opp['opp_a1'] > valid_opp['opp_b1']).sum()
    opp_worsened = (valid_opp['opp_a1'] < valid_opp['opp_b1']).sum()
    
    print(f"\nOpponent immediate impact (B-1 → A+1):")
    print(f"  IMPROVED: {opp_improved} ({opp_improved/len(valid_opp)*100:.1f}%)")
    print(f"  WORSENED: {opp_worsened} ({opp_worsened/len(valid_opp)*100:.1f}%)")
    
    return df, team_avgs, opp_avgs

# Get all yellow cards (from both Foul Committed and Bad Behaviour)
yellow_cards = []

# From Foul Committed
fouls = events_df[events_df['event_type'] == 'Foul Committed']
fc_yellow = fouls[fouls['foul_committed'].str.contains('Yellow', na=False)]
yellow_cards.append(fc_yellow)

# From Bad Behaviour
bb = events_df[events_df['event_type'] == 'Bad Behaviour']
bb_yellow = bb[bb['bad_behaviour'].str.contains('Yellow', na=False)]
yellow_cards.append(bb_yellow)

all_yellow = pd.concat(yellow_cards, ignore_index=True)
print(f"\nTotal Yellow Cards found: {len(all_yellow)}")

# Get all red cards
red_cards = []
fc_red = fouls[fouls['foul_committed'].str.contains('Red Card', na=False)]
bb_red = bb[bb['bad_behaviour'].str.contains('Red Card', na=False)]
red_cards.append(fc_red)
red_cards.append(bb_red)
all_red = pd.concat(red_cards, ignore_index=True)
print(f"Total Red Cards found: {len(all_red)}")

# Get all substitutions
subs = events_df[events_df['event_type'] == 'Substitution']
print(f"Total Substitutions found: {len(subs)}")

# Analyze
print("\n" + "="*70)
sub_results = analyze_event_with_windows(subs, 'Substitution')
print("\n" + "="*70)
yellow_results = analyze_event_with_windows(all_yellow, 'Yellow Card')

if len(all_red) > 0:
    print("\n" + "="*70)
    red_results = analyze_event_with_windows(all_red, 'Red Card')

# Summary
print("\n" + "="*70)
print("SUMMARY & INSIGHTS")
print("="*70)
print("""
EXAMPLE CALCULATION for Sub at minute 35:
=========================================
- Before (B-1): Change at minute 34 = mom(34,33,32) - mom(31,30,29)
- After (A+1):  Change at minute 36 = mom(36,35,34) - mom(33,32,31)
                                      ^^^ Sub at 35 is NOW in this window

The sub AT minute 35 is included in the "After" momentum calculation.
We compare the change BEFORE the sub window vs AFTER to see impact.

HYPOTHESIS TESTING:
- Subs: Made to STOP negative momentum? Check if team was declining before.
- Cards: Give OPPONENT better odds? Check if opponent improves after.
""")

