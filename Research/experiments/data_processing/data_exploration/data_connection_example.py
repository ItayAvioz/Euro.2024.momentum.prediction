#!/usr/bin/env python3
"""
StatsBomb Data Connection Example
Demonstrates how to connect between matches, events, lineups, and 360° data
for a specific competition and season.
"""

import pandas as pd
import requests
import json
from typing import Dict, List, Optional

class StatsBombDataConnector:
    """
    Demonstrates the complete data connection workflow for StatsBomb data.
    """
    
    def __init__(self):
        self.base_url = "https://raw.githubusercontent.com/statsbomb/open-data/master/data"
        
    def step_1_get_competitions(self) -> pd.DataFrame:
        """
        Step 1: Get all available competitions and seasons
        """
        print("🏆 Step 1: Loading competitions.json")
        url = f"{self.base_url}/competitions.json"
        response = requests.get(url)
        competitions = pd.DataFrame(response.json())
        print(f"   Found {len(competitions)} total competitions")
        return competitions
    
    def step_2_select_competition(self, competitions: pd.DataFrame, 
                                  competition_name: str, season_name: str) -> Dict:
        """
        Step 2: Select specific competition and season
        """
        print(f"🔍 Step 2: Selecting {competition_name} {season_name}")
        
        selected = competitions[
            (competitions['competition_name'] == competition_name) & 
            (competitions['season_name'] == season_name)
        ]
        
        if selected.empty:
            print(f"   ❌ No data found for {competition_name} {season_name}")
            return None
            
        comp_data = selected.iloc[0].to_dict()
        print(f"   ✅ Found: competition_id={comp_data['competition_id']}, season_id={comp_data['season_id']}")
        return comp_data
    
    def step_3_get_matches(self, competition_id: int, season_id: int) -> pd.DataFrame:
        """
        Step 3: Get all matches for the selected competition and season
        """
        print(f"📅 Step 3: Loading matches for competition_id={competition_id}, season_id={season_id}")
        
        url = f"{self.base_url}/matches/{competition_id}/{season_id}.json"
        print(f"   URL: {url}")
        
        try:
            response = requests.get(url)
            matches = pd.DataFrame(response.json())
            print(f"   ✅ Found {len(matches)} matches")
            return matches
        except Exception as e:
            print(f"   ❌ Error loading matches: {e}")
            return pd.DataFrame()
    
    def step_4_select_match(self, matches: pd.DataFrame, match_index: int = 0) -> Dict:
        """
        Step 4: Select a specific match
        """
        if matches.empty:
            print("   ❌ No matches available")
            return None
            
        match = matches.iloc[match_index]
        print(f"🏟️  Step 4: Selected match {match_index + 1}")
        print(f"   Match ID: {match['match_id']}")
        print(f"   Teams: {match['home_team']['home_team_name']} vs {match['away_team']['away_team_name']}")
        print(f"   Score: {match['home_score']} - {match['away_score']}")
        
        return match.to_dict()
    
    def step_5a_get_events(self, match_id: int) -> pd.DataFrame:
        """
        Step 5A: Get match events data
        """
        print(f"⚽ Step 5A: Loading events for match_id={match_id}")
        
        url = f"{self.base_url}/events/{match_id}.json"
        print(f"   URL: {url}")
        
        try:
            response = requests.get(url)
            events = pd.DataFrame(response.json())
            print(f"   ✅ Found {len(events)} events")
            
            # Show event type breakdown
            event_types = events['type'].value_counts().head(5)
            print("   Top 5 event types:")
            for event_type, count in event_types.items():
                print(f"     {event_type}: {count}")
                
            return events
        except Exception as e:
            print(f"   ❌ Error loading events: {e}")
            return pd.DataFrame()
    
    def step_5b_get_lineups(self, match_id: int) -> pd.DataFrame:
        """
        Step 5B: Get match lineups data
        """
        print(f"👥 Step 5B: Loading lineups for match_id={match_id}")
        
        url = f"{self.base_url}/lineups/{match_id}.json"
        print(f"   URL: {url}")
        
        try:
            response = requests.get(url)
            lineup_data = response.json()
            
            # Flatten the lineup data
            lineups = []
            for team in lineup_data:
                for player in team['lineup']:
                    lineups.append({
                        'team_id': team['team_id'],
                        'team_name': team['team_name'],
                        'player_id': player['player_id'],
                        'player_name': player['player_name'],
                        'position': player['position']['name'],
                        'jersey_number': player['jersey_number']
                    })
            
            lineups_df = pd.DataFrame(lineups)
            print(f"   ✅ Found {len(lineups_df)} players")
            print(f"   Teams: {lineups_df['team_name'].unique()}")
            
            return lineups_df
        except Exception as e:
            print(f"   ❌ Error loading lineups: {e}")
            return pd.DataFrame()
    
    def step_5c_get_360_data(self, match_id: int) -> pd.DataFrame:
        """
        Step 5C: Get 360° data (if available)
        """
        print(f"🎯 Step 5C: Loading 360° data for match_id={match_id}")
        
        url = f"{self.base_url}/three-sixty/{match_id}.json"
        print(f"   URL: {url}")
        
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data_360 = pd.DataFrame(response.json())
                print(f"   ✅ Found 360° data with {len(data_360)} frames")
                return data_360
            else:
                print(f"   ⚠️  360° data not available for this match")
                return pd.DataFrame()
        except Exception as e:
            print(f"   ❌ Error loading 360° data: {e}")
            return pd.DataFrame()
    
    def step_6_connect_data(self, events: pd.DataFrame, lineups: pd.DataFrame) -> pd.DataFrame:
        """
        Step 6: Demonstrate how to connect events with lineup data
        """
        print("🔗 Step 6: Connecting events with lineup data")
        
        if events.empty or lineups.empty:
            print("   ❌ Cannot connect - missing data")
            return pd.DataFrame()
        
        # Connect events to player information
        events_with_players = events.merge(
            lineups[['player_id', 'player_name', 'position', 'team_name']], 
            on='player_id', 
            how='left',
            suffixes=('', '_lineup')
        )
        
        print(f"   ✅ Connected {len(events_with_players)} events with player data")
        
        # Show example of connected data
        sample_events = events_with_players[
            events_with_players['type'].isin(['Goal', 'Shot', 'Pass'])
        ].dropna(subset=['player_name']).head(3)
        
        print("   Sample connected events:")
        for _, event in sample_events.iterrows():
            print(f"     {event['minute']}' - {event['type']} by {event['player_name']} ({event['position']})")
        
        return events_with_players
    
    def step_7_generate_commentary(self, events: pd.DataFrame) -> List[str]:
        """
        Step 7: Generate sample commentary from connected data
        """
        print("📺 Step 7: Generating commentary from connected data")
        
        if events.empty:
            return []
        
        # Extract key events for commentary
        key_events = events[events['type'].isin(['Goal', 'Shot', 'Card', 'Substitution'])].copy()
        
        commentary = []
        for _, event in key_events.head(5).iterrows():
            minute = event.get('minute', 0)
            event_type = event.get('type', 'Unknown')
            player_name = event.get('player_name', 'Unknown Player')
            team_name = event.get('team_name', 'Unknown Team')
            
            if event_type == 'Goal':
                text = f"⚽ {minute}' - GOAL! {player_name} finds the net for {team_name}!"
            elif event_type == 'Shot':
                text = f"🎯 {minute}' - Shot attempt by {player_name} ({team_name})"
            elif event_type == 'Card':
                text = f"🟨 {minute}' - {player_name} ({team_name}) receives a card"
            elif event_type == 'Substitution':
                text = f"🔄 {minute}' - Substitution: {player_name} ({team_name})"
            else:
                text = f"⚽ {minute}' - {event_type} involving {player_name} ({team_name})"
            
            commentary.append(text)
        
        print(f"   ✅ Generated {len(commentary)} commentary lines")
        for comment in commentary:
            print(f"     {comment}")
        
        return commentary

