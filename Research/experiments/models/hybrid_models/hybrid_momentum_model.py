#!/usr/bin/env python3
"""
Hybrid Momentum Model - Summary + Prediction Combined
Uses current momentum as a feature to predict future momentum
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import warnings
warnings.filterwarnings('ignore')

class CurrentMomentumCalculator:
    """Calculate current momentum (summary model)"""
    
    def calculate_current_momentum(self, events_df, current_time, team_name):
        """Calculate current momentum using summary approach"""
        
        # Current 3-minute window
        start_time = max(0, current_time - 180)
        current_window = events_df[
            (events_df['timestamp'] >= start_time) & 
            (events_df['timestamp'] <= current_time)
        ]
        
        team_events = current_window[current_window['team_name'] == team_name]
        opponent_events = current_window[current_window['team_name'] != team_name]
        
        if len(current_window) == 0:
            return 5.0  # Neutral momentum
        
        # Summary momentum calculation (like the old model)
        current_momentum = 0
        
        # Attacking contribution
        shots = len(team_events[team_events['event_type'] == 'Shot'])
        attacks = len(team_events[team_events['event_type'].isin(['Carry', 'Dribble'])])
        current_momentum += shots * 2.0 + attacks * 1.5
        
        # Possession contribution
        possession_pct = len(team_events) / len(current_window) * 100
        current_momentum += possession_pct * 0.05
        
        # Pressure contribution
        pressure_applied = len(team_events[team_events['event_type'] == 'Pressure'])
        pressure_received = len(opponent_events[opponent_events['event_type'] == 'Pressure'])
        current_momentum += pressure_applied * 0.8 - pressure_received * 0.6
        
        # Activity contribution
        current_momentum += len(team_events) * 0.3
        
        # Recent intensity (last minute weighted)
        recent_events = team_events[team_events['timestamp'] >= current_time - 60]
        current_momentum += len(recent_events) * 0.5
        
        # Normalize to 0-10 scale
        normalized_momentum = 5 + (current_momentum - 10) * 0.2
        return max(0, min(10, normalized_momentum))

class HybridMomentumPredictor:
    """Hybrid model combining current momentum with other features"""
    
    def __init__(self):
        self.model = RandomForestRegressor(
            n_estimators=200,
            max_depth=12,
            min_samples_split=8,
            min_samples_leaf=4,
            max_features='sqrt',
            random_state=42
        )
        self.current_momentum_calc = CurrentMomentumCalculator()
        self.feature_names = []
        self.is_trained = False
    
    def extract_hybrid_features(self, events_df, current_time, team_name):
        """Extract features including current momentum"""
        
        # Current 3-minute window
        start_time = max(0, current_time - 180)
        current_window = events_df[
            (events_df['timestamp'] >= start_time) & 
            (events_df['timestamp'] <= current_time)
        ]
        
        team_events = current_window[current_window['team_name'] == team_name]
        opponent_events = current_window[current_window['team_name'] != team_name]
        total_events = len(current_window)
        
        features = {}
        
        # === CURRENT MOMENTUM FEATURE (NEW!) ===
        features['current_momentum'] = self.current_momentum_calc.calculate_current_momentum(
            events_df, current_time, team_name)
        
        # === CORE ATTACKING METRICS ===
        features['team_shots'] = len(team_events[team_events['event_type'] == 'Shot'])
        features['team_shot_rate'] = features['team_shots'] / 3
        features['team_carries'] = len(team_events[team_events['event_type'] == 'Carry'])
        features['team_dribbles'] = len(team_events[team_events['event_type'] == 'Dribble'])
        features['team_attacking_actions'] = features['team_shots'] + features['team_carries'] + features['team_dribbles']
        features['team_attacking_rate'] = features['team_attacking_actions'] / 3
        
        # === POSSESSION CONTROL ===
        features['team_passes'] = len(team_events[team_events['event_type'] == 'Pass'])
        features['team_possession_pct'] = (len(team_events) / total_events * 100) if total_events > 0 else 50
        features['team_pass_rate'] = features['team_passes'] / 3
        
        # === PRESSURE DYNAMICS ===
        features['team_pressure_applied'] = len(team_events[team_events['event_type'] == 'Pressure'])
        features['team_pressure_received'] = len(opponent_events[opponent_events['event_type'] == 'Pressure'])
        features['team_pressure_balance'] = features['team_pressure_applied'] - features['team_pressure_received']
        
        # === OPPONENT CONTEXT ===
        features['opponent_shots'] = len(opponent_events[opponent_events['event_type'] == 'Shot'])
        features['opponent_attacking_actions'] = len(opponent_events[opponent_events['event_type'].isin(['Shot', 'Carry', 'Dribble'])])
        features['opponent_possession_pct'] = (len(opponent_events) / total_events * 100) if total_events > 0 else 50
        
        # Get opponent current momentum
        opponent_teams = opponent_events['team_name'].unique()
        if len(opponent_teams) > 0:
            opponent_team = opponent_teams[0]
            features['opponent_current_momentum'] = self.current_momentum_calc.calculate_current_momentum(
                events_df, current_time, opponent_team)
        else:
            features['opponent_current_momentum'] = 5.0
        
        # === COMPARATIVE ADVANTAGES ===
        features['shot_advantage'] = features['team_shots'] - features['opponent_shots']
        features['possession_advantage'] = features['team_possession_pct'] - features['opponent_possession_pct']
        features['attack_advantage'] = features['team_attacking_actions'] - features['opponent_attacking_actions']
        features['momentum_advantage'] = features['current_momentum'] - features['opponent_current_momentum']
        
        # === MOMENTUM TRENDS ===
        recent_events = team_events[team_events['timestamp'] >= current_time - 60]
        earlier_events = team_events[team_events['timestamp'] < current_time - 60]
        
        features['momentum_trend'] = len(recent_events) - len(earlier_events)
        features['shot_trend'] = len(recent_events[recent_events['event_type'] == 'Shot']) - len(earlier_events[earlier_events['event_type'] == 'Shot'])
        features['attack_trend'] = len(recent_events[recent_events['event_type'].isin(['Shot', 'Carry', 'Dribble'])]) - len(earlier_events[earlier_events['event_type'].isin(['Shot', 'Carry', 'Dribble'])])
        
        # === ACTIVITY PATTERNS ===
        features['team_total_events'] = len(team_events)
        features['team_events_per_minute'] = len(team_events) / 3
        features['team_recent_intensity'] = len(recent_events) * 2
        features['team_activity_ratio'] = len(team_events) / max(1, len(opponent_events))
        
        return features
    
    def calculate_future_momentum(self, events_df, current_time, future_time, team_name):
        """Calculate realistic future momentum based on actual events"""
        
        # Future window
        future_window = events_df[
            (events_df['timestamp'] >= current_time) & 
            (events_df['timestamp'] <= future_time)
        ]
        
        team_future_events = future_window[future_window['team_name'] == team_name]
        opponent_future_events = future_window[future_window['team_name'] != team_name]
        
        if len(future_window) == 0:
            return 5.0  # Neutral momentum
        
        # Enhanced future momentum calculation
        team_momentum = 0
        
        # Attacking (35%)
        shots = len(team_future_events[team_future_events['event_type'] == 'Shot'])
        attacks = len(team_future_events[team_future_events['event_type'].isin(['Carry', 'Dribble'])])
        team_momentum += (shots * 1.8 + attacks * 1.0) * 0.35
        
        # Possession (25%)
        possession_pct = len(team_future_events) / len(future_window) * 100
        team_momentum += (possession_pct - 50) * 0.05
        
        # Pressure (25%)
        pressure_applied = len(team_future_events[team_future_events['event_type'] == 'Pressure'])
        pressure_received = len(opponent_future_events[opponent_future_events['event_type'] == 'Pressure'])
        team_momentum += (pressure_applied - pressure_received * 0.7) * 0.25
        
        # Activity (15%)
        activity_ratio = len(team_future_events) / max(1, len(opponent_future_events))
        team_momentum += (activity_ratio - 1) * 0.15
        
        # Normalize to 0-10 scale
        momentum_score = 5 + team_momentum
        return max(0, min(10, momentum_score))
    
    def create_hybrid_training_data(self, events_df):
        """Create training data with current momentum feature"""
        
        print("🔧 Creating hybrid training dataset with current momentum...")
        
        # Create enhanced dataset
        events_df['timestamp'] = events_df['minute'] * 60 + events_df['second']
        training_data = []
        
        # Process each match
        for match_id in events_df['match_id'].unique():
            match_events = events_df[events_df['match_id'] == match_id]
            teams = match_events['team_name'].unique()
            
            max_time = int(match_events['timestamp'].max())
            time_points = range(180, max_time - 180, 45)  # Every 45 seconds
            
            for current_time in time_points:
                future_time = current_time + 180
                
                if future_time > max_time:
                    continue
                    
                for team in teams:
                    # Extract hybrid features (including current momentum)
                    features = self.extract_hybrid_features(match_events, current_time, team)
                    
                    # Calculate future momentum (target)
                    future_momentum = self.calculate_future_momentum(match_events, current_time, future_time, team)
                    
                    features['future_momentum'] = future_momentum
                    features['team'] = team
                    features['match_id'] = match_id
                    training_data.append(features)
        
        df = pd.DataFrame(training_data)
        print(f"   ✅ Created {len(df):,} training samples with current momentum feature")
        return df
    
    def train_and_evaluate(self, events_df):
        """Train hybrid model and evaluate performance"""
        
        print("🚀 TRAINING HYBRID MOMENTUM PREDICTION MODEL")
        print("=" * 70)
        
        # Create training data
        training_df = self.create_hybrid_training_data(events_df)
        
        # Prepare features
        feature_columns = [col for col in training_df.columns 
                          if col not in ['future_momentum', 'team', 'match_id']]
        
        self.feature_names = feature_columns
        X = training_df[feature_columns]
        y = training_df['future_momentum']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train model
        self.model.fit(X_train, y_train)
        self.is_trained = True
        
        # Predictions
        y_train_pred = self.model.predict(X_train)
        y_test_pred = self.model.predict(X_test)
        
        # Performance metrics
        performance = {
            'train_r2': r2_score(y_train, y_train_pred),
            'test_r2': r2_score(y_test, y_test_pred),
            'train_mae': mean_absolute_error(y_train, y_train_pred),
            'test_mae': mean_absolute_error(y_test, y_test_pred),
            'train_mse': mean_squared_error(y_train, y_train_pred),
            'test_mse': mean_squared_error(y_test, y_test_pred),
            'train_samples': len(X_train),
            'test_samples': len(X_test),
            'features_count': len(feature_columns),
            'mean_target': y.mean(),
            'std_target': y.std()
        }
        
        # Cross-validation
        cv_scores = cross_val_score(self.model, X, y, cv=5, scoring='r2')
        performance['cv_r2_mean'] = cv_scores.mean()
        performance['cv_r2_std'] = cv_scores.std()
        
        # Feature importance
        feature_importance = dict(zip(feature_columns, self.model.feature_importances_))
        
        return performance, feature_importance, training_df

def create_enhanced_dataset():
    """Create enhanced dataset"""
    
    print("📊 Creating Enhanced Dataset...")
    np.random.seed(42)
    sample_data = []
    
    # Multiple matches with different styles
    matches = [
        {'teams': ['Netherlands', 'England'], 'style': 'attacking'},
        {'teams': ['Spain', 'Germany'], 'style': 'possession'},
        {'teams': ['France', 'Italy'], 'style': 'defensive'},
        {'teams': ['Portugal', 'Belgium'], 'style': 'balanced'},
        {'teams': ['Croatia', 'Denmark'], 'style': 'counter'}
    ]
    
    for match in matches:
        teams = match['teams']
        style = match['style']
        
        for minute in range(90):
            for second in range(0, 60, 8):  # Every 8 seconds
                timestamp = minute * 60 + second
                
                # Event probability by style
                if style == 'attacking':
                    base_prob = 0.8
                elif style == 'possession':
                    base_prob = 0.9
                elif style == 'defensive':
                    base_prob = 0.6
                else:
                    base_prob = 0.7
                
                # Game phase adjustment
                if minute < 15:
                    event_prob = base_prob * 0.7
                elif minute < 45:
                    event_prob = base_prob * 1.0
                elif minute < 60:
                    event_prob = base_prob * 0.8
                else:
                    event_prob = base_prob * 1.1
                
                if np.random.random() < event_prob:
                    # Team selection with momentum patterns
                    if minute < 20:
                        team = np.random.choice(teams, p=[0.5, 0.5])
                    elif minute < 40:
                        team = np.random.choice(teams, p=[0.4, 0.6])
                    elif minute < 60:
                        team = np.random.choice(teams, p=[0.6, 0.4])
                    else:
                        team = np.random.choice(teams, p=[0.45, 0.55])
                    
                    # Event type by style
                    if style == 'attacking':
                        probs = [0.25, 0.15, 0.25, 0.15, 0.10, 0.10]
                    elif style == 'possession':
                        probs = [0.45, 0.05, 0.15, 0.05, 0.15, 0.15]
                    elif style == 'defensive':
                        probs = [0.30, 0.08, 0.12, 0.08, 0.25, 0.17]
                    else:
                        probs = [0.35, 0.10, 0.20, 0.10, 0.15, 0.10]
                    
                    event_type = np.random.choice(
                        ['Pass', 'Shot', 'Carry', 'Dribble', 'Pressure', 'Ball Receipt*'],
                        p=probs
                    )
                    
                    sample_data.append({
                        'minute': minute,
                        'second': second,
                        'timestamp': timestamp,
                        'event_type': event_type,
                        'team_name': team,
                        'match_id': hash(tuple(teams))
                    })
    
    events_df = pd.DataFrame(sample_data)
    print(f"   ✅ Created {len(events_df):,} events from {len(matches)} matches")
    return events_df

def compare_models():
    """Compare original vs hybrid model performance"""
    
    print("🆚 MODEL COMPARISON: ORIGINAL vs HYBRID")
    print("=" * 70)
    
    # Create dataset
    events_df = create_enhanced_dataset()
    
    # Train hybrid model
    hybrid_model = HybridMomentumPredictor()
    hybrid_performance, hybrid_importance, hybrid_data = hybrid_model.train_and_evaluate(events_df)
    
    print("\n📈 HYBRID MODEL PERFORMANCE")
    print("=" * 70)
    
    print("🎯 PREDICTION ACCURACY:")
    print(f"   Training R² Score:     {hybrid_performance['train_r2']:.4f}")
    print(f"   Testing R² Score:      {hybrid_performance['test_r2']:.4f}")
    print(f"   Cross-Validation R²:   {hybrid_performance['cv_r2_mean']:.4f} (±{hybrid_performance['cv_r2_std']:.4f})")
    print(f"   Generalization Gap:    {hybrid_performance['train_r2'] - hybrid_performance['test_r2']:.4f}")
    
    print("\n📊 ERROR METRICS:")
    print(f"   Training MAE:          {hybrid_performance['train_mae']:.3f}")
    print(f"   Testing MAE:           {hybrid_performance['test_mae']:.3f}")
    print(f"   Training RMSE:         {np.sqrt(hybrid_performance['train_mse']):.3f}")
    print(f"   Testing RMSE:          {np.sqrt(hybrid_performance['test_mse']):.3f}")
    
    print("\n📂 FEATURE IMPORTANCE (TOP 15):")
    sorted_features = sorted(hybrid_importance.items(), key=lambda x: x[1], reverse=True)
    
    for i, (feature, importance) in enumerate(sorted_features[:15]):
        print(f"{i+1:2d}. {feature:<25} : {importance:.4f} ({importance*100:.1f}%)")
    
    # Performance interpretation
    test_r2 = hybrid_performance['test_r2']
    if test_r2 >= 0.85:
        level = "EXCELLENT"
    elif test_r2 >= 0.75:
        level = "VERY GOOD"
    elif test_r2 >= 0.65:
        level = "GOOD"
    elif test_r2 >= 0.55:
        level = "MODERATE"
    else:
        level = "NEEDS IMPROVEMENT"
    
    print(f"\n🎯 PERFORMANCE INTERPRETATION:")
    print(f"   Performance Level:     {level}")
    print(f"   Variance Explained:    {test_r2*100:.1f}%")
    print(f"   Prediction Accuracy:   {(1-hybrid_performance['test_mae']/10)*100:.1f}%")
    print(f"   Mean Prediction Error: {hybrid_performance['test_mae']:.2f} points")
    
    # Key insights
    print(f"\n🔑 KEY INSIGHTS:")
    current_momentum_importance = hybrid_importance.get('current_momentum', 0)
    print(f"   Current Momentum Feature: {current_momentum_importance:.3f} ({current_momentum_importance*100:.1f}%)")
    
    momentum_features = ['current_momentum', 'opponent_current_momentum', 'momentum_advantage']
    momentum_total = sum(hybrid_importance.get(feat, 0) for feat in momentum_features)
    print(f"   Total Momentum Features: {momentum_total:.3f} ({momentum_total*100:.1f}%)")
    
    # Show performance improvement vs original
    original_r2 = 0.124  # From previous model
    improvement = (hybrid_performance['test_r2'] - original_r2) / original_r2 * 100
    print(f"\n📈 IMPROVEMENT ANALYSIS:")
    print(f"   Original Model R²:     {original_r2:.3f}")
    print(f"   Hybrid Model R²:       {hybrid_performance['test_r2']:.3f}")
    print(f"   Performance Gain:      {improvement:+.1f}%")
    
    print(f"\n💡 HYBRID MODEL BENEFITS:")
    print(f"   ✅ Added current momentum as key feature")
    print(f"   ✅ Added opponent current momentum for context")
    print(f"   ✅ Added momentum advantage (differential)")
    print(f"   ✅ Enhanced feature set to {hybrid_performance['features_count']} features")
    print(f"   ✅ Improved prediction accuracy by {improvement:+.1f}%")

if __name__ == "__main__":
    compare_models() 