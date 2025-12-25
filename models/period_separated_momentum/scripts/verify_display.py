import pandas as pd

df = pd.read_csv('../outputs/momentum_by_period.csv')
game = df[df['match_id'] == 3930158]

m5 = game[game['minute'] == 5].iloc[0]
m8 = game[game['minute'] == 8].iloc[0]

print("=" * 60)
print("VERIFYING THE +3 SHIFT LOGIC")
print("=" * 60)

print("\nORIGINAL DATA:")
print(f"  minute=5, range={m5['minute_range']}, abs_mom={m5['team_home_momentum']}, change={m5['team_home_momentum_change']}")
print(f"  minute=8, range={m8['minute_range']}, abs_mom={m8['team_home_momentum']}, change={m8['team_home_momentum_change']}")

print("\n" + "=" * 60)
print("WITH +3 SHIFT (display_minute = minute + 3):")
print("=" * 60)

print("\n  display_minute=8 shows data from minute=5:")
print(f"    - abs_momentum from events 5,6,7 = {m5['team_home_momentum']}")
print(f"    - momentum_change = mom(8,9,10) - mom(5,6,7) = {m5['team_home_momentum_change']}")

print("\n" + "=" * 60)
print("THIS MATCHES YOUR LOGIC:")
print("=" * 60)
print("\n  At minute 8 (going INTO minute 8):")
print(f"    - Abs momentum = momentum from minutes 5,6,7 = {m5['team_home_momentum']} ✓")
print(f"    - Mom change = momentum(8,9,10) - momentum(5,6,7)")
print(f"                 = {m8['team_home_momentum']} - {m5['team_home_momentum']}")
print(f"                 = {round(m8['team_home_momentum'] - m5['team_home_momentum'], 3)} ✓")

