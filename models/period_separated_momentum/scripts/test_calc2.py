import pandas as pd
import sys
sys.path.insert(0, 'models/preprocessing/input_generation/scripts')
from momentum_3min_calculator import MomentumCalculator

# Load events
events = pd.read_csv('Data/euro_2024_complete_dataset.csv', low_memory=False)
match = events[events['match_id'] == 3930158]  # Germany vs Scotland

# Filter to period 1 FIRST (like my generator does)
period1 = match[match['period'] == 1].copy()

# Get window 0-2 from period1
window = period1[(period1['minute'] >= 0) & (period1['minute'] <= 2)]

calc = MomentumCalculator()
context = {'score_diff': 0, 'minute': 0}

# What team name does the generator use?
print("Team names from columns:")
if 'home_team' in match.columns:
    print(f"  home_team: {match['home_team'].iloc[0]}")
if 'home_team_name' in match.columns:
    print(f"  home_team_name: {match['home_team_name'].iloc[0]}")

# Extract team name the same way as generator
def get_team_name(team_str):
    if pd.isna(team_str):
        return None
    team_str = str(team_str)
    if "{'id':" in team_str or "{'name':" in team_str:
        import ast
        try:
            team_dict = ast.literal_eval(team_str)
            if isinstance(team_dict, dict) and 'name' in team_dict:
                return team_dict['name']
        except:
            pass
    return team_str

home_team = get_team_name(match['home_team_name'].iloc[0])
away_team = get_team_name(match['away_team_name'].iloc[0])
print(f"\nExtracted team names:")
print(f"  home: '{home_team}'")
print(f"  away: '{away_team}'")

# Calculate with period-filtered data
home_momentum = calc.calculate_3min_team_momentum(window.to_dict('records'), home_team, context)
away_momentum = calc.calculate_3min_team_momentum(window.to_dict('records'), away_team, context)

print(f"\nFrom period-filtered data:")
print(f"  home momentum: {home_momentum}")
print(f"  away momentum: {away_momentum}")

# Calculate with ALL match data (original approach)
window_all = match[(match['minute'] >= 0) & (match['minute'] <= 2)]
home_momentum_all = calc.calculate_3min_team_momentum(window_all.to_dict('records'), home_team, context)
away_momentum_all = calc.calculate_3min_team_momentum(window_all.to_dict('records'), away_team, context)

print(f"\nFrom all match data:")
print(f"  home momentum: {home_momentum_all}")
print(f"  away momentum: {away_momentum_all}")

print(f"\nAre they the same? {home_momentum == home_momentum_all}")

