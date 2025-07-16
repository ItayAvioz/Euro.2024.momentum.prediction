import pandas as pd
import json
from collections import defaultdict

def create_matches_lineups():
    """
    Merge matches_complete.csv with lineups_complete.csv
    Strategy: Aggregate lineups by match_id + team to avoid row multiplication
    Result: 1 row per match with home_lineup and away_lineup as JSON arrays
    """
    
    print("🔄 STEP 1A: Creating matches_lineups.csv")
    print("=" * 60)
    
    # Load data
    print("📋 Loading data...")
    matches_df = pd.read_csv('Data/matches_complete.csv')
    lineups_df = pd.read_csv('Data/lineups_complete.csv')
    
    print(f"✅ Matches: {len(matches_df)} rows, {len(matches_df.columns)} columns")
    print(f"✅ Lineups: {len(lineups_df)} rows, {len(lineups_df.columns)} columns")
    
    # Show sample data structure
    print("\n📋 Matches columns:")
    print(list(matches_df.columns))
    
    print("\n📋 Lineups columns:")
    print(list(lineups_df.columns))
    
    # Group lineups by match_id and team_id
    print("\n🔄 Aggregating lineups by match and team...")
    
    # Create home and away lineups for each match
    match_lineups = defaultdict(lambda: {'home_lineup': [], 'away_lineup': []})
    
    for _, lineup_row in lineups_df.iterrows():
        match_id = lineup_row['match_id']
        team_id = lineup_row['team_id']
        
        # Find if this team is home or away for this match
        match_info = matches_df[matches_df['match_id'] == match_id].iloc[0]
        
        # Use actual column names from lineups data
        player_info = {
            'player_id': lineup_row['player_id'],
            'player_name': lineup_row['player_name'],
            'jersey_number': lineup_row['jersey_number'],
            'position': lineup_row['position'],
            'team_name': lineup_row['team_name']
        }
        
        # Determine if home or away team
        if team_id == match_info['home_team_id']:
            match_lineups[match_id]['home_lineup'].append(player_info)
        elif team_id == match_info['away_team_id']:
            match_lineups[match_id]['away_lineup'].append(player_info)
    
    # Merge with matches data
    print("🔗 Merging with matches data...")
    
    # Add lineup columns to matches
    matches_df['home_lineup'] = matches_df['match_id'].map(
        lambda x: json.dumps(match_lineups[x]['home_lineup']) if x in match_lineups else '[]'
    )
    matches_df['away_lineup'] = matches_df['match_id'].map(
        lambda x: json.dumps(match_lineups[x]['away_lineup']) if x in match_lineups else '[]'
    )
    
    # Remove irrelevant columns (competition, season)
    columns_to_remove = ['competition', 'season']
    available_to_remove = [col for col in columns_to_remove if col in matches_df.columns]
    if available_to_remove:
        matches_df = matches_df.drop(columns=available_to_remove)
        print(f"🗑️ Removed columns: {available_to_remove}")
    
    # Save result
    output_file = 'Data/matches_lineups.csv'
    matches_df.to_csv(output_file, index=False)
    
    print(f"\n✅ SUCCESS: Created {output_file}")
    print(f"📊 Final dimensions: {len(matches_df)} rows × {len(matches_df.columns)} columns")
    print(f"📋 Final columns: {list(matches_df.columns)}")
    
    # Show sample lineup structure
    sample_match = matches_df.iloc[0]
    home_lineup_sample = json.loads(sample_match['home_lineup'])
    print(f"\n📋 Sample home lineup structure (first player):")
    if home_lineup_sample:
        print(json.dumps(home_lineup_sample[0], indent=2))
    
    return matches_df

if __name__ == "__main__":
    result = create_matches_lineups() 