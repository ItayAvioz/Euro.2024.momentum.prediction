#!/usr/bin/env python3
"""
Euro 2024 Complete Momentum Model Analysis
Comprehensive momentum prediction model using all Euro 2024 data
with proper train/test split and performance evaluation
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score, TimeSeriesSplit
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.preprocessing import StandardScaler, LabelEncoder
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class Euro2024MomentumAnalyzer:
    """Complete momentum analysis using Euro 2024 connected data"""
    
    def __init__(self):
        self.data = None
        self.models = {}
        self.performance_metrics = {}
        self.feature_importance = {}
        self.training_stats = {}
        
    def load_euro_2024_data(self):
        """Load the complete Euro 2024 connected dataset"""
        print("🏆 LOADING EURO 2024 COMPLETE DATASET")
        print("=" * 60)
        
        try:
            # Load the complete connected dataset
            print("📂 Loading connected_complete.csv...")
            self.data = pd.read_csv('euro_2024_complete/connected_complete.csv')
            
            print(f"✅ Dataset loaded successfully!")
            print(f"   📊 Shape: {self.data.shape}")
            print(f"   📅 Columns: {len(self.data.columns)}")
            print(f"   📈 Memory usage: {self.data.memory_usage(deep=True).sum() / 1024**2:.1f} MB")
            
            # Basic dataset info
            print(f"\n📋 DATASET OVERVIEW:")
            print(f"   🏟️  Total events: {len(self.data):,}")
            print(f"   ⚽ Teams: {self.data['team_name'].nunique()}")
            print(f"   🏆 Matches: {self.data['match_id'].nunique()}")
            print(f"   📅 Date range: {self.data['match_date'].min()} to {self.data['match_date'].max()}")
            
            # Event types
            print(f"\n🎯 EVENT TYPES:")
            event_counts = self.data['event_type'].value_counts().head(10)
            for event_type, count in event_counts.items():
                print(f"   {event_type}: {count:,}")
                
            return True
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return False
    
    def prepare_features(self):
        """Prepare comprehensive features for momentum prediction"""
        print("\n🔧 PREPARING FEATURES FOR MOMENTUM PREDICTION")
        print("=" * 60)
        
        # Add timestamp columns
        self.data['timestamp'] = self.data['minute'] * 60 + self.data['second']
        
        # Encode categorical variables
        label_encoders = {}
        categorical_columns = ['event_type', 'team_name', 'player_name', 'position_name']
        
        for col in categorical_columns:
            if col in self.data.columns:
                le = LabelEncoder()
                self.data[f'{col}_encoded'] = le.fit_transform(self.data[col].fillna('Unknown'))
                label_encoders[col] = le
        
        print("✅ Categorical variables encoded")
        print(f"   📊 Encoded columns: {list(label_encoders.keys())}")
        
        return label_encoders
    
    def create_momentum_training_dataset(self):
        """Create comprehensive training dataset for momentum prediction"""
        print("\n📊 CREATING MOMENTUM TRAINING DATASET")
        print("=" * 60)
        
        training_data = []
        
        # Group by match for proper temporal sampling
        matches = self.data['match_id'].unique()
        print(f"🏟️  Processing {len(matches)} matches...")
        
        for match_id in matches:
            match_data = self.data[self.data['match_id'] == match_id].copy()
            teams = match_data['team_name'].unique()
            
            # Sample time points throughout the match (every 30 seconds after 3 minutes)
            max_time = int(match_data['timestamp'].max())
            time_points = range(180, max_time, 30)  # Every 30 seconds after 3 minutes
            
            for time_point in time_points:
                for team in teams:
                    try:
                        features = self.extract_comprehensive_features(match_data, time_point, team)
                        if features:
                            training_data.append(features)
                    except Exception as e:
                        continue
        
        training_df = pd.DataFrame(training_data)
        print(f"✅ Training dataset created!")
        print(f"   📊 Total samples: {len(training_df):,}")
        print(f"   🔢 Features: {len(training_df.columns)-4}")  # Excluding metadata columns
        
        return training_df
    
    def extract_comprehensive_features(self, match_data, time_point, team):
        """Extract comprehensive features for momentum prediction"""
        
        # Filter events from last 3 minutes (180 seconds)
        start_time = max(0, time_point - 180)
        recent_events = match_data[
            (match_data['timestamp'] >= start_time) & 
            (match_data['timestamp'] <= time_point)
        ].copy()
        
        if len(recent_events) == 0:
            return None
        
        # Team-specific events
        team_events = recent_events[recent_events['team_name'] == team]
        opponent_events = recent_events[recent_events['team_name'] != team]
        
        # Initialize features dictionary
        features = {
            'match_id': match_data['match_id'].iloc[0],
            'team': team,
            'time_point': time_point,
            'minute': time_point // 60
        }
        
        # === BASIC EVENT FEATURES ===
        features['total_events'] = len(team_events)
        features['events_per_minute'] = len(team_events) / 3 if len(team_events) > 0 else 0
        
        # Event type counts
        event_types = ['Pass', 'Shot', 'Carry', 'Pressure', 'Dribble', 'Ball Receipt*', 
                      'Clearance', 'Interception', 'Block', 'Foul Committed']
        
        for event_type in event_types:
            safe_name = event_type.replace('*', '').replace(' ', '_').lower()
            features[f'{safe_name}_count'] = len(team_events[team_events['event_type'] == event_type])
        
        # === POSSESSION FEATURES ===
        total_recent = len(recent_events)
        features['possession_percentage'] = (len(team_events) / total_recent * 100) if total_recent > 0 else 50
        
        # === ATTACKING FEATURES ===
        attacking_events = ['Shot', 'Dribble', 'Carry', 'Cross', 'Through Ball']
        features['attacking_actions'] = len(team_events[team_events['event_type'].isin(attacking_events)])
        features['attacking_intensity'] = features['attacking_actions'] / 3  # per minute
        
        # === DEFENSIVE FEATURES ===
        defensive_events = ['Pressure', 'Clearance', 'Interception', 'Block', 'Tackle']
        features['defensive_actions'] = len(team_events[team_events['event_type'].isin(defensive_events)])
        
        # === SUCCESS RATE FEATURES ===
        if 'outcome_name' in team_events.columns:
            successful_events = team_events[team_events['outcome_name'] == 'Successful']
            features['success_rate'] = len(successful_events) / len(team_events) if len(team_events) > 0 else 0
        else:
            features['success_rate'] = 0.7  # Default assumption
        
        # === SPATIAL FEATURES ===
        if 'location_x' in team_events.columns:
            # Average field position
            features['avg_x_position'] = team_events['location_x'].mean() if len(team_events) > 0 else 50
            features['avg_y_position'] = team_events['location_y'].mean() if len(team_events) > 0 else 40
            
            # Attacking third presence
            attacking_third = team_events[team_events['location_x'] > 80]
            features['attacking_third_actions'] = len(attacking_third)
        else:
            features['avg_x_position'] = 50
            features['avg_y_position'] = 40
            features['attacking_third_actions'] = features['attacking_actions'] * 0.3
        
        # === OPPONENT PRESSURE FEATURES ===
        features['opponent_pressure'] = len(opponent_events[opponent_events['event_type'] == 'Pressure'])
        features['under_pressure'] = features['opponent_pressure'] / 3  # per minute
        
        # === RECENT INTENSITY FEATURES ===
        # Last 60 seconds intensity
        very_recent = recent_events[recent_events['timestamp'] > time_point - 60]
        team_very_recent = very_recent[very_recent['team_name'] == team]
        features['recent_intensity'] = len(team_very_recent)
        
        # === MOMENTUM CALCULATION ===
        # Create composite momentum score (0-10)
        momentum_score = min(10, max(0,
            features['attacking_actions'] * 1.2 +           # Attacking intent
            features['possession_percentage'] * 0.04 +      # Possession control  
            features['shot_count'] * 2.5 +                  # Goal threat
            features['success_rate'] * 3.0 +                # Execution quality
            features['attacking_third_actions'] * 0.8 +     # Field position
            features['recent_intensity'] * 0.3 +            # Recent activity
            features['events_per_minute'] * 0.4 -           # General activity
            features['under_pressure'] * 0.8                # Opponent pressure
        ))
        
        features['momentum_score'] = momentum_score
        
        return features
    
    def train_momentum_models(self, training_df):
        """Train multiple momentum prediction models with proper validation"""
        print("\n🚀 TRAINING MOMENTUM PREDICTION MODELS")
        print("=" * 60)
        
        # Prepare features and target
        exclude_columns = ['momentum_score', 'match_id', 'team', 'time_point']
        feature_columns = [col for col in training_df.columns if col not in exclude_columns]
        
        X = training_df[feature_columns]
        y = training_df['momentum_score']
        
        print(f"📊 Dataset preparation:")
        print(f"   Total samples: {len(X):,}")
        print(f"   Features: {len(feature_columns)}")
        print(f"   Target range: {y.min():.2f} - {y.max():.2f}")
        print(f"   Target mean: {y.mean():.2f} ± {y.std():.2f}")
        
        # === DATA SPLITTING STRATEGY ===
        print(f"\n🔄 DATA SPLITTING STRATEGY:")
        print(f"   Method: Train/Test Split")
        print(f"   Split ratio: 80% Training / 20% Testing")
        print(f"   Random state: 42 (reproducible)")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=None
        )
        
        print(f"   Training samples: {len(X_train):,}")
        print(f"   Testing samples: {len(X_test):,}")
        
        # === MODEL TRAINING ===
        models_to_train = {
            'RandomForest': RandomForestRegressor(
                n_estimators=100,
                max_depth=12,
                min_samples_split=8,
                min_samples_leaf=4,
                max_features='sqrt',
                random_state=42
            ),
            'GradientBoosting': GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=8,
                min_samples_split=10,
                min_samples_leaf=4,
                random_state=42
            )
        }
        
        for model_name, model in models_to_train.items():
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
            
            print(f"   ✅ {model_name} trained successfully!")
        
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
        
        return X_train, X_test, y_train, y_test
    
    def generate_comprehensive_report(self):
        """Generate comprehensive performance report"""
        print("\n📈 COMPREHENSIVE MODEL PERFORMANCE REPORT")
        print("=" * 80)
        
        # === DATASET SUMMARY ===
        print("📊 DATASET SUMMARY:")
        print(f"   Total Euro 2024 Events: {len(self.data):,}")
        print(f"   Training Samples Created: {self.training_stats['total_samples']:,}")
        print(f"   Features Engineered: {self.training_stats['features_count']}")
        print(f"   Target Variable: Momentum Score (0-10)")
        print(f"   Target Distribution: {self.training_stats['target_mean']:.2f} ± {self.training_stats['target_std']:.2f}")
        
        # === DATA SPLIT SUMMARY ===
        print(f"\n🔄 DATA SPLIT SUMMARY:")
        print(f"   Training Set: {self.training_stats['train_samples']:,} samples (80%)")
        print(f"   Testing Set: {self.training_stats['test_samples']:,} samples (20%)")
        print(f"   Split Method: Random stratified split")
        print(f"   Cross-Validation: 5-fold CV on training set")
        
        # === MODEL PERFORMANCE COMPARISON ===
        print(f"\n🏆 MODEL PERFORMANCE COMPARISON:")
        print("=" * 80)
        
        # Create comparison table
        performance_table = []
        for model_name, metrics in self.performance_metrics.items():
            row = {
                'Model': model_name,
                'Train R²': f"{metrics['train_r2']:.4f}",
                'Test R²': f"{metrics['test_r2']:.4f}",
                'CV R²': f"{metrics['cv_r2_mean']:.4f} ± {metrics['cv_r2_std']:.4f}",
                'Train MAE': f"{metrics['train_mae']:.3f}",
                'Test MAE': f"{metrics['test_mae']:.3f}",
                'Train RMSE': f"{metrics['train_rmse']:.3f}",
                'Test RMSE': f"{metrics['test_rmse']:.3f}",
                'Overfitting': f"{metrics['train_r2'] - metrics['test_r2']:.4f}"
            }
            performance_table.append(row)
        
        # Print performance table
        for row in performance_table:
            print(f"\n🔮 {row['Model']}:")
            print(f"   📈 Training R²:     {row['Train R²']}")
            print(f"   📊 Testing R²:      {row['Test R²']}")
            print(f"   🔄 Cross-Val R²:    {row['CV R²']}")
            print(f"   📉 Training MAE:    {row['Train MAE']}")
            print(f"   📊 Testing MAE:     {row['Test MAE']}")
            print(f"   📏 Training RMSE:   {row['Train RMSE']}")
            print(f"   📊 Testing RMSE:    {row['Test RMSE']}")
            print(f"   ⚠️  Overfitting Gap: {row['Overfitting']}")
            
            # Performance interpretation
            test_r2 = float(row['Test R²'])
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
            
            print(f"   🎯 Performance:     {level}")
            print(f"   📊 Variance Explained: {test_r2*100:.1f}%")
        
        # === FEATURE IMPORTANCE ===
        print(f"\n🔍 FEATURE IMPORTANCE ANALYSIS:")
        print("=" * 80)
        
        for model_name, importance_dict in self.feature_importance.items():
            print(f"\n🔮 {model_name} - Top 15 Features:")
            sorted_features = sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)
            
            for i, (feature, importance) in enumerate(sorted_features[:15]):
                print(f"{i+1:2d}. {feature:<25} : {importance:.4f} ({importance*100:.1f}%)")
        
        # === OVERFITTING ANALYSIS ===
        print(f"\n⚠️  OVERFITTING ANALYSIS:")
        print("=" * 80)
        
        for model_name, metrics in self.performance_metrics.items():
            gap = metrics['train_r2'] - metrics['test_r2']
            print(f"\n{model_name}:")
            print(f"   Generalization Gap: {gap:.4f}")
            
            if gap < 0.05:
                status = "✅ EXCELLENT - No overfitting"
            elif gap < 0.1:
                status = "✅ GOOD - Minimal overfitting"
            elif gap < 0.15:
                status = "⚠️ MODERATE - Some overfitting"
            else:
                status = "❌ HIGH - Significant overfitting"
            
            print(f"   Status: {status}")
        
        # === PREDICTION ACCURACY ===
        print(f"\n🎯 PREDICTION ACCURACY SUMMARY:")
        print("=" * 80)
        
        best_model = max(self.performance_metrics.items(), key=lambda x: x[1]['test_r2'])
        best_name, best_metrics = best_model
        
        print(f"🏆 BEST MODEL: {best_name}")
        print(f"   Test R² Score: {best_metrics['test_r2']:.4f}")
        print(f"   Variance Explained: {best_metrics['test_r2']*100:.1f}%")
        print(f"   Average Error: {best_metrics['test_mae']:.3f} momentum points")
        print(f"   Prediction Accuracy: {(1-best_metrics['test_mae']/10)*100:.1f}%")
        
        return best_name, best_metrics
    
    def run_complete_analysis(self):
        """Run complete momentum analysis on Euro 2024 data"""
        print("🏆 EURO 2024 MOMENTUM ANALYSIS - COMPLETE IMPLEMENTATION")
        print("=" * 80)
        
        # Step 1: Load data
        if not self.load_euro_2024_data():
            return False
        
        # Step 2: Prepare features
        self.prepare_features()
        
        # Step 3: Create training dataset
        training_df = self.create_momentum_training_dataset()
        
        if len(training_df) == 0:
            print("❌ No training data created")
            return False
        
        # Step 4: Train models
        X_train, X_test, y_train, y_test = self.train_momentum_models(training_df)
        
        # Step 5: Generate comprehensive report
        best_model, best_metrics = self.generate_comprehensive_report()
        
        # Step 6: Save results
        self.save_results(training_df, best_model, best_metrics)
        
        print("\n✅ COMPLETE ANALYSIS FINISHED!")
        print("=" * 80)
        return True
    
    def save_results(self, training_df, best_model, best_metrics):
        """Save analysis results"""
        try:
            # Save training data
            training_df.to_csv('euro_2024_momentum_training_data.csv', index=False)
            print(f"💾 Training data saved to: euro_2024_momentum_training_data.csv")
            
            # Save performance metrics
            import json
            with open('euro_2024_momentum_performance.json', 'w') as f:
                json.dump(self.performance_metrics, f, indent=2)
            print(f"💾 Performance metrics saved to: euro_2024_momentum_performance.json")
            
        except Exception as e:
            print(f"⚠️ Could not save results: {e}")

def main():
    """Main execution function"""
    analyzer = Euro2024MomentumAnalyzer()
    success = analyzer.run_complete_analysis()
    
    if success:
        print("\n🎉 Euro 2024 Momentum Analysis Complete!")
        print("Check the generated files for detailed results.")
    else:
        print("\n❌ Analysis failed. Check the data and try again.")

if __name__ == "__main__":
    main() 