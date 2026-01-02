"""Final check for V6.2 - hallucinations and Netherlands vs Turkey."""

import pandas as pd
import glob
import os
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Find latest V6 files
files = sorted(glob.glob('../data/llm_commentary/*V6*.csv'), key=os.path.getmtime, reverse=True)[:10]

print('='*70)
print('V6.2 FINAL VERIFICATION - 10 GAMES')
print('='*70)

# Hallucination patterns
patterns = ['corners so far', 'shots so far', 'shots this half']

print('\n1. HALLUCINATIONS CHECK (strict):')
print('-'*40)
total_hallucinations = 0
for f in files:
    df = pd.read_csv(f)
    match_name = f.split('match_')[1].split('_V6')[0].replace('_', ' ')
    count = 0
    for _, row in df.iterrows():
        comm = str(row.get('llm_commentary', ''))
        for p in patterns:
            if re.search(p, comm, re.IGNORECASE):
                print(f'\n  {match_name} - Min {row["minute"]}:')
                print(f'    {comm}')
                count += 1
                break
    if count == 0:
        print(f'  {match_name}: ✓ No hallucinations')
    total_hallucinations += count

print(f'\n  TOTAL: {total_hallucinations} hallucinations in 10 games')

print('\n\n2. NETHERLANDS VS TURKEY - MINUTES 9 & 13:')
print('-'*40)
for f in files:
    if 'Netherlands' in f and 'Turkey' in f:
        df = pd.read_csv(f)
        for minute in [9, 13]:
            row = df[df['minute'] == minute]
            if len(row) > 0:
                print(f'\nMinute {minute}:')
                print(f'  {row.iloc[0]["llm_commentary"]}')

print('\n\n3. GOALS & PENALTIES (Netherlands vs Turkey):')
print('-'*40)
for f in files:
    if 'Netherlands' in f and 'Turkey' in f:
        df = pd.read_csv(f)
        goals = df[df['detected_type'].isin(['Goal', 'Own Goal', 'Penalty Goal', 'Penalty Awarded'])]
        for _, row in goals.iterrows():
            print(f'\nMin {row["minute"]}: [{row["detected_type"]}] Score: {row["home_score"]}-{row["away_score"]}')
            print(f'  {row["llm_commentary"]}')

print('\n\nDONE!')

