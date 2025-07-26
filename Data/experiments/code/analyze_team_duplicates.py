import pandas as pd

def analyze_team_duplicates():
    """
    Analyze team column redundancy in the merged dataset
    
    Suspected duplicates:
    - team_id (events) vs home_team_id/away_team_id (matches) 
    - team_name (events) vs home_team_name/away_team_name (matches)
    - team column (events) contains both id and name
    """
    
    print("🔍 ANALYZING: Team Column Redundancy")
    print("=" * 60)
    
    # Load the merged dataset
    print("📋 Loading euro_2024_complete_dataset.csv...")
    df = pd.read_csv('Data/euro_2024_complete_dataset.csv', nrows=1000)  # Sample for analysis
    
    print(f"✅ Loaded sample: {len(df)} rows × {len(df.columns)} columns")
    
    # Identify team-related columns
    team_cols = [col for col in df.columns if 'team' in col.lower()]
    
    print(f"\n📋 ALL TEAM-RELATED COLUMNS:")
    for i, col in enumerate(team_cols, 1):
        print(f"   {i:2d}. {col}")
    
    # Analyze the 'team' column from events
    print(f"\n🔍 ANALYZING 'team' COLUMN (from events):")
    if 'team' in df.columns:
        print(f"   Sample values:")
        for i, val in enumerate(df['team'].dropna().iloc[:3]):
            print(f"      {i+1}. {val}")
    
    # Check team_id and team_name from events
    print(f"\n🔍 ANALYZING team_id/team_name COLUMNS (from events):")
    if 'team_id' in df.columns:
        print(f"   team_id sample: {df['team_id'].dropna().iloc[:3].tolist()}")
    if 'team_name' in df.columns:
        print(f"   team_name sample: {df['team_name'].dropna().iloc[:3].tolist()}")
    
    # Check home/away team data from matches
    print(f"\n🔍 ANALYZING home/away team COLUMNS (from matches):")
    match_team_cols = ['home_team_id', 'away_team_id', 'home_team_name', 'away_team_name']
    for col in match_team_cols:
        if col in df.columns:
            unique_vals = df[col].nunique()
            print(f"   {col}: {unique_vals} unique values")
            print(f"      Sample: {df[col].dropna().iloc[:3].tolist()}")
    
    # Check if team column contains JSON with id and name
    print(f"\n🔍 CHECKING FOR JSON STRUCTURE IN 'team' COLUMN:")
    if 'team' in df.columns:
        sample_team = df['team'].dropna().iloc[0]
        print(f"   Sample team value: {sample_team}")
        print(f"   Type: {type(sample_team)}")
        
        # Try to parse if it's JSON-like
        if isinstance(sample_team, str) and ('{' in sample_team or '"' in sample_team):
            print(f"   ✅ Appears to be JSON structure")
        else:
            print(f"   ❌ Not JSON structure - might be simple ID or name")
    
    # Analyze redundancy
    print(f"\n💡 REDUNDANCY ANALYSIS:")
    
    redundant_cols = []
    
    # Check if team_id is redundant
    if 'team' in df.columns and 'team_id' in df.columns:
        print(f"   🔍 team vs team_id:")
        print(f"      team_id appears redundant if 'team' contains ID")
        redundant_cols.append('team_id')
    
    # Check if team_name is redundant  
    if 'team' in df.columns and 'team_name' in df.columns:
        print(f"   🔍 team vs team_name:")
        print(f"      team_name appears redundant if 'team' contains name")
        redundant_cols.append('team_name')
    
    # Check home/away team redundancy
    if 'home_team_id' in df.columns and 'away_team_id' in df.columns:
        print(f"   🔍 home_team_id/away_team_id vs team context:")
        print(f"      These are match-level constants, event-level 'team' is more specific")
        redundant_cols.extend(['home_team_id', 'away_team_id'])
    
    if 'home_team_name' in df.columns and 'away_team_name' in df.columns:
        print(f"   🔍 home_team_name/away_team_name vs team context:")
        print(f"      These are match-level constants, event-level 'team' is more specific")
        redundant_cols.extend(['home_team_name', 'away_team_name'])
    
    print(f"\n❌ RECOMMENDED COLUMNS TO REMOVE:")
    for col in redundant_cols:
        if col in df.columns:
            print(f"   • {col}")
    
    print(f"\n✅ KEEP ESSENTIAL COLUMNS:")
    keep_cols = [col for col in team_cols if col not in redundant_cols]
    for col in keep_cols:
        print(f"   • {col}")
    
    print(f"\n📊 OPTIMIZATION IMPACT:")
    print(f"   Current team columns: {len(team_cols)}")
    print(f"   Columns to remove: {len(redundant_cols)}")
    print(f"   Final team columns: {len(keep_cols)}")
    
    return redundant_cols

if __name__ == "__main__":
    redundant = analyze_team_duplicates() 