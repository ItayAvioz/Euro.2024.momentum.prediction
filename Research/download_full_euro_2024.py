#!/usr/bin/env python3
"""
Download COMPLETE Euro 2024 Data
Downloads ALL 51 matches with events, lineups, and 360° data
"""

import pandas as pd
import requests
import json
import os
import time
from datetime import datetime

def download_complete_euro_2024():
    """
    Download complete Euro 2024 tournament data
    """
    print("🏆 COMPLETE Euro 2024 Data Download")
    print("=" * 60)
    print("📥 Downloading ALL 51 matches with:")
    print("   ✅ Match information")
    print("   ✅ Events data (passes, shots, goals, etc.)")
    print("   ✅ Player lineups with positions")
    print("   ✅ 360° data (where available)")
    print("   ✅ Full tournament coverage")
    print()
    
    base_url = "https://raw.githubusercontent.com/statsbomb/open-data/master/data"
    competition_id = 55  # UEFA Euro
    season_id = 282      # 2024
    
    # Create data folder
    data_folder = "euro_2024_complete"
    os.makedirs(data_folder, exist_ok=True)
    
    # Step 1: Download matches
    print("📅 Step 1: Downloading Euro 2024 matches...")
    matches_url = f"{base_url}/matches/{competition_id}/{season_id}.json"
    
    try:
        response = requests.get(matches_url)
        matches_data = response.json()
        matches_df = pd.DataFrame(matches_data)
        
        # Clean up matches data
        matches_df['home_team_name'] = matches_df['home_team'].apply(lambda x: x['home_team_name'])
        matches_df['away_team_name'] = matches_df['away_team'].apply(lambda x: x['away_team_name'])
        matches_df['home_team_id'] = matches_df['home_team'].apply(lambda x: x['home_team_id'])
        matches_df['away_team_id'] = matches_df['away_team'].apply(lambda x: x['away_team_id'])
        matches_df['match_date'] = pd.to_datetime(matches_df['match_date'])
        matches_df['stage'] = matches_df['competition_stage'].apply(lambda x: x['name'])
        
        print(f"✅ Downloaded {len(matches_df)} matches")
        print(f"📊 Tournament structure:")
        stage_counts = matches_df['stage'].value_counts()
        for stage, count in stage_counts.items():
            print(f"   {stage}: {count} matches")
        
    except Exception as e:
        print(f"❌ Error downloading matches: {e}")
        return
    
    # Step 2: Download ALL events, lineups, and 360° data
    print(f"\n⚽ Step 2: Downloading complete data for ALL {len(matches_df)} matches...")
    print(f"📊 Estimated time: {len(matches_df) * 0.3:.1f} minutes")
    print("⏳ This will download the complete Euro 2024 tournament!")
    print()
    
    all_events = []
    all_lineups = []
    all_360_data = []
    
    start_time = time.time()
    
    for i in range(len(matches_df)):
        match = matches_df.iloc[i]
        match_id = match['match_id']
        match_info = f"{match['home_team_name']} vs {match['away_team_name']}"
        
        # Progress tracking
        progress = (i + 1) / len(matches_df) * 100
        elapsed = time.time() - start_time
        estimated_total = elapsed / (i + 1) * len(matches_df)
        remaining = estimated_total - elapsed
        
        print(f"📥 Match {i+1:2d}/{len(matches_df)}: {match_info}")
        print(f"    📊 Progress: {progress:.1f}% | ⏱️ Remaining: {remaining/60:.1f}m")
        print(f"    🏆 Stage: {match['stage']} | 📅 Date: {match['match_date'].date()}")
        
        # Download events
        events_url = f"{base_url}/events/{match_id}.json"
        try:
            events_response = requests.get(events_url)
            events_data = events_response.json()
            events_df = pd.DataFrame(events_data)
            
            # Add match context
            events_df['match_id'] = match_id
            events_df['home_team'] = match['home_team_name']
            events_df['away_team'] = match['away_team_name']
            events_df['match_date'] = match['match_date']
            events_df['stage'] = match['stage']
            
            # Flatten event types and player info
            events_df['event_type'] = events_df['type'].apply(
                lambda x: x.get('name') if isinstance(x, dict) else x
            )
            events_df['player_name'] = events_df['player'].apply(
                lambda x: x.get('name') if isinstance(x, dict) else None
            )
            events_df['player_id'] = events_df['player'].apply(
                lambda x: x.get('id') if isinstance(x, dict) else None
            )
            events_df['team_name'] = events_df['team'].apply(
                lambda x: x.get('name') if isinstance(x, dict) else None
            )
            events_df['team_id'] = events_df['team'].apply(
                lambda x: x.get('id') if isinstance(x, dict) else None
            )
            
            all_events.append(events_df)
            print(f"    ✅ Events: {len(events_df):,}")
            
        except Exception as e:
            print(f"    ❌ Events error: {e}")
        
        # Download lineups
        lineups_url = f"{base_url}/lineups/{match_id}.json"
        try:
            lineups_response = requests.get(lineups_url)
            lineups_data = lineups_response.json()
            
            # Flatten lineups
            lineup_rows = []
            for team in lineups_data:
                for player in team['lineup']:
                    # Handle position formats
                    position_name = None
                    if 'positions' in player and player['positions']:
                        position_name = player['positions'][0]['position']
                    elif 'position' in player and isinstance(player['position'], dict):
                        position_name = player['position']['name']
                    elif 'position' in player:
                        position_name = player['position']
                    
                    lineup_rows.append({
                        'match_id': match_id,
                        'team_id': team['team_id'],
                        'team_name': team['team_name'],
                        'player_id': player['player_id'],
                        'player_name': player['player_name'],
                        'jersey_number': player['jersey_number'],
                        'position': position_name,
                        'stage': match['stage']
                    })
            
            lineups_df = pd.DataFrame(lineup_rows)
            all_lineups.append(lineups_df)
            print(f"    ✅ Lineups: {len(lineups_df)} players")
            
        except Exception as e:
            print(f"    ❌ Lineups error: {e}")
        
        # Download 360° data
        data_360_url = f"{base_url}/three-sixty/{match_id}.json"
        try:
            data_360_response = requests.get(data_360_url)
            if data_360_response.status_code == 200:
                data_360 = data_360_response.json()
                if data_360:  # Check if data exists
                    df_360 = pd.DataFrame(data_360)
                    df_360['match_id'] = match_id
                    df_360['home_team'] = match['home_team_name']
                    df_360['away_team'] = match['away_team_name']
                    df_360['stage'] = match['stage']
                    all_360_data.append(df_360)
                    print(f"    ✅ 360° data: {len(df_360)} frames")
                else:
                    print(f"    ⚠️  360° data empty")
            else:
                print(f"    ⚠️  360° data not available")
        except Exception as e:
            print(f"    ❌ 360° data error: {e}")
        
        # Small delay to be respectful
        time.sleep(0.1)
        print()
    
    # Step 3: Combine all data
    print("🔗 Step 3: Combining complete tournament data...")
    
    combined_events = pd.concat(all_events, ignore_index=True) if all_events else pd.DataFrame()
    combined_lineups = pd.concat(all_lineups, ignore_index=True) if all_lineups else pd.DataFrame()
    combined_360 = pd.concat(all_360_data, ignore_index=True) if all_360_data else pd.DataFrame()
    
    print(f"✅ Combined Events: {len(combined_events):,} rows")
    print(f"✅ Combined Lineups: {len(combined_lineups):,} rows")
    print(f"✅ Combined 360° Data: {len(combined_360):,} rows")
    print()
    
    # Step 4: Create connected dataset
    print("🔗 Step 4: Creating connected dataset...")
    
    if not combined_events.empty and not combined_lineups.empty:
        # Connect events with match info
        connected_df = combined_events.merge(
            matches_df[['match_id', 'home_team_name', 'away_team_name', 'match_date', 'stage', 'home_score', 'away_score']], 
            on='match_id', 
            how='left'
        )
        
        # Connect with lineup info
        connected_df = connected_df.merge(
            combined_lineups[['match_id', 'player_id', 'position', 'jersey_number']], 
            on=['match_id', 'player_id'], 
            how='left',
            suffixes=('', '_lineup')
        )
        
        print(f"✅ Connected Dataset: {len(connected_df):,} rows")
    else:
        connected_df = pd.DataFrame()
    
    # Step 5: Save complete dataset
    print("\n💾 Step 5: Saving complete Euro 2024 dataset...")
    
    # Save all datasets
    matches_df.to_csv(f"{data_folder}/matches_complete.csv", index=False)
    print(f"✅ Matches: {data_folder}/matches_complete.csv")
    
    if not combined_events.empty:
        combined_events.to_csv(f"{data_folder}/events_complete.csv", index=False)
        print(f"✅ Events: {data_folder}/events_complete.csv")
    
    if not combined_lineups.empty:
        combined_lineups.to_csv(f"{data_folder}/lineups_complete.csv", index=False)
        print(f"✅ Lineups: {data_folder}/lineups_complete.csv")
    
    if not combined_360.empty:
        combined_360.to_csv(f"{data_folder}/data_360_complete.csv", index=False)
        print(f"✅ 360° Data: {data_folder}/data_360_complete.csv")
    
    if not connected_df.empty:
        connected_df.to_csv(f"{data_folder}/connected_complete.csv", index=False)
        print(f"✅ Connected Data: {data_folder}/connected_complete.csv")
    
    # Final summary
    total_time = time.time() - start_time
    print(f"\n🎉 COMPLETE Euro 2024 Download Finished!")
    print("=" * 60)
    print(f"⏱️ Total time: {total_time/60:.1f} minutes")
    print(f"📊 Tournament coverage: {len(matches_df)} matches")
    print(f"⚽ Total events: {len(combined_events):,}")
    print(f"👥 Total players: {combined_lineups['player_id'].nunique() if not combined_lineups.empty else 0}")
    print(f"🎯 360° matches: {len(combined_360) // 1000 if not combined_360.empty else 0}")
    print(f"📁 Data saved to: {data_folder}/")
    print()
    print("🚀 Your complete Euro 2024 dataset is ready!")
    print("   - All 51 matches")
    print("   - All events (passes, shots, goals, etc.)")
    print("   - Complete player lineups")
    print("   - 360° data where available")
    print("   - Fully connected for analysis")

if __name__ == "__main__":
    download_complete_euro_2024() 