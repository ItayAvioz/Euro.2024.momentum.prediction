#!/usr/bin/env python3
"""
Corrected Momentum Model with Proper Temporal Data Handling
Fixes the temporal data leakage issues in the original models
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import os
import warnings
warnings.filterwarnings('ignore')

class CorrectedMomentumModel:
    """
    Momentum prediction model with proper temporal data handling
    Fixes the critical temporal data leakage issues
    """
    
    def __init__(self):
        self.model = None
        self.feature_names = []
        self.is_trained = False
        self.performance_metrics = {}
        
    def load_euro_2024_data(self):
        """Load Euro 2024 data properly"""
        print("📊 Loading Euro 2024 Dataset...")
        
        data_dir = "../Data"
        
        try:
            events_df = pd.read_csv(os.path.join(data_dir, "events_complete.csv"))
            matches_df = pd.read_csv(os.path.join(data_dir, "matches_complete.csv"))
            
            print(f"✅ Events: {len(events_df):,}")
            print(f"✅ Matches: {len(matches_df):,}")
            
            return events_df, matches_df
        except FileNotFoundError as e:
            print(f"❌ Error: {e}")
            return None, None
    
    def create_temporal_momentum_data(self, events_df, sample_matches=20):
        """Create momentum data with proper temporal handling"""
        print(f"\n🔧 CREATING TEMPORAL MOMENTUM DATA")
        print("=" * 50)
        
        # Use a subset of matches for reasonable processing time
        unique_matches = events_df['match_id'].unique()
        if len(unique_matches) > sample_matches:
            unique_matches = unique_matches[:sample_matches]
            print(f"📊 Using {sample_matches} matches for analysis")
        
        momentum_records = []
        
        for i, match_id in enumerate(unique_matches):
            print(f"Processing match {i+1}/{len(unique_matches)}: {match_id}")
            
            match_events = events_df[events_df['match_id'] == match_id].copy()
            
            # Ensure temporal ordering
            match_events = match_events.sort_values('minute')
            
            # Create timestamp in seconds
            match_events['timestamp'] = match_events['minute'] * 60 + match_events['second']
            
            teams = match_events['team'].dropna().unique()
            
            for team in teams:
                # Sample every 3 minutes starting from minute 6
                max_minute = int(match_events['minute'].max())
                
                for minute in range(6, max_minute - 3, 3):  # 3-minute intervals
                    current_start = minute - 3
                    current_end = minute
                    future_start = minute
                    future_end = minute + 3
                    
                    # Current window (for features)
                    current_events = match_events[
                        (match_events['minute'] >= current_start) & 
                        (match_events['minute'] < current_end)
                    ]
                    
                    # Future window (for target)
                    future_events = match_events[
                        (match_events['minute'] >= future_start) & 
                        (match_events['minute'] < future_end)
                    ]
                    
                    if len(current_events) == 0:
                        continue
                    
                    # Extract features and target
                    features = self.extract_temporal_features(current_events, team)
                    future_momentum = self.calculate_future_momentum(future_events, team)
                    
                    # Create record with proper temporal metadata
                    record = {
                        'match_id': match_id,
                        'team': team,
                        'minute': minute,
                        'match_index': i,  # For temporal ordering across matches
                        'global_time': i * 1000 + minute,  # Global temporal order
                        'future_momentum': future_momentum,
                        **features
                    }
                    
                    momentum_records.append(record)
        
        momentum_df = pd.DataFrame(momentum_records)
        
        print(f"✅ Created {len(momentum_df)} temporal samples")
        print(f"   📊 Matches: {momentum_df['match_id'].nunique()}")
        print(f"   ⏱️  Time range: {momentum_df['minute'].min()}-{momentum_df['minute'].max()} minutes")
        print(f"   🎯 Target range: {momentum_df['future_momentum'].min():.2f}-{momentum_df['future_momentum'].max():.2f}")
        
        return momentum_df
    
    def extract_temporal_features(self, events_window, team):
        """Extract features from temporal window"""
        team_events = events_window[events_window['team'] == team]
        all_events = events_window
        
        # Basic counting features
        total_events = len(team_events)
        shot_events = len(team_events[team_events['type'].str.contains('Shot', na=False)])
        attacking_events = len(team_events[team_events['type'].str.contains('Shot|Carry|Dribble', na=False)])
        pass_events = len(team_events[team_events['type'].str.contains('Pass', na=False)])
        
        # Possession and intensity
        possession_pct = (total_events / (len(all_events) + 1)) * 100
        events_per_minute = total_events / 3.0
        
        # Success rates
        successful_actions = len(team_events[team_events.get('outcome', '') == 'Complete'])
        success_rate = (successful_actions / (total_events + 1)) * 100
        
        # Location-based features
        attacking_third_events = len(team_events[team_events.get('location_x', 0) > 70])
        
        return {
            'total_events': total_events,
            'shot_events': shot_events,
            'attacking_events': attacking_events,
            'pass_events': pass_events,
            'possession_pct': possession_pct,
            'events_per_minute': events_per_minute,
            'success_rate': success_rate,
            'attacking_third_events': attacking_third_events
        }
    
    def calculate_future_momentum(self, future_events, team):
        """Calculate future momentum target"""
        team_future = future_events[future_events['team'] == team]
        
        if len(team_future) == 0:
            return 5.0  # Neutral momentum
        
        # Extract features from future window
        future_features = self.extract_temporal_features(future_events, team)
        
        # Calculate momentum score (0-10)
        momentum = (
            future_features['shot_events'] * 2.0 +
            future_features['attacking_events'] * 1.2 +
            future_features['possession_pct'] * 0.04 +
            future_features['events_per_minute'] * 0.5 +
            future_features['success_rate'] * 0.02 +
            future_features['attacking_third_events'] * 1.5
        )
        
        return max(0, min(10, momentum))
    
    def correct_temporal_split(self, momentum_data, method='match_based'):
        """Implement correct temporal splitting"""
        print(f"\n🎯 TEMPORAL DATA SPLITTING")
        print("=" * 40)
        
        if method == 'match_based':
            # Method 1: Match-based split (RECOMMENDED)
            matches = momentum_data['match_id'].unique()
            np.random.seed(42)  # For reproducibility
            np.random.shuffle(matches)
            
            n_train = int(len(matches) * 0.8)
            train_matches = matches[:n_train]
            test_matches = matches[n_train:]
            
            train_data = momentum_data[momentum_data['match_id'].isin(train_matches)]
            test_data = momentum_data[momentum_data['match_id'].isin(test_matches)]
            
            print(f"   📊 Match-based split:")
            print(f"   Training matches: {len(train_matches)}")
            print(f"   Testing matches: {len(test_matches)}")
            
        elif method == 'temporal':
            # Method 2: Temporal split
            sorted_data = momentum_data.sort_values('global_time')
            split_idx = int(len(sorted_data) * 0.8)
            
            train_data = sorted_data.iloc[:split_idx]
            test_data = sorted_data.iloc[split_idx:]
            
            print(f"   ⏱️  Temporal split:")
            print(f"   Split at 80% of timeline")
            
        print(f"   Training samples: {len(train_data)}")
        print(f"   Testing samples: {len(test_data)}")
        
        return train_data, test_data
    
    def train_with_temporal_validation(self, momentum_data):
        """Train model with proper temporal validation"""
        print(f"\n🚀 TRAINING WITH TEMPORAL VALIDATION")
        print("=" * 50)
        
        # Prepare features
        feature_cols = ['total_events', 'shot_events', 'attacking_events', 
                       'pass_events', 'possession_pct', 'events_per_minute', 
                       'success_rate', 'attacking_third_events']
        
        self.feature_names = feature_cols
        
        X = momentum_data[feature_cols]
        y = momentum_data['future_momentum']
        
        print(f"📊 Dataset preparation:")
        print(f"   Features: {len(feature_cols)}")
        print(f"   Samples: {len(X)}")
        print(f"   Target range: {y.min():.2f}-{y.max():.2f}")
        
        # Method 1: Match-based split evaluation
        train_data, test_data = self.correct_temporal_split(momentum_data, 'match_based')
        
        X_train = train_data[feature_cols]
        y_train = train_data['future_momentum']
        X_test = test_data[feature_cols]
        y_test = test_data['future_momentum']
        
        # Train model
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=8,
            min_samples_split=5,
            random_state=42
        )
        
        self.model.fit(X_train, y_train)
        self.is_trained = True
        
        # Evaluate
        y_train_pred = self.model.predict(X_train)
        y_test_pred = self.model.predict(X_test)
        
        # Calculate metrics
        train_r2 = r2_score(y_train, y_train_pred)
        test_r2 = r2_score(y_test, y_test_pred)
        train_mae = mean_absolute_error(y_train, y_train_pred)
        test_mae = mean_absolute_error(y_test, y_test_pred)
        
        print(f"\n📈 MATCH-BASED SPLIT RESULTS:")
        print(f"   Training R²: {train_r2:.3f}")
        print(f"   Testing R²: {test_r2:.3f}")
        print(f"   Training MAE: {train_mae:.3f}")
        print(f"   Testing MAE: {test_mae:.3f}")
        print(f"   Generalization Gap: {train_r2 - test_r2:.3f}")
        
        # Method 2: Time Series Cross-Validation
        print(f"\n⏱️  TIME SERIES CROSS-VALIDATION:")
        
        # Sort by temporal order
        sorted_data = momentum_data.sort_values('global_time')
        X_sorted = sorted_data[feature_cols]
        y_sorted = sorted_data['future_momentum']
        
        tscv = TimeSeriesSplit(n_splits=5)
        cv_scores = []
        
        for fold, (train_idx, test_idx) in enumerate(tscv.split(X_sorted)):
            X_fold_train = X_sorted.iloc[train_idx]
            y_fold_train = y_sorted.iloc[train_idx]
            X_fold_test = X_sorted.iloc[test_idx]
            y_fold_test = y_sorted.iloc[test_idx]
            
            fold_model = RandomForestRegressor(n_estimators=100, random_state=42)
            fold_model.fit(X_fold_train, y_fold_train)
            
            y_fold_pred = fold_model.predict(X_fold_test)
            fold_r2 = r2_score(y_fold_test, y_fold_pred)
            cv_scores.append(fold_r2)
            
            print(f"   Fold {fold + 1}: R² = {fold_r2:.3f}")
        
        cv_mean = np.mean(cv_scores)
        cv_std = np.std(cv_scores)
        
        print(f"   Cross-validation: {cv_mean:.3f} ± {cv_std:.3f}")
        
        # Store performance metrics
        self.performance_metrics = {
            'match_based_train_r2': train_r2,
            'match_based_test_r2': test_r2,
            'match_based_train_mae': train_mae,
            'match_based_test_mae': test_mae,
            'cv_mean_r2': cv_mean,
            'cv_std_r2': cv_std,
            'train_samples': len(X_train),
            'test_samples': len(X_test)
        }
        
        return self.performance_metrics
    
    def compare_with_incorrect_split(self, momentum_data):
        """Compare correct vs incorrect splitting to demonstrate the difference"""
        print(f"\n⚠️  COMPARISON: CORRECT vs INCORRECT SPLITTING")
        print("=" * 60)
        
        feature_cols = self.feature_names
        X = momentum_data[feature_cols]
        y = momentum_data['future_momentum']
        
        # INCORRECT: Random split (current approach)
        from sklearn.model_selection import train_test_split
        X_train_wrong, X_test_wrong, y_train_wrong, y_test_wrong = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        model_wrong = RandomForestRegressor(n_estimators=100, random_state=42)
        model_wrong.fit(X_train_wrong, y_train_wrong)
        y_pred_wrong = model_wrong.predict(X_test_wrong)
        
        r2_wrong = r2_score(y_test_wrong, y_pred_wrong)
        mae_wrong = mean_absolute_error(y_test_wrong, y_pred_wrong)
        
        # CORRECT: Match-based split
        train_data, test_data = self.correct_temporal_split(momentum_data, 'match_based')
        X_train_correct = train_data[feature_cols]
        y_train_correct = train_data['future_momentum']
        X_test_correct = test_data[feature_cols]
        y_test_correct = test_data['future_momentum']
        
        model_correct = RandomForestRegressor(n_estimators=100, random_state=42)
        model_correct.fit(X_train_correct, y_train_correct)
        y_pred_correct = model_correct.predict(X_test_correct)
        
        r2_correct = r2_score(y_test_correct, y_pred_correct)
        mae_correct = mean_absolute_error(y_test_correct, y_pred_correct)
        
        print(f"❌ INCORRECT (Random Split):")
        print(f"   R² Score: {r2_wrong:.3f}")
        print(f"   MAE: {mae_wrong:.3f}")
        print(f"   ⚠️  Artificially inflated due to data leakage")
        
        print(f"\n✅ CORRECT (Match-based Split):")
        print(f"   R² Score: {r2_correct:.3f}")
        print(f"   MAE: {mae_correct:.3f}")
        print(f"   ✅ Realistic generalization performance")
        
        performance_drop = ((r2_wrong - r2_correct) / r2_wrong) * 100
        print(f"\n📉 Performance drop with correct splitting: {performance_drop:.1f}%")
        print(f"   This is NORMAL and expected!")
        
        return {
            'incorrect_r2': r2_wrong,
            'correct_r2': r2_correct,
            'performance_drop_percent': performance_drop
        }
    
    def provide_recommendations(self):
        """Provide recommendations based on corrected analysis"""
        print(f"\n📋 RECOMMENDATIONS FOR TEMPORAL MOMENTUM PREDICTION")
        print("=" * 60)
        
        print("✅ MANDATORY CHANGES:")
        print("   1. Use match-based train/test splitting")
        print("   2. Implement TimeSeriesSplit for cross-validation")
        print("   3. Maintain temporal ordering in data")
        print("   4. No future data leakage in features")
        
        print("\n📊 REALISTIC PERFORMANCE EXPECTATIONS:")
        print("   • Future momentum (3-min): R² = 0.10-0.40")
        print("   • Current momentum: R² = 0.40-0.70")
        print("   • Classification accuracy: 50-65%")
        print("   • Higher performance = suspicious of data leakage")
        
        print("\n🎯 NEXT STEPS:")
        print("   1. Implement corrected splitting in all models")
        print("   2. Re-evaluate all previous results")
        print("   3. Focus on feature engineering with corrected baseline")
        print("   4. Consider ensemble methods for small improvements")
        
        print("\n💡 KEY INSIGHT:")
        print("   Lower performance with correct splitting is GOOD!")
        print("   It means the model will actually generalize to new matches.")

def main():
    """Main function to run corrected momentum analysis"""
    print("🚀 CORRECTED MOMENTUM MODEL ANALYSIS")
    print("=" * 80)
    
    # Initialize model
    model = CorrectedMomentumModel()
    
    # Load data
    events_df, matches_df = model.load_euro_2024_data()
    if events_df is None:
        return
    
    # Create temporal data
    momentum_data = model.create_temporal_momentum_data(events_df, sample_matches=15)
    
    # Train with proper temporal validation
    metrics = model.train_with_temporal_validation(momentum_data)
    
    # Compare with incorrect approach
    comparison = model.compare_with_incorrect_split(momentum_data)
    
    # Provide recommendations
    model.provide_recommendations()
    
    print(f"\n🎯 FINAL RESULTS:")
    print(f"   Correct match-based R²: {metrics['match_based_test_r2']:.3f}")
    print(f"   Time series CV: {metrics['cv_mean_r2']:.3f} ± {metrics['cv_std_r2']:.3f}")
    print(f"   Performance drop from incorrect: {comparison['performance_drop_percent']:.1f}%")
    
    print(f"\n✅ ANALYSIS COMPLETE - Use these corrected approaches!")

if __name__ == "__main__":
    main() 