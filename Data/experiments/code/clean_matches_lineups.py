import pandas as pd

def clean_matches_lineups():
    """
    Clean up matches_lineups.csv by removing irrelevant and duplicate columns
    
    Columns to remove based on user specification:
    - match_status, match_status_360, last_updated, last_updated_360, metadata (irrelevant administrative data)
    - competition_stage (duplicate of stage)  
    - home_team, away_team (complex JSON with manager info that user finds irrelevant)
    """
    
    print("🧹 CLEANING: matches_lineups.csv")
    print("=" * 60)
    
    # Load the current file
    print("📋 Loading matches_lineups.csv...")
    df = pd.read_csv('Data/matches_lineups.csv')
    
    print(f"✅ Current: {len(df)} rows × {len(df.columns)} columns")
    print(f"📋 Current columns: {list(df.columns)}")
    
    # Define columns to remove based on user specifications
    columns_to_remove = [
        'match_status',
        'match_status_360', 
        'last_updated',
        'last_updated_360',
        'metadata',
        'competition_stage',  # duplicate of stage
        'home_team',  # complex JSON with manager info
        'away_team'   # complex JSON with manager info
    ]
    
    # Check which columns actually exist to remove
    available_to_remove = [col for col in columns_to_remove if col in df.columns]
    missing_columns = [col for col in columns_to_remove if col not in df.columns]
    
    if available_to_remove:
        print(f"🗑️ Removing columns: {available_to_remove}")
    if missing_columns:
        print(f"⚠️ Columns not found (already removed?): {missing_columns}")
    
    # Remove the columns
    df_cleaned = df.drop(columns=available_to_remove)
    
    # Save the cleaned file
    df_cleaned.to_csv('Data/matches_lineups.csv', index=False)
    
    print(f"✅ SUCCESS: Cleaned matches_lineups.csv")
    print(f"📊 Final dimensions: {len(df_cleaned)} rows × {len(df_cleaned.columns)} columns")
    print(f"📋 Final columns: {list(df_cleaned.columns)}")
    print(f"📉 Removed {len(available_to_remove)} columns")
    
    return df_cleaned

if __name__ == "__main__":
    clean_matches_lineups() 