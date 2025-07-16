#!/usr/bin/env python3
"""
Practical Tournament Momentum Prediction Guide
How to combine historical tournament data with current match events
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class PracticalTournamentMomentum:
    """
    Practical implementation of tournament momentum prediction
    """
    
    def __init__(self):
        self.events_df = None
        self.team_profiles = {}
        self.match_predictions = {}
        
    def load_data(self):
        """Load tournament data"""
        print("📊 Loading Euro 2024 Tournament Data...")
        try:
            self.events_df = pd.read_csv("../Data/events_complete.csv", low_memory=False)
            print(f"✅ Events loaded: {len(self.events_df):,}")
            
            # Extract event names
            self.events_df['event_name'] = self.events_df['type'].apply(self.extract_event_type)
            
            # Create match identifiers
            if 'match_id' not in self.events_df.columns:
                self.events_df['match_id'] = pd.factorize(
                    self.events_df['home_team'].astype(str) + '_vs_' + 
                    self.events_df['away_team'].astype(str)
                )[0]
            
            return True
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def extract_event_type(self, type_str):
        """Extract event name from type dictionary string"""
        if pd.isna(type_str) or type_str == '':
            return ''
        
        try:
            if "'name':" in str(type_str):
                start = str(type_str).find("'name': '") + 9
                end = str(type_str).find("'", start)
                return str(type_str)[start:end]
            else:
                return str(type_str)
        except:
            return str(type_str)
    
    def build_team_profiles(self):
        """Build comprehensive team profiles from tournament history"""
        print(f"\n🏆 BUILDING TEAM PROFILES FROM TOURNAMENT HISTORY")
        print("=" * 60)
        
        # Get all teams
        teams = set()
        if 'team_name' in self.events_df.columns:
            teams.update(self.events_df['team_name'].dropna().unique())
        if 'home_team' in self.events_df.columns:
            teams.update(self.events_df['home_team'].dropna().unique())
        if 'away_team' in self.events_df.columns:
            teams.update(self.events_df['away_team'].dropna().unique())
        
        teams = [team for team in teams if pd.notna(team) and team != '']
        print(f"📋 Building profiles for {len(teams)} teams")
        
        for team in teams:
            profile = self.create_team_profile(team)
            if profile:
                self.team_profiles[team] = profile
                print(f"   ✅ {team:<20}: {profile['matches_played']} matches, {profile['avg_goals_per_match']:.1f} goals/match")
        
        print(f"\n🎯 TEAM PROFILE SUMMARY:")
        print(f"   Total teams profiled: {len(self.team_profiles)}")
        
        # Show top performing teams
        sorted_teams = sorted(self.team_profiles.items(), 
                            key=lambda x: x[1]['avg_goals_per_match'], 
                            reverse=True)
        
        print(f"\n🔥 TOP GOAL-SCORING TEAMS:")
        for i, (team, profile) in enumerate(sorted_teams[:8]):
            print(f"   {i+1}. {team:<15}: {profile['avg_goals_per_match']:.1f} goals/match")
        
        return self.team_profiles
    
    def create_team_profile(self, team):
        """Create comprehensive team profile"""
        
        # Get team events
        team_events = self.events_df[self.events_df['team_name'] == team]
        
        if len(team_events) == 0:
            return None
        
        # Get unique matches
        matches = team_events['match_id'].unique()
        
        # Calculate comprehensive stats
        profile = {
            'team_name': team,
            'matches_played': len(matches),
            'total_events': len(team_events),
            'total_goals': len(team_events[team_events['event_name'].str.contains('Goal', na=False, case=False)]),
            'total_shots': len(team_events[team_events['event_name'].str.contains('Shot', na=False, case=False)]),
            'total_fouls': len(team_events[team_events['foul_committed'].notna()]),
            'total_cards': len(team_events[team_events['bad_behaviour'].notna()]),
            'total_subs': len(team_events[team_events['substitution'].notna()]),
            'total_pressure': len(team_events[team_events['under_pressure'].notna()]),
            'total_counterpress': len(team_events[team_events['counterpress'].notna()]),
            
            # Per match averages
            'avg_events_per_match': len(team_events) / len(matches),
            'avg_goals_per_match': len(team_events[team_events['event_name'].str.contains('Goal', na=False, case=False)]) / len(matches),
            'avg_shots_per_match': len(team_events[team_events['event_name'].str.contains('Shot', na=False, case=False)]) / len(matches),
            'avg_fouls_per_match': len(team_events[team_events['foul_committed'].notna()]) / len(matches),
            'avg_cards_per_match': len(team_events[team_events['bad_behaviour'].notna()]) / len(matches),
            'avg_subs_per_match': len(team_events[team_events['substitution'].notna()]) / len(matches),
            
            # Performance metrics
            'shot_efficiency': len(team_events[team_events['event_name'].str.contains('Goal', na=False, case=False)]) / max(len(team_events[team_events['event_name'].str.contains('Shot', na=False, case=False)]), 1),
            'pressure_handling': len(team_events[team_events['under_pressure'].notna()]) / len(team_events),
            'aggression_level': len(team_events[team_events['foul_committed'].notna()]) / len(team_events),
            'discipline_level': 1.0 - (len(team_events[team_events['bad_behaviour'].notna()]) / len(team_events)),
            
            # Match phases performance
            'opening_goals': len(team_events[(team_events['event_name'].str.contains('Goal', na=False, case=False)) & (team_events['minute'] <= 15)]),
            'late_goals': len(team_events[(team_events['event_name'].str.contains('Goal', na=False, case=False)) & (team_events['minute'] >= 75)]),
            'stoppage_goals': len(team_events[(team_events['event_name'].str.contains('Goal', na=False, case=False)) & (team_events['minute'] >= 90)]),
            
            # Tactical patterns
            'early_subs': len(team_events[(team_events['substitution'].notna()) & (team_events['minute'] <= 60)]),
            'late_subs': len(team_events[(team_events['substitution'].notna()) & (team_events['minute'] > 60)]),
            'tactical_changes': len(team_events[team_events['tactics'].notna()]),
            
            # Momentum indicators
            'comeback_ability': 0,  # Will calculate based on match analysis
            'closing_strength': len(team_events[(team_events['minute'] >= 75)]) / len(team_events),
            'opening_intensity': len(team_events[(team_events['minute'] <= 15)]) / len(team_events)
        }
        
        return profile
    
    def predict_real_time_momentum(self, team1, team2, current_minute, current_match_events):
        """
        MAIN FUNCTION: Predict real-time momentum using tournament history + current match
        """
        print(f"\n🎯 REAL-TIME MOMENTUM PREDICTION")
        print("=" * 50)
        print(f"   Match: {team1} vs {team2}")
        print(f"   Current minute: {current_minute}")
        print(f"   Current match events: {len(current_match_events)}")
        
        # === STEP 1: GET HISTORICAL PROFILES ===
        team1_profile = self.team_profiles.get(team1, {})
        team2_profile = self.team_profiles.get(team2, {})
        
        print(f"\n📋 HISTORICAL PROFILES:")
        print(f"   {team1:<15}: {team1_profile.get('avg_goals_per_match', 0):.1f} goals/match, {team1_profile.get('matches_played', 0)} matches")
        print(f"   {team2:<15}: {team2_profile.get('avg_goals_per_match', 0):.1f} goals/match, {team2_profile.get('matches_played', 0)} matches")
        
        # === STEP 2: ANALYZE CURRENT MATCH EVENTS ===
        team1_current = current_match_events[current_match_events['team_name'] == team1]
        team2_current = current_match_events[current_match_events['team_name'] == team2]
        
        # Current match events up to current minute
        team1_current = team1_current[team1_current['minute'] <= current_minute]
        team2_current = team2_current[team2_current['minute'] <= current_minute]
        
        # Recent events (last 10 minutes)
        team1_recent = team1_current[team1_current['minute'] >= current_minute - 10]
        team2_recent = team2_current[team2_current['minute'] >= current_minute - 10]
        
        print(f"\n⚡ CURRENT MATCH STATUS:")
        print(f"   {team1} events: {len(team1_current)} total, {len(team1_recent)} recent")
        print(f"   {team2} events: {len(team2_current)} total, {len(team2_recent)} recent")
        
        # === STEP 3: CALCULATE MOMENTUM COMPONENTS ===
        momentum1 = self.calculate_comprehensive_momentum(team1, team1_profile, team1_current, team1_recent, current_minute)
        momentum2 = self.calculate_comprehensive_momentum(team2, team2_profile, team2_current, team2_recent, current_minute)
        
        # === STEP 4: GENERATE PREDICTION ===
        prediction = {
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'minute': current_minute,
            'team1': team1,
            'team2': team2,
            'team1_momentum': momentum1,
            'team2_momentum': momentum2,
            'momentum_advantage': momentum1 - momentum2,
            'predicted_next_goal': team1 if momentum1 > momentum2 else team2,
            'confidence': abs(momentum1 - momentum2) / 10.0,
            'match_phase': self.get_match_phase(current_minute)
        }
        
        print(f"\n🚀 MOMENTUM PREDICTION:")
        print(f"   {team1:<15}: {momentum1:.1f}/10")
        print(f"   {team2:<15}: {momentum2:.1f}/10")
        print(f"   Advantage: {prediction['momentum_advantage']:+.1f} ({prediction['predicted_next_goal']})")
        print(f"   Confidence: {prediction['confidence']:.1f}/1.0")
        
        return prediction
    
    def calculate_comprehensive_momentum(self, team, team_profile, current_events, recent_events, current_minute):
        """Calculate comprehensive momentum using all data sources"""
        
        # === HISTORICAL BASELINE ===
        historical_momentum = (
            team_profile.get('avg_goals_per_match', 0) * 1.0 +
            team_profile.get('avg_shots_per_match', 0) * 0.2 +
            team_profile.get('shot_efficiency', 0) * 2.0 +
            team_profile.get('closing_strength', 0) * 1.5 +
            team_profile.get('opening_intensity', 0) * 1.0
        )
        
        # === CURRENT MATCH PERFORMANCE ===
        current_goals = len(current_events[current_events['event_name'].str.contains('Goal', na=False, case=False)])
        current_shots = len(current_events[current_events['event_name'].str.contains('Shot', na=False, case=False)])
        current_activity = len(current_events) / (current_minute + 1)
        
        current_momentum = (
            current_goals * 2.0 +
            current_shots * 0.5 +
            current_activity * 0.3
        )
        
        # === RECENT ACTIVITY (LAST 10 MINUTES) ===
        recent_goals = len(recent_events[recent_events['event_name'].str.contains('Goal', na=False, case=False)])
        recent_shots = len(recent_events[recent_events['event_name'].str.contains('Shot', na=False, case=False)])
        recent_subs = len(recent_events[recent_events['substitution'].notna()])
        recent_cards = len(recent_events[recent_events['bad_behaviour'].notna()])
        recent_pressure = len(recent_events[recent_events['under_pressure'].notna()])
        
        recent_momentum = (
            recent_goals * 3.0 +
            recent_shots * 1.0 +
            recent_subs * 0.5 +
            recent_pressure * 0.1 -
            recent_cards * 0.5
        )
        
        # === MATCH PHASE MULTIPLIER ===
        phase_multiplier = self.get_phase_multiplier(current_minute)
        
        # === PRESSURE CONTEXT ===
        pressure_multiplier = 1.0
        if current_minute >= 75:
            pressure_multiplier = 1.2  # Late game intensity
        if current_minute >= 90:
            pressure_multiplier = 1.5  # Stoppage time drama
        
        # === COMBINE ALL COMPONENTS ===
        total_momentum = (
            historical_momentum * 0.3 +
            current_momentum * 0.4 +
            recent_momentum * 0.3
        ) * phase_multiplier * pressure_multiplier
        
        return max(0, min(10, total_momentum))
    
    def get_match_phase(self, minute):
        """Get match phase for context"""
        if minute <= 15:
            return "Opening"
        elif minute <= 45:
            return "First Half"
        elif minute <= 60:
            return "Early Second"
        elif minute <= 75:
            return "Mid Second"
        elif minute <= 90:
            return "Late Game"
        elif minute <= 105:
            return "Stoppage"
        else:
            return "Extra Time"
    
    def get_phase_multiplier(self, minute):
        """Get phase multiplier for momentum calculation"""
        if minute <= 15:
            return 1.2  # Opening intensity
        elif minute <= 45:
            return 1.0  # Normal first half
        elif minute <= 60:
            return 1.1  # Second half start
        elif minute <= 75:
            return 1.0  # Mid second half
        elif minute <= 90:
            return 1.3  # Late game
        elif minute <= 105:
            return 1.6  # Stoppage time
        else:
            return 1.9  # Extra time
    
    def simulate_match_progression(self, team1, team2, match_events):
        """Simulate momentum progression throughout a match"""
        print(f"\n📈 MATCH MOMENTUM PROGRESSION SIMULATION")
        print("=" * 50)
        print(f"   Match: {team1} vs {team2}")
        
        # Simulate predictions every 10 minutes
        progression = []
        for minute in range(10, 101, 10):
            current_events = match_events[match_events['minute'] <= minute]
            
            if len(current_events) == 0:
                continue
            
            prediction = self.predict_real_time_momentum(team1, team2, minute, current_events)
            progression.append(prediction)
        
        # Show progression
        print(f"\n📊 MOMENTUM PROGRESSION:")
        print(f"   {'Minute':<8} {'Team1':<8} {'Team2':<8} {'Advantage':<10} {'Phase':<12} {'Confidence':<10}")
        print(f"   {'-'*60}")
        
        for pred in progression:
            print(f"   {pred['minute']:<8} {pred['team1_momentum']:<8.1f} {pred['team2_momentum']:<8.1f} {pred['momentum_advantage']:<+10.1f} {pred['match_phase']:<12} {pred['confidence']:<10.1f}")
        
        return progression
    
    def demonstrate_practical_usage(self):
        """Demonstrate practical usage of the system"""
        print(f"\n🎯 PRACTICAL USAGE DEMONSTRATION")
        print("=" * 50)
        
        # Build team profiles
        self.build_team_profiles()
        
        # Get sample match
        sample_match = self.events_df['match_id'].iloc[0]
        match_events = self.events_df[self.events_df['match_id'] == sample_match]
        
        # Get teams
        teams = match_events['team_name'].dropna().unique()
        if len(teams) >= 2:
            team1, team2 = teams[0], teams[1]
            
            print(f"\n📋 DEMONSTRATION MATCH: {team1} vs {team2}")
            
            # Simulate real-time predictions
            print(f"\n🔴 REAL-TIME PREDICTION EXAMPLES:")
            
            # Example 1: Early match (minute 20)
            print(f"\n   📍 MINUTE 20 (Early Match):")
            early_events = match_events[match_events['minute'] <= 20]
            pred1 = self.predict_real_time_momentum(team1, team2, 20, early_events)
            
            # Example 2: Mid match (minute 60)
            print(f"\n   📍 MINUTE 60 (Mid Match):")
            mid_events = match_events[match_events['minute'] <= 60]
            pred2 = self.predict_real_time_momentum(team1, team2, 60, mid_events)
            
            # Example 3: Late match (minute 85)
            print(f"\n   📍 MINUTE 85 (Late Match):")
            late_events = match_events[match_events['minute'] <= 85]
            pred3 = self.predict_real_time_momentum(team1, team2, 85, late_events)
            
            # Show how predictions change
            print(f"\n📈 MOMENTUM EVOLUTION:")
            print(f"   Minute 20: {pred1['team1_momentum']:.1f} vs {pred1['team2_momentum']:.1f}")
            print(f"   Minute 60: {pred2['team1_momentum']:.1f} vs {pred2['team2_momentum']:.1f}")
            print(f"   Minute 85: {pred3['team1_momentum']:.1f} vs {pred3['team2_momentum']:.1f}")
            
            # Full match simulation
            self.simulate_match_progression(team1, team2, match_events)
        
        print(f"\n💡 PRACTICAL IMPLEMENTATION TIPS:")
        print(f"   1. Build team profiles from all previous tournament matches")
        print(f"   2. Update predictions every 2-3 minutes during live matches")
        print(f"   3. Use historical data as baseline, current events for adjustments")
        print(f"   4. Pay attention to match phase multipliers (late game = higher volatility)")
        print(f"   5. Combine with tactical analysis for best results")

def main():
    """Main demonstration function"""
    print("⚽ PRACTICAL TOURNAMENT MOMENTUM PREDICTION GUIDE")
    print("=" * 80)
    
    predictor = PracticalTournamentMomentum()
    
    # Load data
    if not predictor.load_data():
        return
    
    # Demonstrate practical usage
    predictor.demonstrate_practical_usage()
    
    print(f"\n🎯 KEY ADVANTAGES OF THIS APPROACH:")
    print(f"   ✅ Uses complete tournament history for each team")
    print(f"   ✅ Incorporates current match events up to any minute")
    print(f"   ✅ Provides real-time momentum updates")
    print(f"   ✅ Accounts for match phase effects")
    print(f"   ✅ Combines multiple data sources intelligently")
    print(f"   ✅ Gives confidence scores for predictions")
    
    print(f"\n🚀 READY FOR LIVE MATCH IMPLEMENTATION!")

if __name__ == "__main__":
    main() 