import pandas as pd

def clean_events_360():
    """
    Clean up events_360.csv by removing redundant columns
    
    Columns to remove:
    - home_team, away_team, match_date, stage (duplicates from matches_lineups.csv)
    - player_name, player_id (redundant with unified player column)
    """
    
    print("🧹 CLEANING: events_360.csv")
    print("=" * 60)
    
    # Load the current file
    print("📋 Loading events_360.csv...")
    df = pd.read_csv('Data/events_360.csv')
    
    print(f"✅ Current: {len(df)} rows × {len(df.columns)} columns")
    
    # Define columns to remove based on analysis
    columns_to_remove = [
        # Team/Match duplicates (available in matches_lineups.csv)
        'home_team',
        'away_team', 
        'match_date',
        'stage',
        # Player duplicates (redundant with unified player column)
        'player_name',
        'player_id'
    ]
    
    # Check which columns actually exist to remove
    available_to_remove = [col for col in columns_to_remove if col in df.columns]
    missing_columns = [col for col in columns_to_remove if col not in df.columns]
    
    print(f"\n🔍 ANALYSIS:")
    print(f"   Columns to remove: {len(columns_to_remove)}")
    print(f"   Actually available: {len(available_to_remove)}")
    if missing_columns:
        print(f"   Missing (already removed?): {missing_columns}")
    
    print(f"\n❌ REMOVING REDUNDANT COLUMNS:")
    for col in available_to_remove:
        print(f"   • {col}")
    
    # Remove the columns
    df_cleaned = df.drop(columns=available_to_remove)
    
    print(f"\n✅ CLEANED RESULT:")
    print(f"   Original: {len(df)} rows × {len(df.columns)} columns")
    print(f"   Cleaned:  {len(df_cleaned)} rows × {len(df_cleaned.columns)} columns")
    print(f"   Removed:  {len(available_to_remove)} columns")
    
    # Save the cleaned file
    output_file = 'Data/events_360.csv'
    df_cleaned.to_csv(output_file, index=False)
    
    print(f"\n💾 SAVED: {output_file}")
    print(f"   ✅ Ready for final merge with matches_lineups.csv")
    
    # Show final column list
    print(f"\n📋 FINAL COLUMNS ({len(df_cleaned.columns)}):")
    for i, col in enumerate(df_cleaned.columns, 1):
        print(f"   {i:2d}. {col}")
    
    return df_cleaned

if __name__ == "__main__":
    cleaned_df = clean_events_360() 