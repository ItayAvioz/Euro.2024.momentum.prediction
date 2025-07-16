#!/usr/bin/env python3
"""
Apply Final Momentum Model to Complete Euro 2024 Dataset
Get comprehensive performance results from the most advanced model
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import warnings
warnings.filterwarnings('ignore')

class FinalMomentumModel:
    """Final momentum model with comprehensive feature engineering"""
    
    def __init__(self):
        self.data = None
        self.models = {}
        self.performance_metrics = {}
        self.feature_importance = {}
        self.training_stats = {}
        
    def load_complete_data(self):
        """Load complete Euro 2024 dataset"""
        print("🏆 LOADING COMPLETE EURO 2024 DATASET")
        print("=" * 60)
        
        try:
            # Try to load from Data directory
            file_paths = [
                'Data/events_complete.csv',
                'euro_2024_complete/connected_complete.csv',
                'connected_complete.csv'
            ]
            
            for file_path in file_paths:
                try:
                    print(f"📂 Trying to load: {file_path}")
                    self.data = pd.read_csv(file_path)
                    print(f"✅ Successfully loaded from: {file_path}")
                    break
                except FileNotFoundError:
                    continue
                except Exception as e:
                    print(f"❌ Error with {file_path}: {e}")
                    continue
            
            if self.data is None:
                print("❌ Could not load data from any path")
                return False
            
            print(f"📊 Dataset: {self.data.shape}")
            print(f"🏟️ Matches: {self.data['match_id'].nunique()}")
            print(f"👥 Teams: {self.data['team_name'].nunique()}")
            print(f"⚽ Events: {self.data['event_type'].nunique()}")
            
            # Add timestamp
            self.data['timestamp_seconds'] = self.data['minute'] * 60 + self.data['second']
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return False
    
    def extract_final_features(self, events_df, current_time, team_name):
        """Extract comprehensive features for final model"""
        
        # Define time windows
        window_3min = max(0, current_time - 180)
        window_1min = max(0, current_time - 60)
        
        # Get recent events
        recent_3min = events_df[
            (events_df['timestamp_seconds'] >= window_3min) & 
            (events_df['timestamp_seconds'] <= current_time)
        ]
        recent_1min = events_df[
            (events_df['timestamp_seconds'] >= window_1min) & 
            (events_df['timestamp_seconds'] <= current_time)
        ]
        
        # Team vs opponent events
        team_3min = recent_3min[recent_3min['team_name'] == team_name]
        opponent_3min = recent_3min[recent_3min['team_name'] != team_name]
        team_1min = recent_1min[recent_1min['team_name'] == team_name]
        
        features = {}
        
        # === BASIC ACTIVITY FEATURES ===
        features['total_events'] = len(team_3min)
        features['events_per_minute'] = len(team_3min) / 3 if len(team_3min) > 0 else 0
        features['recent_intensity'] = len(team_1min)
        
        # === EVENT TYPE FEATURES ===
        event_types = ['Pass', 'Shot', 'Carry', 'Pressure', 'Dribble', 'Ball Receipt*', 
                      'Clearance', 'Interception', 'Block', 'Foul Committed']
        
        for event_type in event_types:
            safe_name = event_type.replace('*', '').replace(' ', '_').lower()
            features[f'{safe_name}_count'] = len(team_3min[team_3min['event_type'] == event_type])
        
        # === ATTACKING FEATURES ===
        attacking_events = ['Shot', 'Dribble', 'Carry']
        features['attacking_actions'] = len(team_3min[team_3min['event_type'].isin(attacking_events)])
        features['attacking_intensity'] = features['attacking_actions'] / 3
        features['shot_rate'] = features['shot_count'] / 3
        
        # === POSSESSION FEATURES ===
        total_recent = len(recent_3min)
        features['possession_percentage'] = (len(team_3min) / total_recent * 100) if total_recent > 0 else 50
        features['pass_rate'] = features['pass_count'] / 3
        
        # === DEFENSIVE FEATURES ===
        defensive_events = ['Pressure', 'Clearance', 'Interception', 'Block']
        features['defensive_actions'] = len(team_3min[team_3min['event_type'].isin(defensive_events)])
        features['pressure_applied'] = features['pressure_count']
        
        # === OPPONENT CONTEXT FEATURES ===
        features['opponent_pressure'] = len(opponent_3min[opponent_3min['event_type'] == 'Pressure'])
        features['opponent_shots'] = len(opponent_3min[opponent_3min['event_type'] == 'Shot'])
        features['opponent_attacks'] = len(opponent_3min[opponent_3min['event_type'].isin(attacking_events)])
        features['pressure_balance'] = features['pressure_applied'] - features['opponent_pressure']
        
        # === COMPARATIVE FEATURES ===
        features['shot_advantage'] = features['shot_count'] - features['opponent_shots']
        features['possession_advantage'] = features['possession_percentage'] - 50
        features['attack_advantage'] = features['attacking_actions'] - features['opponent_attacks']
        features['event_advantage'] = len(team_3min) - len(opponent_3min)
        
        # === MOMENTUM TREND FEATURES ===
        earlier_2min = team_3min[team_3min['timestamp_seconds'] < window_1min]
        features['momentum_trend'] = len(team_1min) - len(earlier_2min)
        features['shot_trend'] = len(team_1min[team_1min['event_type'] == 'Shot']) - len(earlier_2min[earlier_2min['event_type'] == 'Shot'])
        
        # === ACTIVITY RATIOS ===
        features['activity_ratio'] = len(team_3min) / max(1, len(opponent_3min))
        features['attacking_ratio'] = features['attacking_actions'] / max(1, features['opponent_attacks'])
        
        # === GAME PHASE FEATURES ===
        game_minute = current_time // 60
        features['game_minute'] = game_minute
        features['early_game'] = 1 if game_minute <= 30 else 0
        features['late_game'] = 1 if game_minute >= 75 else 0
        
        return features
    
    def calculate_momentum_target(self, events_df, current_time, team_name):
        """Calculate realistic momentum target"""
        
        # Get 3-minute window
        window_3min = max(0, current_time - 180)
        recent_events = events_df[
            (events_df['timestamp_seconds'] >= window_3min) & 
            (events_df['timestamp_seconds'] <= current_time)
        ]
        
        team_events = recent_events[recent_events['team_name'] == team_name]
        total_events = len(recent_events)
        
        if len(team_events) == 0:
            return 5.0  # Neutral momentum
        
        # Calculate momentum components
        shots = len(team_events[team_events['event_type'] == 'Shot'])
        attacks = len(team_events[team_events['event_type'].isin(['Shot', 'Dribble', 'Carry'])])
        possession_pct = (len(team_events) / total_events * 100) if total_events > 0 else 50
        
        # Momentum formula
        momentum = (
            shots * 2.0 +                          # Goal threat
            attacks * 1.2 +                       # Attacking intent
            possession_pct * 0.05 +               # Possession control
            len(team_events) * 0.3                # General activity
        )
        
        # Normalize to 0-10 scale
        momentum_score = 5 + (momentum - 8) * 0.25
        return max(0, min(10, momentum_score))
    
    def create_training_dataset(self):
        """Create comprehensive training dataset"""
        print("\n📊 CREATING TRAINING DATASET FROM COMPLETE DATA")
        print("=" * 60)
        
        training_data = []
        matches = self.data['match_id'].unique()
        
        print(f"🏟️ Processing {len(matches)} matches...")
        
        processed_matches = 0
        for match_id in matches:
            match_data = self.data[self.data['match_id'] == match_id].copy()
            teams = match_data['team_name'].unique()
            
            # Sample time points (every 30 seconds after 3 minutes)
            max_time = int(match_data['timestamp_seconds'].max())
            time_points = range(180, max_time, 30)
            
            match_samples = 0
            for time_point in time_points:
                for team in teams:
                    try:
                        # Extract features
                        features = self.extract_final_features(match_data, time_point, team)
                        
                        # Calculate target momentum
                        momentum_target = self.calculate_momentum_target(match_data, time_point, team)
                        
                        # Add metadata
                        features['momentum_score'] = momentum_target
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
        print(f"✅ Training dataset created!")
        print(f"   📊 Total samples: {len(training_df):,}")
        print(f"   🔢 Features: {len([col for col in training_df.columns if col not in ['momentum_score', 'match_id', 'team', 'time_point']])}")
        print(f"   🎯 Target range: {training_df['momentum_score'].min():.2f} - {training_df['momentum_score'].max():.2f}")
        print(f"   📈 Target mean: {training_df['momentum_score'].mean():.2f} ± {training_df['momentum_score'].std():.2f}")
        
        return training_df
    
    def train_final_models(self, training_df):
        """Train final momentum models with comprehensive evaluation"""
        print("\n🚀 TRAINING FINAL MOMENTUM MODELS")
        print("=" * 60)
        
        # Prepare features and target
        exclude_columns = ['momentum_score', 'match_id', 'team', 'time_point']
        feature_columns = [col for col in training_df.columns if col not in exclude_columns]
        
        X = training_df[feature_columns].fillna(0)  # Handle any NaN values
        y = training_df['momentum_score']
        
        print(f"📊 Final dataset preparation:")
        print(f"   Total samples: {len(X):,}")
        print(f"   Features: {len(feature_columns)}")
        print(f"   Target range: {y.min():.2f} - {y.max():.2f}")
        print(f"   Target mean: {y.mean():.2f} ± {y.std():.2f}")
        
        # Train/test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        print(f"\n🔄 Data split:")
        print(f"   Training: {len(X_train):,} samples")
        print(f"   Testing: {len(X_test):,} samples")
        
        # Final model configurations
        models_config = {
            'RandomForest_Final': RandomForestRegressor(
                n_estimators=200,
                max_depth=15,
                min_samples_split=5,
                min_samples_leaf=2,
                max_features='sqrt',
                random_state=42,
                n_jobs=-1
            ),
            'GradientBoosting_Final': GradientBoostingRegressor(
                n_estimators=200,
                learning_rate=0.1,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42
            )
        }
        
        # Train and evaluate each model
        for model_name, model in models_config.items():
            print(f"\n🔮 Training {model_name}...")
            
            # Train model
            model.fit(X_train, y_train)
            
            # Predictions
            y_train_pred = model.predict(X_train)
            y_test_pred = model.predict(X_test)
            
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
            cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='r2')
            performance['cv_r2_mean'] = cv_scores.mean()
            performance['cv_r2_std'] = cv_scores.std()
            
            # Feature importance
            if hasattr(model, 'feature_importances_'):
                feature_importance = dict(zip(feature_columns, model.feature_importances_))
                self.feature_importance[model_name] = feature_importance
            
            # Store results
            self.models[model_name] = model
            self.performance_metrics[model_name] = performance
            
            print(f"   ✅ {model_name} completed!")
            print(f"      Training R²: {performance['train_r2']:.4f}")
            print(f"      Testing R²:  {performance['test_r2']:.4f}")
            print(f"      CV R²:       {performance['cv_r2_mean']:.4f} ± {performance['cv_r2_std']:.4f}")
        
        # Store training statistics
        self.training_stats = {
            'total_samples': len(training_df),
            'train_samples': len(X_train),
            'test_samples': len(X_test),
            'features_count': len(feature_columns),
            'feature_names': feature_columns,
            'target_mean': y.mean(),
            'target_std': y.std(),
            'target_min': y.min(),
            'target_max': y.max()
        }
        
        return feature_columns
    
    def generate_final_performance_report(self):
        """Generate comprehensive final performance report"""
        print("\n📈 FINAL MODEL PERFORMANCE REPORT")
        print("=" * 80)
        
        # Dataset summary
        print("📊 COMPLETE EURO 2024 DATASET ANALYSIS:")
        print(f"   Total Events Processed: {len(self.data):,}")
        print(f"   Training Samples Created: {self.training_stats['total_samples']:,}")
        print(f"   Features Engineered: {self.training_stats['features_count']}")
        print(f"   Matches Analyzed: {self.data['match_id'].nunique()}")
        print(f"   Teams Covered: {self.data['team_name'].nunique()}")
        print(f"   Event Types: {self.data['event_type'].nunique()}")
        
        # Performance comparison
        print(f"\n🏆 FINAL MODEL PERFORMANCE COMPARISON:")
        print("=" * 80)
        
        best_r2 = 0
        best_model_name = ""
        
        for model_name, metrics in self.performance_metrics.items():
            print(f"\n🔮 {model_name}:")
            print(f"   📈 Training R²:      {metrics['train_r2']:.4f} ({metrics['train_r2']*100:.1f}% variance)")
            print(f"   📊 Testing R²:       {metrics['test_r2']:.4f} ({metrics['test_r2']*100:.1f}% variance)")
            print(f"   🔄 Cross-Val R²:     {metrics['cv_r2_mean']:.4f} ± {metrics['cv_r2_std']:.4f}")
            print(f"   📉 Training MAE:     {metrics['train_mae']:.3f} momentum points")
            print(f"   📊 Testing MAE:      {metrics['test_mae']:.3f} momentum points")
            print(f"   📏 Training RMSE:    {metrics['train_rmse']:.3f}")
            print(f"   📊 Testing RMSE:     {metrics['test_rmse']:.3f}")
            
            # Calculate overfitting
            overfitting = metrics['train_r2'] - metrics['test_r2']
            print(f"   ⚠️  Overfitting Gap: {overfitting:.4f}")
            
            # Performance level
            test_r2 = metrics['test_r2']
            if test_r2 >= 0.85:
                level = "EXCELLENT"
            elif test_r2 >= 0.75:
                level = "VERY GOOD"
            elif test_r2 >= 0.65:
                level = "GOOD"
            elif test_r2 >= 0.50:
                level = "MODERATE"
            else:
                level = "NEEDS IMPROVEMENT"
            
            print(f"   🎯 Performance Level: {level}")
            print(f"   📊 Prediction Accuracy: {(1-metrics['test_mae']/10)*100:.1f}%")
            
            # Track best model
            if test_r2 > best_r2:
                best_r2 = test_r2
                best_model_name = model_name
        
        # Feature importance analysis
        print(f"\n🔍 FEATURE IMPORTANCE ANALYSIS:")
        print("=" * 80)
        
        for model_name, importance_dict in self.feature_importance.items():
            print(f"\n🔮 {model_name} - Top 15 Most Important Features:")
            sorted_features = sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)
            
            total_importance = sum(importance_dict.values())
            
            for i, (feature, importance) in enumerate(sorted_features[:15]):
                percentage = (importance / total_importance) * 100
                print(f"   {i+1:2d}. {feature:<25} : {importance:.4f} ({percentage:.1f}%)")
        
        # Best model summary
        print(f"\n🏆 BEST MODEL SUMMARY:")
        print("=" * 80)
        print(f"   Best Model: {best_model_name}")
        print(f"   Testing R²: {best_r2:.4f}")
        print(f"   Variance Explained: {best_r2*100:.1f}%")
        print(f"   Training Samples: {self.training_stats['train_samples']:,}")
        print(f"   Testing Samples: {self.training_stats['test_samples']:,}")
        print(f"   Features Used: {self.training_stats['features_count']}")
        
        return best_model_name, best_r2
    
    def run_complete_analysis(self):
        """Run complete analysis on all Euro 2024 data"""
        print("🏆 FINAL MOMENTUM MODEL - COMPLETE EURO 2024 ANALYSIS")
        print("=" * 80)
        
        # Load data
        if not self.load_complete_data():
            return False
        
        # Create training dataset
        training_df = self.create_training_dataset()
        if len(training_df) == 0:
            print("❌ No training data created")
            return False
        
        # Train models
        feature_columns = self.train_final_models(training_df)
        
        # Generate performance report
        best_model, best_r2 = self.generate_final_performance_report()
        
        print(f"\n✅ FINAL ANALYSIS COMPLETE!")
        print(f"   🏆 Best Model: {best_model}")
        print(f"   📊 Best Performance: {best_r2:.4f} R² ({best_r2*100:.1f}% variance explained)")
        print(f"   📈 Total Samples: {self.training_stats['total_samples']:,}")
        print(f"   🔢 Features: {self.training_stats['features_count']}")
        
        return True

def main():
    """Main execution function"""
    print("🚀 APPLYING FINAL MOMENTUM MODEL TO COMPLETE EURO 2024 DATA")
    print("=" * 80)
    
    model = FinalMomentumModel()
    success = model.run_complete_analysis()
    
    if success:
        print("\n🎉 COMPLETE ANALYSIS SUCCESSFUL!")
        print("All Euro 2024 data has been processed with the final momentum model.")
    else:
        print("\n❌ Analysis failed. Check data availability.")

if __name__ == "__main__":
    main() 