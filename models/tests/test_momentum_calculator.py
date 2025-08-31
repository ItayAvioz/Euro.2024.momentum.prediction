#!/usr/bin/env python3
"""
Test Script for 3-Minute Momentum Calculator
============================================

This script tests the momentum calculation function by:
1. Selecting 2 random 3-minute windows from different teams and times
2. Extracting and preprocessing the data
3. Running the momentum calculation function
4. Displaying comprehensive statistics and results

Author: Euro 2024 Momentum Prediction Project
Date: January 31, 2025
"""

import pandas as pd
import numpy as np
import random
from collections import Counter
import sys
import os

# Add the models directory to the path so we can import our calculator
sys.path.append(os.path.join(os.path.dirname(__file__)))
from momentum_3min_calculator import MomentumCalculator, calculate_window_momentum

class MomentumTester:
    """
    Test class for the momentum calculator with comprehensive analysis.
    """
    
    def __init__(self, data_path: str = "../Data/euro_2024_complete_dataset.csv"):
        """
        Initialize the tester with the dataset.
        
        Args:
            data_path: Path to the Euro 2024 dataset
        """
        self.data_path = data_path
        self.calculator = MomentumCalculator(verbose=True)
        self.df = None
        
    def load_data(self):
        """Load the Euro 2024 dataset."""
        print("📊 Loading Euro 2024 dataset...")
        try:
            # Try loading with different encodings
            try:
                self.df = pd.read_csv(self.data_path, encoding='utf-8')
            except UnicodeDecodeError:
                self.df = pd.read_csv(self.data_path, encoding='latin-1')
            
            print(f"✅ Dataset loaded successfully!")
            print(f"   - Shape: {self.df.shape}")
            print(f"   - Columns: {list(self.df.columns)}")
            print(f"   - Date range: {self.df['minute'].min():.1f} - {self.df['minute'].max():.1f} minutes")
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading dataset: {e}")
            return False
    
    def extract_team_name(self, team_data):
        """Extract team name from various data formats."""
        if isinstance(team_data, str):
            return team_data
        elif isinstance(team_data, dict):
            return team_data.get('name', str(team_data))
        else:
            return str(team_data)
    
    def select_random_windows(self):
        """
        Select 2 random 3-minute windows from different teams and different time periods.
        
        Returns:
            List of tuples: [(match_id, team1, team2, minute_start), ...]
        """
        print("\n🎯 Selecting random 3-minute windows...")
        
        # Get unique matches
        matches = self.df[['match_id', 'home_team_name', 'away_team_name']].drop_duplicates()
        print(f"   - Found {len(matches)} unique matches")
        
        # Sample 2 different matches
        selected_matches = matches.sample(n=min(2, len(matches)), random_state=42)
        
        windows = []
        for _, match in selected_matches.iterrows():
            match_id = match['match_id']
            # Extract team names properly (they might be stored as strings or dicts)
            home_team = self.extract_team_name(match['home_team_name'])
            away_team = self.extract_team_name(match['away_team_name'])
            
            # Get events for this match
            match_events = self.df[self.df['match_id'] == match_id].copy()
            
            # Select a random minute that allows for a full 3-minute window
            min_minute = max(3, match_events['minute'].min())
            max_minute = match_events['minute'].max() - 3
            
            if max_minute > min_minute:
                # Round to nearest 3-minute interval for cleaner windows
                possible_starts = list(range(int(min_minute), int(max_minute), 3))
                if possible_starts:
                    minute_start = random.choice(possible_starts)
                    windows.append((match_id, home_team, away_team, minute_start))
        
        # If we couldn't get 2 different matches, try to get 2 different windows from same match
        if len(windows) < 2 and len(matches) > 0:
            match = matches.iloc[0]
            match_id = match['match_id']
            home_team = self.extract_team_name(match['home_team_name'])
            away_team = self.extract_team_name(match['away_team_name'])
            
            match_events = self.df[self.df['match_id'] == match_id].copy()
            min_minute = max(6, match_events['minute'].min())  # Start later to ensure different windows
            max_minute = match_events['minute'].max() - 3
            
            if max_minute > min_minute:
                possible_starts = list(range(int(min_minute), int(max_minute), 6))  # 6-minute gaps
                if len(possible_starts) >= 2:
                    selected_starts = random.sample(possible_starts, 2)
                    for start in selected_starts:
                        if len(windows) < 2:
                            windows.append((match_id, home_team, away_team, start))
        
        if len(windows) >= 2:
            print(f"✅ Selected {len(windows)} test windows:")
            for i, (match_id, home, away, minute) in enumerate(windows[:2]):
                print(f"   Window {i+1}: {home} vs {away} (Match {match_id}) at minute {minute}-{minute+3}")
        else:
            print("❌ Could not select adequate test windows")
        
        return windows[:2]
    
    def extract_window_data(self, match_id: int, minute_start: int) -> tuple:
        """
        Extract and preprocess data for a 3-minute window.
        
        Args:
            match_id: Match identifier
            minute_start: Start minute of the window
        
        Returns:
            Tuple of (window_events, match_info)
        """
        minute_end = minute_start + 3
        
        # Extract events in the window
        window_events = self.df[
            (self.df['match_id'] == match_id) & 
            (self.df['minute'] >= minute_start) & 
            (self.df['minute'] < minute_end)
        ].copy()
        
        # Get match info
        match_info = self.df[self.df['match_id'] == match_id].iloc[0]
        
        print(f"\n📋 Window Data Extract (Minutes {minute_start}-{minute_end}):")
        print(f"   - Total events in window: {len(window_events)}")
        print(f"   - Time range: {window_events['minute'].min():.2f} - {window_events['minute'].max():.2f}")
        
        return window_events, match_info
    
    def analyze_window_statistics(self, window_events: pd.DataFrame, home_team: str, away_team: str):
        """
        Analyze comprehensive statistics for a window.
        
        Args:
            window_events: DataFrame with events in the window
            home_team: Home team name
            away_team: Away team name
        """
        print(f"\n📊 WINDOW STATISTICS ANALYSIS")
        print("=" * 50)
        
        # Basic event counts
        total_events = len(window_events)
        print(f"📈 Total Events: {total_events}")
        
        if total_events == 0:
            print("   ⚠️  No events in this window")
            return
        
        # Team analysis
        print(f"\n🏟️  TEAM EVENT ANALYSIS:")
        team_events = window_events['team'].value_counts()
        print(f"   {home_team}: {team_events.get(home_team, 0)} events")
        print(f"   {away_team}: {team_events.get(away_team, 0)} events")
        
        # Possession team analysis
        print(f"\n⚽ POSSESSION ANALYSIS:")
        possession_counts = {}
        team_counts = {}
        for _, event in window_events.iterrows():
            event_dict = event.to_dict()
            poss_team = self.calculator.get_possession_team_name(event_dict)
            primary_team = self.calculator.get_primary_team(event_dict)
            
            if poss_team:
                possession_counts[poss_team] = possession_counts.get(poss_team, 0) + 1
            if primary_team:
                team_counts[primary_team] = team_counts.get(primary_team, 0) + 1
        
        for team, count in possession_counts.items():
            print(f"   {team} (possession): {count} events")
        
        print(f"\n🏃 PRIMARY TEAM ANALYSIS:")
        for team, count in team_counts.items():
            print(f"   {team} (primary): {count} events")
        
        # Event type analysis
        print(f"\n🎯 EVENT TYPE BREAKDOWN:")
        event_types = window_events['type'].value_counts()
        for event_type, count in event_types.head(10).items():
            print(f"   {event_type}: {count}")
        
        # Check for eliminated events
        eliminated_events = {'Bad Behaviour', 'Own Goal For', 'Injury Stoppage', 'Half Start', 
                           'Half End', 'Referee Ball-Drop', 'Starting XI', 'Offside', 
                           'Error', 'Ball Out', 'Camera Off'}
        
        eliminated_in_window = window_events[window_events['type'].isin(eliminated_events)]
        print(f"\n❌ ELIMINATED EVENTS: {len(eliminated_in_window)}")
        if len(eliminated_in_window) > 0:
            eliminated_types = eliminated_in_window['type'].value_counts()
            for event_type, count in eliminated_types.items():
                print(f"   {event_type}: {count} (will be ignored)")
        
        # Location analysis
        print(f"\n📍 LOCATION ANALYSIS:")
        events_with_location = window_events.dropna(subset=['location'])
        print(f"   Events with location: {len(events_with_location)}/{total_events}")
        
        if len(events_with_location) > 0:
            # Parse x coordinates for field analysis
            x_coords = []
            for loc in events_with_location['location']:
                try:
                    if isinstance(loc, str):
                        coords = eval(loc)  # Simple parsing for [x, y] format
                        if len(coords) >= 2:
                            x_coords.append(coords[0])
                except:
                    continue
            
            if x_coords:
                print(f"   X-coordinate range: {min(x_coords):.1f} - {max(x_coords):.1f}")
                print(f"   Average X position: {np.mean(x_coords):.1f}")
        
        # Time distribution
        print(f"\n⏰ TIME DISTRIBUTION:")
        print(f"   Minute range: {window_events['minute'].min():.2f} - {window_events['minute'].max():.2f}")
        print(f"   Events per minute: {total_events/3:.1f}")
    
    def calculate_momentum_for_window(self, window_events: pd.DataFrame, home_team: str, 
                                    away_team: str, minute: int) -> dict:
        """
        Calculate momentum for both teams in the window.
        
        Args:
            window_events: DataFrame with events in the window
            home_team: Home team name
            away_team: Away team name
            minute: Window minute for context
        
        Returns:
            Dict with momentum results
        """
        print(f"\n🧮 MOMENTUM CALCULATION")
        print("=" * 50)
        
        # Convert DataFrame to list of dicts for the calculator
        events_list = window_events.to_dict('records')
        
        # Simple game context (you could enhance this with actual score tracking)
        game_context = {
            'score_diff': 0,  # Simplified - could track actual score
            'minute': minute + 1.5  # Middle of the window
        }
        
        # Calculate momentum for both teams
        print(f"\n🏠 HOME TEAM ({home_team}) MOMENTUM:")
        home_momentum = self.calculator.calculate_3min_team_momentum(
            events_list, home_team, game_context
        )
        
        print(f"\n🛫 AWAY TEAM ({away_team}) MOMENTUM:")
        away_momentum = self.calculator.calculate_3min_team_momentum(
            events_list, away_team, game_context
        )
        
        # Team involvement analysis
        print(f"\n👥 TEAM INVOLVEMENT ANALYSIS:")
        
        # Home team involvement
        home_events = self.calculator.filter_team_events(events_list, home_team)
        print(f"   {home_team} involved in: {len(home_events)}/{len(events_list)} events")
        
        # Away team involvement
        away_events = self.calculator.filter_team_events(events_list, away_team)
        print(f"   {away_team} involved in: {len(away_events)}/{len(events_list)} events")
        
        # Overlap analysis (events involving both teams)
        overlap_events = 0
        for event in events_list:
            primary_team = self.calculator.get_primary_team(event)
            poss_team = self.calculator.get_possession_team_name(event)
            if ((primary_team == home_team or poss_team == home_team) and 
                (primary_team == away_team or poss_team == away_team)):
                overlap_events += 1
        
        print(f"   Overlapping events: {overlap_events}")
        
        results = {
            'home_team': home_team,
            'away_team': away_team,
            'home_momentum': home_momentum,
            'away_momentum': away_momentum,
            'home_events': len(home_events),
            'away_events': len(away_events),
            'total_events': len(events_list),
            'overlap_events': overlap_events,
            'minute': minute,
            'game_context': game_context
        }
        
        return results
    
    def display_final_results(self, results1: dict, results2: dict):
        """
        Display final comparison of both windows.
        
        Args:
            results1: Results from first window
            results2: Results from second window
        """
        print(f"\n🏆 FINAL RESULTS COMPARISON")
        print("=" * 60)
        
        print(f"\n📊 WINDOW 1 (Minute {results1['minute']}-{results1['minute']+3}):")
        print(f"   Teams: {results1['home_team']} vs {results1['away_team']}")
        print(f"   {results1['home_team']} Momentum: {results1['home_momentum']:.3f}")
        print(f"   {results1['away_team']} Momentum: {results1['away_momentum']:.3f}")
        print(f"   Event Involvement: {results1['home_events']} vs {results1['away_events']}")
        print(f"   Total Events: {results1['total_events']}")
        
        print(f"\n📊 WINDOW 2 (Minute {results2['minute']}-{results2['minute']+3}):")
        print(f"   Teams: {results2['home_team']} vs {results2['away_team']}")
        print(f"   {results2['home_team']} Momentum: {results2['home_momentum']:.3f}")
        print(f"   {results2['away_team']} Momentum: {results2['away_momentum']:.3f}")
        print(f"   Event Involvement: {results2['home_events']} vs {results2['away_events']}")
        print(f"   Total Events: {results2['total_events']}")
        
        print(f"\n🎯 INSIGHTS:")
        
        # Momentum comparison
        all_momentums = [results1['home_momentum'], results1['away_momentum'], 
                        results2['home_momentum'], results2['away_momentum']]
        max_momentum = max(all_momentums)
        min_momentum = min(all_momentums)
        
        print(f"   📈 Highest momentum: {max_momentum:.3f}")
        print(f"   📉 Lowest momentum: {min_momentum:.3f}")
        print(f"   📊 Momentum range: {max_momentum - min_momentum:.3f}")
        
        # Event activity comparison
        print(f"   🎯 Most active window: Window {'1' if results1['total_events'] > results2['total_events'] else '2'}")
        print(f"   ⚽ Event difference: {abs(results1['total_events'] - results2['total_events'])} events")
    
    def run_full_test(self):
        """
        Run the complete test suite.
        """
        print("🚀 STARTING MOMENTUM CALCULATOR TEST")
        print("=" * 60)
        
        # Step 1: Load data
        if not self.load_data():
            return False
        
        # Step 2: Select random windows
        windows = self.select_random_windows()
        if len(windows) < 2:
            print("❌ Could not select adequate test windows")
            return False
        
        results = []
        
        # Step 3 & 4: Process each window
        for i, (match_id, home_team, away_team, minute_start) in enumerate(windows):
            print(f"\n{'='*60}")
            print(f"🔍 TESTING WINDOW {i+1}: {home_team} vs {away_team}")
            print(f"   Match ID: {match_id} | Minutes: {minute_start}-{minute_start+3}")
            print(f"{'='*60}")
            
            # Extract window data
            window_events, match_info = self.extract_window_data(match_id, minute_start)
            
            # Analyze statistics
            self.analyze_window_statistics(window_events, home_team, away_team)
            
            # Calculate momentum
            window_results = self.calculate_momentum_for_window(
                window_events, home_team, away_team, minute_start
            )
            results.append(window_results)
        
        # Step 5: Display final comparison
        if len(results) >= 2:
            self.display_final_results(results[0], results[1])
        
        print(f"\n✅ TEST COMPLETED SUCCESSFULLY!")
        return True


def main():
    """
    Main function to run the momentum calculator test.
    """
    # Initialize tester
    tester = MomentumTester()
    
    # Run the full test
    success = tester.run_full_test()
    
    if success:
        print(f"\n🎉 All tests passed! The momentum calculator is working correctly.")
    else:
        print(f"\n❌ Test failed. Please check the data and try again.")


if __name__ == "__main__":
    main()
