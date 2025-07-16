import pandas as pd

def create_final_euro_2024_dataset():
    """
    Merge the two cleaned CSV files into one comprehensive Euro 2024 dataset
    
    Input files:
    - matches_lineups.csv (51 rows × 15 columns) - match and lineup data
    - events_360.csv (187,858 rows × 46 columns) - event and 360 tracking data
    
    Output:
    - euro_2024_complete_dataset.csv - comprehensive merged dataset
    """
    
    print("🔗 CREATING: Final Euro 2024 Comprehensive Dataset")
    print("=" * 60)
    
    # Load the cleaned files
    print("📋 Loading cleaned CSV files...")
    
    print("   Loading matches_lineups.csv...")
    matches_df = pd.read_csv('Data/matches_lineups.csv')
    print(f"   ✅ Loaded: {len(matches_df)} rows × {len(matches_df.columns)} columns")
    
    print("   Loading events_360.csv...")
    events_df = pd.read_csv('Data/events_360.csv')
    print(f"   ✅ Loaded: {len(events_df)} rows × {len(events_df.columns)} columns")
    
    # Check the merge key
    print(f"\n🔍 MERGE KEY ANALYSIS:")
    print(f"   matches_lineups.csv - match_id values: {matches_df['match_id'].nunique()} unique")
    print(f"   events_360.csv - match_id values: {events_df['match_id'].nunique()} unique")
    
    # Check for any match_id mismatches
    matches_ids = set(matches_df['match_id'].unique())
    events_ids = set(events_df['match_id'].unique())
    
    common_ids = matches_ids.intersection(events_ids)
    matches_only = matches_ids - events_ids
    events_only = events_ids - matches_ids
    
    print(f"   Common match_ids: {len(common_ids)}")
    if matches_only:
        print(f"   ⚠️  In matches only: {len(matches_only)} - {list(matches_only)}")
    if events_only:
        print(f"   ⚠️  In events only: {len(events_only)} - {list(events_only)}")
    
    # Perform the merge
    print(f"\n🔗 MERGING DATASETS:")
    print(f"   Strategy: LEFT JOIN events_360 ← matches_lineups on match_id")
    print(f"   This preserves all events and adds match/lineup context")
    
    # Left join: keep all events, add match info
    merged_df = events_df.merge(matches_df, on='match_id', how='left')
    
    print(f"\n✅ MERGE COMPLETED:")
    print(f"   Original events: {len(events_df)} rows")
    print(f"   Merged dataset: {len(merged_df)} rows")
    print(f"   Row preservation: {'✅ Perfect' if len(merged_df) == len(events_df) else '❌ Row count changed!'}")
    
    # Column analysis
    expected_columns = len(events_df.columns) + len(matches_df.columns) - 1  # -1 for shared match_id
    actual_columns = len(merged_df.columns)
    
    print(f"\n📊 COLUMN ANALYSIS:")
    print(f"   Events columns: {len(events_df.columns)}")
    print(f"   Matches columns: {len(matches_df.columns)}")
    print(f"   Expected total: {expected_columns} (minus 1 shared match_id)")
    print(f"   Actual total: {actual_columns}")
    print(f"   Column merge: {'✅ Perfect' if actual_columns == expected_columns else '⚠️  Unexpected count'}")
    
    # Check for any null values in critical match fields (indicating unmatched events)
    null_matches = merged_df['match_date'].isnull().sum()
    if null_matches > 0:
        print(f"   ⚠️  Events without match data: {null_matches}")
    else:
        print(f"   ✅ All events have match data")
    
    # Save the final dataset
    output_file = 'Data/euro_2024_complete_dataset.csv'
    print(f"\n💾 SAVING FINAL DATASET:")
    print(f"   Output file: {output_file}")
    
    merged_df.to_csv(output_file, index=False)
    
    print(f"   ✅ Saved: {len(merged_df)} rows × {len(merged_df.columns)} columns")
    
    # Final summary
    print(f"\n🎯 FINAL EURO 2024 COMPREHENSIVE DATASET:")
    print(f"   📁 File: euro_2024_complete_dataset.csv")
    print(f"   📊 Dimensions: {len(merged_df)} rows × {len(merged_df.columns)} columns")
    print(f"   📋 Content: All Euro 2024 events with full match context and lineups")
    print(f"   🎯 Ready for: Momentum prediction analysis and modeling")
    
    # Show column summary
    print(f"\n📋 COLUMN SUMMARY:")
    events_cols = [col for col in merged_df.columns if col in events_df.columns]
    matches_cols = [col for col in merged_df.columns if col in matches_df.columns and col != 'match_id']
    
    print(f"   Event data columns: {len(events_cols)}")
    print(f"   Match data columns: {len(matches_cols)}")
    print(f"   Shared key: match_id")
    
    return merged_df

if __name__ == "__main__":
    final_dataset = create_final_euro_2024_dataset() 