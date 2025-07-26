#!/usr/bin/env python3
"""
Future Momentum Prediction Model - Complete Performance Analysis
Comprehensive report on model performance, features, and techniques
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class FutureMomentumAnalyzer:
    """Complete analysis of future momentum prediction model"""
    
    def __init__(self):
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42
        )
        self.feature_names = []
        self.performance_metrics = {}
        self.feature_importance = {}
        self.training_data = None
        
    def extract_predictive_features(self, events_df, current_time, team_name):
        """Extract comprehensive features for future momentum prediction"""
        
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
        
        # ========== TEAM ACTIVITY FEATURES ==========
        features['team_total_events'] = len(team_events)
        features['team_events_per_minute'] = len(team_events) / 3
        features['team_event_intensity'] = len(team_events[team_events['timestamp'] >= current_time - 60]) * 2
        
        # ========== ATTACKING FEATURES ==========
        features['team_shots'] = len(team_events[team_events['event_type'] == 'Shot'])
        features['team_shot_rate'] = features['team_shots'] / 3
        features['team_carries'] = len(team_events[team_events['event_type'] == 'Carry'])
        features['team_dribbles'] = len(team_events[team_events['event_type'] == 'Dribble'])
        features['team_attacking_actions'] = features['team_shots'] + features['team_carries'] + features['team_dribbles']
        features['team_attacking_rate'] = features['team_attacking_actions'] / 3
        
        # ========== POSSESSION FEATURES ==========
        features['team_passes'] = len(team_events[team_events['event_type'] == 'Pass'])
        features['team_possession_pct'] = (len(team_events) / total_events * 100) if total_events > 0 else 50
        features['team_pass_rate'] = features['team_passes'] / 3
        
        # ========== PRESSURE FEATURES ==========
        features['team_pressure_applied'] = len(team_events[team_events['event_type'] == 'Pressure'])
        features['team_pressure_received'] = len(opponent_events[opponent_events['event_type'] == 'Pressure'])
        features['team_pressure_balance'] = features['team_pressure_applied'] - features['team_pressure_received']
        
        # ========== OPPONENT CONTEXT FEATURES ==========
        features['opponent_total_events'] = len(opponent_events)
        features['opponent_shots'] = len(opponent_events[opponent_events['event_type'] == 'Shot'])
        features['opponent_attacking_actions'] = len(opponent_events[opponent_events['event_type'].isin(['Shot', 'Carry', 'Dribble'])])
        features['opponent_possession_pct'] = (len(opponent_events) / total_events * 100) if total_events > 0 else 50
        
        # ========== COMPARATIVE FEATURES ==========
        features['shot_advantage'] = features['team_shots'] - features['opponent_shots']
        features['possession_advantage'] = features['team_possession_pct'] - features['opponent_possession_pct']
        features['attack_advantage'] = features['team_attacking_actions'] - features['opponent_attacking_actions']
        features['event_dominance'] = features['team_total_events'] - features['opponent_total_events']
        
        # ========== MOMENTUM TREND FEATURES ==========
        # Recent vs earlier activity
        recent_events = team_events[team_events['timestamp'] >= current_time - 60]
        earlier_events = team_events[team_events['timestamp'] < current_time - 60]
        
        features['momentum_trend'] = len(recent_events) - len(earlier_events)
        features['shot_trend'] = len(recent_events[recent_events['event_type'] == 'Shot']) - len(earlier_events[earlier_events['event_type'] == 'Shot'])
        features['attack_trend'] = len(recent_events[recent_events['event_type'].isin(['Shot', 'Carry', 'Dribble'])]) - len(earlier_events[earlier_events['event_type'].isin(['Shot', 'Carry', 'Dribble'])])
        
        # ========== RHYTHM FEATURES ==========
        features['team_consistency'] = len(team_events) / max(1, len(set(team_events['timestamp'] // 30)))  # Events per 30-sec window
        features['opponent_consistency'] = len(opponent_events) / max(1, len(set(opponent_events['timestamp'] // 30)))
        features['rhythm_advantage'] = features['team_consistency'] - features['opponent_consistency']
        
        return features
    
    def calculate_future_momentum(self, events_df, current_time, future_time, team_name):
        """Calculate actual momentum that occurred in future window"""
        
        # Future window: next 3 minutes
        future_window = events_df[
            (events_df['timestamp'] >= current_time) & 
            (events_df['timestamp'] <= future_time)
        ]
        
        team_future_events = future_window[future_window['team_name'] == team_name]
        opponent_future_events = future_window[future_window['team_name'] != team_name]
        
        if len(future_window) == 0:
            return 0
        
        # Calculate comprehensive future momentum score
        future_momentum = min(10, max(0,
            # Attacking dominance
            len(team_future_events[team_future_events['event_type'] == 'Shot']) * 2.5 +
            len(team_future_events[team_future_events['event_type'].isin(['Carry', 'Dribble'])]) * 1.5 +
            
            # Possession control
            (len(team_future_events) / len(future_window) * 100) * 0.05 +
            
            # Pressure dynamics
            len(team_future_events[team_future_events['event_type'] == 'Pressure']) * 1.0 -
            len(opponent_future_events[opponent_future_events['event_type'] == 'Pressure']) * 0.8 +
            
            # General activity
            len(team_future_events) * 0.2 +
            
            # Comparative advantage
            (len(team_future_events) - len(opponent_future_events)) * 0.3
        ))
        
        return future_momentum
    
    def create_comprehensive_training_data(self, events_df):
        """Create comprehensive training dataset"""
        
        print("📊 Creating comprehensive training dataset...")
        
        # Add timestamp
        events_df['timestamp'] = events_df['minute'] * 60 + events_df['second']
        
        training_data = []
        teams = events_df['team_name'].dropna().unique()
        
        # Sample time points (every 30 seconds, ensuring 3-min buffer)
        max_time = int(events_df['timestamp'].max())
        time_points = range(180, max_time - 180, 30)
        
        print(f"   🔍 Analyzing {len(time_points)} time points for {len(teams)} teams...")
        
        for current_time in time_points:
            future_time = current_time + 180
            
            if future_time > max_time:
                continue
                
            for team in teams:
                # Extract current features
                features = self.extract_predictive_features(events_df, current_time, team)
                
                # Calculate future momentum (target)
                future_momentum = self.calculate_future_momentum(events_df, current_time, future_time, team)
                
                # Add metadata
                features['future_momentum'] = future_momentum
                features['team'] = team
                features['current_time'] = current_time
                features['future_time'] = future_time
                
                training_data.append(features)
        
        df = pd.DataFrame(training_data)
        print(f"   ✅ Created {len(df)} training samples")
        
        return df
    
    def train_and_evaluate(self, events_df):
        """Train model and perform comprehensive evaluation"""
        
        print("🚀 TRAINING AND EVALUATING FUTURE MOMENTUM PREDICTION MODEL")
        print("=" * 80)
        
        # Create training data
        self.training_data = self.create_comprehensive_training_data(events_df)
        
        if len(self.training_data) == 0:
            print("❌ No training data available")
            return None
        
        # Prepare features and target
        feature_columns = [col for col in self.training_data.columns 
                          if col not in ['future_momentum', 'team', 'current_time', 'future_time']]
        
        self.feature_names = feature_columns
        X = self.training_data[feature_columns]
        y = self.training_data['future_momentum']
        
        # Split data for validation
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train model
        self.model.fit(X_train, y_train)
        
        # Predictions
        y_train_pred = self.model.predict(X_train)
        y_test_pred = self.model.predict(X_test)
        
        # Performance metrics
        self.performance_metrics = {
            'train_r2': r2_score(y_train, y_train_pred),
            'test_r2': r2_score(y_test, y_test_pred),
            'train_mse': mean_squared_error(y_train, y_train_pred),
            'test_mse': mean_squared_error(y_test, y_test_pred),
            'train_mae': mean_absolute_error(y_train, y_train_pred),
            'test_mae': mean_absolute_error(y_test, y_test_pred),
            'train_samples': len(X_train),
            'test_samples': len(X_test),
            'features_count': len(feature_columns),
            'mean_future_momentum': y.mean(),
            'std_future_momentum': y.std()
        }
        
        # Cross-validation
        cv_scores = cross_val_score(self.model, X, y, cv=5, scoring='r2')
        self.performance_metrics['cv_r2_mean'] = cv_scores.mean()
        self.performance_metrics['cv_r2_std'] = cv_scores.std()
        
        # Feature importance
        self.feature_importance = dict(zip(feature_columns, self.model.feature_importances_))
        
        return self.performance_metrics
    
    def generate_performance_report(self):
        """Generate comprehensive performance report"""
        
        print("\n📈 MODEL PERFORMANCE REPORT")
        print("=" * 80)
        
        metrics = self.performance_metrics
        
        print("🎯 PREDICTION ACCURACY:")
        print(f"   Training R² Score:     {metrics['train_r2']:.4f}")
        print(f"   Testing R² Score:      {metrics['test_r2']:.4f}")
        print(f"   Cross-Validation R²:   {metrics['cv_r2_mean']:.4f} (±{metrics['cv_r2_std']:.4f})")
        print(f"   Generalization Gap:    {metrics['train_r2'] - metrics['test_r2']:.4f}")
        
        print("\n📊 ERROR METRICS:")
        print(f"   Training MAE:          {metrics['train_mae']:.3f}")
        print(f"   Testing MAE:           {metrics['test_mae']:.3f}")
        print(f"   Training RMSE:         {np.sqrt(metrics['train_mse']):.3f}")
        print(f"   Testing RMSE:          {np.sqrt(metrics['test_mse']):.3f}")
        
        print("\n🔢 DATASET STATISTICS:")
        print(f"   Training Samples:      {metrics['train_samples']:,}")
        print(f"   Testing Samples:       {metrics['test_samples']:,}")
        print(f"   Total Features:        {metrics['features_count']}")
        print(f"   Target Mean:           {metrics['mean_future_momentum']:.2f}")
        print(f"   Target Std:            {metrics['std_future_momentum']:.2f}")
        
        # Performance interpretation
        print("\n🎯 PERFORMANCE INTERPRETATION:")
        test_r2 = metrics['test_r2']
        if test_r2 >= 0.9:
            performance_level = "EXCELLENT"
        elif test_r2 >= 0.8:
            performance_level = "VERY GOOD"
        elif test_r2 >= 0.7:
            performance_level = "GOOD"
        elif test_r2 >= 0.6:
            performance_level = "MODERATE"
        else:
            performance_level = "POOR"
        
        print(f"   Performance Level:     {performance_level}")
        print(f"   Variance Explained:    {test_r2*100:.1f}%")
        print(f"   Prediction Accuracy:   {(1-metrics['test_mae']/10)*100:.1f}%")
        
    def analyze_feature_importance(self):
        """Analyze and report feature importance"""
        
        print("\n🔍 FEATURE IMPORTANCE ANALYSIS")
        print("=" * 80)
        
        # Sort features by importance
        sorted_features = sorted(self.feature_importance.items(), key=lambda x: x[1], reverse=True)
        
        print("📊 TOP 15 MOST IMPORTANT FEATURES:")
        for i, (feature, importance) in enumerate(sorted_features[:15]):
            print(f"{i+1:2d}. {feature:<25} : {importance:.4f} ({importance*100:.1f}%)")
        
        # Feature categories
        print("\n📂 FEATURE CATEGORIES:")
        
        categories = {
            'Attacking': ['shot', 'attack', 'carry', 'dribble'],
            'Possession': ['possession', 'pass'],
            'Pressure': ['pressure'],
            'Comparative': ['advantage', 'dominance'],
            'Trend': ['trend'],
            'Opponent': ['opponent'],
            'Rhythm': ['consistency', 'rhythm']
        }
        
        for category, keywords in categories.items():
            category_importance = sum(imp for feat, imp in self.feature_importance.items() 
                                    if any(keyword in feat.lower() for keyword in keywords))
            print(f"   {category:<12} : {category_importance:.4f} ({category_importance*100:.1f}%)")
        
        # Top features by category
        print("\n🏆 TOP FEATURE IN EACH CATEGORY:")
        for category, keywords in categories.items():
            category_features = [(feat, imp) for feat, imp in self.feature_importance.items() 
                               if any(keyword in feat.lower() for keyword in keywords)]
            if category_features:
                top_feature = max(category_features, key=lambda x: x[1])
                print(f"   {category:<12} : {top_feature[0]} ({top_feature[1]:.4f})")
    
    def demonstrate_techniques_and_methods(self):
        """Demonstrate techniques and methods used"""
        
        print("\n🛠️ TECHNIQUES AND METHODS")
        print("=" * 80)
        
        print("🤖 MACHINE LEARNING ALGORITHM:")
        print("   Algorithm:            Random Forest Regressor")
        print("   Estimators:           100 decision trees")
        print("   Max Depth:            15 levels")
        print("   Min Samples Split:    5 samples")
        print("   Min Samples Leaf:     2 samples")
        print("   Random State:         42 (reproducible)")
        
        print("\n🔧 FEATURE ENGINEERING TECHNIQUES:")
        print("   1. Temporal Windows:    3-minute sliding windows")
        print("   2. Rate Features:       Events per minute calculations")
        print("   3. Comparative Features: Team vs opponent metrics")
        print("   4. Trend Analysis:      Recent vs earlier activity")
        print("   5. Pressure Dynamics:   Applied vs received pressure")
        print("   6. Rhythm Metrics:      Consistency over time windows")
        print("   7. Advantage Scoring:   Differential calculations")
        
        print("\n📊 DATA PREPROCESSING:")
        print("   Time Sampling:        Every 30 seconds")
        print("   Window Size:          180 seconds (3 minutes)")
        print("   Buffer Requirements:  3-minute future buffer")
        print("   Event Aggregation:    Count and rate calculations")
        print("   Missing Value Handling: Default values for empty windows")
        
        print("\n🎯 TARGET VARIABLE CREATION:")
        print("   Future Window:        Next 3 minutes after current time")
        print("   Momentum Formula:     Weighted combination of:")
        print("                        - Shots (2.5x weight)")
        print("                        - Attacks (1.5x weight)")
        print("                        - Possession (0.05x weight)")
        print("                        - Pressure (1.0x weight)")
        print("                        - Activity (0.2x weight)")
        print("                        - Comparative (0.3x weight)")
        print("   Score Range:          0-10 (clamped)")
        
        print("\n📈 MODEL VALIDATION:")
        print("   Train/Test Split:     80/20 split")
        print("   Cross-Validation:     5-fold CV")
        print("   Metrics:              R², MAE, MSE, RMSE")
        print("   Overfitting Check:    Train vs test performance")
        
        print("\n🚀 ADVANCED TECHNIQUES:")
        print("   1. Ensemble Method:     Random Forest (bagging)")
        print("   2. Pattern Recognition: Tree-based feature interactions")
        print("   3. Temporal Modeling:   Time-series feature engineering")
        print("   4. Contextual Features: Opponent-aware metrics")
        print("   5. Trend Extraction:    Momentum direction analysis")

def create_sample_data_and_test():
    """Create sample data and test the model"""
    
    print("📊 CREATING SAMPLE EURO 2024 DATA")
    print("=" * 80)
    
    # Create realistic sample data
    np.random.seed(42)
    sample_data = []
    teams = ['Netherlands', 'England']
    
    # Create 90 minutes of events with realistic patterns
    for minute in range(90):
        for second in range(0, 60, 10):  # Every 10 seconds
            timestamp = minute * 60 + second
            
            # Event probability varies by game phase
            if minute < 15:  # Early game
                event_prob = 0.5
            elif minute < 45:  # Mid first half
                event_prob = 0.7
            elif minute < 60:  # Early second half
                event_prob = 0.6
            else:  # Late game
                event_prob = 0.8
            
            if np.random.random() < event_prob:
                # Team selection with some momentum patterns
                if minute < 30:
                    team = np.random.choice(teams, p=[0.45, 0.55])  # England slightly ahead
                elif minute < 60:
                    team = np.random.choice(teams, p=[0.55, 0.45])  # Netherlands comeback
                else:
                    team = np.random.choice(teams, p=[0.6, 0.4])   # Netherlands dominance
                
                # Event type probabilities
                event_type = np.random.choice(
                    ['Pass', 'Shot', 'Carry', 'Dribble', 'Pressure', 'Ball Receipt*'],
                    p=[0.35, 0.08, 0.20, 0.07, 0.15, 0.15]
                )
                
                sample_data.append({
                    'minute': minute,
                    'second': second,
                    'timestamp': timestamp,
                    'event_type': event_type,
                    'team_name': team
                })
    
    events_df = pd.DataFrame(sample_data)
    print(f"   ✅ Created {len(events_df)} realistic events")
    
    # Initialize and train model
    analyzer = FutureMomentumAnalyzer()
    performance = analyzer.train_and_evaluate(events_df)
    
    if performance:
        analyzer.generate_performance_report()
        analyzer.analyze_feature_importance()
        analyzer.demonstrate_techniques_and_methods()
        
        return analyzer
    else:
        print("❌ Model training failed")
        return None

def main():
    """Main function to run complete analysis"""
    
    print("🔮 FUTURE MOMENTUM PREDICTION MODEL - COMPLETE ANALYSIS")
    print("=" * 80)
    
    analyzer = create_sample_data_and_test()
    
    if analyzer:
        print("\n🎯 SUMMARY")
        print("=" * 80)
        
        metrics = analyzer.performance_metrics
        print(f"✅ Model successfully trained on {metrics['train_samples'] + metrics['test_samples']:,} samples")
        print(f"✅ Achieved {metrics['test_r2']:.1%} prediction accuracy")
        print(f"✅ Using {metrics['features_count']} engineered features")
        print(f"✅ Mean prediction error: {metrics['test_mae']:.2f} points")
        
        # Top 3 features
        top_features = sorted(analyzer.feature_importance.items(), key=lambda x: x[1], reverse=True)[:3]
        print(f"✅ Top predictive features:")
        for i, (feature, importance) in enumerate(top_features):
            print(f"   {i+1}. {feature} ({importance:.1%})")

if __name__ == "__main__":
    main() 