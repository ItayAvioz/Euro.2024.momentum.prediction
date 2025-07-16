import pandas as pd

def add_team_ids_back():
    """
    Add home_team_id and away_team_id columns back to the final dataset
    
    These columns provide match context with team IDs (for joins and analysis)
    complementing the existing home_team_name and away_team_name columns
    
    Complete team information needed:
    - Event level: team (JSON with id and name)
    - Match level: home_team_name, away_team_name, home_team_id, away_team_id
    """
    
    print("🔧 ADDING: Missing Team ID Columns")
    print("=" * 60)
    
    # Load the final dataset
    print("📋 Loading euro_2024_complete_dataset.csv...")
    df = pd.read_csv('Data/euro_2024_complete_dataset.csv')
    
    print(f"✅ Current dataset: {len(df)} rows × {len(df.columns)} columns")
    
    # Load matches data to get team IDs
    print("📋 Loading matches_lineups.csv...")
    matches_df = pd.read_csv('Data/matches_lineups.csv')
    
    print(f"✅ Matches data: {len(matches_df)} rows × {len(matches_df.columns)} columns")
    
    # Check what team-related columns we have
    current_team_cols = [col for col in df.columns if 'team' in col.lower()]
    matches_team_cols = [col for col in matches_df.columns if 'team' in col.lower()]
    
    print(f"\n📋 CURRENT TEAM COLUMNS IN DATASET:")
    for col in current_team_cols:
        print(f"   • {col}")
    
    print(f"\n📋 AVAILABLE TEAM COLUMNS IN MATCHES:")
    for col in matches_team_cols:
        print(f"   • {col}")
    
    # Extract team ID columns from matches
    team_ids_data = matches_df[['match_id', 'home_team_id', 'away_team_id']].copy()
    
    print(f"\n🔍 MERGE PREPARATION:")
    print(f"   Final dataset match_ids: {df['match_id'].nunique()}")
    print(f"   Matches data match_ids: {team_ids_data['match_id'].nunique()}")
    print(f"   Team IDs to add: home_team_id, away_team_id")
    
    # Show sample of what we're adding
    print(f"\n📊 SAMPLE TEAM IDS TO ADD:")
    sample = team_ids_data.head(3)
    for _, row in sample.iterrows():
        print(f"   Match {row['match_id']}: Home ID={row['home_team_id']}, Away ID={row['away_team_id']}")
    
    # Merge to add team IDs
    print(f"\n🔗 MERGING TEAM IDS:")
    print(f"   Strategy: LEFT JOIN to add home_team_id and away_team_id")
    
    df_with_team_ids = df.merge(team_ids_data, on='match_id', how='left')
    
    print(f"   Original dataset: {len(df)} rows × {len(df.columns)} columns")
    print(f"   With team IDs: {len(df_with_team_ids)} rows × {len(df_with_team_ids.columns)} columns")
    print(f"   Row preservation: {'✅ Perfect' if len(df_with_team_ids) == len(df) else '❌ Row count changed!'}")
    
    # Check for any null values (indicating unmatched matches)
    null_home_id = df_with_team_ids['home_team_id'].isnull().sum()
    null_away_id = df_with_team_ids['away_team_id'].isnull().sum()
    
    if null_home_id > 0 or null_away_id > 0:
        print(f"   ⚠️  Events without team IDs: {max(null_home_id, null_away_id)}")
    else:
        print(f"   ✅ All events have team IDs")
    
    # Position the team ID columns logically (after team name columns)
    away_team_name_idx = df_with_team_ids.columns.get_loc('away_team_name')
    
    # Reorganize columns to put team IDs after team names
    cols = df_with_team_ids.columns.tolist()
    cols.remove('home_team_id')
    cols.remove('away_team_id')
    cols.insert(away_team_name_idx + 1, 'home_team_id')
    cols.insert(away_team_name_idx + 2, 'away_team_id')
    
    df_with_team_ids = df_with_team_ids[cols]
    
    print(f"   Column positioning: After team names for logical grouping")
    
    # Save the updated dataset
    output_file = 'Data/euro_2024_complete_dataset.csv'
    print(f"\n💾 SAVING UPDATED DATASET:")
    print(f"   Output file: {output_file}")
    
    df_with_team_ids.to_csv(output_file, index=False)
    
    print(f"   ✅ Saved: {len(df_with_team_ids)} rows × {len(df_with_team_ids.columns)} columns")
    
    # Final summary
    print(f"\n🎯 FINAL DATASET WITH COMPLETE TEAM DATA:")
    print(f"   📁 File: euro_2024_complete_dataset.csv")
    print(f"   📊 Dimensions: {len(df_with_team_ids)} rows × {len(df_with_team_ids.columns)} columns")
    print(f"   🏠 Match context: home_team_name, away_team_name, home_team_id, away_team_id")
    print(f"   ⚽ Event context: team column")
    print(f"   ✅ Complete: Full team information at both event and match level")
    
    # Show complete team column structure
    print(f"\n📋 COMPLETE TEAM COLUMN STRUCTURE:")
    team_cols = [col for col in df_with_team_ids.columns if 'team' in col.lower()]
    for i, col in enumerate(team_cols, 1):
        print(f"   {i}. {col}")
    
    # Show column structure around team columns
    print(f"\n📋 COLUMN STRUCTURE (around team columns):")
    team_idx = df_with_team_ids.columns.get_loc('team')
    start_idx = max(0, team_idx - 1)
    end_idx = min(len(df_with_team_ids.columns), team_idx + 6)
    
    for i in range(start_idx, end_idx):
        col = df_with_team_ids.columns[i]
        marker = "🎯" if 'team' in col.lower() else "  "
        print(f"   {marker} {i+1:2d}. {col}")
    
    # Usage examples
    print(f"\n💡 USAGE EXAMPLES:")
    print(f"   Match context: df[['match_id', 'home_team_name', 'home_team_id', 'away_team_name', 'away_team_id']].drop_duplicates()")
    print(f"   Team lookup: df[df['home_team_id'] == 941]  # Netherlands home games")
    print(f"   ID-based joins: df.merge(other_df, left_on='home_team_id', right_on='team_id')")
    print(f"   Head-to-head by ID: df[(df['home_team_id']==941) & (df['away_team_id']==768)]")
    
    return df_with_team_ids

if __name__ == "__main__":
    updated_df = add_team_ids_back() 