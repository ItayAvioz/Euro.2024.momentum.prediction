#!/usr/bin/env python3
"""
Euro 2024 Data Loader and Connector
Downloads and connects all Euro 2024 StatsBomb data into connected DataFrames.

This script:
1. Downloads Euro 2024 competition data
2. Gets all matches
3. Downloads events, lineups, and 360° data for selected matches
4. Connects all data into comprehensive DataFrames
5. Saves the data locally for your project
"""

import pandas as pd
import numpy as np
import requests
import json
import os
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import time

class Euro2024DataLoader:
    """
    Downloads and processes Euro 2024 StatsBomb data
    """
    
    def __init__(self):
        self.base_url = "https://raw.githubusercontent.com/statsbomb/open-data/master/data"
        self.competition_id = 55  # UEFA Euro
        self.season_id = 282      # 2024
        self.data_folder = "euro_2024_data"
        
        # Create data folder
        os.makedirs(self.data_folder, exist_ok=True)
        
        print("🏆 Euro 2024 Data Loader Initialized")
        print(f"📁 Data will be saved to: {self.data_folder}/")
        print(f"🎯 Target: UEFA Euro 2024 (competition_id={self.competition_id}, season_id={self.season_id})")
        print()
    
    def download_matches(self) -> pd.DataFrame:
        """
        Step 1: Download all Euro 2024 matches
        """
        print("📅 Step 1: Downloading Euro 2024 matches...")
        
        url = f"{self.base_url}/matches/{self.competition_id}/{self.season_id}.json"
        print(f"   URL: {url}")
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            matches_data = response.json()
            
            matches_df = pd.DataFrame(matches_data)
            
            # Flatten team information
            matches_df['home_team_name'] = matches_df['home_team'].apply(lambda x: x['home_team_name'])
            matches_df['home_team_id'] = matches_df['home_team'].apply(lambda x: x['home_team_id'])
            matches_df['away_team_name'] = matches_df['away_team'].apply(lambda x: x['away_team_name'])
            matches_df['away_team_id'] = matches_df['away_team'].apply(lambda x: x['away_team_id'])
            
            # Add match info
            matches_df['match_date'] = pd.to_datetime(matches_df['match_date'])
            matches_df['competition_stage'] = matches_df['competition_stage'].apply(lambda x: x['name'])
            
            print(f"   ✅ Downloaded {len(matches_df)} matches")
            print(f"   📊 Date range: {matches_df['match_date'].min().date()} to {matches_df['match_date'].max().date()}")
            print(f"   🏟️  Stages: {', '.join(matches_df['competition_stage'].unique())}")
            
            # Save to CSV
            matches_file = f"{self.data_folder}/euro_2024_matches.csv"
            matches_df.to_csv(matches_file, index=False)
            print(f"   💾 Saved to: {matches_file}")
            print()
            
            return matches_df
            
        except Exception as e:
            print(f"   ❌ Error downloading matches: {e}")
            return pd.DataFrame()
    
    def download_events_for_match(self, match_id: int, match_info: str) -> pd.DataFrame:
        """
        Download events for a specific match
        """
        print(f"   ⚽ Downloading events for {match_info}...")
        
        url = f"{self.base_url}/events/{match_id}.json"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            events_data = response.json()
            
            events_df = pd.DataFrame(events_data)
            
            # Add match_id to events
            events_df['match_id'] = match_id
            
            # Flatten some nested columns for easier analysis
            if 'player' in events_df.columns:
                events_df['player_name'] = events_df['player'].apply(lambda x: x.get('name') if isinstance(x, dict) else None)
                events_df['player_id'] = events_df['player'].apply(lambda x: x.get('id') if isinstance(x, dict) else None)
            
            if 'team' in events_df.columns:
                events_df['team_name'] = events_df['team'].apply(lambda x: x.get('name') if isinstance(x, dict) else None)
                events_df['team_id'] = events_df['team'].apply(lambda x: x.get('id') if isinstance(x, dict) else None)
            
            # Add location coordinates if available
            if 'location' in events_df.columns:
                events_df['location_x'] = events_df['location'].apply(lambda x: x[0] if isinstance(x, list) and len(x) > 0 else None)
                events_df['location_y'] = events_df['location'].apply(lambda x: x[1] if isinstance(x, list) and len(x) > 1 else None)
            
            print(f"     ✅ {len(events_df)} events downloaded")
            return events_df
            
        except Exception as e:
            print(f"     ❌ Error downloading events: {e}")
            return pd.DataFrame()
    
    def download_lineups_for_match(self, match_id: int, match_info: str) -> pd.DataFrame:
        """
        Download lineups for a specific match
        """
        print(f"   👥 Downloading lineups for {match_info}...")
        
        url = f"{self.base_url}/lineups/{match_id}.json"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            lineups_data = response.json()
            
            # Flatten lineups data
            lineup_rows = []
            for team in lineups_data:
                for player in team['lineup']:
                    lineup_rows.append({
                        'match_id': match_id,
                        'team_id': team['team_id'],
                        'team_name': team['team_name'],
                        'player_id': player['player_id'],
                        'player_name': player['player_name'],
                        'jersey_number': player['jersey_number'],
                        'position_id': player['position']['id'],
                        'position_name': player['position']['name'],
                        'country': player.get('country', {}).get('name', None) if player.get('country') else None
                    })
            
            lineups_df = pd.DataFrame(lineup_rows)
            print(f"     ✅ {len(lineups_df)} players downloaded")
            return lineups_df
            
        except Exception as e:
            print(f"     ❌ Error downloading lineups: {e}")
            return pd.DataFrame()
    
    def download_360_for_match(self, match_id: int, match_info: str) -> pd.DataFrame:
        """
        Download 360° data for a specific match (if available)
        """
        print(f"   🎯 Checking 360° data for {match_info}...")
        
        url = f"{self.base_url}/three-sixty/{match_id}.json"
        
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data_360 = response.json()
                df_360 = pd.DataFrame(data_360)
                df_360['match_id'] = match_id
                print(f"     ✅ {len(df_360)} 360° frames downloaded")
                return df_360
            else:
                print(f"     ⚠️  360° data not available")
                return pd.DataFrame()
                
        except Exception as e:
            print(f"     ❌ Error downloading 360° data: {e}")
            return pd.DataFrame()
    
    def download_all_data(self, max_matches: int = 10) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Download all data types for Euro 2024
        """
        print(f"🚀 Step 2: Downloading data for first {max_matches} matches...")
        print()
        
        # Get matches first
        matches_df = self.download_matches()
        if matches_df.empty:
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
        
        # Initialize combined DataFrames
        all_events = []
        all_lineups = []
        all_360_data = []
        
        # Download data for selected matches
        selected_matches = matches_df.head(max_matches)
        
        for i, (_, match) in enumerate(selected_matches.iterrows()):
            match_id = match['match_id']
            match_info = f"{match['home_team_name']} vs {match['away_team_name']}"
            
            print(f"📥 Match {i+1}/{len(selected_matches)}: {match_info}")
            print(f"   Match ID: {match_id}")
            print(f"   Date: {match['match_date'].date()}")
            print(f"   Stage: {match['competition_stage']}")
            print(f"   Score: {match['home_score']} - {match['away_score']}")
            
            # Download events
            events_df = self.download_events_for_match(match_id, match_info)
            if not events_df.empty:
                all_events.append(events_df)
            
            # Download lineups
            lineups_df = self.download_lineups_for_match(match_id, match_info)
            if not lineups_df.empty:
                all_lineups.append(lineups_df)
            
            # Download 360° data
            data_360_df = self.download_360_for_match(match_id, match_info)
            if not data_360_df.empty:
                all_360_data.append(data_360_df)
            
            print()
            time.sleep(0.5)  # Be nice to the server
        
        # Combine all data
        print("🔗 Step 3: Combining all data into DataFrames...")
        
        combined_events = pd.concat(all_events, ignore_index=True) if all_events else pd.DataFrame()
        combined_lineups = pd.concat(all_lineups, ignore_index=True) if all_lineups else pd.DataFrame()
        combined_360 = pd.concat(all_360_data, ignore_index=True) if all_360_data else pd.DataFrame()
        
        print(f"   ✅ Combined Events: {len(combined_events)} rows")
        print(f"   ✅ Combined Lineups: {len(combined_lineups)} rows")
        print(f"   ✅ Combined 360° Data: {len(combined_360)} rows")
        print()
        
        return matches_df, combined_events, combined_lineups, combined_360
    
    def connect_data(self, matches_df: pd.DataFrame, events_df: pd.DataFrame, 
                     lineups_df: pd.DataFrame) -> pd.DataFrame:
        """
        Step 4: Connect all data types using IDs
        """
        print("🔗 Step 4: Connecting data using match_id, player_id, team_id...")
        
        if events_df.empty or lineups_df.empty:
            print("   ❌ Cannot connect - missing data")
            return pd.DataFrame()
        
        # Connect events with match information
        events_with_matches = events_df.merge(
            matches_df[['match_id', 'home_team_name', 'away_team_name', 'match_date', 
                       'competition_stage', 'home_score', 'away_score']], 
            on='match_id', 
            how='left'
        )
        
        # Connect with lineup information
        connected_df = events_with_matches.merge(
            lineups_df[['match_id', 'player_id', 'position_name', 'jersey_number', 'country']], 
            on=['match_id', 'player_id'], 
            how='left',
            suffixes=('', '_lineup')
        )
        
        print(f"   ✅ Connected DataFrame created: {len(connected_df)} rows")
        print(f"   📊 Events with player context: {len(connected_df.dropna(subset=['position_name']))} rows")
        
        # Show sample of connected data
        sample_events = connected_df[
            connected_df['type'].isin(['Goal', 'Shot', 'Pass']) & 
            connected_df['player_name'].notna()
        ].head(5)
        
        print("   📋 Sample connected events:")
        for _, event in sample_events.iterrows():
            print(f"     {event['match_date'].date()} | {event['minute']}' | {event['type']} by {event['player_name']} ({event['position_name']}) | {event['home_team_name']} vs {event['away_team_name']}")
        
        print()
        return connected_df
    
    def save_data(self, matches_df: pd.DataFrame, events_df: pd.DataFrame, 
                  lineups_df: pd.DataFrame, connected_df: pd.DataFrame, data_360_df: pd.DataFrame):
        """
        Step 5: Save all data to CSV files
        """
        print("💾 Step 5: Saving all data to CSV files...")
        
        # Save individual DataFrames
        if not matches_df.empty:
            matches_file = f"{self.data_folder}/euro_2024_matches.csv"
            matches_df.to_csv(matches_file, index=False)
            print(f"   ✅ Matches: {matches_file}")
        
        if not events_df.empty:
            events_file = f"{self.data_folder}/euro_2024_events.csv"
            events_df.to_csv(events_file, index=False)
            print(f"   ✅ Events: {events_file}")
        
        if not lineups_df.empty:
            lineups_file = f"{self.data_folder}/euro_2024_lineups.csv"
            lineups_df.to_csv(lineups_file, index=False)
            print(f"   ✅ Lineups: {lineups_file}")
        
        if not connected_df.empty:
            connected_file = f"{self.data_folder}/euro_2024_connected_data.csv"
            connected_df.to_csv(connected_file, index=False)
            print(f"   ✅ Connected Data: {connected_file}")
        
        if not data_360_df.empty:
            data_360_file = f"{self.data_folder}/euro_2024_360_data.csv"
            data_360_df.to_csv(data_360_file, index=False)
            print(f"   ✅ 360° Data: {data_360_file}")
        
        print()
    
    def analyze_data(self, matches_df: pd.DataFrame, events_df: pd.DataFrame, 
                     lineups_df: pd.DataFrame, connected_df: pd.DataFrame):
        """
        Step 6: Basic analysis of the downloaded data
        """
        print("📊 Step 6: Data Analysis Summary")
        print("=" * 50)
        
        if not matches_df.empty:
            print(f"🏟️  MATCHES ({len(matches_df)} total):")
            print(f"   📅 Tournament period: {matches_df['match_date'].min().date()} to {matches_df['match_date'].max().date()}")
            print(f"   🏆 Stages: {', '.join(matches_df['competition_stage'].unique())}")
            print(f"   ⚽ Total goals: {matches_df['home_score'].sum() + matches_df['away_score'].sum()}")
            print()
        
        if not events_df.empty:
            print(f"⚽ EVENTS ({len(events_df)} total):")
            top_events = events_df['type'].value_counts().head(5)
            for event_type, count in top_events.items():
                print(f"   {event_type}: {count:,}")
            print(f"   📈 Average events per match: {len(events_df) / len(matches_df):.0f}")
            print()
        
        if not lineups_df.empty:
            print(f"👥 LINEUPS ({len(lineups_df)} total players):")
            print(f"   🏃 Unique players: {lineups_df['player_id'].nunique()}")
            print(f"   🏳️ Countries represented: {lineups_df['country'].nunique()}")
            top_positions = lineups_df['position_name'].value_counts().head(3)
            print(f"   📍 Top positions: {', '.join([f'{pos} ({count})' for pos, count in top_positions.items()])}")
            print()
        
        if not connected_df.empty:
            print(f"🔗 CONNECTED DATA ({len(connected_df)} total rows):")
            print(f"   📊 Events with player context: {len(connected_df.dropna(subset=['player_name']))}")
            print(f"   ⚽ Goals: {len(connected_df[connected_df['type'] == 'Goal'])}")
            print(f"   🎯 Shots: {len(connected_df[connected_df['type'] == 'Shot'])}")
            print(f"   🎯 Passes: {len(connected_df[connected_df['type'] == 'Pass'])}")
            print()
        
        print("✅ Data download and connection complete!")
        print(f"📁 All files saved to: {self.data_folder}/")


def main():
    """
    Main function to download and connect Euro 2024 data
    """
    print("🚀 Euro 2024 StatsBomb Data Loader")
    print("=" * 60)
    print("📥 Downloading and connecting UEFA Euro 2024 data...")
    print()
    
    # Initialize loader
    loader = Euro2024DataLoader()
    
    # Download all data (limit to first 10 matches for demonstration)
    matches_df, events_df, lineups_df, data_360_df = loader.download_all_data(max_matches=10)
    
    # Connect the data
    connected_df = loader.connect_data(matches_df, events_df, lineups_df)
    
    # Save everything
    loader.save_data(matches_df, events_df, lineups_df, connected_df, data_360_df)
    
    # Analyze the data
    loader.analyze_data(matches_df, events_df, lineups_df, connected_df)
    
    print("\n🎯 Next Steps for Your Project:")
    print("1. Load the CSV files for analysis: euro_2024_connected_data.csv")
    print("2. Use connected_df for commentary generation")
    print("3. Analyze event sequences for move quality prediction")
    print("4. Explore player performance across matches")
    
    print("\n📚 Example Usage:")
    print("```python")
    print("import pandas as pd")
    print("connected_data = pd.read_csv('euro_2024_data/euro_2024_connected_data.csv')")
    print("goals = connected_data[connected_data['type'] == 'Goal']")
    print("print(goals[['player_name', 'team_name', 'minute', 'match_date']])")
    print("```")

if __name__ == "__main__":
    main() 