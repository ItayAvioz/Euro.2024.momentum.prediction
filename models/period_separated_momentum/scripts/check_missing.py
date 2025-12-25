import pandas as pd

# Load data
events = pd.read_csv('Data/euro_2024_complete_dataset.csv', low_memory=False)
original = pd.read_csv('models/preprocessing/data/targets/momentum_targets_streamlined.csv')
new = pd.read_csv('models/period_separated_momentum/outputs/momentum_by_period.csv')

# Check the 'missing' minute cases
missing_cases = [
    (3930158, 42),   # Germany vs Scotland
    (3930164, 86),   # Belgium vs Slovakia  
    (3930173, 69),   # Netherlands vs France
    (3937376, 35),   # Germany vs Denmark
]

for match_id, minute in missing_cases:
    print(f'Match {match_id}, minute {minute}:')
    e = events[(events['match_id'] == match_id) & (events['minute'] == minute)]
    print(f'  Events at this minute: {len(e)}')
    if len(e) > 0:
        periods = e['period'].unique()
        print(f'  Periods: {periods}')
    
    # Check minute range format
    mr = f'{minute}-{minute+2}'
    orig = original[(original['match_id'] == match_id) & (original['minute_range'] == mr)]
    print(f'  Original records for {mr}: {len(orig)}')
    
    n = new[(new['match_id'] == match_id) & (new['minute_range'] == mr)]
    print(f'  New records for {mr}: {len(n)}')
    
    # Check what windows exist around this minute
    if len(orig) == 0:
        print(f'  (Checking nearby windows in original...)')
        for m in range(minute-2, minute+3):
            mr2 = f'{m}-{m+2}'
            o = original[(original['match_id'] == match_id) & (original['minute_range'] == mr2)]
            if len(o) > 0:
                print(f'    Found: {mr2}')
    
    print()

