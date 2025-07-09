#!/usr/bin/env python3
"""
Final Tournament Momentum Implementation Guide
Complete system for real-time momentum prediction using historical + current data
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class FinalTournamentMomentumSystem:
    """
    Complete implementation of tournament momentum prediction system
    """
    
    def __init__(self):
        self.events_df = None
        self.team_profiles = {}
        self.matchup_history = {}
        
    def load_data(self):
        """Load tournament data"""
        print("📊 Loading Euro 2024 Tournament Data...")
        try:
            self.events_df = pd.read_csv("../Data/events_complete.csv", low_memory=False)
            print(f"✅ Events loaded: {len(self.events_df):,}")
            self.events_df['event_name'] = self.events_df['type'].apply(self.extract_event_type)
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
    
    def explain_system_approach(self):
        """Explain the complete system approach"""
        print(f"\n🎯 TOURNAMENT MOMENTUM PREDICTION SYSTEM EXPLAINED")
        print("=" * 70)
        
        print(f"\n📋 SYSTEM COMPONENTS:")
        print(f"   1. Historical Tournament Data (Past matches for both teams)")
        print(f"   2. Current Match Events (All events up to current minute)")
        print(f"   3. Real-time Momentum Calculation")
        print(f"   4. Prediction Confidence Scoring")
        
        print(f"\n🔍 DATA SOURCES USED:")
        print(f"   📊 Historical Performance:")
        print(f"      • Goals per match")
        print(f"      • Shot efficiency")
        print(f"      • Activity patterns")
        print(f"      • Pressure handling")
        print(f"      • Phase-specific performance")
        
        print(f"\n   ⚡ Current Match Events:")
        print(f"      • Goals scored up to current minute")
        print(f"      • Shots taken")
        print(f"      • Recent activity (last 10 minutes)")
        print(f"      • Substitutions made")
        print(f"      • Cards received")
        print(f"      • Pressure situations")
        
        print(f"\n   ⏱️  Match Context:")
        print(f"      • Current minute")
        print(f"      • Match phase (opening, closing, stoppage)")
        print(f"      • Time pressure effects")
        print(f"      • Phase-specific multipliers")
        
        print(f"\n🧮 MOMENTUM CALCULATION FORMULA:")
        print(f"   Total Momentum = (Historical Baseline × 0.3) +")
        print(f"                   (Current Match Performance × 0.4) +")
        print(f"                   (Recent Activity × 0.3) ×")
        print(f"                   Phase Multiplier × Pressure Factor")
        
        print(f"\n📈 PHASE MULTIPLIERS:")
        print(f"   • Opening (1-15 min): 1.2× (high intensity)")
        print(f"   • First Half (16-45): 1.0× (baseline)")
        print(f"   • Early Second (46-60): 1.1× (tactical adjustments)")
        print(f"   • Mid Second (61-75): 1.0× (baseline)")
        print(f"   • Late Game (76-90): 1.3× (increased urgency)")
        print(f"   • Stoppage (90-105): 1.6× (drama factor)")
        print(f"   • Extra Time (105+): 1.9× (maximum intensity)")
        
        return True
    
    def build_comprehensive_team_profiles(self):
        """Build comprehensive team profiles from tournament history"""
        print(f"\n🏆 BUILDING COMPREHENSIVE TEAM PROFILES")
        print("=" * 50)
        
        # Get all unique teams
        teams = set()
        for col in ['team_name', 'home_team', 'away_team']:
            if col in self.events_df.columns:
                teams.update(self.events_df[col].dropna().unique())
        
        teams = [team for team in teams if pd.notna(team) and team != '']
        print(f"📋 Processing {len(teams)} teams...")
        
        for team in teams:
            profile = self.create_detailed_team_profile(team)
            if profile:
                self.team_profiles[team] = profile
        
        print(f"✅ Built profiles for {len(self.team_profiles)} teams")
        self.show_team_profile_summary()
        
        return self.team_profiles
    
    def create_detailed_team_profile(self, team):
        """Create detailed team profile with all tournament data"""
        
        # Get team events
        team_events = self.events_df[self.events_df['team_name'] == team]
        
        if len(team_events) == 0:
            return None
        
        # Get unique matches
        matches = team_events['match_id'].unique() if 'match_id' in team_events.columns else []
        
        # Calculate comprehensive profile
        profile = {
            # Basic stats
            'team_name': team,
            'matches_played': len(matches),
            'total_events': len(team_events),
            'events_per_match': len(team_events) / max(len(matches), 1),
            
            # Goal statistics
            'total_goals': len(team_events[team_events['event_name'].str.contains('Goal', na=False, case=False)]),
            'goals_per_match': len(team_events[team_events['event_name'].str.contains('Goal', na=False, case=False)]) / max(len(matches), 1),
            
            # Shot statistics
            'total_shots': len(team_events[team_events['event_name'].str.contains('Shot', na=False, case=False)]),
            'shots_per_match': len(team_events[team_events['event_name'].str.contains('Shot', na=False, case=False)]) / max(len(matches), 1),
            'shot_efficiency': len(team_events[team_events['event_name'].str.contains('Goal', na=False, case=False)]) / max(len(team_events[team_events['event_name'].str.contains('Shot', na=False, case=False)]), 1),
            
            # Discipline
            'total_fouls': len(team_events[team_events['foul_committed'].notna()]),
            'fouls_per_match': len(team_events[team_events['foul_committed'].notna()]) / max(len(matches), 1),
            'total_cards': len(team_events[team_events['bad_behaviour'].notna()]),
            'cards_per_match': len(team_events[team_events['bad_behaviour'].notna()]) / max(len(matches), 1),
            
            # Tactical
            'total_subs': len(team_events[team_events['substitution'].notna()]),
            'subs_per_match': len(team_events[team_events['substitution'].notna()]) / max(len(matches), 1),
            'tactical_changes': len(team_events[team_events['tactics'].notna()]),
            
            # Pressure handling
            'pressure_events': len(team_events[team_events['under_pressure'].notna()]),
            'pressure_ratio': len(team_events[team_events['under_pressure'].notna()]) / max(len(team_events), 1),
            'counterpress_events': len(team_events[team_events['counterpress'].notna()]),
            
            # Phase-specific performance
            'opening_events': len(team_events[team_events['minute'] <= 15]),
            'opening_goals': len(team_events[(team_events['minute'] <= 15) & (team_events['event_name'].str.contains('Goal', na=False, case=False))]),
            'opening_intensity': len(team_events[team_events['minute'] <= 15]) / max(len(team_events), 1),
            
            'closing_events': len(team_events[team_events['minute'] >= 75]),
            'closing_goals': len(team_events[(team_events['minute'] >= 75) & (team_events['event_name'].str.contains('Goal', na=False, case=False))]),
            'closing_strength': len(team_events[team_events['minute'] >= 75]) / max(len(team_events), 1),
            
            'stoppage_events': len(team_events[team_events['minute'] >= 90]),
            'stoppage_goals': len(team_events[(team_events['minute'] >= 90) & (team_events['event_name'].str.contains('Goal', na=False, case=False))]),
            
            # Performance indicators
            'avg_activity_per_minute': len(team_events) / max(sum(team_events['minute'].fillna(0)), 1),
            'consistency_score': 1.0 / (1.0 + np.std([len(team_events[team_events['match_id'] == m]) for m in matches]) / max(len(team_events), 1)) if len(matches) > 1 else 1.0
        }
        
        return profile
    
    def show_team_profile_summary(self):
        """Show summary of team profiles"""
        print(f"\n📊 TEAM PROFILE SUMMARY:")
        
        # Top goal scorers
        sorted_by_goals = sorted(self.team_profiles.items(), key=lambda x: x[1]['goals_per_match'], reverse=True)
        print(f"\n⚽ TOP GOAL SCORERS:")
        for i, (team, profile) in enumerate(sorted_by_goals[:8]):
            print(f"   {i+1}. {team:<15}: {profile['goals_per_match']:.1f} goals/match")
        
        # Most active teams
        sorted_by_activity = sorted(self.team_profiles.items(), key=lambda x: x[1]['events_per_match'], reverse=True)
        print(f"\n🔥 MOST ACTIVE TEAMS:")
        for i, (team, profile) in enumerate(sorted_by_activity[:8]):
            print(f"   {i+1}. {team:<15}: {profile['events_per_match']:.0f} events/match")
        
        # Best shot efficiency
        sorted_by_efficiency = sorted(self.team_profiles.items(), key=lambda x: x[1]['shot_efficiency'], reverse=True)
        print(f"\n🎯 BEST SHOT EFFICIENCY:")
        for i, (team, profile) in enumerate(sorted_by_efficiency[:8]):
            print(f"   {i+1}. {team:<15}: {profile['shot_efficiency']:.1%} conversion rate")
    
    def calculate_real_time_momentum(self, team, current_minute, current_match_events):
        """
        CORE FUNCTION: Calculate real-time momentum
        """
        
        # Get team profile
        profile = self.team_profiles.get(team, {})
        
        # Get current match events for this team up to current minute
        team_current = current_match_events[
            (current_match_events['team_name'] == team) & 
            (current_match_events['minute'] <= current_minute)
        ]
        
        # Get recent events (last 10 minutes)
        team_recent = team_current[team_current['minute'] >= current_minute - 10]
        
        # === COMPONENT 1: HISTORICAL BASELINE ===
        historical_baseline = (
            profile.get('goals_per_match', 0) * 0.8 +
            profile.get('shot_efficiency', 0) * 10 +
            profile.get('events_per_match', 0) * 0.01 +
            profile.get('opening_intensity', 0) * 2 +
            profile.get('closing_strength', 0) * 2 +
            profile.get('consistency_score', 0) * 1
        )
        
        # === COMPONENT 2: CURRENT MATCH PERFORMANCE ===
        current_goals = len(team_current[team_current['event_name'].str.contains('Goal', na=False, case=False)])
        current_shots = len(team_current[team_current['event_name'].str.contains('Shot', na=False, case=False)])
        current_events = len(team_current)
        
        current_performance = (
            current_goals * 1.5 +
            current_shots * 0.3 +
            current_events * 0.005 +
            (current_goals / max(current_shots, 1)) * 2  # Current efficiency
        )
        
        # === COMPONENT 3: RECENT ACTIVITY ===
        recent_goals = len(team_recent[team_recent['event_name'].str.contains('Goal', na=False, case=False)])
        recent_shots = len(team_recent[team_recent['event_name'].str.contains('Shot', na=False, case=False)])
        recent_events = len(team_recent)
        recent_subs = len(team_recent[team_recent['substitution'].notna()])
        recent_cards = len(team_recent[team_recent['bad_behaviour'].notna()])
        recent_pressure = len(team_recent[team_recent['under_pressure'].notna()])
        
        recent_activity = (
            recent_goals * 2.0 +
            recent_shots * 0.8 +
            recent_events * 0.02 +
            recent_subs * 0.3 -
            recent_cards * 0.4 +
            recent_pressure * 0.05
        )
        
        # === COMPONENT 4: PHASE MULTIPLIER ===
        phase_multiplier = self.get_phase_multiplier(current_minute)
        
        # === COMPONENT 5: PRESSURE FACTOR ===
        pressure_factor = 1.0
        if current_minute >= 75:
            pressure_factor = 1.2
        if current_minute >= 90:
            pressure_factor = 1.5
        if current_minute >= 105:
            pressure_factor = 1.8
        
        # === COMBINE ALL COMPONENTS ===
        total_momentum = (
            historical_baseline * 0.3 +
            current_performance * 0.4 +
            recent_activity * 0.3
        ) * phase_multiplier * pressure_factor
        
        # Normalize to 0-10 scale
        momentum = max(0, min(10, total_momentum))
        
        return momentum
    
    def get_phase_multiplier(self, minute):
        """Get phase multiplier based on minute"""
        if minute <= 15:
            return 1.2  # Opening intensity
        elif minute <= 45:
            return 1.0  # First half
        elif minute <= 60:
            return 1.1  # Early second half
        elif minute <= 75:
            return 1.0  # Mid second half
        elif minute <= 90:
            return 1.3  # Late game
        elif minute <= 105:
            return 1.6  # Stoppage time
        else:
            return 1.9  # Extra time
    
    def predict_match_momentum(self, team1, team2, current_minute, current_match_events):
        """
        MAIN PREDICTION FUNCTION: Predict momentum for both teams
        """
        
        print(f"\n🎯 REAL-TIME MOMENTUM PREDICTION")
        print("=" * 50)
        print(f"   Match: {team1} vs {team2}")
        print(f"   Current minute: {current_minute}")
        print(f"   Match phase: {self.get_match_phase(current_minute)}")
        
        # Calculate momentum for both teams
        momentum1 = self.calculate_real_time_momentum(team1, current_minute, current_match_events)
        momentum2 = self.calculate_real_time_momentum(team2, current_minute, current_match_events)
        
        # Get team profiles for context
        profile1 = self.team_profiles.get(team1, {})
        profile2 = self.team_profiles.get(team2, {})
        
        # Calculate advantage and confidence
        advantage = momentum1 - momentum2
        confidence = min(abs(advantage) / 10.0, 1.0)
        predicted_next_goal = team1 if momentum1 > momentum2 else team2
        
        # Show detailed prediction
        print(f"\n📊 HISTORICAL CONTEXT:")
        print(f"   {team1:<15}: {profile1.get('goals_per_match', 0):.1f} goals/match, {profile1.get('shot_efficiency', 0):.1%} efficiency")
        print(f"   {team2:<15}: {profile2.get('goals_per_match', 0):.1f} goals/match, {profile2.get('shot_efficiency', 0):.1%} efficiency")
        
        print(f"\n🚀 CURRENT MOMENTUM:")
        print(f"   {team1:<15}: {momentum1:.1f}/10")
        print(f"   {team2:<15}: {momentum2:.1f}/10")
        print(f"   Advantage: {advantage:+.1f} ({predicted_next_goal})")
        print(f"   Confidence: {confidence:.1%}")
        
        # Create prediction object
        prediction = {
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'minute': current_minute,
            'team1': team1,
            'team2': team2,
            'team1_momentum': momentum1,
            'team2_momentum': momentum2,
            'advantage': advantage,
            'predicted_next_goal': predicted_next_goal,
            'confidence': confidence,
            'match_phase': self.get_match_phase(current_minute),
            'phase_multiplier': self.get_phase_multiplier(current_minute)
        }
        
        return prediction
    
    def get_match_phase(self, minute):
        """Get match phase name"""
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
    
    def demonstrate_complete_system(self):
        """Demonstrate the complete system with real examples"""
        print(f"\n🎯 COMPLETE SYSTEM DEMONSTRATION")
        print("=" * 50)
        
        # Build team profiles
        self.build_comprehensive_team_profiles()
        
        # Get sample match
        sample_match = self.events_df['match_id'].iloc[0] if 'match_id' in self.events_df.columns else None
        if sample_match is None:
            print("❌ No match data available")
            return
        
        match_events = self.events_df[self.events_df['match_id'] == sample_match]
        teams = match_events['team_name'].dropna().unique()
        
        if len(teams) >= 2:
            team1, team2 = teams[0], teams[1]
            
            print(f"\n🏆 DEMONSTRATION MATCH: {team1} vs {team2}")
            
            # Show predictions at key moments
            key_moments = [20, 45, 60, 75, 90]
            predictions = []
            
            for minute in key_moments:
                current_events = match_events[match_events['minute'] <= minute]
                prediction = self.predict_match_momentum(team1, team2, minute, current_events)
                predictions.append(prediction)
            
            # Show momentum evolution
            print(f"\n📈 MOMENTUM EVOLUTION:")
            print(f"   {'Minute':<8} {team1[:8]:<8} {team2[:8]:<8} {'Advantage':<10} {'Phase':<12}")
            print(f"   {'-'*50}")
            
            for pred in predictions:
                print(f"   {pred['minute']:<8} {pred['team1_momentum']:<8.1f} {pred['team2_momentum']:<8.1f} {pred['advantage']:<+10.1f} {pred['match_phase']:<12}")
        
        print(f"\n✅ COMPLETE SYSTEM DEMONSTRATION FINISHED")
    
    def show_implementation_guide(self):
        """Show practical implementation guide"""
        print(f"\n📋 PRACTICAL IMPLEMENTATION GUIDE")
        print("=" * 50)
        
        print(f"\n🔧 STEP-BY-STEP IMPLEMENTATION:")
        print(f"   1. Load all tournament data (events, matches, teams)")
        print(f"   2. Build comprehensive team profiles from history")
        print(f"   3. For each live match prediction:")
        print(f"      a. Get current match events up to current minute")
        print(f"      b. Calculate momentum for both teams")
        print(f"      c. Apply phase multipliers and pressure factors")
        print(f"      d. Generate prediction with confidence score")
        print(f"   4. Update predictions every 2-3 minutes")
        print(f"   5. Adjust for specific match context")
        
        print(f"\n🎯 KEY SUCCESS FACTORS:")
        print(f"   ✅ Use complete tournament history (not just recent matches)")
        print(f"   ✅ Weight recent events more heavily than historical")
        print(f"   ✅ Account for match phase effects (late game = higher volatility)")
        print(f"   ✅ Include pressure factors (substitutions, cards, time pressure)")
        print(f"   ✅ Provide confidence scores for predictions")
        print(f"   ✅ Update frequently during live matches")
        
        print(f"\n⚠️  IMPORTANT CONSIDERATIONS:")
        print(f"   • Historical data provides baseline expectations")
        print(f"   • Current match events provide real-time adjustments")
        print(f"   • Phase multipliers capture time-based momentum shifts")
        print(f"   • Confidence scores indicate prediction reliability")
        print(f"   • System works best with regular updates (every 2-3 minutes)")

def main():
    """Main demonstration function"""
    print("🏆 FINAL TOURNAMENT MOMENTUM IMPLEMENTATION")
    print("=" * 80)
    
    system = FinalTournamentMomentumSystem()
    
    # Load data
    if not system.load_data():
        return
    
    # Explain the system
    system.explain_system_approach()
    
    # Demonstrate complete system
    system.demonstrate_complete_system()
    
    # Show implementation guide
    system.show_implementation_guide()
    
    print(f"\n🎯 FINAL SYSTEM SUMMARY:")
    print(f"   • Combines historical tournament data with current match events")
    print(f"   • Uses weighted formula: 30% history + 40% current + 30% recent")
    print(f"   • Applies phase multipliers for time-based effects")
    print(f"   • Provides confidence scores for prediction reliability")
    print(f"   • Ready for real-time live match implementation")
    
    print(f"\n🚀 SYSTEM READY FOR DEPLOYMENT!")

if __name__ == "__main__":
    main() 