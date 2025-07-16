import pandas as pd

def add_event_uuid_back():
    """
    Add event_uuid column back to the final dataset to track 360 data availability
    
    Logic:
    1. Load the final dataset and original 360 data
    2. Create event_uuid column: set to id if event has 360 data, null otherwise
    3. This clearly indicates which events have 360 tracking data
    """
    
    print("🔧 FIXING: Adding event_uuid column back")
    print("=" * 60)
    
    # Load the final dataset
    print("📋 Loading euro_2024_complete_dataset.csv...")
    df = pd.read_csv('Data/euro_2024_complete_dataset.csv')
    
    print(f"✅ Current dataset: {len(df)} rows × {len(df.columns)} columns")
    
    # Load original 360 data to get event_uuid mapping
    print("📋 Loading original data_360_complete.csv...")
    data_360_orig = pd.read_csv('Data/data_360_complete.csv')
    
    print(f"✅ Original 360 data: {len(data_360_orig)} rows")
    
    # Get set of event IDs that have 360 data
    events_with_360 = set(data_360_orig['event_uuid'])
    print(f"📊 Events with 360 data: {len(events_with_360):,}")
    
    # Create event_uuid column based on 360 data availability
    print(f"\n🔧 CREATING event_uuid COLUMN:")
    print(f"   Logic: event_uuid = id if event has 360 data, null otherwise")
    
    # Create the event_uuid column
    df['event_uuid'] = df['id'].apply(lambda x: x if x in events_with_360 else None)
    
    # Verify the logic
    has_360_via_uuid = df['event_uuid'].notnull().sum()
    has_360_via_visible = df['visible_area'].notnull().sum()
    
    print(f"   Events with event_uuid: {has_360_via_uuid:,}")
    print(f"   Events with visible_area: {has_360_via_visible:,}")
    print(f"   Perfect match: {'✅ Yes' if has_360_via_uuid == has_360_via_visible else '❌ No'}")
    
    # Show before/after
    print(f"\n📊 BEFORE/AFTER:")
    print(f"   Original columns: {len(df.columns) - 1}")
    print(f"   New columns: {len(df.columns)}")
    print(f"   Added: event_uuid column")
    
    # Position event_uuid column strategically (after id column)
    id_pos = df.columns.get_loc('id')
    cols = df.columns.tolist()
    cols.remove('event_uuid')
    cols.insert(id_pos + 1, 'event_uuid')
    df = df[cols]
    
    print(f"   Column position: After 'id' column for logical grouping")
    
    # Save the updated dataset
    output_file = 'Data/euro_2024_complete_dataset.csv'
    print(f"\n💾 SAVING UPDATED DATASET:")
    print(f"   Output file: {output_file}")
    
    df.to_csv(output_file, index=False)
    
    print(f"   ✅ Saved: {len(df)} rows × {len(df.columns)} columns")
    
    # Final summary
    print(f"\n🎯 FINAL DATASET WITH 360 TRACKING:")
    print(f"   📁 File: euro_2024_complete_dataset.csv")
    print(f"   📊 Dimensions: {len(df)} rows × {len(df.columns)} columns")
    print(f"   🔍 360 tracking: event_uuid column indicates data availability")
    print(f"   ✅ Data quality: Clear distinction between events with/without 360 data")
    
    # Show column structure around id/event_uuid
    print(f"\n📋 COLUMN STRUCTURE (around id/event_uuid):")
    id_idx = df.columns.get_loc('id')
    start_idx = max(0, id_idx - 2)
    end_idx = min(len(df.columns), id_idx + 5)
    
    for i in range(start_idx, end_idx):
        col = df.columns[i]
        marker = "🎯" if col in ['id', 'event_uuid'] else "  "
        print(f"   {marker} {i+1:2d}. {col}")
    
    # Usage examples
    print(f"\n💡 USAGE EXAMPLES:")
    print(f"   Filter events with 360 data: df[df['event_uuid'].notnull()]")
    print(f"   Filter events without 360 data: df[df['event_uuid'].isnull()]")
    print(f"   Count 360 coverage: df['event_uuid'].notnull().sum()")
    print(f"   360 data percentage: df['event_uuid'].notnull().mean() * 100")
    
    return df

if __name__ == "__main__":
    updated_df = add_event_uuid_back() 