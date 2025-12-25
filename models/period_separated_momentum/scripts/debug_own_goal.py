import pandas as pd

# Load momentum data
momentum_df = pd.read_csv('../outputs/momentum_by_period.csv')
match_id = 3930158

match_mom = momentum_df[momentum_df['match_id'] == match_id]
p2 = match_mom[match_mom['period'] == 2].copy()
p2['display_minute'] = p2['minute'] + 3

print("2nd Half Momentum Data for Germany vs Scotland:")
print(f"Minutes available: {sorted(p2['minute'].unique())}")
print(f"Display minutes: {sorted(p2['display_minute'].unique())}")
print()

# Own goal at minute 86
# On graph, this should display at minute 86 (event minute) or 89 (display minute)?
# Looking at the code: display_min = em + 3
# So minute 86 event should show at display_min = 89

print("Checking if display minute 89 exists in momentum data:")
mom_89 = p2[p2['display_minute'] == 89]
print(f"Found: {len(mom_89)} rows")
if len(mom_89) > 0:
    print(mom_89[['minute', 'display_minute', 'team_home_momentum', 'team_away_momentum']])

# But wait - the event at minute 86 should show AT minute 86 on the graph
# NOT at 89... let me check the logic again
print()
print("Checking if minute 86 is in the momentum data (as display minute):")
mom_86 = p2[p2['display_minute'] == 86]
print(f"Found: {len(mom_86)} rows")
if len(mom_86) > 0:
    print(mom_86[['minute', 'display_minute', 'team_home_momentum', 'team_away_momentum']])

print()
print("Max display minute in 2nd half:", p2['display_minute'].max())

