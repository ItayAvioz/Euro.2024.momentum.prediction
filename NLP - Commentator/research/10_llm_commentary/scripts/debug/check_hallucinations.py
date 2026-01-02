"""
Check for hallucinated corner/shot counts in generated commentary
"""
import pandas as pd
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

# Get most recent V6 files
data_dir = Path(__file__).parent.parent / "data" / "llm_commentary"
v6_files = sorted(data_dir.glob("*_V6_*.csv"), key=lambda x: x.stat().st_mtime, reverse=True)[:5]

print(f"Checking {len(v6_files)} most recent V6 commentary files\n")

total_hallucinations = 0

for file in v6_files:
    df = pd.read_csv(file)
    match_name = file.stem.split('_')[1:4]  # Extract match info
    match_name = ' '.join(match_name)
    
    print('=' * 70)
    print(f'CHECKING: {file.name}')
    print('=' * 70)
    
    # Check for hallucinations (corner/shot counts that are NOT about multiple events in same minute)
    print('\n--- Potential Hallucinations (invented counts) ---')
    keywords = ['corners', 'shots']
    count_words = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']
    
    found = []
    for _, row in df.iterrows():
        commentary = str(row['llm_commentary']).lower()
        detected_type = str(row['detected_type'])
        
        # Check for corner/shot counts
        for kw in keywords:
            if kw in commentary:
                for count in count_words:
                    if count in commentary:
                        # Check if this is a "so far" or "total" count (hallucination)
                        if 'so far' in commentary or 'total' in commentary or (kw == 'corners' and 'Shot' in detected_type):
                            found.append({
                                'minute': row['minute'],
                                'type': detected_type,
                                'chain': row.get('chain_used', False),
                                'commentary': row['llm_commentary']
                            })
                        break
                break
    
    if found:
        print(f'Found {len(found)} potential hallucinations:')
        for f in found:
            chain_str = " [CHAIN]" if f['chain'] else ""
            print(f"\nMin {f['minute']}: [{f['type']}]{chain_str}")
            print(f"  {f['commentary']}")
        total_hallucinations += len(found)
    else:
        print('No hallucinations found!')
    
    # Check for VALID multiple events (should have counts)
    print('\n--- Minutes with Multiple Corners/Shots (valid counts) ---')
    multi_count = 0
    for minute in df['minute'].unique():
        minute_rows = df[df['minute'] == minute]
        
        # Count corners and shots
        corners = minute_rows[minute_rows['detected_type'] == 'Corner']
        shots = minute_rows[minute_rows['detected_type'].str.contains('Shot', na=False)]
        
        if len(corners) >= 2:
            print(f"Min {minute}: {len(corners)} Corners")
            multi_count += 1
        if len(shots) >= 2:
            print(f"Min {minute}: {len(shots)} Shots")
            multi_count += 1
    
    if multi_count == 0:
        print("No multiple corners/shots in same minute found")
    
    print()

print('=' * 70)
print(f'TOTAL HALLUCINATIONS ACROSS ALL MATCHES: {total_hallucinations}')
if total_hallucinations == 0:
    print('✅ SUCCESS: All commentary is clean!')
else:
    print(f'⚠️ ISSUES FOUND: {total_hallucinations} hallucinations detected')
print('=' * 70)
