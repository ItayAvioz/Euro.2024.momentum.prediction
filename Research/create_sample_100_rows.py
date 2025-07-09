#!/usr/bin/env python3
"""
Create Sample CSV with 100 Rows from Complete Euro 2024 Data
"""

import pandas as pd

def create_sample_csv():
    """Create a sample CSV with 100 rows from the complete dataset"""
    print("📊 Creating Sample CSV with 100 Rows")
    print("=" * 50)
    
    # Load the complete connected dataset
    print("📥 Loading complete dataset...")
    df = pd.read_csv('euro_2024_complete/connected_complete.csv')
    
    print(f"✅ Loaded {len(df):,} total rows")
    print(f"📊 Columns: {len(df.columns)}")
    print()
    
    # Select key columns for the sample
    key_columns = [
        'match_id', 'minute', 'second', 'event_type', 'player_name', 
        'team_name', 'position', 'home_team', 'away_team', 'match_date',
        'stage', 'home_score', 'away_score', 'jersey_number'
    ]
    
    # Filter to columns that exist
    available_columns = [col for col in key_columns if col in df.columns]
    
    print(f"📋 Selected columns: {', '.join(available_columns)}")
    print()
    
    # Get diverse sample - mix of different event types and matches
    sample_events = []
    
    # Get some events from different types
    event_types = ['Goal', 'Shot', 'Pass', 'Duel', 'Substitution', 'Yellow Card', 'Red Card']
    
    for event_type in event_types:
        events_of_type = df[df['event_type'] == event_type]
        if not events_of_type.empty:
            # Get up to 10 events of this type
            sample_count = min(10, len(events_of_type))
            sample_events.append(events_of_type.sample(n=sample_count, random_state=42))
            print(f"   ✅ Added {sample_count} {event_type} events")
    
    # Fill remaining slots with random events
    combined_sample = pd.concat(sample_events, ignore_index=True) if sample_events else pd.DataFrame()
    
    if len(combined_sample) < 100:
        remaining_needed = 100 - len(combined_sample)
        additional_sample = df.sample(n=remaining_needed, random_state=42)
        combined_sample = pd.concat([combined_sample, additional_sample], ignore_index=True)
        print(f"   ✅ Added {remaining_needed} random events")
    
    # Take exactly 100 rows
    sample_100 = combined_sample.head(100).copy()
    
    # Select only available columns
    sample_100 = sample_100[available_columns]
    
    # Clean up the data
    sample_100 = sample_100.fillna('N/A')
    
    # Sort by match_id and minute for better readability
    sample_100 = sample_100.sort_values(['match_id', 'minute', 'second']).reset_index(drop=True)
    
    # Save to CSV
    output_file = 'euro_2024_sample_100_rows.csv'
    sample_100.to_csv(output_file, index=False)
    
    print()
    print(f"💾 Sample CSV created: {output_file}")
    print(f"📊 Sample contains:")
    print(f"   Rows: {len(sample_100)}")
    print(f"   Columns: {len(sample_100.columns)}")
    print(f"   Matches covered: {sample_100['match_id'].nunique()}")
    print(f"   Players: {sample_100[sample_100['player_name'] != 'N/A']['player_name'].nunique()}")
    print()
    
    # Show event type distribution in sample
    print("📈 Event types in sample:")
    event_counts = sample_100['event_type'].value_counts()
    for event_type, count in event_counts.items():
        print(f"   {event_type}: {count}")
    
    print()
    print("🎯 Sample matches:")
    matches_in_sample = sample_100[['home_team', 'away_team', 'stage']].drop_duplicates()
    for i, (_, match) in enumerate(matches_in_sample.head(5).iterrows(), 1):
        print(f"   {i}. {match['home_team']} vs {match['away_team']} | {match['stage']}")
    
    print()
    print(f"✅ Sample file ready: {output_file}")
    print("   Perfect for viewing the data structure!")
    print("   Load with: pd.read_csv('euro_2024_sample_100_rows.csv')")
    
    return sample_100

if __name__ == "__main__":
    sample_df = create_sample_csv()
    
    # Show first few rows as preview
    print("\n📋 Preview of first 5 rows:")
    print("-" * 80)
    print(sample_df.head().to_string(index=False)) 