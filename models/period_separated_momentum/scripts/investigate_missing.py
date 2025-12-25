import pandas as pd

# Load data
events = pd.read_csv('Data/euro_2024_complete_dataset.csv', low_memory=False)
original = pd.read_csv('models/preprocessing/data/targets/momentum_targets_streamlined.csv')
new = pd.read_csv('models/period_separated_momentum/outputs/momentum_by_period.csv')

print("="*70)
print("INVESTIGATION: Why is window 42-44 missing in Germany vs Scotland?")
print("="*70)

match_id = 3930158
match = events[events['match_id'] == match_id]

print("\nEvents at minutes 42, 43, 44:")
for m in [42, 43, 44]:
    m_events = match[match['minute'] == m]
    print(f"  Minute {m}: {len(m_events)} events")

print("\nEvents around that time (minutes 40-46):")
for m in range(40, 47):
    m_events = match[match['minute'] == m]
    periods = list(m_events['period'].unique()) if len(m_events) > 0 else []
    print(f"  Minute {m}: {len(m_events)} events, periods: {periods}")

# What does original have?
print("\nOriginal data windows around minute 42:")
for m in range(40, 48):
    mr = f'{m}-{m+2}'
    orig = original[(original['match_id'] == match_id) & (original['minute_range'] == mr)]
    if len(orig) > 0:
        row = orig.iloc[0]
        print(f"  {mr}: home={row['team_home_momentum']:.3f}, away={row['team_away_momentum']:.3f}")

# What does my new generator have?
print("\nNew data windows around minute 42 (Period 1):")
for m in range(40, 48):
    mr = f'{m}-{m+2}'
    n = new[(new['match_id'] == match_id) & (new['minute_range'] == mr) & (new['period'] == 1)]
    if len(n) > 0:
        row = n.iloc[0]
        print(f"  {mr}: home={row['team_home_momentum']:.3f}, away={row['team_away_momentum']:.3f}")

print("\n" + "="*70)
print("SUMMARY OF ALL 'MISSING' CASES (non-overtime)")
print("="*70)

# Find all missing cases (comparing original to new, period 1, non-overtime)
missing_cases = []
for _, orig_row in original.iterrows():
    minute = int(orig_row['minute_range'].split('-')[0])
    if minute >= 100:  # Skip overtime
        continue
    if minute >= 88:  # Skip 2nd half stoppage
        continue
    if 43 <= minute <= 51:  # Skip 1st half stoppage  
        continue
        
    mr = orig_row['minute_range']
    match_id = orig_row['match_id']
    
    # Check if exists in new (period 1 for min < 45, period 2 for min >= 45)
    period = 1 if minute < 45 else 2
    n = new[(new['match_id'] == match_id) & (new['minute_range'] == mr) & (new['period'] == period)]
    
    if len(n) == 0:
        missing_cases.append({
            'match_id': match_id,
            'minute_range': mr,
            'minute': minute,
            'home_team': orig_row['team_home'],
            'away_team': orig_row['team_away']
        })

print(f"\nTotal missing (non-overlap, non-overtime): {len(missing_cases)}")

if len(missing_cases) > 0:
    print("\nDetails:")
    for case in missing_cases[:20]:
        match_id = case['match_id']
        mr = case['minute_range']
        minute = case['minute']
        
        # Check events at this minute
        m_events = events[(events['match_id'] == match_id) & (events['minute'] == minute)]
        m_events_p1 = m_events[m_events['period'] == 1]
        m_events_p2 = m_events[m_events['period'] == 2]
        
        print(f"  {case['home_team']} vs {case['away_team']}, {mr}: "
              f"min {minute} has {len(m_events)} events (P1: {len(m_events_p1)}, P2: {len(m_events_p2)})")

