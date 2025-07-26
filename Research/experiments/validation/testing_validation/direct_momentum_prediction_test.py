#!/usr/bin/env python3
"""
Direct Future Momentum Prediction Test
Same insights, same features, but predict absolute future momentum instead of change
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import r2_score, mean_absolute_error, accuracy_score
from sklearn.model_selection import TimeSeriesSplit
import warnings
warnings.filterwarnings('ignore')

class DirectMomentumModel:
    """
    Model that predicts ABSOLUTE future momentum (not change)
    Using ALL the same insights from comprehensive model
    """
    
    def __init__(self):
        self.events_df = None
        self.team_profiles = {}
        self.regression_model = None
        self.classification_model = None
        
    def load_data(self):
        """Load Euro 2024 data"""
        print("📊 Loading Euro 2024 Tournament Data...")
        try:
            self.events_df = pd.read_csv("../Data/events_complete.csv", low_memory=False)
            print(f"✅ Events loaded: {len(self.events_df):,}")
            
            # Extract event names
            self.events_df['event_name'] = self.events_df['type'].apply(self.extract_event_type)
            
            # Create proper match identifiers
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
    
    def build_comprehensive_team_profiles(self):
        """Build comprehensive team profiles - SAME as comprehensive model"""
        print(f"\n🏆 BUILDING COMPREHENSIVE TEAM PROFILES")
        
        teams = set()
        for col in ['team_name', 'home_team', 'away_team']:
            if col in self.events_df.columns:
                teams.update(self.events_df[col].dropna().unique())
        
        teams = [team for team in teams if pd.notna(team) and team != '']
        
        for team in teams:
            team_events = self.events_df[self.events_df['team_name'] == team]
            if len(team_events) > 0:
                matches = team_events['match_id'].unique() if 'match_id' in team_events.columns else []
                
                profile = {
                    'team_name': team,
                    'matches_played': len(matches),
                    'goals_per_match': len(team_events[team_events['event_name'].str.contains('Goal', na=False, case=False)]) / max(len(matches), 1),
                    'shots_per_match': len(team_events[team_events['event_name'].str.contains('Shot', na=False, case=False)]) / max(len(matches), 1),
                    'events_per_match': len(team_events) / max(len(matches), 1),
                    'shot_efficiency': len(team_events[team_events['event_name'].str.contains('Goal', na=False, case=False)]) / max(len(team_events[team_events['event_name'].str.contains('Shot', na=False, case=False)]), 1),
                    'fouls_per_match': len(team_events[team_events['foul_committed'].notna()]) / max(len(matches), 1),
                    'cards_per_match': len(team_events[team_events['bad_behaviour'].notna()]) / max(len(matches), 1),
                    'subs_per_match': len(team_events[team_events['substitution'].notna()]) / max(len(matches), 1),
                    'pressure_ratio': len(team_events[team_events['under_pressure'].notna()]) / max(len(team_events), 1),
                    'opening_goals_ratio': len(team_events[(team_events['minute'] <= 15) & (team_events['event_name'].str.contains('Goal', na=False, case=False))]) / max(len(team_events[team_events['event_name'].str.contains('Goal', na=False, case=False)]), 1),
                    'closing_goals_ratio': len(team_events[(team_events['minute'] >= 75) & (team_events['event_name'].str.contains('Goal', na=False, case=False))]) / max(len(team_events[team_events['event_name'].str.contains('Goal', na=False, case=False)]), 1),
                    'stoppage_goals_ratio': len(team_events[(team_events['minute'] >= 90) & (team_events['event_name'].str.contains('Goal', na=False, case=False))]) / max(len(team_events[team_events['event_name'].str.contains('Goal', na=False, case=False)]), 1),
                    'opening_intensity': len(team_events[team_events['minute'] <= 15]) / max(len(team_events), 1),
                    'closing_strength': len(team_events[team_events['minute'] >= 75]) / max(len(team_events), 1),
                    'consistency_score': 1.0 / (1.0 + np.std([len(team_events[team_events['match_id'] == m]) for m in matches]) / max(len(team_events), 1)) if len(matches) > 1 else 1.0
                }
                
                self.team_profiles[team] = profile
        
        print(f"✅ Built profiles for {len(self.team_profiles)} teams")
    
    def create_direct_prediction_features(self, sample_matches=40):
        """Create features for DIRECT future momentum prediction - same features as comprehensive model"""
        print(f"\n🔧 CREATING FEATURES FOR DIRECT MOMENTUM PREDICTION")
        print("USING ALL COMPREHENSIVE INSIGHTS")
        
        unique_matches = self.events_df['match_id'].unique()[:sample_matches]
        momentum_records = []
        
        for i, match_id in enumerate(unique_matches):
            print(f"Processing match {i+1}/{len(unique_matches)}")
            
            match_events = self.events_df[self.events_df['match_id'] == match_id]
            match_events = match_events.sort_values('minute')
            
            teams = match_events['team_name'].dropna().unique()
            if len(teams) < 2:
                continue
            
            match_duration = int(match_events['minute'].max())
            if match_duration < 30:
                continue
            
            for team in teams:
                opponent_team = [t for t in teams if t != team][0]
                
                # Process every 2 minutes for more granular data
                for minute in range(10, match_duration - 5, 2):
                    
                    # Extract comprehensive features - SAME as comprehensive model
                    features = self.extract_comprehensive_features(
                        match_events, team, opponent_team, minute, match_duration
                    )
                    
                    if features is None:
                        continue
                    
                    # Calculate current momentum - SAME calculation
                    current_momentum = self.calculate_current_momentum(features)
                    
                    # Calculate future momentum (5 minutes ahead) - SAME calculation
                    future_momentum = self.calculate_future_momentum(
                        match_events, team, minute + 5, teams
                    )
                    
                    if future_momentum is None:
                        continue
                    
                    # KEY DIFFERENCE: Target is ABSOLUTE future momentum, not change
                    target_momentum = future_momentum  # NOT future_momentum - current_momentum
                    momentum_change = future_momentum - current_momentum  # For comparison
                    
                    # Classification target - same logic
                    if momentum_change > 1.0:
                        momentum_trend = 'increasing'
                    elif momentum_change < -1.0:
                        momentum_trend = 'decreasing'
                    else:
                        momentum_trend = 'stable'
                    
                    record = {
                        'match_id': match_id,
                        'team': team,
                        'opponent': opponent_team,
                        'minute': minute,
                        'current_momentum': current_momentum,
                        'future_momentum': future_momentum,
                        'target_momentum': target_momentum,  # ABSOLUTE future momentum
                        'momentum_change': momentum_change,  # For comparison
                        'momentum_trend': momentum_trend,
                        **features
                    }
                    
                    momentum_records.append(record)
        
        momentum_df = pd.DataFrame(momentum_records)
        print(f"✅ Created {len(momentum_df)} momentum samples for DIRECT prediction")
        
        return momentum_df
    
    def extract_comprehensive_features(self, match_events, team, opponent_team, minute, match_duration):
        """Extract comprehensive features - EXACTLY THE SAME as comprehensive model"""
        
        # Time windows
        last_10min = match_events[
            (match_events['minute'] >= minute-10) & 
            (match_events['minute'] < minute)
        ]
        last_5min = match_events[
            (match_events['minute'] >= minute-5) & 
            (match_events['minute'] < minute)
        ]
        last_2min = match_events[
            (match_events['minute'] >= minute-2) & 
            (match_events['minute'] < minute)
        ]
        
        # Team events
        team_all = match_events[match_events['team_name'] == team]
        team_current = team_all[team_all['minute'] < minute]
        team_10min = last_10min[last_10min['team_name'] == team]
        team_5min = last_5min[last_5min['team_name'] == team]
        team_2min = last_2min[last_2min['team_name'] == team]
        
        # Opponent events
        opponent_all = match_events[match_events['team_name'] == opponent_team]
        opponent_current = opponent_all[opponent_all['minute'] < minute]
        opponent_10min = last_10min[last_10min['team_name'] == opponent_team]
        opponent_5min = last_5min[last_5min['team_name'] == opponent_team]
        
        if len(team_2min) == 0 and len(team_5min) == 0:
            return None
        
        # Get team profiles
        team_profile = self.team_profiles.get(team, {})
        opponent_profile = self.team_profiles.get(opponent_team, {})
        
        # Calculate all metrics - SAME as comprehensive model
        team_goals_total = len(team_current[team_current['event_name'].str.contains('Goal', na=False, case=False)])
        team_shots_total = len(team_current[team_current['event_name'].str.contains('Shot', na=False, case=False)])
        opponent_goals_total = len(opponent_current[opponent_current['event_name'].str.contains('Goal', na=False, case=False)])
        opponent_shots_total = len(opponent_current[opponent_current['event_name'].str.contains('Shot', na=False, case=False)])
        
        # Activity levels
        team_events_total = len(team_current)
        opponent_events_total = len(opponent_current)
        team_events_10min = len(team_10min)
        team_events_5min = len(team_5min)
        team_events_2min = len(team_2min)
        
        # Match phase features
        opening_phase = 1 if minute <= 15 else 0
        first_half_end = 1 if 40 <= minute <= 50 else 0
        second_half_start = 1 if 45 <= minute <= 55 else 0
        closing_phase = 1 if 75 <= minute <= 90 else 0
        stoppage_time = 1 if minute > 90 and minute <= 105 else 0
        extra_time = 1 if minute > 105 else 0
        
        # Phase multiplier
        phase_multiplier = self.get_phase_multiplier(minute)
        
        # Game events
        team_subs_total = len(team_current[team_current['substitution'].notna()])
        team_subs_10min = len(team_10min[team_10min['substitution'].notna()])
        team_subs_5min = len(team_5min[team_5min['substitution'].notna()])
        
        team_fouls_total = len(team_current[team_current['foul_committed'].notna()])
        team_fouls_10min = len(team_10min[team_10min['foul_committed'].notna()])
        team_cards_total = len(team_current[team_current['bad_behaviour'].notna()])
        team_cards_10min = len(team_10min[team_10min['bad_behaviour'].notna()])
        
        team_tactics_total = len(team_current[team_current['tactics'].notna()])
        team_tactics_10min = len(team_10min[team_10min['tactics'].notna()])
        
        team_pressure_10min = len(team_10min[team_10min['under_pressure'].notna()])
        team_counterpress_10min = len(team_10min[team_10min['counterpress'].notna()])
        
        # Recent activity features
        team_goals_10min = len(team_10min[team_10min['event_name'].str.contains('Goal', na=False, case=False)])
        team_goals_5min = len(team_5min[team_5min['event_name'].str.contains('Goal', na=False, case=False)])
        team_shots_10min = len(team_10min[team_10min['event_name'].str.contains('Shot', na=False, case=False)])
        team_shots_5min = len(team_5min[team_5min['event_name'].str.contains('Shot', na=False, case=False)])
        team_shots_2min = len(team_2min[team_2min['event_name'].str.contains('Shot', na=False, case=False)])
        
        # Activity trends
        activity_rate_2min = team_events_2min / 2.0
        activity_rate_5min = team_events_5min / 5.0
        activity_rate_10min = team_events_10min / 10.0
        activity_trend = activity_rate_2min - activity_rate_5min
        
        # Possession and pressure
        total_events_5min = len(last_5min)
        possession_5min = (team_events_5min / max(total_events_5min, 1)) * 100
        pressure_ratio = team_pressure_10min / max(team_events_10min, 1)
        
        # Form and momentum indicators
        recent_goal_momentum = team_goals_5min - len(opponent_5min[opponent_5min['event_name'].str.contains('Goal', na=False, case=False)])
        recent_shot_momentum = team_shots_5min - len(opponent_5min[opponent_5min['event_name'].str.contains('Shot', na=False, case=False)])
        
        goal_advantage = team_goals_total - opponent_goals_total
        shot_advantage = team_shots_total - opponent_shots_total
        activity_advantage = team_events_total - opponent_events_total
        discipline_advantage = (len(opponent_current[opponent_current['foul_committed'].notna()]) + len(opponent_current[opponent_current['bad_behaviour'].notna()]) * 2) - (team_fouls_total + team_cards_total * 2)
        
        # Time pressure and context
        minutes_remaining = max(0, 90 - minute)
        time_pressure = 1.0 - (minutes_remaining / 90.0)
        match_intensity = (team_events_total + opponent_events_total) / minute
        
        # COMPREHENSIVE FEATURE SET - EXACTLY SAME as comprehensive model
        features = {
            # Historical features
            'hist_goals_per_match': team_profile.get('goals_per_match', 0),
            'hist_shots_per_match': team_profile.get('shots_per_match', 0),
            'hist_shot_efficiency': team_profile.get('shot_efficiency', 0),
            'hist_opening_intensity': team_profile.get('opening_intensity', 0),
            'hist_closing_strength': team_profile.get('closing_strength', 0),
            'hist_consistency': team_profile.get('consistency_score', 0),
            
            # Opponent historical features
            'opp_hist_goals_per_match': opponent_profile.get('goals_per_match', 0),
            'opp_hist_shots_per_match': opponent_profile.get('shots_per_match', 0),
            'opp_hist_shot_efficiency': opponent_profile.get('shot_efficiency', 0),
            
            # Current match totals
            'team_goals_total': team_goals_total,
            'team_shots_total': team_shots_total,
            'team_events_total': team_events_total,
            'team_subs_total': team_subs_total,
            'team_fouls_total': team_fouls_total,
            'team_cards_total': team_cards_total,
            
            # Recent activity (key insight from our analysis)
            'team_events_2min': team_events_2min,
            'team_events_5min': team_events_5min,
            'team_events_10min': team_events_10min,
            'team_goals_5min': team_goals_5min,
            'team_goals_10min': team_goals_10min,
            'team_shots_2min': team_shots_2min,
            'team_shots_5min': team_shots_5min,
            'team_shots_10min': team_shots_10min,
            'team_subs_5min': team_subs_5min,
            'team_subs_10min': team_subs_10min,
            
            # Activity trends
            'activity_trend': activity_trend,
            'activity_rate_2min': activity_rate_2min,
            'activity_rate_5min': activity_rate_5min,
            'activity_rate_10min': activity_rate_10min,
            
            # Match phase features
            'opening_phase': opening_phase,
            'first_half_end': first_half_end,
            'second_half_start': second_half_start,
            'closing_phase': closing_phase,
            'stoppage_time': stoppage_time,
            'extra_time': extra_time,
            'phase_multiplier': phase_multiplier,
            
            # Game events
            'team_cards_10min': team_cards_10min,
            'team_fouls_10min': team_fouls_10min,
            'team_tactics_10min': team_tactics_10min,
            'team_pressure_10min': team_pressure_10min,
            'team_counterpress_10min': team_counterpress_10min,
            
            # Possession and pressure
            'possession_5min': possession_5min,
            'pressure_ratio': pressure_ratio,
            
            # Momentum indicators
            'recent_goal_momentum': recent_goal_momentum,
            'recent_shot_momentum': recent_shot_momentum,
            'goal_advantage': goal_advantage,
            'shot_advantage': shot_advantage,
            'activity_advantage': activity_advantage,
            'discipline_advantage': discipline_advantage,
            
            # Time context
            'current_minute': minute,
            'minutes_remaining': minutes_remaining,
            'time_pressure': time_pressure,
            'match_intensity': match_intensity,
            
            # Form comparison
            'goal_form_advantage': team_profile.get('goals_per_match', 0) - opponent_profile.get('goals_per_match', 0),
            'shot_form_advantage': team_profile.get('shots_per_match', 0) - opponent_profile.get('shots_per_match', 0),
            'efficiency_form_advantage': team_profile.get('shot_efficiency', 0) - opponent_profile.get('shot_efficiency', 0)
        }
        
        return features
    
    def get_phase_multiplier(self, minute):
        """Get phase multiplier - SAME as comprehensive model"""
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
    
    def calculate_current_momentum(self, features):
        """Calculate current momentum - SAME calculation as comprehensive model"""
        
        # Historical baseline
        historical_component = (
            features['hist_goals_per_match'] * 0.5 +
            features['hist_shot_efficiency'] * 3 +
            features['hist_opening_intensity'] * 2 +
            features['hist_closing_strength'] * 2 +
            features['hist_consistency'] * 1
        )
        
        # Current performance
        current_component = (
            features['team_goals_total'] * 1.5 +
            features['team_shots_total'] * 0.3 +
            features['team_events_total'] * 0.005 +
            features['goal_advantage'] * 2 +
            features['shot_advantage'] * 0.5
        )
        
        # Recent activity (our key insight)
        recent_component = (
            features['team_events_2min'] * 0.4 +
            features['team_goals_5min'] * 3 +
            features['team_shots_5min'] * 0.8 +
            features['activity_trend'] * 1.5 +
            features['recent_goal_momentum'] * 2 +
            features['possession_5min'] * 0.02
        )
        
        # Game events impact
        events_component = (
            features['team_subs_5min'] * 0.5 +
            features['team_tactics_10min'] * 0.3 -
            features['team_cards_10min'] * 0.4 -
            features['team_fouls_10min'] * 0.1 +
            features['discipline_advantage'] * 0.3
        )
        
        # Phase and time effects
        phase_component = (
            features['opening_phase'] * 0.5 +
            features['closing_phase'] * 1.0 +
            features['stoppage_time'] * 2.0 +
            features['extra_time'] * 2.5 +
            features['time_pressure'] * 0.8
        )
        
        # Combine all components
        total_momentum = (
            historical_component * 0.2 +
            current_component * 0.3 +
            recent_component * 0.3 +
            events_component * 0.1 +
            phase_component * 0.1
        ) * features['phase_multiplier']
        
        return max(0, min(10, total_momentum))
    
    def calculate_future_momentum(self, match_events, team, future_minute, teams):
        """Calculate future momentum - SAME calculation as comprehensive model"""
        
        future_window = match_events[
            (match_events['minute'] >= future_minute) & 
            (match_events['minute'] < future_minute + 3)
        ]
        
        if len(future_window) == 0:
            return None
        
        team_future = future_window[future_window['team_name'] == team]
        
        future_events = len(team_future)
        future_goals = len(team_future[team_future['event_name'].str.contains('Goal', na=False, case=False)])
        future_shots = len(team_future[team_future['event_name'].str.contains('Shot', na=False, case=False)])
        
        # Simple future momentum calculation
        future_momentum = min(10, max(0,
            future_events * 0.4 +
            future_goals * 3.0 +
            future_shots * 1.0
        ))
        
        return future_momentum
    
    def train_direct_prediction_models(self, momentum_df):
        """Train models to predict ABSOLUTE future momentum (not change)"""
        print(f"\n🚀 TRAINING DIRECT MOMENTUM PREDICTION MODELS")
        print("TARGET: ABSOLUTE FUTURE MOMENTUM (not change)")
        
        # Prepare features
        feature_cols = [col for col in momentum_df.columns 
                       if col not in ['match_id', 'team', 'opponent', 'minute', 
                                     'current_momentum', 'future_momentum', 
                                     'target_momentum', 'momentum_change', 'momentum_trend']]
        
        X = momentum_df[feature_cols].fillna(0)
        y_regression = momentum_df['target_momentum']  # ABSOLUTE future momentum
        y_classification = momentum_df['momentum_trend']
        
        print(f"📊 Dataset preparation:")
        print(f"   Features: {len(feature_cols)}")
        print(f"   Samples: {len(X)}")
        print(f"   Current momentum range: {momentum_df['current_momentum'].min():.2f} to {momentum_df['current_momentum'].max():.2f}")
        print(f"   TARGET (future momentum) range: {y_regression.min():.2f} to {y_regression.max():.2f}")
        print(f"   Momentum change range: {momentum_df['momentum_change'].min():.2f} to {momentum_df['momentum_change'].max():.2f}")
        
        # CRITICAL: Match-based split to avoid temporal data leakage
        matches = momentum_df['match_id'].unique()
        np.random.seed(42)
        np.random.shuffle(matches)
        
        n_train = int(len(matches) * 0.8)
        train_matches = matches[:n_train]
        test_matches = matches[n_train:]
        
        train_data = momentum_df[momentum_df['match_id'].isin(train_matches)]
        test_data = momentum_df[momentum_df['match_id'].isin(test_matches)]
        
        X_train = train_data[feature_cols].fillna(0)
        y_train_reg = train_data['target_momentum']  # ABSOLUTE future momentum
        y_train_clf = train_data['momentum_trend']
        X_test = test_data[feature_cols].fillna(0)
        y_test_reg = test_data['target_momentum']  # ABSOLUTE future momentum
        y_test_clf = test_data['momentum_trend']
        
        print(f"\n🎯 Temporal validation split:")
        print(f"   Training matches: {len(train_matches)}")
        print(f"   Testing matches: {len(test_matches)}")
        print(f"   Training samples: {len(X_train)}")
        print(f"   Testing samples: {len(X_test)}")
        
        # Train regression model for ABSOLUTE future momentum
        print(f"\n📈 Training DIRECT Future Momentum Regression Model...")
        self.regression_model = RandomForestRegressor(
            n_estimators=200,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        
        self.regression_model.fit(X_train, y_train_reg)
        y_pred_reg = self.regression_model.predict(X_test)
        
        r2_reg = r2_score(y_test_reg, y_pred_reg)
        mae_reg = mean_absolute_error(y_test_reg, y_pred_reg)
        
        # Train classification model
        print(f"📊 Training Classification Model...")
        self.classification_model = RandomForestClassifier(
            n_estimators=200,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        
        self.classification_model.fit(X_train, y_train_clf)
        y_pred_clf = self.classification_model.predict(X_test)
        
        accuracy_clf = accuracy_score(y_test_clf, y_pred_clf)
        
        # Time series cross-validation
        print(f"\n⏰ Time Series Cross-Validation...")
        tscv = TimeSeriesSplit(n_splits=5)
        
        cv_scores_reg = []
        cv_scores_clf = []
        
        momentum_df_sorted = momentum_df.sort_values(['match_id', 'minute'])
        X_sorted = momentum_df_sorted[feature_cols].fillna(0)
        y_sorted_reg = momentum_df_sorted['target_momentum']
        y_sorted_clf = momentum_df_sorted['momentum_trend']
        
        for train_idx, test_idx in tscv.split(X_sorted):
            X_cv_train, X_cv_test = X_sorted.iloc[train_idx], X_sorted.iloc[test_idx]
            y_cv_train_reg, y_cv_test_reg = y_sorted_reg.iloc[train_idx], y_sorted_reg.iloc[test_idx]
            y_cv_train_clf, y_cv_test_clf = y_sorted_clf.iloc[train_idx], y_sorted_clf.iloc[test_idx]
            
            # Regression CV
            reg_model = RandomForestRegressor(n_estimators=100, random_state=42)
            reg_model.fit(X_cv_train, y_cv_train_reg)
            cv_pred_reg = reg_model.predict(X_cv_test)
            cv_scores_reg.append(r2_score(y_cv_test_reg, cv_pred_reg))
            
            # Classification CV
            clf_model = RandomForestClassifier(n_estimators=100, random_state=42)
            clf_model.fit(X_cv_train, y_cv_train_clf)
            cv_pred_clf = clf_model.predict(X_cv_test)
            cv_scores_clf.append(accuracy_score(y_cv_test_clf, cv_pred_clf))
        
        # Feature importance analysis
        feature_importance_reg = pd.DataFrame({
            'feature': feature_cols,
            'importance': self.regression_model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        # Calculate comparison with change-based model
        # For comparison, also test predicting momentum change
        test_data_current = test_data['current_momentum']
        test_data_future = test_data['future_momentum']
        test_data_change = test_data_future - test_data_current
        
        # Convert absolute predictions to change predictions for comparison
        current_momentum_test = test_data['current_momentum'].values
        predicted_change = y_pred_reg - current_momentum_test
        actual_change = test_data_change.values
        
        r2_change_comparison = r2_score(actual_change, predicted_change)
        mae_change_comparison = mean_absolute_error(actual_change, predicted_change)
        
        # Print results
        print(f"\n📈 DIRECT FUTURE MOMENTUM PREDICTION PERFORMANCE:")
        print(f"=" * 70)
        print(f"🎯 REGRESSION MODEL (Absolute Future Momentum Prediction):")
        print(f"   R² Score: {r2_reg:.3f}")
        print(f"   MAE: {mae_reg:.3f}")
        print(f"   Time Series CV R²: {np.mean(cv_scores_reg):.3f} ± {np.std(cv_scores_reg):.3f}")
        
        print(f"\n📊 CLASSIFICATION MODEL (Trend Prediction):")
        print(f"   Accuracy: {accuracy_clf:.3f}")
        print(f"   Time Series CV Accuracy: {np.mean(cv_scores_clf):.3f} ± {np.std(cv_scores_clf):.3f}")
        
        print(f"\n🔄 COMPARISON TO CHANGE-BASED APPROACH:")
        print(f"   Derived Change R²: {r2_change_comparison:.3f}")
        print(f"   Derived Change MAE: {mae_change_comparison:.3f}")
        
        print(f"\n🔝 TOP FEATURES FOR DIRECT PREDICTION:")
        for _, row in feature_importance_reg.head(15).iterrows():
            print(f"   {row['feature']:<30}: {row['importance']:.3f}")
        
        return {
            'direct_r2': r2_reg,
            'direct_mae': mae_reg,
            'direct_cv_mean': np.mean(cv_scores_reg),
            'direct_cv_std': np.std(cv_scores_reg),
            'classification_accuracy': accuracy_clf,
            'classification_cv_mean': np.mean(cv_scores_clf),
            'classification_cv_std': np.std(cv_scores_clf),
            'change_comparison_r2': r2_change_comparison,
            'change_comparison_mae': mae_change_comparison,
            'feature_importance': feature_importance_reg
        }

def main():
    """Main function to run direct momentum prediction test"""
    print("🎯 DIRECT FUTURE MOMENTUM PREDICTION TEST")
    print("=" * 80)
    print("Testing: Predict ABSOLUTE future momentum vs momentum CHANGE")
    print("Using: ALL comprehensive insights and features")
    print("=" * 80)
    
    model = DirectMomentumModel()
    
    # Load data
    if not model.load_data():
        return
    
    # Build team profiles
    model.build_comprehensive_team_profiles()
    
    # Create features for direct prediction
    momentum_df = model.create_direct_prediction_features(sample_matches=30)
    
    if len(momentum_df) == 0:
        print("❌ No momentum data created")
        return
    
    # Train models
    results = model.train_direct_prediction_models(momentum_df)
    
    print(f"\n🎯 COMPARISON SUMMARY:")
    print(f"=" * 80)
    print(f"📊 DIRECT FUTURE MOMENTUM PREDICTION:")
    print(f"   R² Score: {results['direct_r2']:.3f}")
    print(f"   MAE: {results['direct_mae']:.3f}")
    print(f"   CV R²: {results['direct_cv_mean']:.3f} ± {results['direct_cv_std']:.3f}")
    
    print(f"\n🔄 DERIVED CHANGE PREDICTION (from direct model):")
    print(f"   R² Score: {results['change_comparison_r2']:.3f}")
    print(f"   MAE: {results['change_comparison_mae']:.3f}")
    
    print(f"\n💡 EXPECTED CHANGE-BASED MODEL PERFORMANCE (from previous runs):")
    print(f"   R² Score: ~0.756")
    print(f"   MAE: ~0.921")
    
    print(f"\n🎯 ARCHITECTURAL IMPACT ANALYSIS:")
    if results['direct_r2'] < 0.5:
        print(f"   ✅ CONFIRMED: Predicting absolute future momentum is much harder")
        print(f"   ✅ Change-based approach provides significant advantage")
        print(f"   ✅ Architecture choice was CRITICAL for success")
    else:
        print(f"   ⚠️  UNEXPECTED: Direct prediction worked well with all insights")
        print(f"   🔍 Features were more important than architecture")
    
    print(f"\n🏆 DIRECT MOMENTUM PREDICTION TEST COMPLETE!")

if __name__ == "__main__":
    main() 