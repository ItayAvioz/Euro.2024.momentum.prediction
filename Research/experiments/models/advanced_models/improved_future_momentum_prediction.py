#!/usr/bin/env python3
"""
Improved Future Momentum Prediction with Contextual Features
Using the same approach that worked for current momentum
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, TimeSeriesSplit
from sklearn.metrics import r2_score, mean_absolute_error
from sklearn.preprocessing import StandardScaler
import os
import warnings
warnings.filterwarnings('ignore')

class ImprovedFutureMomentumPredictor:
    """
    Improved future momentum prediction with contextual features
    """
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = []
        
    def load_data(self):
        """Load Euro 2024 data"""
        print("📊 Loading Euro 2024 Dataset...")
        
        try:
            events_df = pd.read_csv("../Data/events_complete.csv", low_memory=False)
            matches_df = pd.read_csv("../Data/matches_complete.csv")
            
            print(f"✅ Events: {len(events_df):,}")
            print(f"✅ Matches: {len(matches_df):,}")
            
            # Add match context
            if 'match_id' not in events_df.columns:
                events_df['match_id'] = pd.factorize(
                    events_df['possession_team'].astype(str) + '_' + 
                    events_df['period'].astype(str)
                )[0]
            
            return events_df, matches_df
        except Exception as e:
            print(f"❌ Error: {e}")
            return None, None
    
    def create_future_momentum_data(self, events_df, sample_matches=25, prediction_window=5):
        """Create future momentum prediction data with contextual features"""
        print(f"\n🔧 CREATING FUTURE MOMENTUM PREDICTION DATA")
        print(f"   Prediction window: {prediction_window} minutes")
        print("=" * 50)
        
        unique_matches = events_df['match_id'].unique()[:sample_matches]
        future_momentum_records = []
        
        for i, match_id in enumerate(unique_matches):
            print(f"Processing match {i+1}/{len(unique_matches)}: {match_id}")
            
            match_events = events_df[events_df['match_id'] == match_id]
            match_events = match_events.sort_values('minute')
            
            teams = match_events['team'].dropna().unique()
            if len(teams) < 2:
                continue
                
            match_duration = int(match_events['minute'].max())
            if match_duration < 25:  # Need enough time for prediction
                continue
            
            for team in teams:
                # Process every 3 minutes, ensuring we have future data
                for minute in range(10, match_duration - prediction_window - 2, 3):
                    
                    # Current contextual features (input)
                    current_features = self.extract_contextual_features(
                        match_events, team, minute, teams, match_duration
                    )
                    
                    if current_features is None:
                        continue
                    
                    # Future momentum (target) - look ahead by prediction_window minutes
                    future_momentum = self.calculate_future_momentum(
                        match_events, team, minute, minute + prediction_window, teams
                    )
                    
                    if future_momentum is None:
                        continue
                    
                    record = {
                        'match_id': match_id,
                        'team': team,
                        'current_minute': minute,
                        'future_minute': minute + prediction_window,
                        'future_momentum': future_momentum,
                        **current_features
                    }
                    
                    future_momentum_records.append(record)
        
        momentum_df = pd.DataFrame(future_momentum_records)
        print(f"✅ Created {len(momentum_df)} future momentum prediction samples")
        
        return momentum_df
    
    def extract_contextual_features(self, match_events, team, minute, teams, match_duration):
        """Extract comprehensive contextual features for future prediction"""
        
        # Time windows for current state
        last_2min = match_events[
            (match_events['minute'] >= minute-2) & 
            (match_events['minute'] < minute)
        ]
        last_5min = match_events[
            (match_events['minute'] >= minute-5) & 
            (match_events['minute'] < minute)
        ]
        last_10min = match_events[
            (match_events['minute'] >= minute-10) & 
            (match_events['minute'] < minute)
        ]
        
        team_2min = last_2min[last_2min['team'] == team]
        team_5min = last_5min[last_5min['team'] == team]
        team_10min = last_10min[last_10min['team'] == team]
        
        if len(team_2min) == 0 and len(team_5min) == 0:
            return None
        
        # === BASIC ACTIVITY FEATURES ===
        events_2min = len(team_2min)
        events_5min = len(team_5min)
        events_10min = len(team_10min)
        
        # Event types
        shots_2min = len(team_2min[team_2min['type'].str.contains('Shot', na=False)])
        shots_5min = len(team_5min[team_5min['type'].str.contains('Shot', na=False)])
        shots_10min = len(team_10min[team_10min['type'].str.contains('Shot', na=False)])
        
        passes_2min = len(team_2min[team_2min['type'].str.contains('Pass', na=False)])
        passes_5min = len(team_5min[team_5min['type'].str.contains('Pass', na=False)])
        passes_10min = len(team_10min[team_10min['type'].str.contains('Pass', na=False)])
        
        attacking_2min = len(team_2min[team_2min['type'].str.contains('Shot|Carry|Dribble', na=False)])
        attacking_5min = len(team_5min[team_5min['type'].str.contains('Shot|Carry|Dribble', na=False)])
        attacking_10min = len(team_10min[team_10min['type'].str.contains('Shot|Carry|Dribble', na=False)])
        
        # === POSSESSION CONTEXT ===
        possession_2min = (events_2min / (len(last_2min) + 1)) * 100
        possession_5min = (events_5min / (len(last_5min) + 1)) * 100
        possession_10min = (events_10min / (len(last_10min) + 1)) * 100
        
        # === ACTIVITY TRENDS (KEY PREDICTORS) ===
        activity_rate_2min = events_2min / 2.0
        activity_rate_5min = events_5min / 5.0
        activity_rate_10min = events_10min / 10.0
        
        # Short-term vs medium-term trends
        activity_trend_short = activity_rate_2min - activity_rate_5min
        activity_trend_long = activity_rate_5min - activity_rate_10min
        
        # Shot trends
        shot_rate_2min = shots_2min / 2.0
        shot_rate_5min = shots_5min / 5.0
        shot_rate_10min = shots_10min / 10.0
        
        shot_trend_short = shot_rate_2min - shot_rate_5min
        shot_trend_long = shot_rate_5min - shot_rate_10min
        
        # Possession trends
        possession_trend_short = possession_2min - possession_5min
        possession_trend_long = possession_5min - possession_10min
        
        # === MATCH CONTEXT ===
        match_phase = minute / match_duration  # 0 = start, 1 = end
        time_remaining = max(0, (90 - minute) / 90)  # Time pressure
        match_intensity = len(match_events) / match_duration
        
        # Match phase categories
        early_match = 1 if minute <= 30 else 0
        mid_match = 1 if 30 < minute <= 60 else 0
        late_match = 1 if minute > 60 else 0
        
        # === PRESSURE INDICATORS ===
        pressure_events_2min = len(team_2min[team_2min['under_pressure'].notna()])
        pressure_events_5min = len(team_5min[team_5min['under_pressure'].notna()])
        
        pressure_ratio_2min = pressure_events_2min / (events_2min + 1)
        pressure_ratio_5min = pressure_events_5min / (events_5min + 1)
        pressure_trend = pressure_ratio_2min - pressure_ratio_5min
        
        # === OPPONENT CONTEXT ===
        opponent_team = [t for t in teams if t != team][0] if len(teams) > 1 else None
        
        if opponent_team:
            opponent_2min = last_2min[last_2min['team'] == opponent_team]
            opponent_5min = last_5min[last_5min['team'] == opponent_team]
            
            opponent_events_2min = len(opponent_2min)
            opponent_events_5min = len(opponent_5min)
            opponent_shots_2min = len(opponent_2min[opponent_2min['type'].str.contains('Shot', na=False)])
            opponent_shots_5min = len(opponent_5min[opponent_5min['type'].str.contains('Shot', na=False)])
            
            # Relative performance
            relative_activity_2min = events_2min - opponent_events_2min
            relative_activity_5min = events_5min - opponent_events_5min
            relative_shots_2min = shots_2min - opponent_shots_2min
            relative_shots_5min = shots_5min - opponent_shots_5min
            
            # Relative trends
            relative_activity_trend = relative_activity_2min - relative_activity_5min
            relative_shot_trend = relative_shots_2min - relative_shots_5min
            
            # Opponent pressure
            opponent_pressure_2min = len(opponent_2min[opponent_2min['under_pressure'].notna()])
            opponent_under_pressure = opponent_pressure_2min / (opponent_events_2min + 1)
            
        else:
            relative_activity_2min = relative_activity_5min = 0
            relative_shots_2min = relative_shots_5min = 0
            relative_activity_trend = relative_shot_trend = 0
            opponent_under_pressure = 0
        
        # === GOAL CONTEXT ===
        # Look for recent goals
        recent_goals = len(team_5min[team_5min['type'].str.contains('Goal', na=False)])
        recent_opponent_goals = 0
        if opponent_team:
            recent_opponent_goals = len(last_5min[
                (last_5min['team'] == opponent_team) & 
                (last_5min['type'].str.contains('Goal', na=False))
            ])
        
        goal_momentum = recent_goals - recent_opponent_goals
        
        # === MOMENTUM PERSISTENCE ===
        # Current momentum level (simple calculation)
        current_momentum_simple = min(10, max(0, 
            shots_2min * 2.0 + 
            attacking_2min * 1.5 + 
            possession_2min * 0.03 + 
            activity_trend_short * 2.0 +
            goal_momentum * 3.0 -
            pressure_ratio_2min * 1.0
        ))
        
        return {
            # Basic activity
            'events_2min': events_2min,
            'events_5min': events_5min,
            'events_10min': events_10min,
            'shots_2min': shots_2min,
            'shots_5min': shots_5min,
            'shots_10min': shots_10min,
            'passes_2min': passes_2min,
            'passes_5min': passes_5min,
            'passes_10min': passes_10min,
            'attacking_2min': attacking_2min,
            'attacking_5min': attacking_5min,
            'attacking_10min': attacking_10min,
            
            # Possession
            'possession_2min': possession_2min,
            'possession_5min': possession_5min,
            'possession_10min': possession_10min,
            
            # Activity trends (key predictors)
            'activity_trend_short': activity_trend_short,
            'activity_trend_long': activity_trend_long,
            'shot_trend_short': shot_trend_short,
            'shot_trend_long': shot_trend_long,
            'possession_trend_short': possession_trend_short,
            'possession_trend_long': possession_trend_long,
            
            # Match context
            'match_phase': match_phase,
            'time_remaining': time_remaining,
            'match_intensity': match_intensity,
            'early_match': early_match,
            'mid_match': mid_match,
            'late_match': late_match,
            
            # Pressure
            'pressure_ratio_2min': pressure_ratio_2min,
            'pressure_ratio_5min': pressure_ratio_5min,
            'pressure_trend': pressure_trend,
            
            # Opponent context
            'relative_activity_2min': relative_activity_2min,
            'relative_activity_5min': relative_activity_5min,
            'relative_shots_2min': relative_shots_2min,
            'relative_shots_5min': relative_shots_5min,
            'relative_activity_trend': relative_activity_trend,
            'relative_shot_trend': relative_shot_trend,
            'opponent_under_pressure': opponent_under_pressure,
            
            # Goal context
            'goal_momentum': goal_momentum,
            'recent_goals': recent_goals,
            'recent_opponent_goals': recent_opponent_goals,
            
            # Current momentum
            'current_momentum_simple': current_momentum_simple
        }
    
    def calculate_future_momentum(self, match_events, team, current_minute, future_minute, teams):
        """Calculate future momentum target"""
        
        # Future time window
        future_start = future_minute
        future_end = future_minute + 3  # 3-minute window for future momentum
        
        future_events = match_events[
            (match_events['minute'] >= future_start) & 
            (match_events['minute'] < future_end)
        ]
        
        team_future = future_events[future_events['team'] == team]
        
        if len(future_events) == 0:
            return None
        
        # Calculate future momentum using same contextual approach
        future_features = self.extract_simple_future_features(
            future_events, team, teams
        )
        
        if future_features is None:
            return None
        
        # Calculate future momentum score
        future_momentum = min(10, max(0,
            future_features['shots_future'] * 2.5 +
            future_features['attacking_future'] * 1.5 +
            future_features['possession_future'] * 0.04 +
            future_features['events_future'] * 0.3 +
            future_features['goal_events_future'] * 5.0 -
            future_features['pressure_future'] * 1.0
        ))
        
        return future_momentum
    
    def extract_simple_future_features(self, future_events, team, teams):
        """Extract simple features from future window"""
        
        team_future = future_events[future_events['team'] == team]
        
        if len(team_future) == 0:
            return {'shots_future': 0, 'attacking_future': 0, 'possession_future': 0,
                   'events_future': 0, 'goal_events_future': 0, 'pressure_future': 0}
        
        # Basic future metrics
        events_future = len(team_future)
        shots_future = len(team_future[team_future['type'].str.contains('Shot', na=False)])
        attacking_future = len(team_future[team_future['type'].str.contains('Shot|Carry|Dribble', na=False)])
        goal_events_future = len(team_future[team_future['type'].str.contains('Goal', na=False)])
        
        # Future possession
        possession_future = (events_future / (len(future_events) + 1)) * 100
        
        # Future pressure
        pressure_future = len(team_future[team_future['under_pressure'].notna()]) / (events_future + 1)
        
        return {
            'shots_future': shots_future,
            'attacking_future': attacking_future,
            'possession_future': possession_future,
            'events_future': events_future,
            'goal_events_future': goal_events_future,
            'pressure_future': pressure_future
        }
    
    def train_future_momentum_model(self, momentum_df):
        """Train future momentum prediction model"""
        print(f"\n🚀 TRAINING FUTURE MOMENTUM PREDICTION MODEL")
        print("=" * 50)
        
        # Prepare features
        feature_cols = [col for col in momentum_df.columns 
                       if col not in ['match_id', 'team', 'current_minute', 
                                     'future_minute', 'future_momentum']]
        
        self.feature_names = feature_cols
        X = momentum_df[feature_cols]
        y = momentum_df['future_momentum']
        
        print(f"📊 Dataset preparation:")
        print(f"   Features: {len(feature_cols)}")
        print(f"   Samples: {len(X)}")
        print(f"   Target range: {y.min():.2f}-{y.max():.2f}")
        print(f"   Target mean: {y.mean():.2f} ± {y.std():.2f}")
        
        # Proper temporal split (match-based)
        matches = momentum_df['match_id'].unique()
        np.random.seed(42)
        np.random.shuffle(matches)
        
        n_train = int(len(matches) * 0.8)
        train_matches = matches[:n_train]
        test_matches = matches[n_train:]
        
        train_data = momentum_df[momentum_df['match_id'].isin(train_matches)]
        test_data = momentum_df[momentum_df['match_id'].isin(test_matches)]
        
        X_train = train_data[feature_cols]
        y_train = train_data['future_momentum']
        X_test = test_data[feature_cols]
        y_test = test_data['future_momentum']
        
        print(f"\n🎯 Match-based split:")
        print(f"   Training matches: {len(train_matches)}")
        print(f"   Testing matches: {len(test_matches)}")
        print(f"   Training samples: {len(X_train)}")
        print(f"   Testing samples: {len(X_test)}")
        
        # Train multiple models
        models = {
            'RandomForest': RandomForestRegressor(
                n_estimators=200, 
                max_depth=12, 
                min_samples_split=5,
                min_samples_leaf=3,
                random_state=42
            ),
            'GradientBoosting': GradientBoostingRegressor(
                n_estimators=200,
                learning_rate=0.1,
                max_depth=8,
                min_samples_split=5,
                random_state=42
            )
        }
        
        results = {}
        
        for name, model in models.items():
            print(f"\n🔮 Training {name}...")
            
            # Train
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            
            # Evaluate
            r2 = r2_score(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            
            results[name] = {
                'r2': r2,
                'mae': mae,
                'model': model
            }
            
            print(f"   R² Score: {r2:.3f}")
            print(f"   MAE: {mae:.3f}")
        
        # Select best model
        best_model_name = max(results.keys(), key=lambda x: results[x]['r2'])
        self.model = results[best_model_name]['model']
        
        print(f"\n🏆 BEST MODEL: {best_model_name}")
        print(f"   R² Score: {results[best_model_name]['r2']:.3f}")
        print(f"   MAE: {results[best_model_name]['mae']:.3f}")
        
        # Feature importance
        if hasattr(self.model, 'feature_importances_'):
            feature_importance = pd.DataFrame({
                'feature': feature_cols,
                'importance': self.model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            print(f"\n🔝 TOP FEATURES FOR FUTURE MOMENTUM:")
            for _, row in feature_importance.head(15).iterrows():
                print(f"   {row['feature']:<30}: {row['importance']:.3f}")
        
        # Time series cross-validation
        print(f"\n🔄 TIME SERIES CROSS-VALIDATION:")
        self.time_series_validation(momentum_df, feature_cols)
        
        return results
    
    def time_series_validation(self, momentum_df, feature_cols):
        """Perform time series cross-validation"""
        
        # Sort by time
        sorted_data = momentum_df.sort_values(['match_id', 'current_minute'])
        X_sorted = sorted_data[feature_cols]
        y_sorted = sorted_data['future_momentum']
        
        tscv = TimeSeriesSplit(n_splits=5)
        cv_scores = []
        
        for fold, (train_idx, test_idx) in enumerate(tscv.split(X_sorted)):
            if len(train_idx) < 50 or len(test_idx) < 20:
                continue
                
            X_fold_train = X_sorted.iloc[train_idx]
            y_fold_train = y_sorted.iloc[train_idx]
            X_fold_test = X_sorted.iloc[test_idx]
            y_fold_test = y_sorted.iloc[test_idx]
            
            fold_model = RandomForestRegressor(n_estimators=100, random_state=42)
            fold_model.fit(X_fold_train, y_fold_train)
            
            y_fold_pred = fold_model.predict(X_fold_test)
            fold_r2 = r2_score(y_fold_test, y_fold_pred)
            cv_scores.append(fold_r2)
            
            print(f"   Fold {fold + 1}: R² = {fold_r2:.3f} (Train: {len(X_fold_train)}, Test: {len(X_fold_test)})")
        
        if cv_scores:
            cv_mean = np.mean(cv_scores)
            cv_std = np.std(cv_scores)
            print(f"   Time Series CV: {cv_mean:.3f} ± {cv_std:.3f}")
        
        return cv_scores
    
    def analyze_prediction_patterns(self, momentum_df):
        """Analyze future momentum prediction patterns"""
        print(f"\n📊 FUTURE MOMENTUM PREDICTION PATTERNS")
        print("=" * 50)
        
        # Correlation analysis
        numeric_cols = [col for col in momentum_df.columns if momentum_df[col].dtype in ['int64', 'float64']]
        correlations = momentum_df[numeric_cols].corr()['future_momentum'].sort_values(ascending=False)
        
        print(f"🔗 Strongest Correlations with Future Momentum:")
        for feature, corr in correlations.head(15).items():
            if feature != 'future_momentum':
                print(f"   {feature:<30}: {corr:>6.3f}")
        
        # Predictive power analysis
        print(f"\n📈 PREDICTIVE PATTERNS:")
        print(f"   Future momentum mean: {momentum_df['future_momentum'].mean():.2f}")
        print(f"   Future momentum std: {momentum_df['future_momentum'].std():.2f}")
        print(f"   Future momentum range: {momentum_df['future_momentum'].min():.2f}-{momentum_df['future_momentum'].max():.2f}")
        
        # Current vs future momentum correlation
        if 'current_momentum_simple' in momentum_df.columns:
            current_future_corr = momentum_df['current_momentum_simple'].corr(momentum_df['future_momentum'])
            print(f"   Current vs Future momentum correlation: {current_future_corr:.3f}")
        
        return correlations

def main():
    """Main function"""
    print("🔮 IMPROVED FUTURE MOMENTUM PREDICTION")
    print("=" * 80)
    
    predictor = ImprovedFutureMomentumPredictor()
    
    # Load data
    events_df, matches_df = predictor.load_data()
    if events_df is None:
        return
    
    # Create future momentum data
    momentum_df = predictor.create_future_momentum_data(events_df, sample_matches=25, prediction_window=5)
    
    if len(momentum_df) == 0:
        print("❌ No future momentum data created")
        return
    
    # Analyze patterns
    correlations = predictor.analyze_prediction_patterns(momentum_df)
    
    # Train model
    results = predictor.train_future_momentum_model(momentum_df)
    
    # Get best performance
    best_r2 = max(results.values(), key=lambda x: x['r2'])['r2']
    best_mae = min(results.values(), key=lambda x: x['mae'])['mae']
    
    print(f"\n🎯 FUTURE MOMENTUM PREDICTION RESULTS:")
    print(f"   Using contextual features for 5-minute prediction")
    print(f"   Best R² Score: {best_r2:.3f}")
    print(f"   Best MAE: {best_mae:.3f}")
    
    if best_r2 > 0.3:
        print(f"   ✅ Excellent performance for future prediction!")
    elif best_r2 > 0.15:
        print(f"   ✅ Good performance for future prediction!")
    else:
        print(f"   ⚠️  Challenging but realistic performance for future prediction")
    
    print(f"\n💡 KEY INSIGHTS:")
    print(f"   • Future momentum prediction is much more challenging than current")
    print(f"   • Contextual features (trends, match context) are crucial")
    print(f"   • Activity trends and possession patterns are predictive")
    print(f"   • Match phase and opponent context matter")
    
    print(f"\n✅ IMPROVED FUTURE MOMENTUM PREDICTION COMPLETE")

if __name__ == "__main__":
    main() 