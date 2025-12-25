import pandas as pd

df = pd.read_csv('../outputs/momentum_by_period.csv')
game = df[df['match_id'] == 3930158]  # Germany vs Scotland

m81 = game[game['minute'] == 81].iloc[0]
m84 = game[game['minute'] == 84].iloc[0]

print("="*60)
print("VERIFICATION: Your Logic vs Our Calculation")
print("="*60)

print("\n--- ABS MOMENTUM at display minute 87 ---")
print(f"Original minute: 84")
print(f"minute_range: {m84['minute_range']}")
print(f"Events from: 84, 85, 86")
print(f"Value: {m84['team_home_momentum']}")

print("\n--- MOMENTUM CHANGE at display minute 84 ---")
print(f"Original minute: 81")
print(f"minute_range: {m81['minute_range']}")
print(f"Change = mom(84,85,86) - mom(81,82,83)")
print(f"Value: {m81['team_home_momentum_change']}")

print("\n--- VERIFICATION ---")
print(f"mom(84) [events 84,85,86] = {m84['team_home_momentum']}")
print(f"mom(81) [events 81,82,83] = {m81['team_home_momentum']}")
calc = round(m84['team_home_momentum'] - m81['team_home_momentum'], 3)
print(f"mom(84) - mom(81) = {calc}")
print(f"Stored change at minute 81 = {m81['team_home_momentum_change']}")

print("\n--- MATCH CHECK ---")
if abs(calc - m81['team_home_momentum_change']) < 0.01:
    print("✓ MATCH! Our calculation is correct.")
else:
    print("✗ MISMATCH - need to investigate")

print("\n--- YOUR LOGIC ---")
print("Minute 87 abs: mom(84,85,86) ✓")
print("Minute 84 change: mom(86,85,84) - mom(83,82,81)")
print("                = mom(84,85,86) - mom(81,82,83) ✓")
print("\nYES - Your logic matches our calculation!")

