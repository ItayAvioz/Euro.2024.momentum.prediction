import pandas as pd
import numpy as np

def analyze_360_data_coverage():
    """
    Analyze 360 data coverage and event_uuid vs id relationship
    
    Issues to check:
    1. How many events have null 360 data
    2. Is event_uuid always equal to id when 360 data exists
    3. Should event_uuid be kept as a separate tracking column
    """
    
    print("🔍 ANALYZING: 360 Data Coverage Issue")
    print("=" * 60)
    
    # Load the final dataset
    print("📋 Loading euro_2024_complete_dataset.csv...")
    df = pd.read_csv('Data/euro_2024_complete_dataset.csv')
    
    print(f"✅ Loaded: {len(df)} rows × {len(df.columns)} columns")
    
    # Check for 360 data columns
    data_360_cols = [col for col in df.columns if any(keyword in col.lower() for keyword in ['visible_area', 'freeze_frame'])]
    
    print(f"\n📋 360 DATA COLUMNS:")
    for col in data_360_cols:
        print(f"   • {col}")
    
    # Analyze null values in 360 data
    print(f"\n🔍 ANALYZING 360 DATA COVERAGE:")
    
    if 'visible_area' in df.columns:
        null_360_count = df['visible_area'].isnull().sum()
        has_360_count = df['visible_area'].notnull().sum()
        
        print(f"   Events with 360 data: {has_360_count:,}")
        print(f"   Events without 360 data: {null_360_count:,}")
        print(f"   Total events: {len(df):,}")
        print(f"   360 data coverage: {has_360_count/len(df)*100:.1f}%")
        print(f"   Missing 360 data: {null_360_count/len(df)*100:.1f}%")
    
    # Check if we still have event_uuid column
    has_event_uuid = 'event_uuid' in df.columns
    print(f"\n🔍 EVENT_UUID COLUMN STATUS:")
    print(f"   event_uuid column exists: {'✅ Yes' if has_event_uuid else '❌ No (removed)'}")
    
    if has_event_uuid:
        print(f"   Analyzing event_uuid vs id relationship...")
        
        # Check if event_uuid == id when both exist
        non_null_uuid = df['event_uuid'].notnull()
        matching_ids = df[non_null_uuid]['event_uuid'] == df[non_null_uuid]['id']
        
        print(f"   Events with event_uuid: {non_null_uuid.sum():,}")
        print(f"   event_uuid == id: {matching_ids.sum():,}")
        print(f"   Perfect match: {'✅ Yes' if matching_ids.all() else '❌ No'}")
        
        if not matching_ids.all():
            mismatched = df[non_null_uuid][~matching_ids]
            print(f"   Mismatched rows: {len(mismatched)}")
            print(f"   Sample mismatches:")
            for i, row in mismatched.head(3).iterrows():
                print(f"      Row {i}: id={row['id']}, event_uuid={row['event_uuid']}")
    
    # Check the original data files to understand the relationship
    print(f"\n🔍 CHECKING ORIGINAL DATA FILES:")
    
    try:
        print("   Loading original events_complete.csv...")
        events_orig = pd.read_csv('Data/events_complete.csv')
        print(f"   Original events: {len(events_orig):,} rows")
        
        print("   Loading original data_360_complete.csv...")
        data_360_orig = pd.read_csv('Data/data_360_complete.csv')
        print(f"   Original 360 data: {len(data_360_orig):,} rows")
        
        # Check the relationship in original data
        print(f"\n   📊 ORIGINAL DATA RELATIONSHIP:")
        print(f"   Events without 360 data: {len(events_orig) - len(data_360_orig):,}")
        print(f"   360 data coverage: {len(data_360_orig)/len(events_orig)*100:.1f}%")
        
        # Check if event_uuid in 360 data matches id in events
        if 'event_uuid' in data_360_orig.columns:
            print(f"   event_uuid column in original 360 data: ✅ Yes")
            
            # Check if all event_uuid values exist in events.id
            events_ids = set(events_orig['id'])
            uuid_ids = set(data_360_orig['event_uuid'])
            
            missing_in_events = uuid_ids - events_ids
            print(f"   event_uuid values not in events.id: {len(missing_in_events)}")
            
            if missing_in_events:
                print(f"   Sample missing: {list(missing_in_events)[:5]}")
        
    except Exception as e:
        print(f"   ❌ Error loading original files: {e}")
    
    # Recommendation
    print(f"\n💡 RECOMMENDATION:")
    
    if not has_event_uuid:
        print(f"   🚨 ISSUE: event_uuid column was removed during merge")
        print(f"   📋 PROBLEM: Cannot distinguish events with/without 360 data")
        print(f"   ✅ SOLUTION: Add event_uuid column back to track 360 data availability")
        print(f"   📊 BENEFIT: Clear indication of which events have 360 tracking data")
        
        return True  # Need to fix
    else:
        print(f"   ✅ event_uuid column exists - no action needed")
        return False  # Already good

if __name__ == "__main__":
    needs_fix = analyze_360_data_coverage() 