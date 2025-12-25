"""
Debug: Why is momentum at minute 43 different?
"""
import pandas as pd

# Load events
events = pd.read_csv('Data/euro_2024_complete_dataset.csv', low_memory=False)
match_id = 3930158
match_events = events[events['match_id'] == match_id]

print("="*60)
print("EVENTS AT MINUTES 43, 44, 45 (window 43-45)")
print("="*60)

# Original approach: ALL events at these minutes
print("\nALL events at minutes 43-45:")
all_events = match_events[match_events['minute'].between(43, 45)]
print(f"  Total events: {len(all_events)}")
print(f"  By period: {all_events['period'].value_counts().to_dict()}")

# Period 1 only
print("\nPeriod 1 events at minutes 43-45:")
p1_events = match_events[(match_events['minute'].between(43, 45)) & (match_events['period'] == 1)]
print(f"  Total events: {len(p1_events)}")

# Period 2 only
print("\nPeriod 2 events at minutes 43-45:")
p2_events = match_events[(match_events['minute'].between(43, 45)) & (match_events['period'] == 2)]
print(f"  Total events: {len(p2_events)}")

# The original doesn't filter by period - it uses ALL events
print("\n" + "="*60)
print("KEY INSIGHT: Original uses ALL events (no period filter)")
print("="*60)
print(f"Original would use {len(all_events)} events")
print(f"Period-separated P1 uses {len(p1_events)} events")
print(f"Difference: {len(all_events) - len(p1_events)} events")

