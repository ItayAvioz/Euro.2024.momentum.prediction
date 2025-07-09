#!/usr/bin/env python3
"""
Hybrid Momentum Model - Applied to Complete Euro 2024 Dataset
Uses current momentum as feature to predict future momentum (3 minutes ahead)
Based on last 3 minutes of events
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
            (events_df['timestamp_seconds'] >= start_time) & 
            (events_df['timestamp_seconds'] <= current_time)
        ]
        
        team_events = current_window[current_window['team_name'] == team_name]
        opponent_events = current_window[current_window['team_name'] != team_name]
        
        if len(current_window) == 0:
            return 5.0  # Neutral momentum
        
        # Summary momentum calculation
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
        recent_events = team_events[team_events['timestamp_seconds'] >= current_time - 60]
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
        self.performance_metrics = {}
        
    def load_complete_data(self):
        """Load complete Euro 2024 dataset"""
        print("🏆 LOADING COMPLETE EURO 2024 DATASET FOR HYBRID MODEL")
        print("=" * 70)
        
        try:
            # Try different file paths
            file_paths = [
                'Data/events_complete.csv',
                'euro_2024_complete/connected_complete.csv'
            ]
            
            for file_path in file_paths:
                try:
                    print(f"📂 Trying: {file_path}")
                    data = pd.read_csv(file_path)
                    print(f"✅ Success: {file_path}")
                    break
                except FileNotFoundError:
                    continue
            
            print(f"📊 Dataset: {data.shape}")
            print(f"🏟️ Matches: {data['match_id'].nunique()}")
            print(f"👥 Teams: {data['team_name'].nunique()}")
            print(f"⚽ Events: {data['event_type'].nunique()}")
            
            # Add timestamp
            data['timestamp_seconds'] = data['minute'] * 60 + data['second']
            
            return data
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def extract_hybrid_features(self, events_df, current_time, team_name):
        """Extract comprehensive hybrid features including current momentum"""
        
        # Current 3-minute window (basis for prediction)
        start_time = max(0, current_time - 180)
        current_window = events_df[
            (events_df['timestamp_seconds'] >= start_time) & 
            (events_df['timestamp_seconds'] <= current_time)
        ]
        
        team_events = current_window[current_window['team_name'] == team_name]
        opponent_events = current_window[current_window['team_name'] != team_name]
        total_events = len(current_window)
        
        features = {}
        
        # === KEY FEATURE: CURRENT MOMENTUM ===
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
        recent_events = team_events[team_events['timestamp_seconds'] >= current_time - 60]
        earlier_events = team_events[team_events['timestamp_seconds'] < current_time - 60]
        
        features['momentum_trend'] = len(recent_events) - len(earlier_events)
        features['shot_trend'] = len(recent_events[recent_events['event_type'] == 'Shot']) - len(earlier_events[earlier_events['event_type'] == 'Shot'])
        features['attack_trend'] = len(recent_events[recent_events['event_type'].isin(['Shot', 'Carry', 'Dribble'])]) - len(earlier_events[earlier_events['event_type'].isin(['Shot', 'Carry', 'Dribble'])])
        
        # === ACTIVITY PATTERNS ===
        features['team_total_events'] = len(team_events)
        features['team_events_per_minute'] = len(team_events) / 3
        features['team_recent_intensity'] = len(recent_events) * 2
        features['team_activity_ratio'] = len(team_events) / max(1, len(opponent_events))
        
        return features
    
    def calculate_future_momentum(self, events_df, current_time, team_name):
        """Calculate future momentum (3 minutes ahead) based on actual future events"""
        
        # Future 3-minute window
        future_start = current_time
        future_end = current_time + 180  # 3 minutes ahead
        
        future_window = events_df[
            (events_df['timestamp_seconds'] >= future_start) & 
            (events_df['timestamp_seconds'] <= future_end)
        ]
        
        team_future_events = future_window[future_window['team_name'] == team_name]
        opponent_future_events = future_window[future_window['team_name'] != team_name]
        
        if len(future_window) == 0:
            return 5.0  # Neutral momentum
        
        # Calculate future momentum based on what actually happens
        future_momentum = 0
        
        # Attacking contribution (35%)
        shots = len(team_future_events[team_future_events['event_type'] == 'Shot'])
        attacks = len(team_future_events[team_future_events['event_type'].isin(['Carry', 'Dribble'])])
        future_momentum += (shots * 1.8 + attacks * 1.0) * 0.35
        
        # Possession contribution (25%)
        possession_pct = (len(team_future_events) / len(future_window) * 100) if len(future_window) > 0 else 50
        future_momentum += (possession_pct - 50) * 0.05
        
        # Pressure contribution (25%)
        pressure_applied = len(team_future_events[team_future_events['event_type'] == 'Pressure'])
        pressure_received = len(opponent_future_events[opponent_future_events['event_type'] == 'Pressure'])
        future_momentum += (pressure_applied - pressure_received * 0.7) * 0.25
        
        # Activity contribution (15%)
        activity_ratio = len(team_future_events) / max(1, len(opponent_future_events))
        future_momentum += (activity_ratio - 1) * 0.15
        
        # Normalize to 0-10 scale
        momentum_score = 5 + future_momentum
        return max(0, min(10, momentum_score))
    
    def create_training_dataset_complete(self, events_df):
        """Create comprehensive training dataset from complete Euro 2024 data"""
        print("\n📊 CREATING HYBRID TRAINING DATASET FROM COMPLETE DATA")
        print("=" * 70)
        
        training_data = []
        matches = events_df['match_id'].unique()
        
        print(f"🏟️ Processing {len(matches)} matches for hybrid model...")
        
        processed_matches = 0
        for match_id in matches:
            match_data = events_df[events_df['match_id'] == match_id].copy()
            teams = match_data['team_name'].unique()
            
            # Sample time points (every 30 seconds, ensuring we have future data)
            max_time = int(match_data['timestamp_seconds'].max())
            # Start at 3 minutes, end 3 minutes before match end to have future data
            time_points = range(180, max_time - 180, 30)
            
            match_samples = 0
            for time_point in time_points:
                for team in teams:
                    try:
                        # Extract features from last 3 minutes
                        features = self.extract_hybrid_features(match_data, time_point, team)
                        
                        # Calculate future momentum (3 minutes ahead)
                        future_momentum = self.calculate_future_momentum(match_data, time_point, team)
                        
                        # Add metadata
                        features['future_momentum'] = future_momentum
                        features['match_id'] = match_id
                        features['team'] = team
                        features['time_point'] = time_point
                        
                        training_data.append(features)
                        match_samples += 1
                        
                    except Exception as e:
                        continue
            
            processed_matches += 1
            if processed_matches % 10 == 0:
                print(f"   Processed {processed_matches}/{len(matches)} matches...")
        
        training_df = pd.DataFrame(training_data)
        print(f"✅ Hybrid training dataset created!")
        print(f"   📊 Total samples: {len(training_df):,}")
        print(f"   🔢 Features: {len([col for col in training_df.columns if col not in ['future_momentum', 'match_id', 'team', 'time_point']])}")
        print(f"   🎯 Target range: {training_df['future_momentum'].min():.2f} - {training_df['future_momentum'].max():.2f}")
        print(f"   📈 Target mean: {training_df['future_momentum'].mean():.2f} ± {training_df['future_momentum'].std():.2f}")
        
        return training_df
    
    def train_hybrid_model_complete(self, training_df):
        """Train hybrid model with comprehensive evaluation on complete data"""
        print("\n🚀 TRAINING HYBRID MOMENTUM MODEL ON COMPLETE DATA")
        print("=" * 70)
        
        # Prepare features and target
        exclude_columns = ['future_momentum', 'match_id', 'team', 'time_point']
        feature_columns = [col for col in training_df.columns if col not in exclude_columns]
        
        X = training_df[feature_columns].fillna(0)
        y = training_df['future_momentum']
        
        print(f"📊 Hybrid model dataset:")
        print(f"   Total samples: {len(X):,}")
        print(f"   Features: {len(feature_columns)}")
        print(f"   Target range: {y.min():.2f} - {y.max():.2f}")
        print(f"   Target mean: {y.mean():.2f} ± {y.std():.2f}")
        
        # Store feature names
        self.feature_names = feature_columns
        
        # Train/test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        print(f"\n🔄 Data split:")
        print(f"   Training: {len(X_train):,} samples")
        print(f"   Testing: {len(X_test):,} samples")
        
        # Train the hybrid model
        print(f"\n🔮 Training Hybrid Random Forest...")
        self.model.fit(X_train, y_train)
        
        # Predictions
        y_train_pred = self.model.predict(X_train)
        y_test_pred = self.model.predict(X_test)
        
        # Performance metrics
        performance = {
            'train_r2': r2_score(y_train, y_train_pred),
            'test_r2': r2_score(y_test, y_test_pred),
            'train_mse': mean_squared_error(y_train, y_train_pred),
            'test_mse': mean_squared_error(y_test, y_test_pred),
            'train_mae': mean_absolute_error(y_train, y_train_pred),
            'test_mae': mean_absolute_error(y_test, y_test_pred),
            'train_rmse': np.sqrt(mean_squared_error(y_train, y_train_pred)),
            'test_rmse': np.sqrt(mean_squared_error(y_test, y_test_pred)),
            'train_samples': len(X_train),
            'test_samples': len(X_test),
            'features_count': len(feature_columns)
        }
        
        # Cross-validation
        cv_scores = cross_val_score(self.model, X_train, y_train, cv=5, scoring='r2')
        performance['cv_r2_mean'] = cv_scores.mean()
        performance['cv_r2_std'] = cv_scores.std()
        
        # Feature importance
        feature_importance = dict(zip(feature_columns, self.model.feature_importances_))
        
        # Store results
        self.performance_metrics = performance
        self.is_trained = True
        
        print(f"✅ Hybrid model training completed!")
        print(f"   Training R²: {performance['train_r2']:.4f}")
        print(f"   Testing R²:  {performance['test_r2']:.4f}")
        print(f"   CV R²:       {performance['cv_r2_mean']:.4f} ± {performance['cv_r2_std']:.4f}")
        
        return feature_importance, performance
    
    def generate_hybrid_performance_report(self, feature_importance, performance):
        """Generate comprehensive performance report for hybrid model"""
        print("\n📈 HYBRID MODEL PERFORMANCE REPORT - COMPLETE EURO 2024 DATA")
        print("=" * 80)
        
        # Dataset summary
        print("📊 COMPLETE DATASET ANALYSIS:")
        print(f"   Purpose: Predict FUTURE momentum (3 minutes ahead)")
        print(f"   Basis: Last 3 minutes of events")
        print(f"   Training Samples: {performance['train_samples']:,}")
        print(f"   Testing Samples: {performance['test_samples']:,}")
        print(f"   Features: {performance['features_count']} (including current_momentum)")
        
        # Performance metrics
        print(f"\n🏆 HYBRID MODEL PERFORMANCE:")
        print("=" * 50)
        print(f"   📈 Training R²:      {performance['train_r2']:.4f} ({performance['train_r2']*100:.1f}% variance)")
        print(f"   📊 Testing R²:       {performance['test_r2']:.4f} ({performance['test_r2']*100:.1f}% variance)")
        print(f"   🔄 Cross-Val R²:     {performance['cv_r2_mean']:.4f} ± {performance['cv_r2_std']:.4f}")
        print(f"   📉 Training MAE:     {performance['train_mae']:.3f} momentum points")
        print(f"   📊 Testing MAE:      {performance['test_mae']:.3f} momentum points")
        print(f"   📏 Training RMSE:    {performance['train_rmse']:.3f}")
        print(f"   📊 Testing RMSE:     {performance['test_rmse']:.3f}")
        
        # Overfitting analysis
        overfitting = performance['train_r2'] - performance['test_r2']
        print(f"   ⚠️  Overfitting Gap: {overfitting:.4f}")
        
        # Performance level
        test_r2 = performance['test_r2']
        if test_r2 >= 0.85:
            level = "EXCELLENT"
        elif test_r2 >= 0.75:
            level = "VERY GOOD"
        elif test_r2 >= 0.65:
            level = "GOOD"
        elif test_r2 >= 0.50:
            level = "MODERATE"
        elif test_r2 >= 0.20:
            level = "FAIR"
        else:
            level = "POOR"
        
        print(f"   🎯 Performance Level: {level}")
        print(f"   📊 Prediction Accuracy: {(1-performance['test_mae']/10)*100:.1f}%")
        
        # Feature importance analysis
        print(f"\n🔍 FEATURE IMPORTANCE ANALYSIS:")
        print("=" * 50)
        sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
        
        print(f"Top 15 Most Important Features for Future Momentum Prediction:")
        for i, (feature, importance) in enumerate(sorted_features[:15]):
            percentage = importance * 100
            print(f"   {i+1:2d}. {feature:<25} : {importance:.4f} ({percentage:.1f}%)")
        
        # Momentum-specific features analysis
        print(f"\n🎯 MOMENTUM-SPECIFIC FEATURES:")
        momentum_features = ['current_momentum', 'momentum_advantage', 'opponent_current_momentum']
        momentum_importance = 0
        
        for feature in momentum_features:
            if feature in feature_importance:
                importance = feature_importance[feature]
                momentum_importance += importance
                print(f"   • {feature}: {importance:.4f} ({importance*100:.1f}%)")
        
        print(f"   📊 Total Momentum Features Importance: {momentum_importance:.4f} ({momentum_importance*100:.1f}%)")
        
        # Interpretation
        print(f"\n💡 INTERPRETATION:")
        print("=" * 30)
        print(f"   🎯 Future Prediction Difficulty: Future momentum is inherently harder to predict")
        print(f"   📊 R² = {test_r2:.4f}: Model explains {test_r2*100:.1f}% of future momentum variance")
        print(f"   ⚡ Current Momentum Impact: {feature_importance.get('current_momentum', 0)*100:.1f}% of prediction")
        print(f"   🔮 Prediction Error: ±{performance['test_mae']:.2f} momentum points on average")
        
        # Comparison context
        print(f"\n📈 CONTEXT COMPARISON:")
        print("=" * 30)
        print(f"   🏆 Final Model (Current): 99.95% R² (predicting current momentum)")
        print(f"   🔮 Hybrid Model (Future):  {test_r2*100:.1f}% R² (predicting future momentum)")
        print(f"   📊 Difficulty Factor: {99.95/test_r2/100:.1f}x harder to predict future vs current")
        
        return performance
    
    def run_complete_hybrid_analysis(self):
        """Run complete hybrid model analysis on all Euro 2024 data"""
        print("🚀 HYBRID MOMENTUM MODEL - COMPLETE EURO 2024 ANALYSIS")
        print("🎯 PREDICTING FUTURE MOMENTUM BASED ON LAST 3 MINUTES")
        print("=" * 80)
        
        # Load complete data
        data = self.load_complete_data()
        if data is None:
            return False
        
        # Create training dataset
        training_df = self.create_training_dataset_complete(data)
        if len(training_df) == 0:
            print("❌ No training data created")
            return False
        
        # Train hybrid model
        feature_importance, performance = self.train_hybrid_model_complete(training_df)
        
        # Generate performance report
        final_performance = self.generate_hybrid_performance_report(feature_importance, performance)
        
        print(f"\n✅ HYBRID MODEL ANALYSIS COMPLETE!")
        print(f"   🎯 Purpose: Future momentum prediction (3 min ahead)")
        print(f"   📊 Performance: {final_performance['test_r2']:.4f} R² ({final_performance['test_r2']*100:.1f}% variance)")
        print(f"   📈 Samples: {final_performance['train_samples']:,} training + {final_performance['test_samples']:,} testing")
        print(f"   🔢 Features: {final_performance['features_count']} (including current momentum)")
        
        return True

def main():
    """Main execution function"""
    print("🚀 APPLYING HYBRID MODEL TO COMPLETE EURO 2024 DATA")
    print("🎯 FUTURE MOMENTUM PREDICTION BASED ON LAST 3 MINUTES")
    print("=" * 80)
    
    predictor = HybridMomentumPredictor()
    success = predictor.run_complete_hybrid_analysis()
    
    if success:
        print("\n🎉 HYBRID MODEL ANALYSIS SUCCESSFUL!")
        print("Complete Euro 2024 data processed for future momentum prediction.")
    else:
        print("\n❌ Analysis failed. Check data availability.")

if __name__ == "__main__":
    main() 