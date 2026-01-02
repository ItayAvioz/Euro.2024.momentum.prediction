"""Check own goal commentary."""
import pandas as pd
import glob
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

files = sorted(glob.glob('../../data/llm_commentary/*V6*.csv'), key=os.path.getmtime, reverse=True)[:2]

print("=" * 70)
print("OWN GOAL COMMENTARY CHECK")
print("=" * 70)

for f in files:
    df = pd.read_csv(f)
    match = os.path.basename(f).split('_V6')[0].replace('match_', '').replace('_', ' ')
    
    # Show all detected types
    print(f"\n{match}:")
    types = df['detected_type'].value_counts().head(10)
    print(f"  Types: {dict(types)}")
    
    # Check for own goals
    own_goals = df[df['detected_type'] == 'Own Goal']
    if len(own_goals) > 0:
        print("  OWN GOALS:")
        for _, row in own_goals.iterrows():
            print(f"    Min {row['minute']}: {row['llm_commentary']}")
    else:
        # Check for Goal containing "own"
        goals = df[df['detected_type'] == 'Goal']
        for _, row in goals.iterrows():
            if 'own' in str(row['llm_commentary']).lower():
                print(f"  Goal with 'own': Min {row['minute']}: {row['llm_commentary']}")

