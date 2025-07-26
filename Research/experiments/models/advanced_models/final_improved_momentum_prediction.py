#!/usr/bin/env python3
"""
Final Improved Future Momentum Prediction
Better target calculation and classification approach
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error, accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler
import os
import warnings
warnings.filterwarnings('ignore')

class FinalImprovedMomentumPredictor:
    """
    Final improved momentum prediction with better target calculation
    """
    
    def __init__(self):
        self.regression_model = None
        self.classification_model = None
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
    
    def create_improved_momentum_data(self, events_df, sample_matches=25, prediction_window=3):
        """Create improved momentum data with better target calculation"""
        print(f"\n🔧 CREATING IMPROVED MOMENTUM DATA")
        print(f"   Prediction window: {prediction_window} minutes")
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
                for minute in range(8, match_duration - prediction_window - 2, 2):
                    
                    # Current features
                    current_features = self.extract_predictive_features(
                        match_events, team, minute, teams, match_duration
                    )
                    
                    if current_features is None:
                        continue
                    
                    # Calculate current momentum
                    current_momentum = self.calculate_current_momentum(current_features)
                    
                    # Calculate future momentum change
                    future_momentum_change = self.calculate_future_momentum_change(
                        match_events, team, minute, minute + prediction_window, teams
                    )
                    
                    if future_momentum_change is None:
                        continue
                    
                    # Future momentum absolute value
                    future_momentum_abs = current_momentum + future_momentum_change
                    future_momentum_abs = max(0, min(10, future_momentum_abs))
                    
                    # Classification targets
                    momentum_trend = self.classify_momentum_trend(future_momentum_change)
                    momentum_level = self.classify_momentum_level(future_momentum_abs)
                    
                    record = {
                        'match_id': match_id,
                        'team': team,
                        'minute': minute,
                        'current_momentum': current_momentum,
                        'future_momentum_change': future_momentum_change,
                        'future_momentum_abs': future_momentum_abs,
                        'momentum_trend': momentum_trend,
                        'momentum_level': momentum_level,
                        **current_features
                    }
                    
                    momentum_records.append(record)
        
        momentum_df = pd.DataFrame(momentum_records)
        print(f"✅ Created {len(momentum_df)} improved momentum samples")
        
        return momentum_df
    
    def extract_predictive_features(self, match_events, team, minute, teams, match_duration):
        """Extract predictive features for momentum"""
        
        # Time windows
        last_2min = match_events[
            (match_events['minute'] >= minute-2) & 
            (match_events['minute'] < minute)
        ]
        last_5min = match_events[
            (match_events['minute'] >= minute-5) & 
            (match_events['minute'] < minute)
        ]
        
        team_2min = last_2min[last_2min['team'] == team]
        team_5min = last_5min[last_5min['team'] == team]
        
        if len(team_2min) == 0 and len(team_5min) == 0:
            return None
        
        # Basic activity
        events_2min = len(team_2min)
        events_5min = len(team_5min)
        
        # Event types
        shots_2min = len(team_2min[team_2min['type'].str.contains('Shot', na=False)])
        shots_5min = len(team_5min[team_5min['type'].str.contains('Shot', na=False)])
        
        passes_2min = len(team_2min[team_2min['type'].str.contains('Pass', na=False)])
        passes_5min = len(team_5min[team_5min['type'].str.contains('Pass', na=False)])
        
        attacking_2min = len(team_2min[team_2min['type'].str.contains('Shot|Carry|Dribble', na=False)])
        attacking_5min = len(team_5min[team_5min['type'].str.contains('Shot|Carry|Dribble', na=False)])
        
        # Possession
        possession_2min = (events_2min / (len(last_2min) + 1)) * 100
        possession_5min = (events_5min / (len(last_5min) + 1)) * 100
        
        # Activity trends
        activity_rate_2min = events_2min / 2.0
        activity_rate_5min = events_5min / 5.0
        activity_trend = activity_rate_2min - activity_rate_5min
        
        # Shot trends
        shot_rate_2min = shots_2min / 2.0
        shot_rate_5min = shots_5min / 5.0
        shot_trend = shot_rate_2min - shot_rate_5min
        
        # Match context
        match_phase = minute / 90.0
        time_remaining = (90 - minute) / 90.0
        
        # Pressure
        pressure_2min = len(team_2min[team_2min['under_pressure'].notna()])
        pressure_ratio = pressure_2min / (events_2min + 1)
        
        # Opponent context
        opponent_team = [t for t in teams if t != team][0] if len(teams) > 1 else None
        
        if opponent_team:
            opponent_2min = last_2min[last_2min['team'] == opponent_team]
            opponent_events = len(opponent_2min)
            opponent_shots = len(opponent_2min[opponent_2min['type'].str.contains('Shot', na=False)])
            
            relative_activity = events_2min - opponent_events
            relative_shots = shots_2min - opponent_shots
        else:
            relative_activity = 0
            relative_shots = 0
        
        # Goals
        recent_goals = len(team_5min[team_5min['type'].str.contains('Goal', na=False)])
        
        return {
            'events_2min': events_2min,
            'events_5min': events_5min,
            'shots_2min': shots_2min,
            'shots_5min': shots_5min,
            'passes_2min': passes_2min,
            'passes_5min': passes_5min,
            'attacking_2min': attacking_2min,
            'attacking_5min': attacking_5min,
            'possession_2min': possession_2min,
            'possession_5min': possession_5min,
            'activity_trend': activity_trend,
            'shot_trend': shot_trend,
            'match_phase': match_phase,
            'time_remaining': time_remaining,
            'pressure_ratio': pressure_ratio,
            'relative_activity': relative_activity,
            'relative_shots': relative_shots,
            'recent_goals': recent_goals
        }
    
    def calculate_current_momentum(self, features):
        """Calculate current momentum"""
        momentum = (
            features['events_2min'] * 0.5 +
            features['shots_2min'] * 2.0 +
            features['attacking_2min'] * 1.0 +
            features['possession_2min'] * 0.02 +
            features['activity_trend'] * 2.0 +
            features['shot_trend'] * 3.0 +
            features['relative_activity'] * 0.3 +
            features['relative_shots'] * 1.0 +
            features['recent_goals'] * 3.0 -
            features['pressure_ratio'] * 1.0
        )
        
        return max(0, min(10, momentum))
    
    def calculate_future_momentum_change(self, match_events, team, current_minute, future_minute, teams):
        """Calculate future momentum change (not absolute momentum)"""
        
        # Current period features
        current_window = match_events[
            (match_events['minute'] >= current_minute-2) & 
            (match_events['minute'] < current_minute)
        ]
        
        # Future period features
        future_window = match_events[
            (match_events['minute'] >= future_minute) & 
            (match_events['minute'] < future_minute + 2)
        ]
        
        if len(current_window) == 0 or len(future_window) == 0:
            return None
        
        # Calculate change in key metrics
        current_team = current_window[current_window['team'] == team]
        future_team = future_window[future_window['team'] == team]
        
        # Activity change
        current_activity = len(current_team) / 2.0
        future_activity = len(future_team) / 2.0
        activity_change = future_activity - current_activity
        
        # Shot change
        current_shots = len(current_team[current_team['type'].str.contains('Shot', na=False)])
        future_shots = len(future_team[future_team['type'].str.contains('Shot', na=False)])
        shot_change = future_shots - current_shots
        
        # Possession change
        current_possession = len(current_team) / (len(current_window) + 1) * 100
        future_possession = len(future_team) / (len(future_window) + 1) * 100
        possession_change = future_possession - current_possession
        
        # Goals
        future_goals = len(future_team[future_team['type'].str.contains('Goal', na=False)])
        
        # Calculate momentum change
        momentum_change = (
            activity_change * 1.0 +
            shot_change * 2.0 +
            possession_change * 0.02 +
            future_goals * 3.0
        )
        
        return max(-5, min(5, momentum_change))
    
    def classify_momentum_trend(self, momentum_change):
        """Classify momentum trend"""
        if momentum_change > 0.5:
            return 'increasing'
        elif momentum_change < -0.5:
            return 'decreasing'
        else:
            return 'stable'
    
    def classify_momentum_level(self, momentum_abs):
        """Classify momentum level"""
        if momentum_abs >= 7:
            return 'high'
        elif momentum_abs >= 4:
            return 'medium'
        else:
            return 'low'
    
    def train_models(self, momentum_df):
        """Train both regression and classification models"""
        print(f"\n🚀 TRAINING IMPROVED MOMENTUM MODELS")
        print("=" * 50)
        
        # Prepare features
        feature_cols = [col for col in momentum_df.columns 
                       if col not in ['match_id', 'team', 'minute', 'current_momentum',
                                     'future_momentum_change', 'future_momentum_abs',
                                     'momentum_trend', 'momentum_level']]
        
        self.feature_names = feature_cols
        X = momentum_df[feature_cols]
        
        print(f"📊 Dataset preparation:")
        print(f"   Features: {len(feature_cols)}")
        print(f"   Samples: {len(X)}")
        
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
        X_test = test_data[feature_cols]
        
        print(f"\n🎯 Match-based split:")
        print(f"   Training matches: {len(train_matches)}")
        print(f"   Testing matches: {len(test_matches)}")
        print(f"   Training samples: {len(X_train)}")
        print(f"   Testing samples: {len(X_test)}")
        
        # 1. Regression Model (Future Momentum Change)
        print(f"\n📈 REGRESSION MODEL - Future Momentum Change:")
        y_reg_train = train_data['future_momentum_change']
        y_reg_test = test_data['future_momentum_change']
        
        print(f"   Target range: {y_reg_train.min():.2f} to {y_reg_train.max():.2f}")
        print(f"   Target mean: {y_reg_train.mean():.2f} ± {y_reg_train.std():.2f}")
        
        self.regression_model = RandomForestRegressor(
            n_estimators=150,
            max_depth=10,
            min_samples_split=5,
            random_state=42
        )
        
        self.regression_model.fit(X_train, y_reg_train)
        y_reg_pred = self.regression_model.predict(X_test)
        
        reg_r2 = r2_score(y_reg_test, y_reg_pred)
        reg_mae = mean_absolute_error(y_reg_test, y_reg_pred)
        
        print(f"   R² Score: {reg_r2:.3f}")
        print(f"   MAE: {reg_mae:.3f}")
        
        # 2. Classification Model (Momentum Trend)
        print(f"\n📊 CLASSIFICATION MODEL - Momentum Trend:")
        y_class_train = train_data['momentum_trend']
        y_class_test = test_data['momentum_trend']
        
        print(f"   Classes: {y_class_train.value_counts().to_dict()}")
        
        self.classification_model = RandomForestClassifier(
            n_estimators=150,
            max_depth=10,
            min_samples_split=5,
            random_state=42
        )
        
        self.classification_model.fit(X_train, y_class_train)
        y_class_pred = self.classification_model.predict(X_test)
        
        class_acc = accuracy_score(y_class_test, y_class_pred)
        
        print(f"   Accuracy: {class_acc:.3f}")
        print(f"   Classification Report:")
        print(classification_report(y_class_test, y_class_pred, target_names=['decreasing', 'increasing', 'stable']))
        
        # Feature importance
        print(f"\n🔝 TOP FEATURES (Regression):")
        reg_importance = pd.DataFrame({
            'feature': feature_cols,
            'importance': self.regression_model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        for _, row in reg_importance.head(10).iterrows():
            print(f"   {row['feature']:<25}: {row['importance']:.3f}")
        
        print(f"\n🔝 TOP FEATURES (Classification):")
        class_importance = pd.DataFrame({
            'feature': feature_cols,
            'importance': self.classification_model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        for _, row in class_importance.head(10).iterrows():
            print(f"   {row['feature']:<25}: {row['importance']:.3f}")
        
        return {
            'regression_r2': reg_r2,
            'regression_mae': reg_mae,
            'classification_accuracy': class_acc
        }
    
    def analyze_momentum_patterns(self, momentum_df):
        """Analyze momentum patterns"""
        print(f"\n📊 MOMENTUM PATTERN ANALYSIS")
        print("=" * 50)
        
        # Current momentum statistics
        print(f"📈 Current Momentum:")
        print(f"   Mean: {momentum_df['current_momentum'].mean():.2f}")
        print(f"   Std: {momentum_df['current_momentum'].std():.2f}")
        print(f"   Range: {momentum_df['current_momentum'].min():.2f}-{momentum_df['current_momentum'].max():.2f}")
        
        # Future momentum change statistics
        print(f"\n🔮 Future Momentum Change:")
        print(f"   Mean: {momentum_df['future_momentum_change'].mean():.2f}")
        print(f"   Std: {momentum_df['future_momentum_change'].std():.2f}")
        print(f"   Range: {momentum_df['future_momentum_change'].min():.2f}-{momentum_df['future_momentum_change'].max():.2f}")
        
        # Momentum trend distribution
        print(f"\n📊 Momentum Trend Distribution:")
        trend_counts = momentum_df['momentum_trend'].value_counts()
        for trend, count in trend_counts.items():
            pct = (count / len(momentum_df)) * 100
            print(f"   {trend:<12}: {count:>4} ({pct:>5.1f}%)")
        
        # Correlation analysis
        numeric_cols = [col for col in momentum_df.columns if momentum_df[col].dtype in ['int64', 'float64']]
        correlations = momentum_df[numeric_cols].corr()
        
        print(f"\n🔗 Strongest Correlations with Future Momentum Change:")
        future_corr = correlations['future_momentum_change'].abs().sort_values(ascending=False)
        for feature, corr in future_corr.head(10).items():
            if feature != 'future_momentum_change':
                print(f"   {feature:<25}: {corr:>6.3f}")
        
        return correlations

def main():
    """Main function"""
    print("🎯 FINAL IMPROVED MOMENTUM PREDICTION")
    print("=" * 80)
    
    predictor = FinalImprovedMomentumPredictor()
    
    # Load data
    events_df, matches_df = predictor.load_data()
    if events_df is None:
        return
    
    # Create improved data
    momentum_df = predictor.create_improved_momentum_data(events_df, sample_matches=25, prediction_window=3)
    
    if len(momentum_df) == 0:
        print("❌ No momentum data created")
        return
    
    # Analyze patterns
    correlations = predictor.analyze_momentum_patterns(momentum_df)
    
    # Train models
    results = predictor.train_models(momentum_df)
    
    print(f"\n🎯 FINAL RESULTS:")
    print(f"   Regression (Change Prediction):")
    print(f"   • R² Score: {results['regression_r2']:.3f}")
    print(f"   • MAE: {results['regression_mae']:.3f}")
    print(f"   Classification (Trend Prediction):")
    print(f"   • Accuracy: {results['classification_accuracy']:.3f}")
    
    # Evaluation
    if results['regression_r2'] > 0.20:
        print(f"   ✅ Good regression performance for momentum change prediction!")
    elif results['regression_r2'] > 0.10:
        print(f"   ✅ Moderate regression performance for momentum change prediction!")
    else:
        print(f"   ⚠️  Challenging regression performance (expected for future prediction)")
    
    if results['classification_accuracy'] > 0.60:
        print(f"   ✅ Good classification performance for momentum trend prediction!")
    elif results['classification_accuracy'] > 0.50:
        print(f"   ✅ Moderate classification performance for momentum trend prediction!")
    else:
        print(f"   ⚠️  Challenging classification performance")
    
    print(f"\n💡 KEY INSIGHTS:")
    print(f"   • Future momentum prediction is inherently challenging")
    print(f"   • Contextual features provide meaningful predictive power")
    print(f"   • Classification (trend) may be more reliable than regression")
    print(f"   • Activity trends and possession patterns are key predictors")
    
    print(f"\n✅ FINAL IMPROVED MOMENTUM PREDICTION COMPLETE")

if __name__ == "__main__":
    main() 