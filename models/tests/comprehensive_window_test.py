#!/usr/bin/env python3
"""
Comprehensive 3-Minute Window Analysis
====================================

Analyzes specific 3-minute windows across multiple Euro 2024 matches:
- Portugal vs Czech Republic: Windows 40-42, 61-63, 66-68
- Netherlands vs Austria: Windows 58-60, 74-76, 77-79  
- Spain vs France: Windows 8-10, 20-22, 23-25
- England vs Switzerland: Windows 72-74, 78-80, 81-83

For each window, provides comprehensive analysis including momentum calculations,
score tracking, event analysis, position analysis, and top/bottom momentum events.

Author: Euro 2024 Momentum Prediction Project
Date: January 31, 2025
"""

import pandas as pd
import numpy as np
import json
from collections import Counter, defaultdict
import sys
import os

# Import our momentum calculator
sys.path.append(os.path.join(os.path.dirname(__file__)))
from momentum_3min_calculator import MomentumCalculator, calculate_window_momentum

class ComprehensiveWindowAnalyzer:
    """
    Comprehensive analyzer for specific 3-minute windows across multiple matches.
    """
    
    def __init__(self, data_path: str = "../Data/euro_2024_complete_dataset.csv"):
        """Initialize the analyzer with the dataset."""
        self.data_path = data_path
        self.calculator = MomentumCalculator(verbose=False)
        self.df = None
        self.results = []
        
        # Define the specific windows to analyze
        self.target_windows = {
            "Portugal vs Czech Republic": {
                "team1": "Portugal", "team2": "Czech Republic",
                "windows": [(40, 42), (61, 63), (66, 68)]
            },
            "Netherlands vs Austria": {
                "team1": "Netherlands", "team2": "Austria", 
                "windows": [(58, 60), (74, 76), (77, 79)]
            },
            "Spain vs France": {
                "team1": "Spain", "team2": "France",
                "windows": [(8, 10), (20, 22), (23, 25)]
            },
            "England vs Switzerland": {
                "team1": "England", "team2": "Switzerland",
                "windows": [(72, 74), (78, 80), (81, 83)]
            }
        }
        
    def load_data(self):
        """Load the Euro 2024 dataset."""
        print("📊 Loading Euro 2024 dataset...")
        try:
            self.df = pd.read_csv(self.data_path, encoding='utf-8')
            print(f"✅ Dataset loaded: {len(self.df):,} events")
            return True
        except Exception as e:
            print(f"❌ Error loading dataset: {e}")
            return False
    
    def find_match_data(self, team1: str, team2: str):
        """Find match data for specific teams."""
        # Try different combinations to find the match
        match_data = self.df[
            ((self.df['home_team_name'].str.contains(team1, na=False) & 
              self.df['away_team_name'].str.contains(team2, na=False)) |
             (self.df['home_team_name'].str.contains(team2, na=False) & 
              self.df['away_team_name'].str.contains(team1, na=False)))
        ]
        
        if len(match_data) == 0:
            # Try extracting team names from the dict format
            for _, row in self.df.iterrows():
                home_team = self.calculator.get_team_name(row.get('home_team_name', ''))
                away_team = self.calculator.get_team_name(row.get('away_team_name', ''))
                
                if ((home_team == team1 and away_team == team2) or
                    (home_team == team2 and away_team == team1)):
                    match_id = row.get('match_id')
                    match_data = self.df[self.df['match_id'] == match_id]
                    break
                    
        return match_data
    
    def determine_game_phase(self, minute: float) -> str:
        """Determine the game phase based on minute."""
        if 0 <= minute <= 15:
            return "Early First Half (0-15 min)"
        elif 15 < minute <= 30:
            return "Mid First Half (15-30 min)"
        elif 30 < minute <= 45:
            return "Late First Half (30-45 min)"
        elif 45 < minute <= 60:
            return "Early Second Half (45-60 min)"
        elif 60 < minute <= 75:
            return "Mid Second Half (60-75 min)"
        elif 75 < minute <= 90:
            return "Late Second Half (75-90 min)"
        else:
            return "Extra Time (90+ min)"
    
    def calculate_score_at_minute(self, match_data: pd.DataFrame, minute: float, home_team: str, away_team: str):
        """Calculate score at specific minute."""
        # Use the fixed score calculation from momentum calculator
        score_result = self.calculator.calculate_score_at_minute(match_data, minute)
        return score_result['home_score'], score_result['away_score']
    
    def extract_window_events(self, match_data: pd.DataFrame, start_min: float, end_min: float):
        """Extract events for specific window."""
        window_events = match_data[
            (match_data['minute'] >= start_min) & 
            (match_data['minute'] <= end_min)  # Fixed: Changed < to <= to include end_min
        ].copy()
        
        return window_events
    
    def analyze_position_data(self, window_events: pd.DataFrame, team: str):
        """Analyze position data for team events."""
        team_events = []
        for _, event in window_events.iterrows():
            event_dict = event.to_dict()
            primary_team = self.calculator.get_primary_team(event_dict)
            possession_team = self.calculator.get_possession_team_name(event_dict)
            
            if primary_team == team or possession_team == team:
                team_events.append(event_dict)
        
        if not team_events:
            return {"defensive_third": 0, "middle_third": 0, "attacking_third": 0, "no_location": 0}
        
        position_analysis = {"defensive_third": 0, "middle_third": 0, "attacking_third": 0, "no_location": 0}
        
        for event in team_events:
            if self.calculator.has_valid_coordinates(event):
                x_coord = self.calculator.get_x_coordinate(event.get('location'))
                if x_coord < 40:
                    position_analysis["defensive_third"] += 1
                elif x_coord <= 80:
                    position_analysis["middle_third"] += 1
                else:
                    position_analysis["attacking_third"] += 1
            else:
                position_analysis["no_location"] += 1
        
        return position_analysis
    
    def get_team_event_momentums(self, window_events: pd.DataFrame, team: str, game_context: dict):
        """Get individual event momentums for a team."""
        team_events = []
        event_momentums = []
        
        for _, event in window_events.iterrows():
            event_dict = event.to_dict()
            primary_team = self.calculator.get_primary_team(event_dict)
            possession_team = self.calculator.get_possession_team_name(event_dict)
            
            if primary_team == team or possession_team == team:
                momentum = self.calculator.calculate_momentum_weight(event_dict, team, game_context)
                if momentum > 0:  # Only include meaningful events
                    team_events.append({
                        'event': event_dict,
                        'momentum': momentum,
                        'minute': event_dict.get('minute', 0),
                        'type': event_dict.get('type', 'Unknown'),
                        'description': f"{event_dict.get('type', 'Unknown')} at {event_dict.get('minute', 0):.1f}min"
                    })
                    event_momentums.append(momentum)
        
        return team_events, event_momentums
    
    def analyze_window(self, match_name: str, team1: str, team2: str, start_min: float, end_min: float):
        """Comprehensive analysis of a single 3-minute window."""
        print(f"\n🎯 ANALYZING: {match_name} - Minutes {start_min}-{end_min}")
        print("=" * 80)
        
        # Find match data
        match_data = self.find_match_data(team1, team2)
        if len(match_data) == 0:
            print(f"❌ No match data found for {team1} vs {team2}")
            return None
        
        # Determine actual team order from data
        sample_row = match_data.iloc[0]
        home_team = self.calculator.get_team_name(sample_row.get('home_team_name', ''))
        away_team = self.calculator.get_team_name(sample_row.get('away_team_name', ''))
        match_id = sample_row.get('match_id', 'Unknown')
        
        # Extract window events
        window_events = self.extract_window_events(match_data, start_min, end_min)
        
        # Determine game phase
        phase = self.determine_game_phase(start_min)
        
        # Calculate scores
        score_start_home, score_start_away = self.calculate_score_at_minute(match_data, start_min, home_team, away_team)
        score_end_home, score_end_away = self.calculate_score_at_minute(match_data, end_min, home_team, away_team)
        
        # Calculate momentum for both teams
        home_context = {'score_diff': score_start_home - score_start_away, 'minute': start_min}
        away_context = {'score_diff': score_start_away - score_start_home, 'minute': start_min}
        
        home_momentum = self.calculator.calculate_3min_team_momentum(
            window_events.to_dict('records'), home_team, home_context
        )
        away_momentum = self.calculator.calculate_3min_team_momentum(
            window_events.to_dict('records'), away_team, away_context
        )
        
        # Event analysis
        total_events = len(window_events)
        eliminated_events = {'Bad Behaviour', 'Own Goal For', 'Injury Stoppage', 'Half Start', 
                           'Half End', 'Referee Ball-Drop', 'Starting XI', 'Offside', 
                           'Error', 'Ball Out', 'Camera Off'}
        
        # Correctly count eliminated events by parsing event type names
        ignored_events = 0
        for _, event in window_events.iterrows():
            event_dict = event.to_dict()
            event_type_clean = self.calculator.get_event_type_name(event_dict.get('type', ''))
            if event_type_clean in eliminated_events:
                ignored_events += 1
        
        processed_events = total_events - ignored_events
        
        # Team involvement analysis
        home_involvement = 0
        away_involvement = 0
        possession_home = 0
        possession_away = 0
        overlapping_events = 0
        
        for _, event in window_events.iterrows():
            event_dict = event.to_dict()
            primary_team = self.calculator.get_primary_team(event_dict)
            possession_team = self.calculator.get_possession_team_name(event_dict)
            
            is_home_primary = primary_team == home_team
            is_away_primary = primary_team == away_team
            is_home_possession = possession_team == home_team
            is_away_possession = possession_team == away_team
            
            if is_home_primary or is_home_possession:
                home_involvement += 1
            if is_away_primary or is_away_possession:
                away_involvement += 1
            if is_home_possession:
                possession_home += 1
            if is_away_possession:
                possession_away += 1
            if (is_home_primary or is_home_possession) and (is_away_primary or is_away_possession):
                overlapping_events += 1
        
        # Event type analysis
        home_event_types = Counter()
        away_event_types = Counter()
        
        for _, event in window_events.iterrows():
            event_dict = event.to_dict()
            primary_team = self.calculator.get_primary_team(event_dict)
            possession_team = self.calculator.get_possession_team_name(event_dict)
            event_type = event_dict.get('type', 'Unknown')
            
            if primary_team == home_team or possession_team == home_team:
                home_event_types[event_type] += 1
            if primary_team == away_team or possession_team == away_team:
                away_event_types[event_type] += 1
        
        # Position analysis
        home_positions = self.analyze_position_data(window_events, home_team)
        away_positions = self.analyze_position_data(window_events, away_team)
        
        # Get individual event momentums
        home_events, home_event_momentums = self.get_team_event_momentums(window_events, home_team, home_context)
        away_events, away_event_momentums = self.get_team_event_momentums(window_events, away_team, away_context)
        
        # Top 5 highest and lowest momentum events
        home_events_sorted = sorted(home_events, key=lambda x: x['momentum'], reverse=True)
        away_events_sorted = sorted(away_events, key=lambda x: x['momentum'], reverse=True)
        
        # Compile results
        result = {
            'match': match_name,
            'match_id': match_id,
            'home_team': home_team,
            'away_team': away_team,
            'window': f"{start_min}-{end_min}",
            'phase': phase,
            'score_start': f"{score_start_home}-{score_start_away}",
            'score_end': f"{score_end_home}-{score_end_away}",
            'home_momentum': home_momentum,
            'away_momentum': away_momentum,
            'total_events': total_events,
            'ignored_events': ignored_events,
            'processed_events': processed_events,
            'home_involvement': home_involvement,
            'away_involvement': away_involvement,
            'overlapping_events': overlapping_events,
            'possession_home': possession_home,
            'possession_away': possession_away,
            'home_event_types': dict(home_event_types),
            'away_event_types': dict(away_event_types),
            'home_positions': home_positions,
            'away_positions': away_positions,
            'home_top5_high': home_events_sorted[:5],
            'home_top5_low': home_events_sorted[-5:] if len(home_events_sorted) >= 5 else home_events_sorted,
            'away_top5_high': away_events_sorted[:5],
            'away_top5_low': away_events_sorted[-5:] if len(away_events_sorted) >= 5 else away_events_sorted
        }
        
        return result
    
    def display_window_results(self, result):
        """Display comprehensive results for a window."""
        if not result:
            return
        
        print(f"\n📋 MATCH: {result['match']}")
        print(f"🆔 MATCH ID: {result['match_id']}")
        print(f"⏰ WINDOW: Minutes {result['window']}")
        print(f"🎮 PHASE: {result['phase']}")
        print(f"🏠 HOME: {result['home_team']} | 🛫 AWAY: {result['away_team']}")
        
        print(f"\n📊 SCORES:")
        print(f"   Start of window: {result['score_start']}")
        print(f"   End of window: {result['score_end']}")
        
        print(f"\n🎯 MOMENTUM:")
        print(f"   {result['home_team']}: {result['home_momentum']:.3f}")
        print(f"   {result['away_team']}: {result['away_momentum']:.3f}")
        print(f"   Advantage: {result['home_team'] if result['home_momentum'] > result['away_momentum'] else result['away_team']} (+{abs(result['home_momentum'] - result['away_momentum']):.3f})")
        
        print(f"\n📈 EVENT STATISTICS:")
        print(f"   Total events: {result['total_events']}")
        print(f"   Ignored events: {result['ignored_events']}")
        print(f"   Processed events: {result['processed_events']}")
        print(f"   Overlapping events: {result['overlapping_events']}")
        
        print(f"\n🏃 TEAM INVOLVEMENT:")
        print(f"   {result['home_team']}: {result['home_involvement']} events")
        print(f"   {result['away_team']}: {result['away_involvement']} events")
        
        print(f"\n⚽ POSSESSION ANALYSIS:")
        print(f"   {result['home_team']}: {result['possession_home']} events")
        print(f"   {result['away_team']}: {result['possession_away']} events")
        
        print(f"\n🎯 EVENT TYPES - {result['home_team']}:")
        for event_type, count in sorted(result['home_event_types'].items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"   {event_type}: {count}")
        
        print(f"\n🎯 EVENT TYPES - {result['away_team']}:")
        for event_type, count in sorted(result['away_event_types'].items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"   {event_type}: {count}")
        
        print(f"\n📍 POSITION ANALYSIS - {result['home_team']}:")
        print(f"   Defensive third: {result['home_positions']['defensive_third']}")
        print(f"   Middle third: {result['home_positions']['middle_third']}")
        print(f"   Attacking third: {result['home_positions']['attacking_third']}")
        print(f"   No location: {result['home_positions']['no_location']}")
        
        print(f"\n📍 POSITION ANALYSIS - {result['away_team']}:")
        print(f"   Defensive third: {result['away_positions']['defensive_third']}")
        print(f"   Middle third: {result['away_positions']['middle_third']}")
        print(f"   Attacking third: {result['away_positions']['attacking_third']}")
        print(f"   No location: {result['away_positions']['no_location']}")
        
        print(f"\n🏆 TOP 5 HIGHEST MOMENTUM - {result['home_team']}:")
        for i, event in enumerate(result['home_top5_high'], 1):
            print(f"   {i}. {event['type']} (min {event['minute']:.1f}): {event['momentum']:.3f}")
        
        print(f"\n🏆 TOP 5 HIGHEST MOMENTUM - {result['away_team']}:")
        for i, event in enumerate(result['away_top5_high'], 1):
            print(f"   {i}. {event['type']} (min {event['minute']:.1f}): {event['momentum']:.3f}")
        
        print(f"\n⬇️  TOP 5 LOWEST MOMENTUM - {result['home_team']}:")
        for i, event in enumerate(result['home_top5_low'], 1):
            print(f"   {i}. {event['type']} (min {event['minute']:.1f}): {event['momentum']:.3f}")
        
        print(f"\n⬇️  TOP 5 LOWEST MOMENTUM - {result['away_team']}:")
        for i, event in enumerate(result['away_top5_low'], 1):
            print(f"   {i}. {event['type']} (min {event['minute']:.1f}): {event['momentum']:.3f}")
    
    def run_comprehensive_analysis(self):
        """Run the complete comprehensive analysis."""
        print("🎯 COMPREHENSIVE 3-MINUTE WINDOW ANALYSIS")
        print("=" * 80)
        print("Analyzing 12 specific windows across 4 Euro 2024 matches")
        
        if not self.load_data():
            return False
        
        all_results = []
        
        # Process each match and its windows
        for match_name, match_info in self.target_windows.items():
            print(f"\n🏟️  PROCESSING MATCH: {match_name}")
            team1 = match_info["team1"]
            team2 = match_info["team2"]
            
            for start_min, end_min in match_info["windows"]:
                result = self.analyze_window(match_name, team1, team2, start_min, end_min)
                if result:
                    self.display_window_results(result)
                    all_results.append(result)
                    print("\n" + "-" * 80)
        
        # Generate summary
        self.generate_comprehensive_summary(all_results)
        
        return True
    
    def generate_comprehensive_summary(self, results):
        """Generate and save comprehensive summary to test.md."""
        print(f"\n📋 GENERATING COMPREHENSIVE SUMMARY")
        print("=" * 80)
        
        summary_content = f"""# Comprehensive 3-Minute Window Analysis - Test Results

## Overview
Analysis of {len(results)} specific 3-minute windows across 4 Euro 2024 matches using the momentum calculation system.

**Test Date:** January 31, 2025  
**Calculator Version:** 3-Minute Momentum Calculator v1.0  
**Dataset:** Euro 2024 Complete Dataset

---

"""
        
        # Add detailed results for each window
        for i, result in enumerate(results, 1):
            summary_content += f"""## Window {i}: {result['match']} (Minutes {result['window']})

### Basic Information
- **Match:** {result['match']}
- **Match ID:** {result['match_id']}
- **Teams:** {result['home_team']} (Home) vs {result['away_team']} (Away)
- **Phase:** {result['phase']}
- **Score Start:** {result['score_start']}
- **Score End:** {result['score_end']}

### Momentum Results
- **{result['home_team']} Momentum:** {result['home_momentum']:.3f}
- **{result['away_team']} Momentum:** {result['away_momentum']:.3f}
- **Advantage:** {result['home_team'] if result['home_momentum'] > result['away_momentum'] else result['away_team']} (+{abs(result['home_momentum'] - result['away_momentum']):.3f})

### Event Statistics
- **Total Events:** {result['total_events']}
- **Ignored Events:** {result['ignored_events']}
- **Processed Events:** {result['processed_events']}
- **Overlapping Events:** {result['overlapping_events']}

### Team Involvement
- **{result['home_team']}:** {result['home_involvement']} events involved
- **{result['away_team']}:** {result['away_involvement']} events involved

### Possession Analysis
- **{result['home_team']}:** {result['possession_home']} possession events
- **{result['away_team']}:** {result['possession_away']} possession events

### Position Analysis
**{result['home_team']}:**
- Defensive Third: {result['home_positions']['defensive_third']}
- Middle Third: {result['home_positions']['middle_third']}  
- Attacking Third: {result['home_positions']['attacking_third']}
- No Location: {result['home_positions']['no_location']}

**{result['away_team']}:**
- Defensive Third: {result['away_positions']['defensive_third']}
- Middle Third: {result['away_positions']['middle_third']}
- Attacking Third: {result['away_positions']['attacking_third']}
- No Location: {result['away_positions']['no_location']}

### Top Event Types
**{result['home_team']}:**
"""
            
            # Add top event types for home team
            for event_type, count in sorted(result['home_event_types'].items(), key=lambda x: x[1], reverse=True)[:5]:
                summary_content += f"- {event_type}: {count}\n"
            
            summary_content += f"""
**{result['away_team']}:**
"""
            
            # Add top event types for away team
            for event_type, count in sorted(result['away_event_types'].items(), key=lambda x: x[1], reverse=True)[:5]:
                summary_content += f"- {event_type}: {count}\n"
            
            summary_content += f"""
### Highest Momentum Events
**{result['home_team']}:**
"""
            for j, event in enumerate(result['home_top5_high'], 1):
                summary_content += f"{j}. {event['type']} (min {event['minute']:.1f}): {event['momentum']:.3f}\n"
            
            summary_content += f"""
**{result['away_team']}:**
"""
            for j, event in enumerate(result['away_top5_high'], 1):
                summary_content += f"{j}. {event['type']} (min {event['minute']:.1f}): {event['momentum']:.3f}\n"
            
            summary_content += f"""
### Lowest Momentum Events
**{result['home_team']}:**
"""
            for j, event in enumerate(result['home_top5_low'], 1):
                summary_content += f"{j}. {event['type']} (min {event['minute']:.1f}): {event['momentum']:.3f}\n"
            
            summary_content += f"""
**{result['away_team']}:**
"""
            for j, event in enumerate(result['away_top5_low'], 1):
                summary_content += f"{j}. {event['type']} (min {event['minute']:.1f}): {event['momentum']:.3f}\n"
            
            summary_content += "\n---\n\n"
        
        # Add overall summary statistics
        total_momentum_home = sum(r['home_momentum'] for r in results)
        total_momentum_away = sum(r['away_momentum'] for r in results)
        avg_momentum_home = total_momentum_home / len(results)
        avg_momentum_away = total_momentum_away / len(results)
        
        summary_content += f"""## Overall Analysis Summary

### Global Statistics
- **Total Windows Analyzed:** {len(results)}
- **Average Home Team Momentum:** {avg_momentum_home:.3f}
- **Average Away Team Momentum:** {avg_momentum_away:.3f}
- **Total Events Processed:** {sum(r['processed_events'] for r in results):,}
- **Total Events Ignored:** {sum(r['ignored_events'] for r in results):,}

### Key Insights
- **Highest Single Momentum:** {max(max(r['home_momentum'], r['away_momentum']) for r in results):.3f}
- **Lowest Single Momentum:** {min(min(r['home_momentum'], r['away_momentum']) for r in results):.3f}
- **Most Active Window:** {max(results, key=lambda x: x['processed_events'])['match']} - {max(results, key=lambda x: x['processed_events'])['window']} ({max(r['processed_events'] for r in results)} events)
- **Least Active Window:** {min(results, key=lambda x: x['processed_events'])['match']} - {min(results, key=lambda x: x['processed_events'])['window']} ({min(r['processed_events'] for r in results)} events)

---

*Test completed successfully using the 3-Minute Momentum Calculator*  
*All score coefficients calculated at window start as per updated methodology*
"""
        
        # Save the comprehensive summary
        with open('test.md', 'w', encoding='utf-8') as f:
            f.write(summary_content)
        
        print(f"✅ Comprehensive summary saved to 'test.md'")
        print(f"📊 Analyzed {len(results)} windows with complete details")

def main():
    """Run the comprehensive window analysis."""
    analyzer = ComprehensiveWindowAnalyzer()
    success = analyzer.run_comprehensive_analysis()
    
    if success:
        print(f"\n🎉 COMPREHENSIVE ANALYSIS COMPLETED SUCCESSFULLY!")
        print(f"📋 Check 'test.md' for complete detailed results")
    else:
        print(f"\n❌ Analysis failed. Please check the data and try again.")

if __name__ == "__main__":
    main()
