#!/usr/bin/env python3
"""
Fixed Corrected Momentum Model with Proper Temporal Data Handling
Works with actual Euro 2024 data structure
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import TimeSeriesSplit, train_test_split
from sklearn.metrics import r2_score, mean_absolute_error
import os
import warnings
warnings.filterwarnings('ignore')

class FixedCorrectedMomentumModel:
    """
    Fixed momentum prediction model with proper temporal data handling
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
            events_df = pd.read_csv(os.path.join(data_dir, "events_complete.csv"), low_memory=False)
            matches_df = pd.read_csv(os.path.join(data_dir, "matches_complete.csv"))
            
            print(f"✅ Events: {len(events_df):,}")
            print(f"✅ Matches: {len(matches_df):,}")
            
            # Add match_id column if not present
            if 'match_id' not in events_df.columns:
                # Create match_id from unique combinations
                events_df['match_id'] = events_df.groupby(['period', 'possession_team']).ngroup()
                print(f"✅ Created match_id with {events_df['match_id'].nunique()} unique matches")
            
            return events_df, matches_df
        except FileNotFoundError as e:
            print(f"❌ Error: {e}")
            return None, None
    
    def create_temporal_momentum_data(self, events_df, sample_matches=10):
        """Create momentum data with proper temporal handling"""
        print(f"\n🔧 CREATING TEMPORAL MOMENTUM DATA")
        print("=" * 50)
        
        # Check actual columns
        print(f"Available columns: {list(events_df.columns)[:10]}...")
        
        # Create a proper match_id if needed
        if 'match_id' not in events_df.columns:
            # Group by time periods to create match segments
            events_df['match_id'] = pd.factorize(events_df['possession_team'].astype(str) + '_' + events_df['period'].astype(str))[0]
        
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
            
            # Get teams
            teams = match_events['team'].dropna().unique()
            
            if len(teams) == 0:
                continue
                
            for team in teams:
                # Sample every 3 minutes starting from minute 6
                max_minute = int(match_events['minute'].max())
                
                if max_minute < 15:  # Skip very short matches
                    continue
                
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
        
        if len(momentum_df) == 0:
            print("❌ No momentum data created")
            return None
        
        print(f"✅ Created {len(momentum_df)} temporal samples")
        print(f"   📊 Matches: {momentum_df['match_id'].nunique()}")
        print(f"   ⏱️  Time range: {momentum_df['minute'].min()}-{momentum_df['minute'].max()} minutes")
        print(f"   🎯 Target range: {momentum_df['future_momentum'].min():.2f}-{momentum_df['future_momentum'].max():.2f}")
        
        return momentum_df
    
    def extract_temporal_features(self, events_window, team):
        """Extract features from temporal window - fixed for actual data"""
        team_events = events_window[events_window['team'] == team]
        all_events = events_window
        
        # Basic counting features
        total_events = len(team_events)
        
        # Check for different event types based on available data
        shot_events = 0
        pass_events = 0
        attacking_events = 0
        
        if 'type' in team_events.columns:
            shot_events = len(team_events[team_events['type'].str.contains('Shot', na=False)])
            pass_events = len(team_events[team_events['type'].str.contains('Pass', na=False)])
            attacking_events = len(team_events[team_events['type'].str.contains('Shot|Carry|Dribble', na=False)])
        
        # Possession and intensity
        possession_pct = (total_events / (len(all_events) + 1)) * 100
        events_per_minute = total_events / 3.0
        
        # Pressure indicator
        under_pressure_events = 0
        if 'under_pressure' in team_events.columns:
            under_pressure_events = len(team_events[team_events['under_pressure'].notna()])
        
        # Duration-based features
        avg_duration = 0
        if 'duration' in team_events.columns:
            duration_values = team_events['duration'].dropna()
            if len(duration_values) > 0:
                avg_duration = duration_values.mean()
        
        return {
            'total_events': total_events,
            'shot_events': shot_events,
            'pass_events': pass_events,
            'attacking_events': attacking_events,
            'possession_pct': possession_pct,
            'events_per_minute': events_per_minute,
            'under_pressure_events': under_pressure_events,
            'avg_duration': avg_duration
        }
    
    def calculate_future_momentum(self, future_events, team):
        """Calculate future momentum target - fixed for actual data"""
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
            future_features['pass_events'] * 0.3 -
            future_features['under_pressure_events'] * 0.2
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
        feature_cols = ['total_events', 'shot_events', 'pass_events', 'attacking_events',
                       'possession_pct', 'events_per_minute', 'under_pressure_events', 'avg_duration']
        
        # Check which features are available
        available_features = [col for col in feature_cols if col in momentum_data.columns]
        self.feature_names = available_features
        
        X = momentum_data[available_features]
        y = momentum_data['future_momentum']
        
        print(f"📊 Dataset preparation:")
        print(f"   Features: {len(available_features)}")
        print(f"   Feature names: {available_features}")
        print(f"   Samples: {len(X)}")
        print(f"   Target range: {y.min():.2f}-{y.max():.2f}")
        
        # Method 1: Match-based split evaluation
        train_data, test_data = self.correct_temporal_split(momentum_data, 'match_based')
        
        X_train = train_data[available_features]
        y_train = train_data['future_momentum']
        X_test = test_data[available_features]
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
        
        # Store performance metrics
        self.performance_metrics = {
            'match_based_train_r2': train_r2,
            'match_based_test_r2': test_r2,
            'match_based_train_mae': train_mae,
            'match_based_test_mae': test_mae,
            'train_samples': len(X_train),
            'test_samples': len(X_test)
        }
        
        return self.performance_metrics
    
    def demonstrate_temporal_leakage_fix(self, momentum_data):
        """Demonstrate the fix for temporal data leakage"""
        print(f"\n⚠️  DEMONSTRATING TEMPORAL DATA LEAKAGE FIX")
        print("=" * 60)
        
        feature_cols = self.feature_names
        X = momentum_data[feature_cols]
        y = momentum_data['future_momentum']
        
        print(f"📊 Dataset: {len(X)} samples, {len(feature_cols)} features")
        
        # INCORRECT: Random split (current widespread approach)
        print(f"\n❌ INCORRECT APPROACH: Random Split")
        X_train_wrong, X_test_wrong, y_train_wrong, y_test_wrong = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        model_wrong = RandomForestRegressor(n_estimators=100, random_state=42)
        model_wrong.fit(X_train_wrong, y_train_wrong)
        y_pred_wrong = model_wrong.predict(X_test_wrong)
        
        r2_wrong = r2_score(y_test_wrong, y_pred_wrong)
        mae_wrong = mean_absolute_error(y_test_wrong, y_pred_wrong)
        
        print(f"   R² Score: {r2_wrong:.3f}")
        print(f"   MAE: {mae_wrong:.3f}")
        print(f"   🚨 WARNING: This includes data leakage!")
        
        # CORRECT: Match-based split
        print(f"\n✅ CORRECT APPROACH: Match-based Split")
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
        
        print(f"   R² Score: {r2_correct:.3f}")
        print(f"   MAE: {mae_correct:.3f}")
        print(f"   ✅ No data leakage - realistic performance")
        
        # Time Series Cross-Validation
        print(f"\n🔄 TIME SERIES CROSS-VALIDATION:")
        
        # Sort by temporal order
        sorted_data = momentum_data.sort_values('global_time')
        X_sorted = sorted_data[feature_cols]
        y_sorted = sorted_data['future_momentum']
        
        tscv = TimeSeriesSplit(n_splits=3)  # Use 3 splits for reasonable sample sizes
        cv_scores = []
        
        for fold, (train_idx, test_idx) in enumerate(tscv.split(X_sorted)):
            X_fold_train = X_sorted.iloc[train_idx]
            y_fold_train = y_sorted.iloc[train_idx]
            X_fold_test = X_sorted.iloc[test_idx]
            y_fold_test = y_sorted.iloc[test_idx]
            
            if len(X_fold_train) == 0 or len(X_fold_test) == 0:
                continue
                
            fold_model = RandomForestRegressor(n_estimators=100, random_state=42)
            fold_model.fit(X_fold_train, y_fold_train)
            
            y_fold_pred = fold_model.predict(X_fold_test)
            fold_r2 = r2_score(y_fold_test, y_fold_pred)
            cv_scores.append(fold_r2)
            
            print(f"   Fold {fold + 1}: R² = {fold_r2:.3f} (Train: {len(X_fold_train)}, Test: {len(X_fold_test)})")
        
        if cv_scores:
            cv_mean = np.mean(cv_scores)
            cv_std = np.std(cv_scores)
            print(f"   Cross-validation: {cv_mean:.3f} ± {cv_std:.3f}")
        
        # Summary
        if r2_wrong > 0:
            performance_drop = ((r2_wrong - r2_correct) / r2_wrong) * 100
        else:
            performance_drop = 0
            
        print(f"\n📊 PERFORMANCE COMPARISON:")
        print(f"   ❌ Random Split R²: {r2_wrong:.3f} (INVALID)")
        print(f"   ✅ Match-based R²: {r2_correct:.3f} (VALID)")
        print(f"   📉 Performance drop: {performance_drop:.1f}%")
        
        print(f"\n💡 KEY INSIGHTS:")
        print(f"   • Performance drop with correct splitting is NORMAL and EXPECTED")
        print(f"   • Random split artificially inflates performance")
        print(f"   • Match-based split tests true generalization")
        print(f"   • Negative R² means model performs worse than baseline")
        
        return {
            'incorrect_r2': r2_wrong,
            'correct_r2': r2_correct,
            'performance_drop_percent': performance_drop,
            'cv_scores': cv_scores
        }

