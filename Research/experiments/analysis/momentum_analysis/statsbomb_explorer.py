#!/usr/bin/env python3
"""
StatsBomb Data Explorer
A practical script to explore StatsBomb Open Data for soccer prediction and commentary projects.

This script helps you:
1. Explore available competitions and seasons
2. Load match data
3. Analyze events data for commentary and prediction
4. Extract text descriptions for NLP tasks
"""

import pandas as pd
import numpy as np
import json
import requests
from typing import Dict, List, Optional
import matplotlib.pyplot as plt
import seaborn as sns

class StatsBombExplorer:
    """
    A class to explore StatsBomb Open Data for soccer analysis projects.
    """
    
    def __init__(self):
        self.base_url = "https://raw.githubusercontent.com/statsbomb/open-data/master/data"
        self.competitions_cache = None
        self.matches_cache = {}
        
    def get_competitions(self) -> pd.DataFrame:
        """
        Get all available competitions and seasons.
        
        Returns:
            DataFrame with competition information
        """
        if self.competitions_cache is None:
            url = f"{self.base_url}/competitions.json"
            response = requests.get(url)
            data = response.json()
            self.competitions_cache = pd.DataFrame(data)
        
        return self.competitions_cache
    
    def get_matches(self, competition_id: int, season_id: int) -> pd.DataFrame:
        """
        Get all matches for a specific competition and season.
        
        Args:
            competition_id: ID of the competition
            season_id: ID of the season
            
        Returns:
            DataFrame with match information
        """
        cache_key = f"{competition_id}_{season_id}"
        
        if cache_key not in self.matches_cache:
            url = f"{self.base_url}/matches/{competition_id}/{season_id}.json"
            response = requests.get(url)
            data = response.json()
            self.matches_cache[cache_key] = pd.DataFrame(data)
        
        return self.matches_cache[cache_key]
    
    def get_events(self, match_id: int) -> pd.DataFrame:
        """
        Get all events for a specific match.
        
        Args:
            match_id: ID of the match
            
        Returns:
            DataFrame with event information
        """
        url = f"{self.base_url}/events/{match_id}.json"
        response = requests.get(url)
        data = response.json()
        return pd.DataFrame(data)
    
    def get_lineups(self, match_id: int) -> pd.DataFrame:
        """
        Get lineups for a specific match.
        
        Args:
            match_id: ID of the match
            
        Returns:
            DataFrame with lineup information
        """
        url = f"{self.base_url}/lineups/{match_id}.json"
        response = requests.get(url)
        data = response.json()
        
        # Flatten the lineup data
        lineup_data = []
        for team in data:
            for player in team['lineup']:
                lineup_data.append({
                    'team_id': team['team_id'],
                    'team_name': team['team_name'],
                    'player_id': player['player_id'],
                    'player_name': player['player_name'],
                    'jersey_number': player['jersey_number'],
                    'position': player['position']['name']
                })
        
        return pd.DataFrame(lineup_data)
    
    def explore_competitions(self) -> None:
        """
        Display available competitions in a user-friendly format.
        """
        comps = self.get_competitions()
        
        print("🏆 Available Competitions for Your Project:")
        print("=" * 60)
        
        # Focus on major competitions relevant to the user's needs
        major_comps = comps[comps['competition_name'].isin([
            'FIFA World Cup', 'UEFA Euro', 'Premier League', 'La Liga',
            'Serie A', 'Bundesliga', 'Ligue 1', 'UEFA Champions League',
            'Copa América', "FIFA Women's World Cup"
        ])]
        
        for _, comp in major_comps.iterrows():
            print(f"🏆 {comp['competition_name']} ({comp['season_name']})")
            print(f"   Competition ID: {comp['competition_id']}, Season ID: {comp['season_id']}")
            print(f"   Country: {comp['country_name']}")
            print()
    
    def analyze_match_events(self, match_id: int) -> Dict:
        """
        Analyze events from a match for commentary and prediction insights.
        
        Args:
            match_id: ID of the match to analyze
            
        Returns:
            Dictionary with analysis results
        """
        events = self.get_events(match_id)
        
        analysis = {
            'total_events': len(events),
            'event_types': events['type'].value_counts().to_dict(),
            'possession_changes': len(events[events['type'] == 'Ball Recovery']),
            'shots': len(events[events['type'] == 'Shot']),
            'passes': len(events[events['type'] == 'Pass']),
            'match_timeline': []
        }
        
        # Extract key moments for commentary
        key_events = events[events['type'].isin(['Goal', 'Shot', 'Foul', 'Card', 'Substitution'])]
        
        for _, event in key_events.iterrows():
            moment = {
                'minute': event['minute'],
                'type': event['type'],
                'team': event.get('team', {}).get('name', 'Unknown'),
                'player': event.get('player', {}).get('name', 'Unknown'),
                'description': self._generate_event_description(event)
            }
            analysis['match_timeline'].append(moment)
        
        return analysis
    
    def _generate_event_description(self, event: pd.Series) -> str:
        """
        Generate a natural language description of an event.
        
        Args:
            event: Event data from the events DataFrame
            
        Returns:
            String description of the event
        """
        event_type = event['type']
        player_name = event.get('player', {}).get('name', 'Unknown') if isinstance(event.get('player'), dict) else 'Unknown'
        team_name = event.get('team', {}).get('name', 'Unknown') if isinstance(event.get('team'), dict) else 'Unknown'
        minute = event.get('minute', 0)
        
        if event_type == 'Goal':
            return f"⚽ GOAL! {player_name} ({team_name}) scores in the {minute}th minute!"
        elif event_type == 'Shot':
            return f"🎯 Shot attempt by {player_name} ({team_name}) in the {minute}th minute"
        elif event_type == 'Foul':
            return f"🚫 Foul committed by {player_name} ({team_name}) in the {minute}th minute"
        elif event_type == 'Card':
            return f"🟨 Card shown to {player_name} ({team_name}) in the {minute}th minute"
        elif event_type == 'Substitution':
            return f"🔄 Substitution: {player_name} ({team_name}) in the {minute}th minute"
        else:
            return f"{event_type} by {player_name} ({team_name}) in the {minute}th minute"
    
    def get_commentary_data(self, competition_id: int, season_id: int, num_matches: int = 5) -> List[Dict]:
        """
        Extract commentary-ready data from multiple matches.
        
        Args:
            competition_id: ID of the competition
            season_id: ID of the season
            num_matches: Number of matches to analyze
            
        Returns:
            List of commentary data dictionaries
        """
        matches = self.get_matches(competition_id, season_id)
        commentary_data = []
        
        for i, (_, match) in enumerate(matches.head(num_matches).iterrows()):
            match_id = match['match_id']
            print(f"Processing match {i+1}/{num_matches}: {match['home_team']['home_team_name']} vs {match['away_team']['away_team_name']}")
            
            analysis = self.analyze_match_events(match_id)
            
            match_data = {
                'match_id': match_id,
                'home_team': match['home_team']['home_team_name'],
                'away_team': match['away_team']['away_team_name'],
                'home_score': match['home_score'],
                'away_score': match['away_score'],
                'analysis': analysis
            }
            
            commentary_data.append(match_data)
        
        return commentary_data
    
    def export_training_data(self, commentary_data: List[Dict], filename: str = "soccer_commentary_data.json") -> None:
        """
        Export commentary data for training ML models.
        
        Args:
            commentary_data: List of commentary data dictionaries
            filename: Name of the output file
        """
        with open(filename, 'w') as f:
            json.dump(commentary_data, f, indent=2, default=str)
        
        print(f"✅ Training data exported to {filename}")
        print(f"📊 Total matches: {len(commentary_data)}")
        total_events = sum(len(match['analysis']['match_timeline']) for match in commentary_data)
        print(f"📈 Total events: {total_events}")


