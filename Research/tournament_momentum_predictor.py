#!/usr/bin/env python3
"""
Tournament Momentum Predictor
Combines historical tournament data with current match events for real-time prediction
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

class TournamentMomentumPredictor:
    def __init__(self):
        self.events_df = None
        self.matches_df = None
        self.team_history = {}
        self.head_to_head = {}
        
    def load_data(self):
        """Load Euro 2024 tournament data"""
        print("📊 Loading Euro 2024 Tournament Data...")
        try:
            self.events_df = pd.read_csv("../Data/events_complete.csv", low_memory=False)
            self.matches_df = pd.read_csv("../Data/matches_complete.csv")
            
            print(f"✅ Events loaded: {len(self.events_df):,}")
            print(f"✅ Matches loaded: {len(self.matches_df):,}")
            
            # Extract event names
            self.events_df['event_name'] = self.events_df['type'].apply(self.extract_event_type)
            
            # Create match identifiers
            if 'match_id' not in self.events_df.columns:
                self.events_df['match_id'] = pd.factorize(
                    self.events_df['home_team'].astype(str) + '_vs_' + 
                    self.events_df['away_team'].astype(str) + '_' +
                    self.events_df['match_date'].astype(str)
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
    
    def build_team_tournament_history(self):
        """Build historical performance data for each team throughout tournament"""
        print(f"\n🏆 BUILDING TEAM TOURNAMENT HISTORY")
        print("=" * 50)
        
        # Get unique teams
        teams = set()
        if 'home_team' in self.events_df.columns:
            teams.update(self.events_df['home_team'].dropna().unique())
        if 'away_team' in self.events_df.columns:
            teams.update(self.events_df['away_team'].dropna().unique())
        if 'team_name' in self.events_df.columns:
            teams.update(self.events_df['team_name'].dropna().unique())
        
        print(f"📋 Found {len(teams)} teams in tournament")
        
        # Build history for each team
        for team in teams:
            if pd.isna(team) or team == '':
                continue
                
            team_history = self.analyze_team_tournament_performance(team)
            if team_history:
                self.team_history[team] = team_history
        
        print(f"✅ Built history for {len(self.team_history)} teams")
        
        return self.team_history
    
    def analyze_team_tournament_performance(self, team):
        """Analyze a team's performance throughout the tournament"""
        
        # Get team's events
        team_events = self.events_df[
            (self.events_df['team_name'] == team) |
            (self.events_df['home_team'] == team) |
            (self.events_df['away_team'] == team)
        ]
        
        if len(team_events) == 0:
            return None
        
        # Get team's matches
        team_matches = set()
        if 'match_id' in team_events.columns:
            team_matches = team_events['match_id'].unique()
        
        # Calculate performance metrics
        performance = {
            'matches_played': len(team_matches),
            'total_events': len(team_events),
            'goals_scored': len(team_events[team_events['event_name'].str.contains('Goal', na=False, case=False)]),
            'shots_taken': len(team_events[team_events['event_name'].str.contains('Shot', na=False, case=False)]),
            'fouls_committed': len(team_events[team_events['foul_committed'].notna()]),
            'cards_received': len(team_events[team_events['bad_behaviour'].notna()]),
            'substitutions_made': len(team_events[team_events['substitution'].notna()]),
            'tactical_changes': len(team_events[team_events['tactics'].notna()]),
            'avg_possession': 0,  # Will calculate later
            'momentum_trend': 0,  # Will calculate later
            'pressure_situations': len(team_events[team_events['under_pressure'].notna()]),
            'counterpress_actions': len(team_events[team_events['counterpress'].notna()])
        }
        
        # Calculate match-by-match trends
        match_performance = []
        for match_id in team_matches:
            match_events = team_events[team_events['match_id'] == match_id]
            
            if len(match_events) == 0:
                continue
                
            match_stats = {
                'match_id': match_id,
                'events': len(match_events),
                'goals': len(match_events[match_events['event_name'].str.contains('Goal', na=False, case=False)]),
                'shots': len(match_events[match_events['event_name'].str.contains('Shot', na=False, case=False)]),
                'fouls': len(match_events[match_events['foul_committed'].notna()]),
                'cards': len(match_events[match_events['bad_behaviour'].notna()]),
                'subs': len(match_events[match_events['substitution'].notna()]),
                'pressure_events': len(match_events[match_events['under_pressure'].notna()]),
                'avg_minute': match_events['minute'].mean() if len(match_events) > 0 else 0
            }
            
            match_performance.append(match_stats)
        
        performance['match_history'] = match_performance
        
        # Calculate trends
        if len(match_performance) > 1:
            # Goal trend
            recent_goals = sum([m['goals'] for m in match_performance[-2:]])
            early_goals = sum([m['goals'] for m in match_performance[:2]])
            performance['goal_trend'] = recent_goals - early_goals
            
            # Event trend
            recent_events = np.mean([m['events'] for m in match_performance[-2:]])
            early_events = np.mean([m['events'] for m in match_performance[:2]])
            performance['activity_trend'] = recent_events - early_events
            
            # Pressure trend
            recent_pressure = np.mean([m['pressure_events'] for m in match_performance[-2:]])
            early_pressure = np.mean([m['pressure_events'] for m in match_performance[:2]])
            performance['pressure_trend'] = recent_pressure - early_pressure
        
        return performance
    
    def build_head_to_head_history(self):
        """Build head-to-head history between teams"""
        print(f"\n🤝 BUILDING HEAD-TO-HEAD HISTORY")
        print("=" * 50)
        
        # Get unique match combinations
        match_combinations = set()
        
        for _, row in self.events_df.iterrows():
            if pd.notna(row.get('home_team')) and pd.notna(row.get('away_team')):
                team1 = row['home_team']
                team2 = row['away_team']
                
                # Create normalized key
                key = tuple(sorted([team1, team2]))
                match_combinations.add(key)
        
        print(f"📋 Found {len(match_combinations)} unique team combinations")
        
        # Analyze each combination
        for team1, team2 in match_combinations:
            h2h_data = self.analyze_head_to_head(team1, team2)
            if h2h_data:
                self.head_to_head[f"{team1}_vs_{team2}"] = h2h_data
        
        print(f"✅ Built head-to-head data for {len(self.head_to_head)} matchups")
        
        return self.head_to_head
    
    def analyze_head_to_head(self, team1, team2):
        """Analyze head-to-head performance between two teams"""
        
        # Get events where both teams played
        h2h_events = self.events_df[
            ((self.events_df['home_team'] == team1) & (self.events_df['away_team'] == team2)) |
            ((self.events_df['home_team'] == team2) & (self.events_df['away_team'] == team1))
        ]
        
        if len(h2h_events) == 0:
            return None
        
        # Separate events by team
        team1_events = h2h_events[h2h_events['team_name'] == team1]
        team2_events = h2h_events[h2h_events['team_name'] == team2]
        
        h2h_data = {
            'total_meetings': len(h2h_events['match_id'].unique()),
            'team1_events': len(team1_events),
            'team2_events': len(team2_events),
            'team1_goals': len(team1_events[team1_events['event_name'].str.contains('Goal', na=False, case=False)]),
            'team2_goals': len(team2_events[team2_events['event_name'].str.contains('Goal', na=False, case=False)]),
            'team1_shots': len(team1_events[team1_events['event_name'].str.contains('Shot', na=False, case=False)]),
            'team2_shots': len(team2_events[team2_events['event_name'].str.contains('Shot', na=False, case=False)]),
            'team1_fouls': len(team1_events[team1_events['foul_committed'].notna()]),
            'team2_fouls': len(team2_events[team2_events['foul_committed'].notna()]),
            'team1_cards': len(team1_events[team1_events['bad_behaviour'].notna()]),
            'team2_cards': len(team2_events[team2_events['bad_behaviour'].notna()]),
            'possession_balance': (len(team1_events) / (len(team1_events) + len(team2_events))) * 100 if len(team1_events) + len(team2_events) > 0 else 50
        }
        
        # Calculate dominance metrics
        h2h_data['team1_dominance'] = (
            h2h_data['team1_goals'] - h2h_data['team2_goals'] +
            (h2h_data['team1_shots'] - h2h_data['team2_shots']) * 0.2 +
            (h2h_data['team1_events'] - h2h_data['team2_events']) * 0.01
        )
        
        return h2h_data
    
    def create_tournament_features(self, current_match_events, team, opponent_team, current_minute):
        """Create features combining tournament history with current match"""
        
        # Get current match events up to current minute
        current_events = current_match_events[
            (current_match_events['minute'] <= current_minute) &
            (current_match_events['team_name'] == team)
        ]
        
        if len(current_events) == 0:
            return None
        
        # === CURRENT MATCH FEATURES ===
        current_features = self.extract_current_match_features(current_events, current_minute)
        
        # === HISTORICAL TOURNAMENT FEATURES ===
        historical_features = self.extract_historical_features(team, opponent_team)
        
        # === HEAD-TO-HEAD FEATURES ===
        h2h_features = self.extract_head_to_head_features(team, opponent_team)
        
        # === TOURNAMENT PROGRESSION FEATURES ===
        progression_features = self.extract_tournament_progression_features(team, current_minute)
        
        # Combine all features
        combined_features = {
            **current_features,
            **historical_features,
            **h2h_features,
            **progression_features
        }
        
        return combined_features
    
    def extract_current_match_features(self, current_events, current_minute):
        """Extract features from current match up to current minute"""
        
        # Time windows
        last_10min = current_events[current_events['minute'] >= current_minute - 10]
        last_5min = current_events[current_events['minute'] >= current_minute - 5]
        last_2min = current_events[current_events['minute'] >= current_minute - 2]
        
        # Match phase
        match_phase = self.get_match_phase(current_minute)
        
        # Current activity
        current_activity = len(last_5min) / 5.0
        recent_activity = len(last_2min) / 2.0
        activity_trend = recent_activity - current_activity
        
        # Current events
        current_goals = len(current_events[current_events['event_name'].str.contains('Goal', na=False, case=False)])
        current_shots = len(current_events[current_events['event_name'].str.contains('Shot', na=False, case=False)])
        current_subs = len(current_events[current_events['substitution'].notna()])
        current_cards = len(current_events[current_events['bad_behaviour'].notna()])
        
        # Recent events
        recent_goals = len(last_10min[last_10min['event_name'].str.contains('Goal', na=False, case=False)])
        recent_shots = len(last_10min[last_10min['event_name'].str.contains('Shot', na=False, case=False)])
        recent_subs = len(last_10min[last_10min['substitution'].notna()])
        recent_cards = len(last_10min[last_10min['bad_behaviour'].notna()])
        
        # Pressure indicators
        pressure_events = len(last_5min[last_5min['under_pressure'].notna()])
        pressure_ratio = pressure_events / (len(last_5min) + 1)
        
        return {
            'current_minute': current_minute,
            'match_phase': match_phase,
            'current_activity': current_activity,
            'recent_activity': recent_activity,
            'activity_trend': activity_trend,
            'current_goals': current_goals,
            'current_shots': current_shots,
            'current_subs': current_subs,
            'current_cards': current_cards,
            'recent_goals': recent_goals,
            'recent_shots': recent_shots,
            'recent_subs': recent_subs,
            'recent_cards': recent_cards,
            'pressure_ratio': pressure_ratio,
            'total_events': len(current_events)
        }
    
    def extract_historical_features(self, team, opponent_team):
        """Extract historical tournament features for team"""
        
        # Team history
        team_hist = self.team_history.get(team, {})
        opponent_hist = self.team_history.get(opponent_team, {})
        
        # Tournament form
        team_form = {
            'historical_goals_per_match': team_hist.get('goals_scored', 0) / max(team_hist.get('matches_played', 1), 1),
            'historical_shots_per_match': team_hist.get('shots_taken', 0) / max(team_hist.get('matches_played', 1), 1),
            'historical_events_per_match': team_hist.get('total_events', 0) / max(team_hist.get('matches_played', 1), 1),
            'historical_fouls_per_match': team_hist.get('fouls_committed', 0) / max(team_hist.get('matches_played', 1), 1),
            'historical_cards_per_match': team_hist.get('cards_received', 0) / max(team_hist.get('matches_played', 1), 1),
            'historical_subs_per_match': team_hist.get('substitutions_made', 0) / max(team_hist.get('matches_played', 1), 1),
            'goal_trend': team_hist.get('goal_trend', 0),
            'activity_trend': team_hist.get('activity_trend', 0),
            'pressure_trend': team_hist.get('pressure_trend', 0)
        }
        
        # Opponent comparison
        opponent_form = {
            'opponent_goals_per_match': opponent_hist.get('goals_scored', 0) / max(opponent_hist.get('matches_played', 1), 1),
            'opponent_shots_per_match': opponent_hist.get('shots_taken', 0) / max(opponent_hist.get('matches_played', 1), 1),
            'opponent_events_per_match': opponent_hist.get('total_events', 0) / max(opponent_hist.get('matches_played', 1), 1),
            'opponent_fouls_per_match': opponent_hist.get('fouls_committed', 0) / max(opponent_hist.get('matches_played', 1), 1)
        }
        
        # Form comparison
        form_comparison = {
            'goal_form_advantage': team_form['historical_goals_per_match'] - opponent_form['opponent_goals_per_match'],
            'shot_form_advantage': team_form['historical_shots_per_match'] - opponent_form['opponent_shots_per_match'],
            'activity_form_advantage': team_form['historical_events_per_match'] - opponent_form['opponent_events_per_match'],
            'discipline_form_advantage': opponent_form['opponent_fouls_per_match'] - team_form['historical_fouls_per_match']
        }
        
        return {**team_form, **opponent_form, **form_comparison}
    
    def extract_head_to_head_features(self, team, opponent_team):
        """Extract head-to-head features"""
        
        # Try both key combinations
        h2h_key1 = f"{team}_vs_{opponent_team}"
        h2h_key2 = f"{opponent_team}_vs_{team}"
        
        h2h_data = self.head_to_head.get(h2h_key1) or self.head_to_head.get(h2h_key2)
        
        if not h2h_data:
            return {
                'h2h_meetings': 0,
                'h2h_dominance': 0,
                'h2h_goal_ratio': 1.0,
                'h2h_shot_ratio': 1.0,
                'h2h_possession_advantage': 0,
                'h2h_discipline_advantage': 0
            }
        
        # Determine team order in h2h data
        team_is_team1 = h2h_key1 in self.head_to_head
        
        if team_is_team1:
            team_goals = h2h_data['team1_goals']
            team_shots = h2h_data['team1_shots']
            team_fouls = h2h_data['team1_fouls']
            team_cards = h2h_data['team1_cards']
            opponent_goals = h2h_data['team2_goals']
            opponent_shots = h2h_data['team2_shots']
            opponent_fouls = h2h_data['team2_fouls']
            opponent_cards = h2h_data['team2_cards']
            dominance = h2h_data['team1_dominance']
            possession_advantage = h2h_data['possession_balance'] - 50
        else:
            team_goals = h2h_data['team2_goals']
            team_shots = h2h_data['team2_shots']
            team_fouls = h2h_data['team2_fouls']
            team_cards = h2h_data['team2_cards']
            opponent_goals = h2h_data['team1_goals']
            opponent_shots = h2h_data['team1_shots']
            opponent_fouls = h2h_data['team1_fouls']
            opponent_cards = h2h_data['team1_cards']
            dominance = -h2h_data['team1_dominance']
            possession_advantage = 50 - h2h_data['possession_balance']
        
        return {
            'h2h_meetings': h2h_data['total_meetings'],
            'h2h_dominance': dominance,
            'h2h_goal_ratio': team_goals / max(opponent_goals, 1),
            'h2h_shot_ratio': team_shots / max(opponent_shots, 1),
            'h2h_possession_advantage': possession_advantage,
            'h2h_discipline_advantage': (opponent_fouls + opponent_cards * 2) - (team_fouls + team_cards * 2)
        }
    
    def extract_tournament_progression_features(self, team, current_minute):
        """Extract tournament progression features"""
        
        team_hist = self.team_history.get(team, {})
        matches_played = team_hist.get('matches_played', 0)
        
        # Tournament stage estimation
        tournament_stage = min(matches_played / 7.0, 1.0)  # Normalize to 0-1
        
        # Experience factor
        experience_factor = min(matches_played * 0.2, 1.0)
        
        # Fatigue factor (more matches = more fatigue)
        fatigue_factor = matches_played * 0.1
        
        # Time pressure in tournament
        tournament_pressure = tournament_stage * 0.5 + (current_minute / 120.0) * 0.5
        
        return {
            'tournament_stage': tournament_stage,
            'matches_played': matches_played,
            'experience_factor': experience_factor,
            'fatigue_factor': fatigue_factor,
            'tournament_pressure': tournament_pressure
        }
    
    def get_match_phase(self, minute):
        """Get match phase based on minute"""
        if minute <= 15:
            return 1  # Opening
        elif minute <= 45:
            return 2  # First half
        elif minute <= 60:
            return 3  # Early second half
        elif minute <= 75:
            return 4  # Mid second half
        elif minute <= 90:
            return 5  # Late second half
        elif minute <= 105:
            return 6  # Stoppage time
        else:
            return 7  # Extra time
    
    def calculate_tournament_momentum(self, features):
        """Calculate momentum using tournament + current match features"""
        
        # Base momentum from current match
        base_momentum = (
            features['current_activity'] * 0.3 +
            features['recent_goals'] * 2.0 +
            features['recent_shots'] * 0.8 +
            features['activity_trend'] * 1.5 +
            features['current_goals'] * 1.5
        )
        
        # Historical form boost
        form_boost = (
            features['goal_form_advantage'] * 1.0 +
            features['shot_form_advantage'] * 0.5 +
            features['activity_form_advantage'] * 0.01 +
            features['goal_trend'] * 0.5 +
            features['activity_trend'] * 0.3
        )
        
        # Head-to-head advantage
        h2h_boost = (
            features['h2h_dominance'] * 0.5 +
            features['h2h_goal_ratio'] * 0.3 +
            features['h2h_possession_advantage'] * 0.02 +
            features['h2h_discipline_advantage'] * 0.1
        )
        
        # Tournament context
        tournament_factor = (
            features['experience_factor'] * 0.5 +
            features['tournament_pressure'] * 0.3 -
            features['fatigue_factor'] * 0.2
        )
        
        # Match phase multiplier
        phase_multiplier = {
            1: 1.2,  # Opening intensity
            2: 1.0,  # Normal first half
            3: 1.1,  # Second half start
            4: 1.0,  # Mid second half
            5: 1.3,  # Late second half
            6: 1.5,  # Stoppage time
            7: 1.8   # Extra time
        }.get(features['match_phase'], 1.0)
        
        total_momentum = (
            base_momentum * phase_multiplier +
            form_boost +
            h2h_boost +
            tournament_factor
        )
        
        return max(0, min(10, total_momentum))
    
    def demonstrate_tournament_prediction(self, sample_matches=10):
        """Demonstrate tournament momentum prediction"""
        print(f"\n🚀 TOURNAMENT MOMENTUM PREDICTION DEMO")
        print("=" * 50)
        
        # Build historical data
        self.build_team_tournament_history()
        self.build_head_to_head_history()
        
        # Sample matches for demonstration
        unique_matches = self.events_df['match_id'].unique()[:sample_matches]
        predictions = []
        
        for i, match_id in enumerate(unique_matches):
            print(f"\nProcessing match {i+1}/{len(unique_matches)}")
            
            match_events = self.events_df[self.events_df['match_id'] == match_id]
            
            # Get teams
            teams = match_events['team_name'].dropna().unique()
            if len(teams) < 2:
                continue
            
            team1, team2 = teams[0], teams[1]
            
            # Simulate predictions at different minutes
            for minute in range(20, 91, 10):
                
                # Get features for team1
                features1 = self.create_tournament_features(match_events, team1, team2, minute)
                if features1 is None:
                    continue
                
                # Get features for team2
                features2 = self.create_tournament_features(match_events, team2, team1, minute)
                if features2 is None:
                    continue
                
                # Calculate momentum
                momentum1 = self.calculate_tournament_momentum(features1)
                momentum2 = self.calculate_tournament_momentum(features2)
                
                # Calculate future momentum (5 minutes later)
                future_features1 = self.create_tournament_features(match_events, team1, team2, minute + 5)
                future_features2 = self.create_tournament_features(match_events, team2, team1, minute + 5)
                
                future_momentum1 = self.calculate_tournament_momentum(future_features1) if future_features1 else momentum1
                future_momentum2 = self.calculate_tournament_momentum(future_features2) if future_features2 else momentum2
                
                prediction = {
                    'match_id': match_id,
                    'minute': minute,
                    'team1': team1,
                    'team2': team2,
                    'team1_current_momentum': momentum1,
                    'team2_current_momentum': momentum2,
                    'team1_future_momentum': future_momentum1,
                    'team2_future_momentum': future_momentum2,
                    'momentum_advantage': momentum1 - momentum2,
                    'predicted_change1': future_momentum1 - momentum1,
                    'predicted_change2': future_momentum2 - momentum2,
                    **{f'team1_{k}': v for k, v in features1.items()},
                    **{f'team2_{k}': v for k, v in features2.items()}
                }
                
                predictions.append(prediction)
        
        predictions_df = pd.DataFrame(predictions)
        print(f"\n✅ Generated {len(predictions_df)} tournament predictions")
        
        return predictions_df
    
    def analyze_prediction_accuracy(self, predictions_df):
        """Analyze prediction accuracy"""
        print(f"\n📊 TOURNAMENT PREDICTION ANALYSIS")
        print("=" * 50)
        
        if len(predictions_df) == 0:
            print("No predictions to analyze")
            return
        
        # Analyze momentum distributions
        print(f"📈 Momentum Distribution:")
        print(f"   Team1 momentum: {predictions_df['team1_current_momentum'].mean():.2f} ± {predictions_df['team1_current_momentum'].std():.2f}")
        print(f"   Team2 momentum: {predictions_df['team2_current_momentum'].mean():.2f} ± {predictions_df['team2_current_momentum'].std():.2f}")
        print(f"   Momentum advantage: {predictions_df['momentum_advantage'].mean():.2f} ± {predictions_df['momentum_advantage'].std():.2f}")
        
        # Analyze by match phase
        print(f"\n⏱️  Momentum by Match Phase:")
        for phase in sorted(predictions_df['team1_match_phase'].unique()):
            phase_data = predictions_df[predictions_df['team1_match_phase'] == phase]
            if len(phase_data) > 0:
                avg_momentum = phase_data['team1_current_momentum'].mean()
                avg_change = phase_data['predicted_change1'].mean()
                phase_names = {1: "Opening", 2: "First Half", 3: "Early 2nd", 4: "Mid 2nd", 5: "Late 2nd", 6: "Stoppage", 7: "Extra Time"}
                print(f"   {phase_names.get(phase, f'Phase {phase}'):<12}: {avg_momentum:.2f} momentum, {avg_change:+.2f} change")
        
        # Analyze key features
        print(f"\n🔑 Key Feature Analysis:")
        key_features = ['team1_goal_form_advantage', 'team1_h2h_dominance', 'team1_experience_factor', 'team1_tournament_pressure']
        for feature in key_features:
            if feature in predictions_df.columns:
                correlation = predictions_df[feature].corr(predictions_df['team1_current_momentum'])
                print(f"   {feature.replace('team1_', '').replace('_', ' ').title():<25}: {correlation:.3f}")
        
        # Show sample predictions
        print(f"\n🎯 SAMPLE PREDICTIONS:")
        sample_predictions = predictions_df.sample(min(5, len(predictions_df)))
        for _, pred in sample_predictions.iterrows():
            print(f"   Minute {pred['minute']:2d}: {pred['team1'][:8]} {pred['team1_current_momentum']:.1f} vs {pred['team2'][:8]} {pred['team2_current_momentum']:.1f} (advantage: {pred['momentum_advantage']:+.1f})")

def main():
    """Main function"""
    print("🏆 TOURNAMENT MOMENTUM PREDICTION SYSTEM")
    print("=" * 80)
    
    predictor = TournamentMomentumPredictor()
    
    # Load data
    if not predictor.load_data():
        return
    
    # Demonstrate tournament prediction
    predictions_df = predictor.demonstrate_tournament_prediction(sample_matches=15)
    
    # Analyze results
    predictor.analyze_prediction_accuracy(predictions_df)
    
    print(f"\n💡 TOURNAMENT PREDICTION INSIGHTS:")
    print(f"   • Historical tournament data provides team baseline momentum")
    print(f"   • Head-to-head data shows specific matchup advantages")
    print(f"   • Current match events provide real-time momentum adjustments")
    print(f"   • Tournament progression adds experience/fatigue factors")
    print(f"   • Combined approach gives comprehensive momentum prediction")
    
    print(f"\n✅ TOURNAMENT PREDICTION SYSTEM COMPLETE")

if __name__ == "__main__":
    main() 