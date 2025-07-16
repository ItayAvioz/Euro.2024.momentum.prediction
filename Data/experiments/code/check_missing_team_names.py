import pandas as pd

def check_missing_team_names():
    """
    Check if home_team_name and away_team_name columns are missing from the final dataset
    These columns are actually NOT redundant - they provide match context (who were the two teams)
    while 'team' column provides event context (which team did this specific action)
    """
    
    print("🔍 CHECKING: Missing Team Name Columns")
    print("=" * 60)
    
    # Load the final dataset
    print("📋 Loading euro_2024_complete_dataset.csv...")
    df = pd.read_csv('Data/euro_2024_complete_dataset.csv')
    
    print(f"✅ Current dataset: {len(df)} rows × {len(df.columns)} columns")
    
    # Check for team-related columns
    team_cols = [col for col in df.columns if 'team' in col.lower()]
    
    print(f"\n📋 CURRENT TEAM COLUMNS:")
    for col in team_cols:
        print(f"   • {col}")
    
    # Check if home_team_name and away_team_name are missing
    missing_cols = []
    if 'home_team_name' not in df.columns:
        missing_cols.append('home_team_name')
    if 'away_team_name' not in df.columns:
        missing_cols.append('away_team_name')
    
    print(f"\n🔍 MISSING TEAM NAME COLUMNS:")
    if missing_cols:
        for col in missing_cols:
            print(f"   ❌ {col}")
    else:
        print(f"   ✅ No missing columns")
    
    if missing_cols:
        print(f"\n💡 WHY THESE ARE NEEDED:")
        print(f"   🎯 Different purposes:")
        print(f"      • team = Which team did THIS specific event (event-level)")
        print(f"      • home_team_name/away_team_name = Who were the TWO teams in this match (match-level)")
        print(f"   📊 Use cases:")
        print(f"      • Match context: Who was playing against whom")
        print(f"      • Opponent analysis: Team performance vs specific opponents")
        print(f"      • Home advantage: Compare home vs away team performance")
        
        # Check if we have this data in matches_lineups.csv
        print(f"\n🔍 CHECKING AVAILABLE DATA:")
        try:
            matches_df = pd.read_csv('Data/matches_lineups.csv')
            print(f"   📋 matches_lineups.csv: {len(matches_df)} rows × {len(matches_df.columns)} columns")
            
            if 'home_team_name' in matches_df.columns and 'away_team_name' in matches_df.columns:
                print(f"   ✅ home_team_name and away_team_name available in matches_lineups.csv")
                print(f"   📊 Sample data:")
                sample = matches_df[['match_id', 'home_team_name', 'away_team_name']].head(3)
                for _, row in sample.iterrows():
                    print(f"      Match {row['match_id']}: {row['home_team_name']} vs {row['away_team_name']}")
                
                return True  # Can fix by re-merging
            else:
                print(f"   ❌ Data not available in matches_lineups.csv")
                return False  # Cannot fix
                
        except Exception as e:
            print(f"   ❌ Error checking matches_lineups.csv: {e}")
            return False
    
    return False  # No fix needed

if __name__ == "__main__":
    needs_fix = check_missing_team_names() 