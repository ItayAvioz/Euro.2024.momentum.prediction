"""Verify V6.2 fixes for the 3 test games."""

import pandas as pd
import glob
import os
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Get the 2 most recent files (Germany-Scotland, Netherlands-Turkey)
files = sorted(glob.glob('../data/llm_commentary/*V6*.csv'), key=os.path.getmtime, reverse=True)[:2]

print('='*70)
print('V6.2 FIXES VERIFICATION')
print('='*70)

# 1. Hallucinations
print('\n1. HALLUCINATIONS CHECK:')
print('-'*40)
patterns = ['corners so far', 'shots so far', 'shots this half']
for f in files:
    df = pd.read_csv(f)
    match = f.split('match_')[1].split('_V6')[0].replace('_', ' ')
    count = 0
    for _, row in df.iterrows():
        comm = str(row.get('llm_commentary', ''))
        for p in patterns:
            if re.search(p, comm, re.IGNORECASE):
                print(f'\n  {match} - Min {row["minute"]}:')
                print(f'    {comm}')
                count += 1
                break
    if count == 0:
        print(f'  {match}: ✓ No hallucinations')

# 2. Area Fix (England vs Switzerland minute 23)
print('\n\n2. AREA FIX (England vs Switzerland):')
print('-'*40)
for f in files:
    if 'England' in f and 'Switzerland' in f:
        df = pd.read_csv(f)
        for minute in [23, 56]:  # Check a couple of General events
            rows = df[df['minute'] == minute]
            for _, row in rows.iterrows():
                if row['detected_type'] == 'General':
                    print(f'\n  Minute {minute}: {row["llm_commentary"]}')

# 3. Own Goal Fix (Germany vs Scotland)
print('\n\n3. OWN GOAL FIX:')
print('-'*40)
for f in files:
    df = pd.read_csv(f)
    match = f.split('match_')[1].split('_V6')[0].replace('_', ' ')
    own_goals = df[df['detected_type'] == 'Own Goal']
    if len(own_goals) > 0:
        print(f'\n  {match}:')
        for _, row in own_goals.iterrows():
            print(f'    Min {row["minute"]}: Score {row["home_score"]}-{row["away_score"]}')
            print(f'    {row["llm_commentary"]}')

# 4. Most Active Player Fix (Netherlands vs Turkey min 9, 13)
print('\n\n4. MOST ACTIVE PLAYER FIX (Netherlands vs Turkey):')
print('-'*40)
for f in files:
    if 'Netherlands' in f and 'Turkey' in f:
        df = pd.read_csv(f)
        for minute in [9, 13]:
            rows = df[df['minute'] == minute]
            for _, row in rows.iterrows():
                print(f'\n  Minute {minute}: {row["llm_commentary"]}')

# 5. Goals from Chain (Netherlands vs Turkey)
print('\n\n5. GOALS FROM CHAIN:')
print('-'*40)
for f in files:
    if 'Netherlands' in f and 'Turkey' in f:
        df = pd.read_csv(f)
        goals = df[df['detected_type'].isin(['Goal', 'Own Goal'])]
        for _, row in goals.iterrows():
            print(f'\n  Min {row["minute"]}: [{row["detected_type"]}] Score: {row["home_score"]}-{row["away_score"]}')
            print(f'    {row["llm_commentary"]}')

print('\n\nDONE!')

