import pandas as pd
import sys
sys.path.insert(0, 'models/preprocessing/input_generation/scripts')
from momentum_3min_calculator import MomentumCalculator

# Load events
events = pd.read_csv('Data/euro_2024_complete_dataset.csv', low_memory=False)
match = events[events['match_id'] == 3930158]  # Germany vs Scotland

# EXACTLY replicate my generator's logic
calc = MomentumCalculator()

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

# Get team names from match_events (as my generator does)
home_team = get_team_name(match['home_team_name'].iloc[0] if 'home_team_name' in match.columns else '')
away_team = get_team_name(match['away_team_name'].iloc[0] if 'away_team_name' in match.columns else '')

print(f"Home team: {home_team}")
print(f"Away team: {away_team}")

# Filter to period 1
period = 1
period_events = match[match['period'] == period].copy()
period_events = period_events.sort_values('minute').reset_index(drop=True)

print(f"\nPeriod {period}: {len(period_events)} events")

# Window 0-2
window_start = 0
window_end = 2

window_events = period_events[
    (period_events['minute'] >= window_start) & 
    (period_events['minute'] <= window_end)
].to_dict('records')

print(f"Window {window_start}-{window_end}: {len(window_events)} events")

# Calculate
home_context = {'score_diff': 0, 'minute': window_start}
away_context = {'score_diff': 0, 'minute': window_start}

home_momentum = calc.calculate_3min_team_momentum(window_events, home_team, home_context)
away_momentum = calc.calculate_3min_team_momentum(window_events, away_team, away_context)

print(f"\nRaw calculation:")
print(f"  Home: {home_momentum}")
print(f"  Away: {away_momentum}")

print(f"\nRounded to 3 decimals:")
print(f"  Home: {round(home_momentum, 3)}")
print(f"  Away: {round(away_momentum, 3)}")

# What my generator stored
new = pd.read_csv('models/period_separated_momentum/outputs/momentum_by_period.csv')
new_row = new[(new['match_id'] == 3930158) & (new['minute_range'] == '0-2') & (new['period'] == 1)].iloc[0]
print(f"\nMy generator stored:")
print(f"  Home: {new_row['team_home_momentum']}")
print(f"  Away: {new_row['team_away_momentum']}")

# Check if there are different events
print(f"\n=== DEBUGGING ===")
print(f"Checking event count...")

# What does my generator see?
# It loads from the same CSV file
gen_events = pd.read_csv('Data/euro_2024_complete_dataset.csv', low_memory=False)
gen_match = gen_events[gen_events['match_id'] == 3930158]
gen_p1 = gen_match[gen_match['period'] == 1]
gen_window = gen_p1[(gen_p1['minute'] >= 0) & (gen_p1['minute'] <= 2)]
print(f"Generator should see {len(gen_window)} events in window 0-2")