def main():
    """
    Main function demonstrating the complete data connection workflow
    """
    print("🚀 StatsBomb Data Connection Example")
    print("=" * 60)
    
    # Initialize connector
    connector = StatsBombDataConnector()
    
    # Step 1: Get competitions
    competitions = connector.step_1_get_competitions()
    
    # Step 2: Select UEFA Euro 2024 (most recent complete tournament)
    comp_data = connector.step_2_select_competition(competitions, 'UEFA Euro', '2024')
    
    if not comp_data:
        print("❌ Competition not found. Available competitions:")
        major_comps = competitions[competitions['competition_name'].isin([
            'UEFA Euro', 'FIFA World Cup', 'Premier League', 'UEFA Champions League'
        ])]
        print(major_comps[['competition_name', 'season_name', 'competition_id', 'season_id']])
        return
    
    # Step 3: Get matches
    matches = connector.step_3_get_matches(comp_data['competition_id'], comp_data['season_id'])
    
    if matches.empty:
        print("❌ No matches found")
        return
    
    # Step 4: Select first match
    match = connector.step_4_select_match(matches, 0)
    
    if not match:
        print("❌ No match selected")
        return
    
    match_id = match['match_id']
    
    # Step 5: Get all data types
    events = connector.step_5a_get_events(match_id)
    lineups = connector.step_5b_get_lineups(match_id)
    data_360 = connector.step_5c_get_360_data(match_id)
    
    # Step 6: Connect the data
    connected_events = connector.step_6_connect_data(events, lineups)
    
    # Step 7: Generate commentary
    commentary = connector.step_7_generate_commentary(connected_events)
    
    print("\n" + "=" * 60)
    print("✅ Data Connection Workflow Complete!")
    print(f"📊 Total events: {len(events)}")
    print(f"👥 Total players: {len(lineups)}")
    print(f"🎯 360° data available: {'Yes' if not data_360.empty else 'No'}")
    print(f"📺 Commentary lines: {len(commentary)}")
    
    print("\n🎯 Next Steps:")
    print("1. Use connected_events DataFrame for analysis")
    print("2. Build ML models using the event features")
    print("3. Generate more sophisticated commentary")
    print("4. Analyze tactical patterns with 360° data")

if __name__ == "__main__":
    main() 