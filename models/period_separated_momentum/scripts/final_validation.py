#!/usr/bin/env python3
"""
Final validation of period-separated momentum data.
"""

import pandas as pd
from pathlib import Path

# Paths
base_path = Path(__file__).parent.parent.parent
original_path = base_path / "preprocessing" / "data" / "targets" / "momentum_targets_streamlined.csv"
new_path = base_path / "period_separated_momentum" / "outputs" / "momentum_by_period.csv"

# Load data
print("Loading data...")
original_df = pd.read_csv(original_path)
new_df = pd.read_csv(new_path)

# Extract minute
original_df['minute'] = original_df['minute_range'].apply(lambda x: int(x.split('-')[0]))

print(f"Original: {len(original_df)} records")
print(f"New: {len(new_df)} records")

# Define overlap zones
OVERLAP_1H = list(range(43, 52))   # 43-51 (first half stoppage)
OVERLAP_2H = list(range(88, 100))  # 88-99 (second half stoppage)
OVERTIME = list(range(100, 130))   # 100+ (overtime)

# Count matches
exact_match = 0
close_match = 0  # within 0.001
different = 0
missing_in_new = 0
extra_in_new = 0

expected_diff = 0  # Differences in overlap zones
unexpected_diff = 0

for _, orig_row in original_df.iterrows():
    minute = orig_row['minute']
    mr = orig_row['minute_range']
    match_id = orig_row['match_id']
    
    # Determine which period to check
    if minute < 45:
        period = 1
    elif minute < 90:
        period = 2
    elif minute < 105:
        period = 3
    else:
        period = 4
    
    # Find in new
    new_row = new_df[(new_df['match_id'] == match_id) & 
                      (new_df['minute_range'] == mr) & 
                      (new_df['period'] == period)]
    
    if len(new_row) == 0:
        # Try other periods for overlap zones
        new_row = new_df[(new_df['match_id'] == match_id) & (new_df['minute_range'] == mr)]
        if len(new_row) == 0:
            missing_in_new += 1
            continue
        new_row = new_row.iloc[0]
    else:
        new_row = new_row.iloc[0]
    
    home_diff = abs(orig_row['team_home_momentum'] - new_row['team_home_momentum'])
    away_diff = abs(orig_row['team_away_momentum'] - new_row['team_away_momentum'])
    
    if home_diff < 0.001 and away_diff < 0.001:
        exact_match += 1
    elif home_diff < 0.01 and away_diff < 0.01:
        close_match += 1
    else:
        different += 1
        if minute in OVERLAP_1H or minute in OVERLAP_2H or minute in OVERTIME:
            expected_diff += 1
        else:
            unexpected_diff += 1

# Results
print("\n" + "="*60)
print("FINAL VALIDATION RESULTS")
print("="*60)

print(f"\n📊 Match Statistics:")
print(f"  Exact match (diff < 0.001): {exact_match} ({100*exact_match/len(original_df):.1f}%)")
print(f"  Close match (diff < 0.01):  {close_match} ({100*close_match/len(original_df):.1f}%)")
print(f"  Different:                  {different} ({100*different/len(original_df):.1f}%)")
print(f"  Missing in new:             {missing_in_new}")

print(f"\n📊 Difference Analysis:")
print(f"  Expected (overlap/overtime): {expected_diff}")
print(f"  Unexpected:                  {unexpected_diff}")

total_same = exact_match + close_match
print(f"\n✅ TOTAL MATCHING: {total_same}/{len(original_df)} ({100*total_same/len(original_df):.1f}%)")

if unexpected_diff == 0 and missing_in_new <= 15:
    print("\n🎉 SUCCESS! All differences are in expected zones (overlap/overtime)!")
else:
    print(f"\n⚠️ {unexpected_diff} unexpected differences found")

# Period distribution in new data
print("\n📊 New Data Period Distribution:")
for p in sorted(new_df['period'].unique()):
    count = len(new_df[new_df['period'] == p])
    print(f"  Period {p}: {count} records")

