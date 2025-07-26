import pandas as pd

def add_team_names_back():
    """
    Add home_team_name and away_team_name columns back to the final dataset
    
    These columns provide match context (who were the two teams in this match)
    while 'team' column provides event context (which team did this specific action)
    
    Both are needed for comprehensive analysis.
    """
    
    print("🔧 ADDING: Missing Team Name Columns")
    print("=" * 60)
    
    # Load the final dataset
    print("📋 Loading euro_2024_complete_dataset.csv...")
    df = pd.read_csv('Data/euro_2024_complete_dataset.csv')
    
    print(f"✅ Current dataset: {len(df)} rows × {len(df.columns)} columns")
    
    # Load matches data to get team names
    print("📋 Loading matches_lineups.csv...")
    matches_df = pd.read_csv('Data/matches_lineups.csv')
    
    print(f"✅ Matches data: {len(matches_df)} rows × {len(matches_df.columns)} columns")
    
    # Extract only the needed columns for merge
    team_names_data = matches_df[['match_id', 'home_team_name', 'away_team_name']].copy()
    
    print(f"\n🔍 MERGE PREPARATION:")
    print(f"   Final dataset match_ids: {df['match_id'].nunique()}")
    print(f"   Matches data match_ids: {team_names_data['match_id'].nunique()}")
    print(f"   Team names to add: home_team_name, away_team_name")
    
    # Show sample of what we're adding
    print(f"\n📊 SAMPLE TEAM NAMES TO ADD:")
    sample = team_names_data.head(3)
    for _, row in sample.iterrows():
        print(f"   Match {row['match_id']}: {row['home_team_name']} vs {row['away_team_name']}")
    
    # Merge to add team names
    print(f"\n🔗 MERGING TEAM NAMES:")
    print(f"   Strategy: LEFT JOIN to add home_team_name and away_team_name")
    
    df_with_teams = df.merge(team_names_data, on='match_id', how='left')
    
    print(f"   Original dataset: {len(df)} rows × {len(df.columns)} columns")
    print(f"   With team names: {len(df_with_teams)} rows × {len(df_with_teams.columns)} columns")
    print(f"   Row preservation: {'✅ Perfect' if len(df_with_teams) == len(df) else '❌ Row count changed!'}")
    
    # Check for any null values (indicating unmatched matches)
    null_home = df_with_teams['home_team_name'].isnull().sum()
    null_away = df_with_teams['away_team_name'].isnull().sum()
    
    if null_home > 0 or null_away > 0:
        print(f"   ⚠️  Events without team names: {max(null_home, null_away)}")
    else:
        print(f"   ✅ All events have team names")
    
    # Position the team name columns logically (after team-related columns)
    team_col_idx = df_with_teams.columns.get_loc('team')
    
    # Reorganize columns to put team names after 'team' column
    cols = df_with_teams.columns.tolist()
    cols.remove('home_team_name')
    cols.remove('away_team_name')
    cols.insert(team_col_idx + 1, 'home_team_name')
    cols.insert(team_col_idx + 2, 'away_team_name')
    
    df_with_teams = df_with_teams[cols]
    
    print(f"   Column positioning: After 'team' column for logical grouping")
    
    # Save the updated dataset
    output_file = 'Data/euro_2024_complete_dataset.csv'
    print(f"\n💾 SAVING UPDATED DATASET:")
    print(f"   Output file: {output_file}")
    
    df_with_teams.to_csv(output_file, index=False)
    
    print(f"   ✅ Saved: {len(df_with_teams)} rows × {len(df_with_teams.columns)} columns")
    
    # Final summary
    print(f"\n🎯 FINAL DATASET WITH TEAM NAMES:")
    print(f"   📁 File: euro_2024_complete_dataset.csv")
    print(f"   📊 Dimensions: {len(df_with_teams)} rows × {len(df_with_teams.columns)} columns")
    print(f"   🏠 Match context: home_team_name, away_team_name")
    print(f"   ⚽ Event context: team column")
    print(f"   ✅ Complete: Both match and event team information available")
    
    # Show team column structure
    print(f"\n📋 TEAM COLUMN STRUCTURE:")
    team_cols = [col for col in df_with_teams.columns if 'team' in col.lower()]
    for i, col in enumerate(team_cols, 1):
        print(f"   {i}. {col}")
    
    # Show column structure around team columns
    print(f"\n📋 COLUMN STRUCTURE (around team columns):")
    team_idx = df_with_teams.columns.get_loc('team')
    start_idx = max(0, team_idx - 1)
    end_idx = min(len(df_with_teams.columns), team_idx + 4)
    
    for i in range(start_idx, end_idx):
        col = df_with_teams.columns[i]
        marker = "🎯" if 'team' in col.lower() else "  "
        print(f"   {marker} {i+1:2d}. {col}")
    
    # Usage examples
    print(f"\n💡 USAGE EXAMPLES:")
    print(f"   Match context: df[['match_id', 'home_team_name', 'away_team_name']].drop_duplicates()")
    print(f"   Home team events: df[df['team'].str.contains('home_team_name_value')]")
    print(f"   Away team events: df[df['team'].str.contains('away_team_name_value')]")
    print(f"   Head-to-head: df[(df['home_team_name']=='Spain') & (df['away_team_name']=='England')]")
    
    return df_with_teams

if __name__ == "__main__":
    updated_df = add_team_names_back() 