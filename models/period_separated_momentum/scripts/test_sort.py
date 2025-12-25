import pandas as pd
import sys
sys.path.insert(0, 'models/preprocessing/input_generation/scripts')
from momentum_3min_calculator import MomentumCalculator

# Load events
events = pd.read_csv('Data/euro_2024_complete_dataset.csv', low_memory=False)
match = events[events['match_id'] == 3930158]  # Germany vs Scotland

calc = MomentumCalculator()
context = {'score_diff': 0, 'minute': 0}

# WITHOUT sorting (original approach)
window1 = match[(match['minute'] >= 0) & (match['minute'] <= 2)]
home1 = calc.calculate_3min_team_momentum(window1.to_dict('records'), 'Germany', context)
print(f"WITHOUT sorting: {home1}")

# WITH sorting (my approach)
match_sorted = match.copy().sort_values('minute').reset_index(drop=True)
window2 = match_sorted[(match_sorted['minute'] >= 0) & (match_sorted['minute'] <= 2)]
home2 = calc.calculate_3min_team_momentum(window2.to_dict('records'), 'Germany', context)
print(f"WITH sorting: {home2}")

# Filter by period THEN sort (exactly what my generator does)
period1 = match[match['period'] == 1].copy()
period1_sorted = period1.sort_values('minute').reset_index(drop=True)
window3 = period1_sorted[(period1_sorted['minute'] >= 0) & (period1_sorted['minute'] <= 2)]
home3 = calc.calculate_3min_team_momentum(window3.to_dict('records'), 'Germany', context)
print(f"Period filter + sorting: {home3}")

# Filter by period WITHOUT sort
window4 = period1[(period1['minute'] >= 0) & (period1['minute'] <= 2)]
home4 = calc.calculate_3min_team_momentum(window4.to_dict('records'), 'Germany', context)
print(f"Period filter, NO sorting: {home4}")

print(f"\nOriginal stored: 4.813")
print(f"My generator stored: 4.802")

