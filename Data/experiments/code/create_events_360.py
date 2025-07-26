import pandas as pd
import numpy as np

def create_events_360():
    """
    Merge events_complete.csv with data_360_complete.csv
    Strategy: LEFT JOIN on event UUID to preserve ALL events
    Result: All events with 360 data where available (nulls where missing)
    """
    
    print("🔄 STEP 1B: Creating events_360.csv")
    print("=" * 60)
    
    # Load data in chunks for events (large file)
    print("📋 Loading events data...")
    events_df = pd.read_csv('Data/events_complete.csv')
    
    print("📋 Loading 360 data...")
    data_360_df = pd.read_csv('Data/data_360_complete.csv')
    
    print(f"✅ Events: {len(events_df)} rows, {len(events_df.columns)} columns")
    print(f"✅ Data 360: {len(data_360_df)} rows, {len(data_360_df.columns)} columns")
    
    # Show columns
    print("\n📋 Events columns:")
    print(list(events_df.columns))
    
    print("\n📋 Data 360 columns:")
    print(list(data_360_df.columns))
    
    # Correct join: events.id = data_360.event_uuid
    print(f"\n🔗 Join strategy: events.id = data_360.event_uuid")
    
    # Check if join keys exist
    if 'id' not in events_df.columns:
        print("❌ ERROR: 'id' column not found in events data!")
        return None
    
    if 'event_uuid' not in data_360_df.columns:
        print("❌ ERROR: 'event_uuid' column not found in 360 data!")
        return None
    
    # Remove overlapping columns (except join keys)
    overlap_cols = set(events_df.columns) & set(data_360_df.columns)
    overlap_cols.discard('id')  # Keep events.id
    overlap_cols.discard('event_uuid')  # Keep data_360.event_uuid
    
    if overlap_cols:
        print(f"🔍 Overlapping columns (will keep events version): {list(overlap_cols)}")
        data_360_df = data_360_df.drop(columns=list(overlap_cols))
    
    # Perform LEFT JOIN
    print("\n🔗 Performing LEFT JOIN (preserving all events)...")
    merged_df = events_df.merge(
        data_360_df, 
        left_on='id', 
        right_on='event_uuid', 
        how='left'
    )
    
    # Drop the duplicate event_uuid column (we keep 'id')
    if 'event_uuid' in merged_df.columns:
        merged_df = merged_df.drop(columns=['event_uuid'])
    
    # Check merge results
    data_360_cols = [col for col in data_360_df.columns if col != 'event_uuid']
    if data_360_cols:
        events_with_360 = merged_df[data_360_cols[0]].notna().sum()
        events_without_360 = len(merged_df) - events_with_360
        
        print(f"✅ Merge complete!")
        print(f"📊 Events with 360 data: {events_with_360:,}")
        print(f"📊 Events without 360 data: {events_without_360:,}")
    
    print(f"📊 Total events: {len(merged_df):,}")
    print(f"📊 Final dimensions: {len(merged_df)} rows × {len(merged_df.columns)} columns")
    
    # Save result
    output_file = 'Data/events_360.csv'
    merged_df.to_csv(output_file, index=False)
    
    print(f"\n✅ SUCCESS: Created {output_file}")
    print(f"📋 Final columns ({len(merged_df.columns)}): {list(merged_df.columns)}")
    
    # Sample data check
    if data_360_cols:
        print("\n📋 Sample merged row with 360 data:")
        sample_with_360 = merged_df[merged_df[data_360_cols[0]].notna()]
        if len(sample_with_360) > 0:
            sample = sample_with_360.iloc[0]
            print(f"Event type: {sample.get('type', 'N/A')}")
            print(f"Has 360 data: Yes")
    
    return merged_df

if __name__ == "__main__":
    result = create_events_360() 