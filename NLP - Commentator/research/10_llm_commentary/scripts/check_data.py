import pandas as pd
import ast

# Load the complete dataset
df = pd.read_csv('C:/Users/yonatanam/Desktop/Euro 2024 - momentum - DS-AI project/Data/euro_2024_complete_dataset.csv', low_memory=False)

# Filter for the Final match
final = df[df['match_id'] == 3943043].copy()
print(f'Final match events: {len(final)}')

# Check for ID columns
print('\n=== ID COLUMNS ===')
id_cols = [c for c in final.columns if 'id' in c.lower() or 'uuid' in c.lower()]
print(id_cols[:10])

# Check event linking - minute 24 (where Harry Kane got yellow card)
print('\n=== FOUL EVENTS MINUTE 24 ===')
m24 = final[(final['minute'] == 24) & (final['type'].str.contains('Foul', na=False))]
for _, row in m24.iterrows():
    print(f"Type: {row['type']}")
    print(f"  Player: {row.get('player', 'N/A')}")
    print(f"  Team: {row.get('team', 'N/A')}")
    print(f"  ID: {row.get('id', 'N/A')}")
    print(f"  Related: {row.get('related_events', 'N/A')}")
    fc = row.get('foul_committed', '')
    print(f"  Foul Committed: {fc}")
    if 'card' in str(fc).lower():
        print(f"  *** HAS CARD! ***")

# Check all cards in the Final
print('\n=== ALL CARDS IN FINAL ===')
for _, row in final.iterrows():
    fc = str(row.get('foul_committed', ''))
    bb = str(row.get('bad_behaviour', ''))
    if 'card' in fc.lower() or 'card' in bb.lower():
        print(f"Minute {row['minute']}: {row.get('player', 'N/A')} ({row.get('team', 'N/A')})")
        if 'card' in fc.lower():
            print(f"  foul_committed: {fc[:100]}")
        if 'card' in bb.lower():
            print(f"  bad_behaviour: {bb[:100]}")

# Check related_events structure
print('\n=== RELATED_EVENTS STRUCTURE ===')
sample_with_related = final[final['related_events'].notna()].head(3)
for _, row in sample_with_related.iterrows():
    print(f"ID: {row.get('id', 'N/A')}")
    print(f"  related_events: {row['related_events']}")
    print(f"  Type: {row['type']}")

