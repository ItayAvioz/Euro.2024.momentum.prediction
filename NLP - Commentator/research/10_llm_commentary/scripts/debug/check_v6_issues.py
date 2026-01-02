"""Check V6 issues: hallucinations, goals from chain, penalties, own goals."""

import pandas as pd
import glob
import os
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Find latest V6 files (by modification time, not alphabetically)
files = sorted(glob.glob('../data/llm_commentary/*V6*.csv'), key=os.path.getmtime, reverse=True)[:5]

print('='*70)
print('V6.2 VERIFICATION')
print('='*70)

# Hallucination patterns
patterns = ['corners so far', 'shots so far', 'shots this half', 'corners in quick', 
            'with [0-9]+ corners', 'with [0-9]+ shots', 'piling on with', 'in quick succession']

print('\n1. HALLUCINATIONS CHECK:')
print('-'*40)
for f in files:
    df = pd.read_csv(f)
    match_name = f.split('match_')[1].split('_V6')[0].replace('_', ' ')
    print(f'\n{match_name}:')
    found = 0
    for idx, row in df.iterrows():
        comm = str(row.get('llm_commentary', ''))
        for p in patterns:
            if re.search(p, comm, re.IGNORECASE):
                print(f'  Min {row["minute"]}: {comm[:120]}...')
                found += 1
                break
    if found == 0:
        print('  ✓ No hallucinations!')

print('\n\n2. NETHERLANDS VS TURKEY GOALS:')
print('-'*40)
for f in files:
    if 'Netherlands' in f and 'Turkey' in f:
        df = pd.read_csv(f)
        goals = df[df['detected_type'].isin(['Goal', 'Own Goal'])]
        for _, row in goals.iterrows():
            print(f"\nMin {row['minute']}: [{row['detected_type']}]")
            print(f"  Score: {row['home_score']}-{row['away_score']}")
            print(f"  Commentary: {row['llm_commentary']}")

print('\n\n3. PENALTY (Period 1-4) CHECK:')
print('-'*40)
for f in files:
    if 'Germany' in f and 'Denmark' in f:
        df = pd.read_csv(f)
        penalties = df[df['detected_type'].str.contains('Penalty', na=False)]
        for _, row in penalties.iterrows():
            if row.get('period', 1) <= 4:  # Period 1-4 only
                print(f"Min {row['minute']}: [{row['detected_type']}]")
                print(f"  {row['llm_commentary']}")

print('\n\n4. SHOOTOUT CHECK:')
print('-'*40)
for f in files:
    df = pd.read_csv(f)
    shootout = df[df['period'] == 5] if 'period' in df.columns else pd.DataFrame()
    if len(shootout) > 0:
        match_name = f.split('match_')[1].split('_V6')[0].replace('_', ' ')
        print(f'\n{match_name}: {len(shootout)} penalties')
        for _, row in shootout.head(3).iterrows():
            print(f"  {row['llm_commentary'][:80]}...")

print('\n\n5. DETAILED HALLUCINATION EXAMPLES:')
print('-'*40)
for f in files:
    df = pd.read_csv(f)
    match_name = f.split('match_')[1].split('_V6')[0].replace('_', ' ')
    for idx, row in df.iterrows():
        comm = str(row.get('llm_commentary', ''))
        if ('corners so far' in comm.lower() or 
            'shots so far' in comm.lower() or
            'shots this half' in comm.lower()):
            minute = row['minute']
            print(f'\n{match_name} - Min {minute}:')
            print(f'  {comm}')

print('\n\nDONE!')

