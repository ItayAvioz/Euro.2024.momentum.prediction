import pandas as pd

def remove_team_duplicates():
    """
    Remove redundant team columns from the final merged dataset
    
    Columns to remove (6 total):
    - team_id, team_name (redundant with 'team' column that contains JSON with both)
    - home_team_id, away_team_id (match-level constants, less specific than event-level 'team')
    - home_team_name, away_team_name (match-level constants, less specific than event-level 'team')
    
    Keep essential columns:
    - team (event-level JSON with id and name)
    - possession_team (different concept - which team has possession)
    """
    
    print("🧹 REMOVING: Team Column Duplicates")
    print("=" * 60)
    
    # Load the merged dataset
    print("📋 Loading euro_2024_complete_dataset.csv...")
    df = pd.read_csv('Data/euro_2024_complete_dataset.csv')
    
    print(f"✅ Current: {len(df)} rows × {len(df.columns)} columns")
    
    # Define redundant team columns to remove
    redundant_team_cols = [
        'team_id',           # redundant with 'team' JSON
        'team_name',         # redundant with 'team' JSON
        'home_team_id',      # match-level constant
        'away_team_id',      # match-level constant
        'home_team_name',    # match-level constant
        'away_team_name'     # match-level constant
    ]
    
    # Check which columns actually exist to remove
    available_to_remove = [col for col in redundant_team_cols if col in df.columns]
    missing_columns = [col for col in redundant_team_cols if col not in df.columns]
    
    print(f"\n🔍 ANALYSIS:")
    print(f"   Redundant team columns: {len(redundant_team_cols)}")
    print(f"   Actually available: {len(available_to_remove)}")
    if missing_columns:
        print(f"   Missing (not found): {missing_columns}")
    
    print(f"\n❌ REMOVING REDUNDANT TEAM COLUMNS:")
    for col in available_to_remove:
        print(f"   • {col}")
    
    # Show what we're keeping
    team_cols = [col for col in df.columns if 'team' in col.lower()]
    keeping_team_cols = [col for col in team_cols if col not in available_to_remove]
    
    print(f"\n✅ KEEPING ESSENTIAL TEAM COLUMNS:")
    for col in keeping_team_cols:
        print(f"   • {col}")
    
    # Remove the redundant columns
    df_cleaned = df.drop(columns=available_to_remove)
    
    print(f"\n✅ CLEANUP COMPLETED:")
    print(f"   Original: {len(df)} rows × {len(df.columns)} columns")
    print(f"   Cleaned:  {len(df_cleaned)} rows × {len(df_cleaned.columns)} columns")
    print(f"   Removed:  {len(available_to_remove)} columns")
    print(f"   Reduction: {len(available_to_remove)/len(df.columns)*100:.1f}%")
    
    # Save the final optimized dataset
    output_file = 'Data/euro_2024_complete_dataset.csv'
    print(f"\n💾 SAVING OPTIMIZED DATASET:")
    print(f"   Output file: {output_file}")
    
    df_cleaned.to_csv(output_file, index=False)
    
    print(f"   ✅ Saved: {len(df_cleaned)} rows × {len(df_cleaned.columns)} columns")
    
    # Final summary
    print(f"\n🎯 FINAL OPTIMIZED EURO 2024 DATASET:")
    print(f"   📁 File: euro_2024_complete_dataset.csv")
    print(f"   📊 Dimensions: {len(df_cleaned)} rows × {len(df_cleaned.columns)} columns")
    print(f"   🧹 Optimization: Removed all redundant team columns")
    print(f"   ✅ Team data: Unified in 'team' column + 'possession_team'")
    print(f"   🎯 Ready for: Clean momentum prediction analysis")
    
    # Show final team columns
    final_team_cols = [col for col in df_cleaned.columns if 'team' in col.lower()]
    print(f"\n📋 FINAL TEAM COLUMNS ({len(final_team_cols)}):")
    for col in final_team_cols:
        print(f"   • {col}")
    
    return df_cleaned

if __name__ == "__main__":
    optimized_df = remove_team_duplicates() 