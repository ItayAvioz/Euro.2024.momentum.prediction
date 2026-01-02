"""Check penalties, own goals, and specific issues."""

import pandas as pd
import glob
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

files = sorted(glob.glob('../data/llm_commentary/*V6*.csv'), key=os.path.getmtime, reverse=True)[:10]

print('='*70)
print('1. PENALTIES CHECK (Period 1-4)')
print('='*70)
for f in files:
    df = pd.read_csv(f)
    match = f.split('match_')[1].split('_V6')[0].replace('_', ' ')
    penalties = df[df['detected_type'].str.contains('Penalty', na=False)]
    if len(penalties) > 0:
        print(f'\n{match}:')
        for _, row in penalties.iterrows():
            period = row.get('period', 1)
            if period <= 4:
                print(f"  Min {row['minute']}: [{row['detected_type']}] Score: {row['home_score']}-{row['away_score']}")
                print(f"    {row['llm_commentary']}")

print('\n\n' + '='*70)
print('2. OWN GOALS CHECK')
print('='*70)
for f in files:
    df = pd.read_csv(f)
    match = f.split('match_')[1].split('_V6')[0].replace('_', ' ')
    own_goals = df[df['detected_type'] == 'Own Goal']
    if len(own_goals) > 0:
        print(f'\n{match}:')
        for _, row in own_goals.iterrows():
            print(f"  Min {row['minute']}: [{row['detected_type']}] Score: {row['home_score']}-{row['away_score']}")
            print(f"    {row['llm_commentary']}")

print('\n\n' + '='*70)
print('3. GERMANY VS SCOTLAND - ALL GOALS')
print('='*70)
for f in files:
    if 'Germany' in f and 'Scotland' in f:
        df = pd.read_csv(f)
        goals = df[df['detected_type'].isin(['Goal', 'Own Goal', 'Penalty Goal'])]
        for _, row in goals.iterrows():
            print(f"\nMin {row['minute']}: [{row['detected_type']}] Score: {row['home_score']}-{row['away_score']}")
            print(f"  {row['llm_commentary']}")

print('\n\n' + '='*70)
print('4. ENGLAND VS SWITZERLAND - MINUTE 23')
print('='*70)
for f in files:
    if 'England' in f and 'Switzerland' in f:
        df = pd.read_csv(f)
        min23 = df[df['minute'] == 23]
        for _, row in min23.iterrows():
            print(f"\nMin 23: [{row['detected_type']}]")
            print(f"  {row['llm_commentary']}")

print('\n\nDONE!')

