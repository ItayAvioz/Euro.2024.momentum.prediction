"""
Check for hallucinations, own goals, penalties, and chain detection in generated commentary
"""
import pandas as pd
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

# Get most recent V6 files
data_dir = Path(__file__).parent.parent / "data" / "llm_commentary"
v6_files = sorted(data_dir.glob("*_V6_*.csv"), key=lambda x: x.stat().st_mtime, reverse=True)[:5]

print(f"Checking {len(v6_files)} most recent V6 commentary files\n")
print("=" * 70)

total_hallucinations = 0
total_own_goals = 0
total_penalties = 0
total_goals = 0

for file in v6_files:
    df = pd.read_csv(file)
    match_name = file.stem
    
    print(f'\n=== {file.name} ===')
    
    # 1. Check for HALLUCINATIONS
    print('\n--- Hallucinations Check ---')
    keywords = ['corners', 'shots']
    count_words = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']
    
    hallucinations = []
    for _, row in df.iterrows():
        commentary = str(row['llm_commentary']).lower()
        detected_type = str(row['detected_type'])
        
        for kw in keywords:
            if kw in commentary:
                for count in count_words:
                    if count in commentary:
                        if 'so far' in commentary or 'total' in commentary or (kw == 'corners' and 'Shot' in detected_type):
                            hallucinations.append({
                                'minute': row['minute'],
                                'type': detected_type,
                                'commentary': row['llm_commentary'][:80]
                            })
                        break
                break
    
    if hallucinations:
        print(f'  ⚠️ Found {len(hallucinations)} potential hallucinations:')
        for h in hallucinations:
            print(f"    Min {h['minute']}: [{h['type']}] {h['commentary']}...")
        total_hallucinations += len(hallucinations)
    else:
        print('  ✅ No hallucinations found')
    
    # 2. Check for OWN GOALS
    print('\n--- Own Goal Check ---')
    own_goals = df[df['detected_type'] == 'Own Goal']
    if len(own_goals) > 0:
        print(f'  ✅ Found {len(own_goals)} Own Goal(s):')
        for _, og in own_goals.iterrows():
            score = f"{og['home_score']}-{og['away_score']}"
            print(f"    Min {og['minute']} (Score: {score}): {og['llm_commentary'][:70]}...")
        total_own_goals += len(own_goals)
    else:
        match_id = df['match_id'].iloc[0]
        if match_id == 3942382:
            print('  ⚠️ Expected Own Goal in Netherlands vs Turkey (min 76) - NOT FOUND!')
        else:
            print('  ℹ️ No own goals expected/found')
    
    # 3. Check for PENALTIES (Period 1-4)
    print('\n--- Penalty Check (Period 1-4) ---')
    penalty_awarded = df[df['detected_type'] == 'Penalty Awarded']
    penalty_goal = df[df['detected_type'] == 'Penalty Goal']
    penalty_saved = df[df['detected_type'] == 'Penalty Saved']
    penalty_missed = df[df['detected_type'] == 'Penalty Missed']
    
    all_penalties = len(penalty_awarded) + len(penalty_goal) + len(penalty_saved) + len(penalty_missed)
    
    if all_penalties > 0:
        print(f'  ✅ Found {all_penalties} Penalty event(s):')
        if len(penalty_awarded) > 0:
            for _, p in penalty_awarded.iterrows():
                print(f"    [Penalty Awarded] Min {p['minute']}: {p['llm_commentary'][:55]}...")
        if len(penalty_goal) > 0:
            for _, p in penalty_goal.iterrows():
                print(f"    [Penalty Goal] Min {p['minute']}: {p['llm_commentary'][:55]}...")
        if len(penalty_saved) > 0:
            for _, p in penalty_saved.iterrows():
                print(f"    [Penalty Saved] Min {p['minute']}: {p['llm_commentary'][:55]}...")
        if len(penalty_missed) > 0:
            for _, p in penalty_missed.iterrows():
                print(f"    [Penalty Missed] Min {p['minute']}: {p['llm_commentary'][:55]}...")
        total_penalties += all_penalties
    else:
        match_id = df['match_id'].iloc[0]
        if match_id == 3940983:
            print('  ⚠️ Expected Penalty in Germany vs Denmark (min 52) - NOT FOUND!')
        else:
            print('  ℹ️ No penalties expected/found in period 1-4')
    
    # 4. Check GOALS with chain info (direct/indirect)
    print('\n--- Goals Check (with Chain) ---')
    goals = df[df['detected_type'] == 'Goal']
    if len(goals) > 0:
        for _, g in goals.iterrows():
            chain_used = g.get('chain_used', False)
            score = f"{g['home_score']}-{g['away_score']}"
            chain_str = " [CHAIN]" if chain_used else ""
            print(f"    Min {g['minute']} (Score: {score}){chain_str}: {g['llm_commentary'][:60]}...")
        total_goals += len(goals)
    else:
        print('  ℹ️ No regular goals found')
    
    # 5. Check for SHOOTOUT penalties (Period 5)
    shootout = df[df['detected_type'].str.startswith('Penalty ', na=False)]
    if len(shootout) > 0:
        print(f'\n--- Shootout Check (Period 5) ---')
        print(f'  ✅ Found {len(shootout)} Shootout penalties')

print("\n" + "=" * 70)
print(f'\nSUMMARY:')
print(f'  Hallucinations: {total_hallucinations}')
print(f'  Own Goals detected: {total_own_goals}')
print(f'  Penalties (Period 1-4): {total_penalties}')
print(f'  Regular Goals: {total_goals}')
print("=" * 70)

