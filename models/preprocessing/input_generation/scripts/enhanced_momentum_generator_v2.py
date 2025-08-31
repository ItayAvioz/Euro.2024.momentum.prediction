"""
Enhanced Momentum Generator V2 for Euro 2024 Dataset

Creates comprehensive 3-minute momentum windows with detailed analytics
in a clean CSV format with standardized column names.

Author: Euro 2024 Momentum Analysis Team  
Date: February 2024
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys
import os
import json
from collections import Counter, defaultdict

# Add the momentum calculator to path
sys.path.append(os.path.join(os.path.dirname(__file__)))
from momentum_3min_calculator import MomentumCalculator

class EnhancedMomentumGeneratorV2:
    """
    Enhanced momentum generator with clean CSV structure.
    """
    
    def __init__(self, data_path: str = None):
        """Initialize with data path."""
        if data_path is None:
            # Default path to Euro 2024 dataset
            script_dir = Path(__file__).parent
            data_path = script_dir / ".." / ".." / ".." / ".." / "Data" / "euro_2024_complete_dataset.csv"
        
        self.data_path = str(data_path)
        self.calculator = MomentumCalculator()
        self.eliminated_events = {
            'Bad Behaviour', 'Own Goal For', 'Injury Stoppage', 'Half Start', 
            'Half End', 'Referee Ball-Drop', 'Starting XI', 'Offside', 
            'Error', 'Ball Out', 'Camera Off'
        }
        
    def load_data(self):
        """Load the Euro 2024 dataset."""
        print(f"Loading data from: {self.data_path}")
        self.data = pd.read_csv(self.data_path)
        print(f"Loaded {len(self.data)} events from {self.data['match_id'].nunique()} matches")
        return self.data
    
    def extract_team_name(self, team_str):
        """Extract team name from string representation."""
        return self.calculator.get_team_name(team_str)
    
    def get_match_teams(self, match_id):
        """Get home and away team names for a match."""
        match_data = self.data[self.data['match_id'] == match_id]
        
        # Get unique teams from both team and possession_team columns
        teams = set()
        
        for team_str in match_data['team'].dropna().unique():
            team_name = self.extract_team_name(team_str)
            if team_name and team_name != "Unknown":
                teams.add(team_name)
        
        for team_str in match_data['possession_team'].dropna().unique():
            team_name = self.extract_team_name(team_str)
            if team_name and team_name != "Unknown":
                teams.add(team_name)
        
        teams_list = list(teams)
        if len(teams_list) >= 2:
            return teams_list[0], teams_list[1]
        else:
            return "Unknown", "Unknown"
    
    def extract_window_events(self, match_data, start_min, end_min):
        """Extract events for a specific 3-minute window."""
        return match_data[
            (match_data['minute'] >= start_min) & 
            (match_data['minute'] <= end_min)
        ].copy()
    
    def get_event_type_name(self, event_type_str):
        """Extract event type name from string representation."""
        return self.calculator.get_event_type_name(event_type_str)
    
    def analyze_event_statistics(self, window_events):
        """Analyze event statistics for the window."""
        total_events = len(window_events)
        
        # Count ignored events
        ignored_events = 0
        for _, event in window_events.iterrows():
            event_type = self.get_event_type_name(event.get('type', ''))
            if event_type in self.eliminated_events:
                ignored_events += 1
        
        processed_events = total_events - ignored_events
        
        # Count overlapping events (events where both team and possession_team are present and different)
        overlapping_events = 0
        for _, event in window_events.iterrows():
            team_name = self.extract_team_name(event.get('team', ''))
            possession_team = self.extract_team_name(event.get('possession_team', ''))
            if (team_name and possession_team and 
                team_name != "Unknown" and possession_team != "Unknown" and 
                team_name != possession_team):
                overlapping_events += 1
        
        return {
            'total_events': total_events,
            'ignored_events': ignored_events,
            'processed_events': processed_events,
            'overlapping_events': overlapping_events
        }
    
    def analyze_team_involvement(self, window_events, home_team, away_team):
        """Analyze team involvement in events."""
        home_involvement = 0
        away_involvement = 0
        
        for _, event in window_events.iterrows():
            primary_team = self.calculator.get_primary_team(event.to_dict())
            if primary_team == home_team:
                home_involvement += 1
            elif primary_team == away_team:
                away_involvement += 1
        
        return {
            'home_team_involvement': home_involvement,
            'away_team_involvement': away_involvement
        }
    
    def analyze_possession(self, window_events, home_team, away_team):
        """Analyze possession events per team."""
        home_possession = 0
        away_possession = 0
        
        for _, event in window_events.iterrows():
            possession_team = self.extract_team_name(event.get('possession_team', ''))
            if possession_team == home_team:
                home_possession += 1
            elif possession_team == away_team:
                away_possession += 1
        
        return {
            'home_team_possession': home_possession,
            'away_team_possession': away_possession
        }
    
    def get_location_third(self, location_str):
        """Determine which third of the pitch the location is in."""
        if pd.isna(location_str) or location_str == '' or location_str == 'None':
            return 'No Location'
        
        try:
            # Parse location string
            if isinstance(location_str, str):
                location = eval(location_str)
            else:
                return 'No Location'
            
            if len(location) >= 1:
                x_coord = float(location[0])
                if x_coord <= 40:
                    return 'Defensive Third'
                elif x_coord <= 80:
                    return 'Middle Third'
                else:
                    return 'Attacking Third'
            else:
                return 'No Location'
                
        except:
            return 'No Location'
    
    def analyze_position(self, window_events, home_team, away_team):
        """Analyze position distribution per team."""
        home_positions = {'Defensive Third': 0, 'Middle Third': 0, 'Attacking Third': 0, 'No Location': 0}
        away_positions = {'Defensive Third': 0, 'Middle Third': 0, 'Attacking Third': 0, 'No Location': 0}
        
        for _, event in window_events.iterrows():
            primary_team = self.calculator.get_primary_team(event.to_dict())
            location_third = self.get_location_third(event.get('location', ''))
            
            if primary_team == home_team:
                home_positions[location_third] += 1
            elif primary_team == away_team:
                away_positions[location_third] += 1
        
        return {
            'home_defensive_third': home_positions['Defensive Third'],
            'home_middle_third': home_positions['Middle Third'],
            'home_attacking_third': home_positions['Attacking Third'],
            'home_no_location': home_positions['No Location'],
            'away_defensive_third': away_positions['Defensive Third'],
            'away_middle_third': away_positions['Middle Third'],
            'away_attacking_third': away_positions['Attacking Third'],
            'away_no_location': away_positions['No Location']
        }
    
    def analyze_event_types(self, window_events, home_team, away_team):
        """Analyze top 5 event types per team."""
        home_events = Counter()
        away_events = Counter()
        
        for _, event in window_events.iterrows():
            primary_team = self.calculator.get_primary_team(event.to_dict())
            event_type = self.get_event_type_name(event.get('type', ''))
            
            if primary_team == home_team:
                home_events[event_type] += 1
            elif primary_team == away_team:
                away_events[event_type] += 1
        
        # Get top 5 for each team
        home_top5 = dict(home_events.most_common(5))
        away_top5 = dict(away_events.most_common(5))
        
        return {
            'home_top_events': json.dumps(home_top5),
            'away_top_events': json.dumps(away_top5)
        }
    
    def analyze_momentum_events(self, window_events, home_team, away_team):
        """Analyze highest and lowest momentum events per team."""
        home_momentum_events = []
        away_momentum_events = []
        
        # Create game context for momentum calculation
        start_min = window_events['minute'].min() if len(window_events) > 0 else 0
        home_context = {'score_diff': 0, 'minute': start_min}
        away_context = {'score_diff': 0, 'minute': start_min}
        
        for _, event in window_events.iterrows():
            primary_team = self.calculator.get_primary_team(event.to_dict())
            event_dict = event.to_dict()
            
            if primary_team == home_team:
                try:
                    momentum = self.calculator.calculate_momentum_weight(event_dict, home_team, home_context)
                    event_type = self.get_event_type_name(event.get('type', ''))
                    minute = event.get('minute', 0)
                    home_momentum_events.append({
                        'event_type': event_type,
                        'minute': minute,
                        'momentum': momentum
                    })
                except:
                    pass
            elif primary_team == away_team:
                try:
                    momentum = self.calculator.calculate_momentum_weight(event_dict, away_team, away_context)
                    event_type = self.get_event_type_name(event.get('type', ''))
                    minute = event.get('minute', 0)
                    away_momentum_events.append({
                        'event_type': event_type,
                        'minute': minute,
                        'momentum': momentum
                    })
                except:
                    pass
        
        # Sort and get top/bottom 5
        home_momentum_events.sort(key=lambda x: x['momentum'], reverse=True)
        away_momentum_events.sort(key=lambda x: x['momentum'], reverse=True)
        
        home_highest = home_momentum_events[:5] if len(home_momentum_events) >= 5 else home_momentum_events
        home_lowest = home_momentum_events[-5:] if len(home_momentum_events) >= 5 else home_momentum_events
        away_highest = away_momentum_events[:5] if len(away_momentum_events) >= 5 else away_momentum_events
        away_lowest = away_momentum_events[-5:] if len(away_momentum_events) >= 5 else away_momentum_events
        
        return {
            'home_highest_momentum': json.dumps(home_highest),
            'home_lowest_momentum': json.dumps(home_lowest),
            'away_highest_momentum': json.dumps(away_highest),
            'away_lowest_momentum': json.dumps(away_lowest)
        }
    
    def generate_match_windows(self, match_id):
        """Generate enhanced analysis for all 3-minute windows in a match."""
        print(f"Processing match {match_id}...")
        
        match_data = self.data[self.data['match_id'] == match_id]
        home_team, away_team = self.get_match_teams(match_id)
        
        if home_team == "Unknown" or away_team == "Unknown":
            print(f"  Warning: Could not identify teams for match {match_id}")
            return []
        
        # Get match duration
        max_minute = match_data['minute'].max()
        
        # Generate windows: 0-2, 1-3, 2-4, etc.
        results = []
        start_minute = 0
        
        while start_minute + 2 <= max_minute:
            end_minute = start_minute + 2
            
            # Extract window events
            window_events = self.extract_window_events(match_data, start_minute, end_minute)
            
            # Create minute range string
            minute_range = f"{start_minute}-{end_minute}"
            
            if len(window_events) == 0:
                # Empty window - create minimal record
                window_result = {
                    'match_id': match_id,
                    'minute_window': start_minute,
                    'minute_range': minute_range,
                    'team_home': home_team,
                    'team_away': away_team,
                    'team_home_momentum': 0.0,
                    'team_away_momentum': 0.0,
                    'total_events': 0,
                    'ignored_events': 0,
                    'processed_events': 0,
                    'overlapping_events': 0,
                    'home_team_involvement': 0,
                    'away_team_involvement': 0,
                    'home_team_possession': 0,
                    'away_team_possession': 0,
                    'home_defensive_third': 0,
                    'home_middle_third': 0,
                    'home_attacking_third': 0,
                    'home_no_location': 0,
                    'away_defensive_third': 0,
                    'away_middle_third': 0,
                    'away_attacking_third': 0,
                    'away_no_location': 0,
                    'home_top_events': '{}',
                    'away_top_events': '{}',
                    'home_highest_momentum': '[]',
                    'home_lowest_momentum': '[]',
                    'away_highest_momentum': '[]',
                    'away_lowest_momentum': '[]'
                }
            else:
                # Calculate momentum using the proven approach
                home_context = {'score_diff': 0, 'minute': start_minute}
                away_context = {'score_diff': 0, 'minute': start_minute}
                
                # Calculate momentum
                try:
                    home_momentum = self.calculator.calculate_3min_team_momentum(
                        window_events.to_dict('records'), home_team, home_context
                    )
                    away_momentum = self.calculator.calculate_3min_team_momentum(
                        window_events.to_dict('records'), away_team, away_context
                    )
                except Exception as e:
                    print(f"    Error calculating momentum for window {start_minute}-{end_minute}: {str(e)}")
                    home_momentum = 0.0
                    away_momentum = 0.0
                
                # Analyze all aspects
                event_stats = self.analyze_event_statistics(window_events)
                team_involvement = self.analyze_team_involvement(window_events, home_team, away_team)
                possession_analysis = self.analyze_possession(window_events, home_team, away_team)
                position_analysis = self.analyze_position(window_events, home_team, away_team)
                event_types = self.analyze_event_types(window_events, home_team, away_team)
                momentum_events = self.analyze_momentum_events(window_events, home_team, away_team)
                
                # Combine all data
                window_result = {
                    'match_id': match_id,
                    'minute_window': start_minute,
                    'minute_range': minute_range,
                    'team_home': home_team,
                    'team_away': away_team,
                    'team_home_momentum': round(home_momentum, 3),
                    'team_away_momentum': round(away_momentum, 3),
                    **event_stats,
                    **team_involvement,
                    **possession_analysis,
                    **position_analysis,
                    **event_types,
                    **momentum_events
                }
            
            results.append(window_result)
            start_minute += 1  # 1-minute lag
        
        print(f"  Generated {len(results)} enhanced windows")
        return results
    
    def generate_all_matches(self):
        """Generate enhanced momentum windows for all matches."""
        if not hasattr(self, 'data'):
            self.load_data()
        
        all_results = []
        match_list = sorted(self.data['match_id'].unique())
        
        print(f"Processing {len(match_list)} matches...")
        
        for i, match_id in enumerate(match_list, 1):
            try:
                match_results = self.generate_match_windows(match_id)
                all_results.extend(match_results)
                
                if i % 10 == 0:  # Progress update every 10 matches
                    print(f"Completed {i}/{len(match_list)} matches ({len(all_results)} windows total)")
                    
            except Exception as e:
                print(f"Error processing match {match_id}: {str(e)}")
                continue
        
        print(f"Completed processing: {len(all_results)} enhanced windows from {len(match_list)} matches")
        return all_results
    
    def export_to_csv(self, results, output_path=None):
        """Export enhanced results to CSV."""
        if output_path is None:
            script_dir = Path(__file__).parent.parent
            output_path = script_dir / "momentum_windows_enhanced_v2.csv"
        
        # Convert to DataFrame
        df = pd.DataFrame(results)
        
        # Sort by match_id and minute_window
        df = df.sort_values(['match_id', 'minute_window'])
        
        # Save to CSV
        df.to_csv(output_path, index=False)
        
        print(f"Exported {len(df)} enhanced windows to: {output_path}")
        return str(output_path)
    
    def run_complete_generation(self):
        """Run the complete enhanced momentum generation process."""
        print("Euro 2024 Enhanced Momentum Generator V2")
        print("=" * 50)
        
        # Generate all windows
        results = self.generate_all_matches()
        
        # Export to CSV
        output_file = self.export_to_csv(results)
        
        # Print summary
        df = pd.DataFrame(results)
        print(f"\nSummary Statistics:")
        print(f"  Total windows: {len(df):,}")
        print(f"  Total matches: {df['match_id'].nunique()}")
        print(f"  Avg windows per match: {len(df) / df['match_id'].nunique():.1f}")
        print(f"  Avg home momentum: {df['team_home_momentum'].mean():.3f}")
        print(f"  Avg away momentum: {df['team_away_momentum'].mean():.3f}")
        print(f"  Total events processed: {df['total_events'].sum():,}")
        print(f"  Total ignored events: {df['ignored_events'].sum():,}")
        
        return output_file

def main():
    """Main execution function."""
    generator = EnhancedMomentumGeneratorV2()
    output_file = generator.run_complete_generation()
    print(f"\nEnhanced momentum dataset V2 generated: {output_file}")

if __name__ == "__main__":
    main()
