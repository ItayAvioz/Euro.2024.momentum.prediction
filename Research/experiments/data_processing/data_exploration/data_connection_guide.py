#!/usr/bin/env python3
"""
StatsBomb Data Connection Guide
Step-by-step example showing how to connect all data types for a specific competition and season.

Example: UEFA Euro 2024 (competition_id=55, season_id=282)
"""

import pandas as pd
import requests
import json

def demonstrate_data_connections():
    """
    Complete walkthrough of StatsBomb data connections
    """
    print("🚀 StatsBomb Data Connection Guide")
    print("=" * 50)
    print("Example: UEFA Euro 2024")
    print("Competition ID: 55, Season ID: 282")
    print()
    
    base_url = "https://raw.githubusercontent.com/statsbomb/open-data/master/data"
    
    # STEP 1: Get competitions list
    print("📋 STEP 1: Load competitions.json")
    competitions_url = f"{base_url}/competitions.json"
    print(f"URL: {competitions_url}")
    
    try:
        comp_response = requests.get(competitions_url)
        competitions = pd.DataFrame(comp_response.json())
        print(f"✅ Loaded {len(competitions)} competitions")
        
        # Find Euro 2024
        euro_2024 = competitions[
            (competitions['competition_id'] == 55) & 
            (competitions['season_id'] == 282)
        ]
        if not euro_2024.empty:
            print("✅ Found UEFA Euro 2024")
        print()
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # STEP 2: Get matches for competition/season
    print("📅 STEP 2: Load matches/55/282.json")
    matches_url = f"{base_url}/matches/55/282.json"
    print(f"URL: {matches_url}")
    
    try:
        matches_response = requests.get(matches_url)
        matches = pd.DataFrame(matches_response.json())
        print(f"✅ Loaded {len(matches)} matches")
        
        # Show sample match
        sample_match = matches.iloc[0]
        match_id = sample_match['match_id']
        print(f"🏟️  Sample Match ID: {match_id}")
        print(f"   Teams: {sample_match['home_team']['home_team_name']} vs {sample_match['away_team']['away_team_name']}")
        print()
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # STEP 3A: Get events data
    print(f"⚽ STEP 3A: Load events/{match_id}.json")
    events_url = f"{base_url}/events/{match_id}.json"
    print(f"URL: {events_url}")
    
    try:
        events_response = requests.get(events_url)
        events = pd.DataFrame(events_response.json())
        print(f"✅ Loaded {len(events)} events")
        
        # Show event types
        top_events = events['type'].value_counts().head(5)
        print("   Top event types:")
        for event_type, count in top_events.items():
            print(f"     {event_type}: {count}")
        print()
    except Exception as e:
        print(f"❌ Error: {e}")
        events = pd.DataFrame()
    
    # STEP 3B: Get lineups data  
    print(f"👥 STEP 3B: Load lineups/{match_id}.json")
    lineups_url = f"{base_url}/lineups/{match_id}.json"
    print(f"URL: {lineups_url}")
    
    try:
        lineups_response = requests.get(lineups_url)
        lineups_data = lineups_response.json()
        
        # Flatten lineups
        lineup_rows = []
        for team in lineups_data:
            for player in team['lineup']:
                lineup_rows.append({
                    'team_id': team['team_id'],
                    'team_name': team['team_name'],
                    'player_id': player['player_id'],
                    'player_name': player['player_name'],
                    'position': player['position']['name']
                })
        
        lineups = pd.DataFrame(lineup_rows)
        print(f"✅ Loaded {len(lineups)} players")
        print(f"   Teams: {', '.join(lineups['team_name'].unique())}")
        print()
    except Exception as e:
        print(f"❌ Error: {e}")
        lineups = pd.DataFrame()
    
    # STEP 3C: Get 360° data (if available)
    print(f"🎯 STEP 3C: Load three-sixty/{match_id}.json")
    threesixty_url = f"{base_url}/three-sixty/{match_id}.json"
    print(f"URL: {threesixty_url}")
    
    try:
        threesixty_response = requests.get(threesixty_url)
        if threesixty_response.status_code == 200:
            threesixty = pd.DataFrame(threesixty_response.json())
            print(f"✅ Loaded 360° data with {len(threesixty)} frames")
        else:
            print("⚠️  360° data not available for this match")
            threesixty = pd.DataFrame()
        print()
    except Exception as e:
        print(f"❌ Error: {e}")
        threesixty = pd.DataFrame()
    
    # STEP 4: Demonstrate data connections
    print("🔗 STEP 4: Connect data using IDs")
    
    if not events.empty and not lineups.empty:
        # Connect events with player info
        events_with_players = events.merge(
            lineups[['player_id', 'player_name', 'position', 'team_name']], 
            on='player_id', 
            how='left',
            suffixes=('', '_lineup')
        )
        
        print(f"✅ Connected events with player data")
        print(f"   Original events: {len(events)}")
        print(f"   Events with player info: {len(events_with_players.dropna(subset=['player_name']))}")
        
        # Show sample connected data
        sample_connected = events_with_players[
            events_with_players['type'].isin(['Goal', 'Shot']) & 
            events_with_players['player_name'].notna()
        ].head(3)
        
        print("   Sample connected events:")
        for _, event in sample_connected.iterrows():
            print(f"     {event['minute']}' - {event['type']} by {event['player_name']} ({event['position']})")
        print()
    
    # STEP 5: Show connection summary
    print("📊 STEP 5: Data Connection Summary")
    print("Key Connection Fields:")
    print("  • competition_id + season_id → Find matches")
    print("  • match_id → Find events, lineups, 360° data")
    print("  • player_id → Connect player across all data")
    print("  • team_id → Connect team information")
    print()
    
    print("Data Flow:")
    print("  1. competitions.json → Select competition & season")
    print("  2. matches/{comp_id}/{season_id}.json → Get match list")
    print("  3. events/{match_id}.json → Get match events")
    print("  4. lineups/{match_id}.json → Get player lineups")
    print("  5. three-sixty/{match_id}.json → Get 360° data (if available)")
    print()
    
    # STEP 6: Generate practical examples
    print("🎯 STEP 6: Practical Examples for Your Project")
    
    print("\nFor Commentary Generation:")
    print("```python")
    print("# Get key events with player context")
    print("key_events = events_with_players[")
    print("    events_with_players['type'].isin(['Goal', 'Shot', 'Card'])")
    print("].copy()")
    print("")
    print("# Generate commentary")
    print("for _, event in key_events.iterrows():")
    print("    text = f\"{event['minute']}' - {event['type']} by {event['player_name']}\"")
    print("    print(text)")
    print("```")
    print()
    
    print("For Move Quality Prediction:")
    print("```python")
    print("# Analyze passing sequences")
    print("passes = events[events['type'] == 'Pass'].copy()")
    print("passes['success'] = passes['pass_outcome'].isna()  # No outcome = successful")
    print("")
    print("# Add player context")
    print("passes_with_context = passes.merge(lineups, on='player_id')")
    print("```")
    print()
    
    print("✅ Complete data connection guide finished!")
    print("🚀 You now know how to connect all StatsBomb data types!")

if __name__ == "__main__":
    demonstrate_data_connections() 