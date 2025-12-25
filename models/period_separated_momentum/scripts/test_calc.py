import pandas as pd
import sys
sys.path.insert(0, 'models/preprocessing/input_generation/scripts')
from momentum_3min_calculator import MomentumCalculator

# Load events
events = pd.read_csv('Data/euro_2024_complete_dataset.csv', low_memory=False)
match = events[events['match_id'] == 3930158]  # Germany vs Scotland

calc = MomentumCalculator()

# Get window 0-2
window = match[(match['minute'] >= 0) & (match['minute'] <= 2)]

# Calculate momentum
context = {'score_diff': 0, 'minute': 0}

home_momentum = calc.calculate_3min_team_momentum(window.to_dict('records'), 'Germany', context)
away_momentum = calc.calculate_3min_team_momentum(window.to_dict('records'), 'Scotland', context)

print(f"Calculated home momentum: {home_momentum}")
print(f"Calculated away momentum: {away_momentum}")

# Load original data
orig = pd.read_csv('models/preprocessing/data/targets/momentum_targets_streamlined.csv')
orig_row = orig[(orig['match_id'] == 3930158) & (orig['minute_range'] == '0-2')].iloc[0]
print(f"\nOriginal home momentum: {orig_row['team_home_momentum']}")
print(f"Original away momentum: {orig_row['team_away_momentum']}")

print(f"\nDifference home: {abs(home_momentum - orig_row['team_home_momentum'])}")
print(f"Difference away: {abs(away_momentum - orig_row['team_away_momentum'])}")

# Load my new data
new = pd.read_csv('models/period_separated_momentum/outputs/momentum_by_period.csv')
new_row = new[(new['match_id'] == 3930158) & (new['minute_range'] == '0-2') & (new['period'] == 1)].iloc[0]
print(f"\nMy new home momentum: {new_row['team_home_momentum']}")
print(f"My new away momentum: {new_row['team_away_momentum']}")

