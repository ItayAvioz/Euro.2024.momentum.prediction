import pandas as pd

def analyze_events_360_columns():
    """
    Analyze events_360.csv column structure to identify redundant columns
    that duplicate data from matches_lineups.csv or have player redundancy
    """
    print("🔍 ANALYZING: events_360.csv column structure")
    print("=" * 60)
    
    # Read just the header and a few sample rows
    df_sample = pd.read_csv('Data/events_360.csv', nrows=3)
    
    print(f"📊 Total columns: {len(df_sample.columns)}")
    print(f"📊 Sample rows: {len(df_sample)}")
    
    print("\n📋 ALL COLUMNS:")
    for i, col in enumerate(df_sample.columns, 1):
        print(f"{i:2d}. {col}")
    
    print("\n🔍 IDENTIFYING REDUNDANT COLUMNS:")
    print("=" * 40)
    
    # Check for team/match duplicates (available in matches_lineups.csv)
    team_match_cols = []
    for col in df_sample.columns:
        if any(keyword in col.lower() for keyword in ['home_team', 'away_team', 'stage', 'match_date']):
            team_match_cols.append(col)
    
    print(f"\n❌ TEAM/MATCH DUPLICATES (available in matches_lineups.csv):")
    for col in team_match_cols:
        print(f"   • {col}")
    
    # Check for player duplicates
    player_cols = []
    for col in df_sample.columns:
        if any(keyword in col.lower() for keyword in ['player']):
            player_cols.append(col)
    
    print(f"\n🔍 PLAYER COLUMNS (check for redundancy):")
    for col in player_cols:
        print(f"   • {col}")
    
    # Show sample data for player columns to understand structure
    if player_cols:
        print(f"\n📋 SAMPLE PLAYER DATA:")
        for col in player_cols:
            print(f"\n{col}:")
            print(f"   Sample values: {df_sample[col].iloc[0]}")
    
    print(f"\n💾 POTENTIAL COLUMNS TO REMOVE:")
    potential_removals = team_match_cols.copy()
    
    # Check if we have both player_name/player_id AND player column
    has_player = 'player' in df_sample.columns
    has_player_name = 'player_name' in df_sample.columns
    has_player_id = 'player_id' in df_sample.columns
    
    if has_player and (has_player_name or has_player_id):
        print(f"   ✅ Player redundancy detected:")
        if has_player_name:
            potential_removals.append('player_name')
            print(f"      • player_name (redundant with player)")
        if has_player_id:
            potential_removals.append('player_id')
            print(f"      • player_id (redundant with player)")
    
    for col in team_match_cols:
        print(f"   • {col}")
    
    print(f"\n📊 SUMMARY:")
    print(f"   Current columns: {len(df_sample.columns)}")
    print(f"   Columns to remove: {len(potential_removals)}")
    print(f"   Final columns: {len(df_sample.columns) - len(potential_removals)}")
    
    return potential_removals

if __name__ == "__main__":
    removals = analyze_events_360_columns() 