def main():
    """
    Main function to demonstrate the StatsBomb Explorer.
    """
    print("🚀 StatsBomb Data Explorer for Soccer Prediction & Commentary")
    print("=" * 70)
    
    # Initialize explorer
    explorer = StatsBombExplorer()
    
    # Step 1: Explore available competitions
    print("\n📋 Step 1: Exploring Available Competitions")
    explorer.explore_competitions()
    
    # Step 2: Focus on Euro 2024 (great for commentary due to recent matches)
    print("\n⚽ Step 2: Loading Euro 2024 Data")
    competition_id = 55  # UEFA Euro
    season_id = 282      # 2024 Germany
    
    matches = explorer.get_matches(competition_id, season_id)
    print(f"📊 Found {len(matches)} matches in Euro 2024")
    
    # Step 3: Analyze a specific match
    print("\n🎯 Step 3: Analyzing Match Events")
    sample_match = matches.iloc[0]
    match_id = sample_match['match_id']
    
    print(f"🏟️  Sample Match: {sample_match['home_team']['home_team_name']} vs {sample_match['away_team']['away_team_name']}")
    print(f"⚽ Score: {sample_match['home_score']} - {sample_match['away_score']}")
    
    analysis = explorer.analyze_match_events(match_id)
    print(f"📈 Total Events: {analysis['total_events']}")
    print(f"🎯 Shots: {analysis['shots']}")
    print(f"⚽ Passes: {analysis['passes']}")
    
    # Step 4: Show timeline for commentary
    print("\n📺 Step 4: Sample Commentary Timeline")
    for moment in analysis['match_timeline'][:5]:  # Show first 5 key moments
        print(f"  {moment['description']}")
    
    # Step 5: Generate training data
    print("\n🤖 Step 5: Generating Training Data")
    commentary_data = explorer.get_commentary_data(competition_id, season_id, num_matches=3)
    explorer.export_training_data(commentary_data)
    
    print("\n✅ Data exploration complete!")
    print("\n🎯 Next Steps for Your Project:")
    print("1. Use the exported JSON data to train your commentary model")
    print("2. Analyze event sequences for move quality prediction")
    print("3. Experiment with different competitions and seasons")
    print("4. Add 360° data for more tactical insights")


if __name__ == "__main__":
    main() 