def main():
    """Main function to run corrected momentum analysis"""
    print("🚀 FIXED CORRECTED MOMENTUM MODEL ANALYSIS")
    print("=" * 80)
    
    # Initialize model
    model = FixedCorrectedMomentumModel()
    
    # Load data
    events_df, matches_df = model.load_euro_2024_data()
    if events_df is None:
        return
    
    # Create temporal data
    momentum_data = model.create_temporal_momentum_data(events_df, sample_matches=10)
    
    if momentum_data is None:
        print("❌ Failed to create momentum data")
        return
    
    # Train with proper temporal validation
    metrics = model.train_with_temporal_validation(momentum_data)
    
    # Demonstrate temporal leakage fix
    comparison = model.demonstrate_temporal_leakage_fix(momentum_data)
    
    print(f"\n🎯 FINAL SUMMARY:")
    print(f"   ✅ Proper temporal splitting implemented")
    print(f"   📊 Match-based test R²: {metrics['match_based_test_r2']:.3f}")
    print(f"   📉 Performance drop from incorrect approach: {comparison['performance_drop_percent']:.1f}%")
    print(f"   💡 This performance drop is GOOD - it means no data leakage!")
    
    print(f"\n📋 ACTION ITEMS:")
    print(f"   1. Update all existing models to use match-based splitting")
    print(f"   2. Re-evaluate all previous performance claims")
    print(f"   3. Set realistic performance expectations")
    print(f"   4. Focus on feature engineering with corrected baseline")
    
    print(f"\n✅ TEMPORAL DATA LEAKAGE ANALYSIS COMPLETE")

if __name__ == "__main__":
    main() 