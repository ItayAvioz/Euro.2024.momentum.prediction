#!/usr/bin/env python3
"""
Euro 2024 Data Downloader and Connector
Downloads Euro 2024 StatsBomb data and connects it into DataFrames
"""

import pandas as pd
import requests
import json
import os
from datetime import datetime

def download_euro_2024_data():
    """
    Download and connect Euro 2024 data
    """
    print("🏆 Euro 2024 Data Downloader")
    print("=" * 40)
    
    base_url = "https://raw.githubusercontent.com/statsbomb/open-data/master/data"
    competition_id = 55  # UEFA Euro
    season_id = 282      # 2024
    
    # Create data folder
    os.makedirs("euro_2024_data", exist_ok=True)
    
    # Step 1: Download matches
    print("📅 Step 1: Downloading Euro 2024 matches...")
    matches_url = f"{base_url}/matches/{competition_id}/{season_id}.json"
    print(f"URL: {matches_url}")
    
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
        print(f"📊 Date range: {matches_df['match_date'].min().date()} to {matches_df['match_date'].max().date()}")
        
        # Show sample matches
        print("\n📋 Sample matches:")
        for i, match in matches_df.head(5).iterrows():
            print(f"  {match['match_date'].date()} | {match['home_team_name']} {match['home_score']}-{match['away_score']} {match['away_team_name']} | {match['stage']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Step 2: Download events for ALL matches
    print(f"\n⚽ Step 2: Downloading events for ALL {len(matches_df)} matches...")
    print("🚨 This will take several minutes - downloading complete tournament data!")
    print(f"📊 Estimated time: {len(matches_df) * 0.5:.1f} minutes")
    print("⏳ Progress will be shown for each match...")
    print()
    
    all_events = []
    all_lineups = []
    
    for i in range(len(matches_df)):
        match = matches_df.iloc[i]
        match_id = match['match_id']
        match_info = f"{match['home_team_name']} vs {match['away_team_name']}"
        
        print(f"\n📥 Match {i+1}/{len(matches_df)}: {match_info} (ID: {match_id})")
        print(f"    Progress: {(i+1)/len(matches_df)*100:.1f}% complete")
        
        # Download events
        events_url = f"{base_url}/events/{match_id}.json"
        try:
            events_response = requests.get(events_url)
            events_data = events_response.json()
            events_df = pd.DataFrame(events_data)
            
            # Add match info to events
            events_df['match_id'] = match_id
            events_df['home_team'] = match['home_team_name']
            events_df['away_team'] = match['away_team_name']
            events_df['match_date'] = match['match_date']
            
            # Flatten player and team info
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
            print(f"   ✅ Events: {len(events_df)}")
            
            # Flatten event types
            events_df['event_type'] = events_df['type'].apply(
                lambda x: x.get('name') if isinstance(x, dict) else x
            )
            
            # Show event summary
            top_events = events_df['event_type'].value_counts().head(3)
            print(f"   📊 Top events: {', '.join([f'{event}: {count}' for event, count in top_events.items()])}")
            
        except Exception as e:
            print(f"   ❌ Events error: {e}")
        
        # Download lineups
        lineups_url = f"{base_url}/lineups/{match_id}.json"
        try:
            lineups_response = requests.get(lineups_url)
            lineups_data = lineups_response.json()
            
            # Flatten lineups
            lineup_rows = []
            for team in lineups_data:
                for player in team['lineup']:
                    # Handle different position formats
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
                        'position': position_name
                    })
            
            lineups_df = pd.DataFrame(lineup_rows)
            all_lineups.append(lineups_df)
            print(f"   ✅ Lineups: {len(lineups_df)} players")
            
        except Exception as e:
            print(f"   ❌ Lineups error: {e}")
        
        # Download 360° data (if available)
        data_360_url = f"{base_url}/three-sixty/{match_id}.json"
        try:
            data_360_response = requests.get(data_360_url)
            if data_360_response.status_code == 200:
                print(f"   ✅ 360° data available")
            else:
                print(f"   ⚠️  360° data not available")
        except Exception as e:
            print(f"   ❌ 360° data error: {e}")
        
        # Add small delay to be respectful to server
        import time
        time.sleep(0.2)
    
    # Step 3: Combine all data
    print(f"\n🔗 Step 3: Combining all data...")
    
    if all_events:
        combined_events = pd.concat(all_events, ignore_index=True)
        print(f"✅ Combined events: {len(combined_events)} rows")
    else:
        combined_events = pd.DataFrame()
        print("❌ No events data")
    
    if all_lineups:
        combined_lineups = pd.concat(all_lineups, ignore_index=True)
        print(f"✅ Combined lineups: {len(combined_lineups)} rows")
    else:
        combined_lineups = pd.DataFrame()
        print("❌ No lineups data")
    
    # Step 4: Connect events with lineups
    print(f"\n🔗 Step 4: Connecting events with player data...")
    
    if not combined_events.empty and not combined_lineups.empty:
        # Connect events with lineup data
        connected_df = combined_events.merge(
            combined_lineups[['match_id', 'player_id', 'position', 'jersey_number']], 
            on=['match_id', 'player_id'], 
            how='left',
            suffixes=('', '_lineup')
        )
        
        print(f"✅ Connected DataFrame: {len(connected_df)} rows")
        
        # Show sample connected data
        sample_events = connected_df[
            (connected_df['event_type'].isin(['Goal', 'Shot'])) & 
            (connected_df['player_name'].notna())
        ].head(10)
        
        print(f"📋 Sample connected events:")
        for _, event in sample_events.iterrows():
            print(f"   {event['minute']}' - {event['event_type']} by {event['player_name']} ({event['position']}) | {event['home_team']} vs {event['away_team']}")
        
    else:
        connected_df = pd.DataFrame()
        print("❌ Cannot connect - missing data")
    
    # Step 5: Save data
    print(f"\n💾 Step 5: Saving data to CSV files...")
    
    matches_df.to_csv("euro_2024_data/matches.csv", index=False)
    print("✅ Saved: euro_2024_data/matches.csv")
    
    if not combined_events.empty:
        combined_events.to_csv("euro_2024_data/events.csv", index=False)
        print("✅ Saved: euro_2024_data/events.csv")
    
    if not combined_lineups.empty:
        combined_lineups.to_csv("euro_2024_data/lineups.csv", index=False)
        print("✅ Saved: euro_2024_data/lineups.csv")
    
    if not connected_df.empty:
        connected_df.to_csv("euro_2024_data/connected_data.csv", index=False)
        print("✅ Saved: euro_2024_data/connected_data.csv")
    
    # Step 6: Data summary
    print(f"\n📊 Step 6: Data Summary")
    print("=" * 30)
    print(f"🏟️  Total matches: {len(matches_df)}")
    if not combined_events.empty:
        print(f"⚽ Total events: {len(combined_events):,}")
        print(f"🎯 Goals: {len(combined_events[combined_events['event_type'] == 'Goal'])}")
        print(f"🎯 Shots: {len(combined_events[combined_events['event_type'] == 'Shot'])}")
        print(f"⚽ Passes: {len(combined_events[combined_events['event_type'] == 'Pass']):,}")
    
    if not combined_lineups.empty:
        print(f"👥 Total players: {combined_lineups['player_id'].nunique()}")
        print(f"🏳️ Countries: {combined_lineups['team_name'].nunique()}")
    
    print(f"\n✅ Euro 2024 data download complete!")
    print(f"📁 Data saved to: euro_2024_data/")
    
    # Return DataFrames for further use
    return {
        'matches': matches_df,
        'events': combined_events,
        'lineups': combined_lineups,
        'connected': connected_df
    }

if __name__ == "__main__":
    # Download the data
    data = download_euro_2024_data()
    
    print(f"\n🎯 Next steps:")
    print("1. Load data: df = pd.read_csv('euro_2024_data/connected_data.csv')")
    print("2. Analyze goals: goals = df[df['type'] == 'Goal']")
    print("3. Build commentary system using connected data")
    print("4. Predict move quality using event sequences") 