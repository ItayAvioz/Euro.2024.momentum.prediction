#!/usr/bin/env python3
"""
Game Event Momentum Patterns Analysis
Finding specific events that predict future momentum changes
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error, accuracy_score
import os
import warnings
warnings.filterwarnings('ignore')

class GameEventMomentumAnalyzer:
    """
    Analyze specific game events that predict momentum changes
    """
    
    def __init__(self):
        self.events_df = None
        self.model = None
        
    def load_data(self):
        """Load Euro 2024 data"""
        print("📊 Loading Euro 2024 Dataset...")
        
        try:
            self.events_df = pd.read_csv("../Data/events_complete.csv", low_memory=False)
            matches_df = pd.read_csv("../Data/matches_complete.csv")
            
            print(f"✅ Events: {len(self.events_df):,}")
            print(f"✅ Matches: {len(matches_df):,}")
            
            # Add match context
            if 'match_id' not in self.events_df.columns:
                self.events_df['match_id'] = pd.factorize(
                    self.events_df['possession_team'].astype(str) + '_' + 
                    self.events_df['period'].astype(str)
                )[0]
            
            return True
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def analyze_game_events(self):
        """Analyze what game events are available in the data"""
        print(f"\n🔍 ANALYZING AVAILABLE GAME EVENTS")
        print("=" * 50)
        
        # Check event types
        event_types = self.events_df['type'].value_counts()
        print(f"📊 Event Types (Top 20):")
        for event_type, count in event_types.head(20).items():
            print(f"   {event_type:<25}: {count:>8,}")
        
        # Check for specific high-impact events
        high_impact_events = [
            'Substitution', 'Yellow Card', 'Red Card', 'Goal', 'Penalty',
            'Corner', 'Free Kick', 'Throw-in', 'Offside', 'Foul'
        ]
        
        print(f"\n🎯 HIGH-IMPACT EVENTS:")
        for event in high_impact_events:
            count = len(self.events_df[self.events_df['type'].str.contains(event, na=False, case=False)])
            if count > 0:
                print(f"   {event:<20}: {count:>6,} events")
        
        # Check for tactical/formation data
        if 'tactics' in self.events_df.columns:
            tactics_count = self.events_df['tactics'].notna().sum()
            print(f"\n🎪 TACTICAL DATA:")
            print(f"   Tactics entries: {tactics_count:,}")
        
        # Check for substitution data
        if 'substitution' in self.events_df.columns:
            sub_count = self.events_df['substitution'].notna().sum()
            print(f"   Substitution data: {sub_count:,}")
        
        # Check match phases
        print(f"\n⏱️  MATCH PHASES:")
        print(f"   First 15 minutes: {len(self.events_df[self.events_df['minute'] <= 15]):,}")
        print(f"   Last 15 minutes (75+): {len(self.events_df[self.events_df['minute'] >= 75]):,}")
        print(f"   Stoppage time (90+): {len(self.events_df[self.events_df['minute'] >= 90]):,}")
        print(f"   Extra time (105+): {len(self.events_df[self.events_df['minute'] >= 105]):,}")
        
        return event_types
    
    def create_game_event_features(self, events_df, sample_matches=25):
        """Create features based on specific game events"""
        print(f"\n🔧 CREATING GAME EVENT MOMENTUM FEATURES")
        print("=" * 50)
        
        unique_matches = events_df['match_id'].unique()[:sample_matches]
        momentum_records = []
        
        for i, match_id in enumerate(unique_matches):
            print(f"Processing match {i+1}/{len(unique_matches)}: {match_id}")
            
            match_events = events_df[events_df['match_id'] == match_id]
            match_events = match_events.sort_values('minute')
            
            teams = match_events['team'].dropna().unique()
            if len(teams) < 2:
                continue
                
            match_duration = int(match_events['minute'].max())
            if match_duration < 20:
                continue
            
            for team in teams:
                # Process every 2 minutes
                for minute in range(8, match_duration - 5, 2):
                    
                    # Extract game event features
                    features = self.extract_game_event_features(
                        match_events, team, minute, teams, match_duration
                    )
                    
                    if features is None:
                        continue
                    
                    # Calculate current momentum
                    current_momentum = self.calculate_current_momentum(features)
                    
                    # Calculate future momentum (3 minutes ahead)
                    future_momentum = self.calculate_future_momentum(
                        match_events, team, minute + 3, teams
                    )
                    
                    if future_momentum is None:
                        continue
                    
                    momentum_change = future_momentum - current_momentum
                    
                    record = {
                        'match_id': match_id,
                        'team': team,
                        'minute': minute,
                        'current_momentum': current_momentum,
                        'future_momentum': future_momentum,
                        'momentum_change': momentum_change,
                        **features
                    }
                    
                    momentum_records.append(record)
        
        momentum_df = pd.DataFrame(momentum_records)
        print(f"✅ Created {len(momentum_df)} game event momentum samples")
        
        return momentum_df
    
    def extract_game_event_features(self, match_events, team, minute, teams, match_duration):
        """Extract features based on specific game events"""
        
        # Time windows
        last_5min = match_events[
            (match_events['minute'] >= minute-5) & 
            (match_events['minute'] < minute)
        ]
        last_2min = match_events[
            (match_events['minute'] >= minute-2) & 
            (match_events['minute'] < minute)
        ]
        
        team_5min = last_5min[last_5min['team'] == team]
        team_2min = last_2min[last_2min['team'] == team]
        
        if len(team_2min) == 0 and len(team_5min) == 0:
            return None
        
        # === BASIC ACTIVITY ===
        events_2min = len(team_2min)
        events_5min = len(team_5min)
        shots_2min = len(team_2min[team_2min['type'].str.contains('Shot', na=False)])
        
        # === MATCH PHASE FEATURES ===
        # Opening phase (first 15 minutes)
        opening_phase = 1 if minute <= 15 else 0
        
        # Closing phase (last 15 minutes of regulation)
        closing_phase = 1 if minute >= 75 and minute < 90 else 0
        
        # Stoppage time
        stoppage_time = 1 if minute >= 90 and minute < 105 else 0
        
        # Extra time / Overtime
        extra_time = 1 if minute >= 105 else 0
        
        # Match intensity phase
        early_match = 1 if minute <= 30 else 0
        mid_match = 1 if 30 < minute <= 60 else 0
        late_match = 1 if minute > 60 else 0
        
        # === CARDS AND DISCIPLINE ===
        # Recent cards for team
        team_yellow_cards_5min = len(team_5min[team_5min['type'].str.contains('Yellow Card', na=False)])
        team_red_cards_5min = len(team_5min[team_5min['type'].str.contains('Red Card', na=False)])
        
        # Recent cards for opponent
        opponent_team = [t for t in teams if t != team][0] if len(teams) > 1 else None
        if opponent_team:
            opponent_5min = last_5min[last_5min['team'] == opponent_team]
            opponent_yellow_cards_5min = len(opponent_5min[opponent_5min['type'].str.contains('Yellow Card', na=False)])
            opponent_red_cards_5min = len(opponent_5min[opponent_5min['type'].str.contains('Red Card', na=False)])
        else:
            opponent_yellow_cards_5min = 0
            opponent_red_cards_5min = 0
        
        # Card momentum (team advantage)
        card_advantage = (opponent_yellow_cards_5min + opponent_red_cards_5min * 2) - (team_yellow_cards_5min + team_red_cards_5min * 2)
        
        # === SUBSTITUTIONS ===
        # Recent substitutions
        team_subs_5min = len(team_5min[team_5min['type'].str.contains('Substitution', na=False)])
        opponent_subs_5min = len(opponent_5min[opponent_5min['type'].str.contains('Substitution', na=False)]) if opponent_team else 0
        
        # Fresh legs advantage (recent subs can boost momentum)
        fresh_legs_advantage = team_subs_5min - opponent_subs_5min
        
        # === SET PIECES AND SCORING OPPORTUNITIES ===
        # Corners (attacking momentum)
        team_corners_5min = len(team_5min[team_5min['type'].str.contains('Corner', na=False)])
        
        # Free kicks (potential momentum)
        team_freekicks_5min = len(team_5min[team_5min['type'].str.contains('Free Kick', na=False)])
        
        # Penalties (huge momentum shift)
        team_penalties_5min = len(team_5min[team_5min['type'].str.contains('Penalty', na=False)])
        
        # Goals (massive momentum)
        team_goals_5min = len(team_5min[team_5min['type'].str.contains('Goal', na=False)])
        opponent_goals_5min = len(opponent_5min[opponent_5min['type'].str.contains('Goal', na=False)]) if opponent_team else 0
        
        goal_momentum = team_goals_5min - opponent_goals_5min
        
        # === FOULS AND PRESSURE ===
        # Fouls committed (may indicate pressure/frustration)
        team_fouls_5min = len(team_5min[team_5min['type'].str.contains('Foul', na=False)])
        
        # Offsides (attacking intent but lack of precision)
        team_offsides_5min = len(team_5min[team_5min['type'].str.contains('Offside', na=False)])
        
        # === POSSESSION AND ACTIVITY ===
        possession_2min = (events_2min / (len(last_2min) + 1)) * 100
        
        # Activity trend
        activity_rate_2min = events_2min / 2.0
        activity_rate_5min = events_5min / 5.0
        activity_trend = activity_rate_2min - activity_rate_5min
        
        # === PRESSURE SITUATIONS ===
        # Under pressure events
        pressure_events = len(team_2min[team_2min['under_pressure'].notna()])
        pressure_ratio = pressure_events / (events_2min + 1)
        
        # === TIME PRESSURE FEATURES ===
        # Minutes remaining (creates urgency)
        minutes_remaining = max(0, 90 - minute)
        time_pressure = 1.0 - (minutes_remaining / 90.0)
        
        # Score-based pressure (if we had score data)
        # For now, use goal differential as proxy
        score_pressure = abs(goal_momentum)  # Higher when score difference exists
        
        # === RHYTHM AND MOMENTUM SHIFTS ===
        # Recent momentum events (goals, cards, subs in last 2 minutes)
        recent_momentum_events = (
            team_goals_5min * 3 +
            team_penalties_5min * 2 +
            team_subs_5min * 1 +
            card_advantage * 1
        )
        
        return {
            # Basic activity
            'events_2min': events_2min,
            'events_5min': events_5min,
            'shots_2min': shots_2min,
            'possession_2min': possession_2min,
            'activity_trend': activity_trend,
            'pressure_ratio': pressure_ratio,
            
            # Match phases
            'opening_phase': opening_phase,
            'closing_phase': closing_phase,
            'stoppage_time': stoppage_time,
            'extra_time': extra_time,
            'early_match': early_match,
            'mid_match': mid_match,
            'late_match': late_match,
            
            # Cards and discipline
            'team_yellow_cards_5min': team_yellow_cards_5min,
            'team_red_cards_5min': team_red_cards_5min,
            'opponent_yellow_cards_5min': opponent_yellow_cards_5min,
            'opponent_red_cards_5min': opponent_red_cards_5min,
            'card_advantage': card_advantage,
            
            # Substitutions
            'team_subs_5min': team_subs_5min,
            'opponent_subs_5min': opponent_subs_5min,
            'fresh_legs_advantage': fresh_legs_advantage,
            
            # Set pieces and scoring
            'team_corners_5min': team_corners_5min,
            'team_freekicks_5min': team_freekicks_5min,
            'team_penalties_5min': team_penalties_5min,
            'team_goals_5min': team_goals_5min,
            'opponent_goals_5min': opponent_goals_5min,
            'goal_momentum': goal_momentum,
            
            # Fouls and pressure
            'team_fouls_5min': team_fouls_5min,
            'team_offsides_5min': team_offsides_5min,
            
            # Time pressure
            'minutes_remaining': minutes_remaining,
            'time_pressure': time_pressure,
            'score_pressure': score_pressure,
            
            # Momentum events
            'recent_momentum_events': recent_momentum_events
        }
    
    def calculate_current_momentum(self, features):
        """Calculate current momentum using game event features"""
        momentum = (
            # Basic activity
            features['events_2min'] * 0.3 +
            features['shots_2min'] * 1.5 +
            features['possession_2min'] * 0.02 +
            features['activity_trend'] * 1.5 +
            
            # Goals (massive impact)
            features['goal_momentum'] * 4.0 +
            
            # Cards (momentum shifters)
            features['card_advantage'] * 2.0 +
            
            # Substitutions (fresh energy)
            features['fresh_legs_advantage'] * 1.0 +
            
            # Set pieces (scoring opportunities)
            features['team_corners_5min'] * 0.5 +
            features['team_penalties_5min'] * 3.0 +
            
            # Time pressure boost (end game urgency)
            features['time_pressure'] * features['closing_phase'] * 2.0 +
            features['stoppage_time'] * 2.0 +
            features['extra_time'] * 3.0 +
            
            # Momentum events
            features['recent_momentum_events'] * 0.5 -
            
            # Pressure penalty
            features['pressure_ratio'] * 1.0 -
            features['team_fouls_5min'] * 0.2
        )
        
        return max(0, min(10, momentum))
    
    def calculate_future_momentum(self, match_events, team, future_minute, teams):
        """Calculate future momentum"""
        
        future_window = match_events[
            (match_events['minute'] >= future_minute) & 
            (match_events['minute'] < future_minute + 2)
        ]
        
        if len(future_window) == 0:
            return None
        
        team_future = future_window[future_window['team'] == team]
        
        # Basic future activity
        future_events = len(team_future)
        future_shots = len(team_future[team_future['type'].str.contains('Shot', na=False)])
        future_goals = len(team_future[team_future['type'].str.contains('Goal', na=False)])
        
        # Future possession
        future_possession = (future_events / (len(future_window) + 1)) * 100
        
        # Calculate future momentum
        future_momentum = min(10, max(0,
            future_events * 0.5 +
            future_shots * 2.0 +
            future_goals * 5.0 +
            future_possession * 0.02
        ))
        
        return future_momentum
    
    def train_game_event_model(self, momentum_df):
        """Train model with game event features"""
        print(f"\n🚀 TRAINING GAME EVENT MOMENTUM MODEL")
        print("=" * 50)
        
        # Prepare features
        feature_cols = [col for col in momentum_df.columns 
                       if col not in ['match_id', 'team', 'minute', 'current_momentum',
                                     'future_momentum', 'momentum_change']]
        
        X = momentum_df[feature_cols]
        y = momentum_df['momentum_change']
        
        print(f"📊 Dataset preparation:")
        print(f"   Features: {len(feature_cols)}")
        print(f"   Samples: {len(X)}")
        print(f"   Target range: {y.min():.2f} to {y.max():.2f}")
        print(f"   Target mean: {y.mean():.2f} ± {y.std():.2f}")
        
        # Match-based split
        matches = momentum_df['match_id'].unique()
        np.random.seed(42)
        np.random.shuffle(matches)
        
        n_train = int(len(matches) * 0.8)
        train_matches = matches[:n_train]
        test_matches = matches[n_train:]
        
        train_data = momentum_df[momentum_df['match_id'].isin(train_matches)]
        test_data = momentum_df[momentum_df['match_id'].isin(test_matches)]
        
        X_train = train_data[feature_cols]
        y_train = train_data['momentum_change']
        X_test = test_data[feature_cols]
        y_test = test_data['momentum_change']
        
        print(f"\n🎯 Match-based split:")
        print(f"   Training matches: {len(train_matches)}")
        print(f"   Testing matches: {len(test_matches)}")
        print(f"   Training samples: {len(X_train)}")
        print(f"   Testing samples: {len(X_test)}")
        
        # Train model
        self.model = RandomForestRegressor(
            n_estimators=200,
            max_depth=12,
            min_samples_split=5,
            random_state=42
        )
        
        self.model.fit(X_train, y_train)
        y_pred = self.model.predict(X_test)
        
        # Evaluate
        r2 = r2_score(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        
        print(f"\n📈 MODEL PERFORMANCE:")
        print(f"   R² Score: {r2:.3f}")
        print(f"   MAE: {mae:.3f}")
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': feature_cols,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print(f"\n🔝 TOP GAME EVENT PREDICTORS:")
        for _, row in feature_importance.head(15).iterrows():
            print(f"   {row['feature']:<30}: {row['importance']:.3f}")
        
        return feature_importance, r2, mae
    
    def analyze_specific_event_impacts(self, momentum_df):
        """Analyze impact of specific events on momentum"""
        print(f"\n📊 SPECIFIC EVENT IMPACT ANALYSIS")
        print("=" * 50)
        
        # Impact of different match phases
        print(f"🕐 MATCH PHASE IMPACTS:")
        phases = ['opening_phase', 'closing_phase', 'stoppage_time', 'extra_time']
        for phase in phases:
            if phase in momentum_df.columns:
                phase_data = momentum_df[momentum_df[phase] == 1]
                if len(phase_data) > 5:
                    avg_change = phase_data['momentum_change'].mean()
                    std_change = phase_data['momentum_change'].std()
                    print(f"   {phase:<20}: {avg_change:>6.2f} ± {std_change:.2f} (n={len(phase_data)})")
        
        # Impact of cards
        print(f"\n🟨 CARD IMPACTS:")
        # Teams with recent yellow cards
        yellow_impact = momentum_df[momentum_df['team_yellow_cards_5min'] > 0]['momentum_change'].mean()
        no_yellow_impact = momentum_df[momentum_df['team_yellow_cards_5min'] == 0]['momentum_change'].mean()
        
        print(f"   With recent yellow card: {yellow_impact:.2f}")
        print(f"   Without yellow card:    {no_yellow_impact:.2f}")
        print(f"   Yellow card impact:     {yellow_impact - no_yellow_impact:.2f}")
        
        # Card advantage impact
        card_advantage_groups = momentum_df.groupby('card_advantage')['momentum_change'].mean()
        print(f"   Card advantage impact:")
        for advantage, avg_change in card_advantage_groups.items():
            if not pd.isna(avg_change):
                print(f"   Advantage {advantage:>2}: {avg_change:>6.2f}")
        
        # Impact of substitutions
        print(f"\n🔄 SUBSTITUTION IMPACTS:")
        sub_impact = momentum_df[momentum_df['team_subs_5min'] > 0]['momentum_change'].mean()
        no_sub_impact = momentum_df[momentum_df['team_subs_5min'] == 0]['momentum_change'].mean()
        
        print(f"   With recent substitution: {sub_impact:.2f}")
        print(f"   Without substitution:     {no_sub_impact:.2f}")
        print(f"   Substitution impact:      {sub_impact - no_sub_impact:.2f}")
        
        # Impact of goals
        print(f"\n⚽ GOAL IMPACTS:")
        goal_impact = momentum_df[momentum_df['team_goals_5min'] > 0]['momentum_change'].mean()
        no_goal_impact = momentum_df[momentum_df['team_goals_5min'] == 0]['momentum_change'].mean()
        
        print(f"   With recent goal:    {goal_impact:.2f}")
        print(f"   Without recent goal: {no_goal_impact:.2f}")
        print(f"   Goal impact:         {goal_impact - no_goal_impact:.2f}")
        
        # Impact of set pieces
        print(f"\n🎯 SET PIECE IMPACTS:")
        corner_impact = momentum_df[momentum_df['team_corners_5min'] > 0]['momentum_change'].mean()
        no_corner_impact = momentum_df[momentum_df['team_corners_5min'] == 0]['momentum_change'].mean()
        
        if not pd.isna(corner_impact):
            print(f"   With recent corners: {corner_impact:.2f}")
            print(f"   Without corners:     {no_corner_impact:.2f}")
            print(f"   Corner impact:       {corner_impact - no_corner_impact:.2f}")
        
        return {
            'yellow_card_impact': yellow_impact - no_yellow_impact,
            'substitution_impact': sub_impact - no_sub_impact,
            'goal_impact': goal_impact - no_goal_impact
        }

def main():
    """Main function"""
    print("🎯 GAME EVENT MOMENTUM PATTERN ANALYSIS")
    print("=" * 80)
    
    analyzer = GameEventMomentumAnalyzer()
    
    # Load data
    if not analyzer.load_data():
        return
    
    # Analyze available events
    event_types = analyzer.analyze_game_events()
    
    # Create game event features
    momentum_df = analyzer.create_game_event_features(analyzer.events_df, sample_matches=25)
    
    if len(momentum_df) == 0:
        print("❌ No momentum data created")
        return
    
    # Analyze specific event impacts
    event_impacts = analyzer.analyze_specific_event_impacts(momentum_df)
    
    # Train model
    feature_importance, r2, mae = analyzer.train_game_event_model(momentum_df)
    
    print(f"\n🎯 GAME EVENT MOMENTUM PREDICTION RESULTS:")
    print(f"   R² Score: {r2:.3f}")
    print(f"   MAE: {mae:.3f}")
    
    print(f"\n💡 KEY GAME EVENT PATTERNS:")
    print(f"   • Yellow card impact: {event_impacts['yellow_card_impact']:.2f}")
    print(f"   • Substitution impact: {event_impacts['substitution_impact']:.2f}")
    print(f"   • Goal impact: {event_impacts['goal_impact']:.2f}")
    
    print(f"\n🔝 MOST PREDICTIVE GAME EVENTS:")
    for _, row in feature_importance.head(8).iterrows():
        print(f"   • {row['feature'].replace('_', ' ').title()}: {row['importance']:.3f}")
    
    print(f"\n✅ GAME EVENT MOMENTUM ANALYSIS COMPLETE")

if __name__ == "__main__":
    main() 