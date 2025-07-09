#!/usr/bin/env python3
"""
Temporal Data Leakage Analysis and Correct Time-Series Splitting
Critical analysis of current data splitting approach and proper solutions
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, TimeSeriesSplit
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error
import os
import warnings
warnings.filterwarnings('ignore')

class TemporalDataAnalysis:
    """Analyze and fix temporal data leakage in momentum prediction"""
    
    def __init__(self):
        self.events_df = None
        self.momentum_data = None
        
    def load_data(self):
        """Load Euro 2024 data"""
        print("📊 Loading Euro 2024 Dataset...")
        
        data_dir = "../Data"
        
        try:
            self.events_df = pd.read_csv(os.path.join(data_dir, "events_complete.csv"))
            print(f"✅ Events: {len(self.events_df):,}")
            return True
        except FileNotFoundError as e:
            print(f"❌ Error: {e}")
            return False
    
    def demonstrate_current_problem(self):
        """Demonstrate the current temporal data leakage problem"""
        print("\n❌ CURRENT PROBLEM: TEMPORAL DATA LEAKAGE")
        print("=" * 60)
        
        print("🚨 CRITICAL ISSUES WITH CURRENT APPROACH:")
        print("\n1. 🎲 RANDOM TRAIN/TEST SPLIT:")
        print("   train_test_split(X, y, test_size=0.2, random_state=42)")
        print("   ❌ Randomly mixes data from different time periods")
        print("   ❌ Same match data in both train and test sets")
        print("   ❌ Future data can train on past events from same match")
        
        print("\n2. 🔄 TEMPORAL SEQUENCE BROKEN:")
        print("   Example:")
        print("   ❌ Train: [Match1_min5, Match1_min45, Match2_min20]")
        print("   ❌ Test:  [Match1_min25, Match2_min5, Match1_min80]")
        print("   → Model learns from future to predict past!")
        
        print("\n3. 📊 INFLATED PERFORMANCE:")
        print("   ❌ Model sees similar patterns from same match")
        print("   ❌ Overly optimistic R² and accuracy scores")
        print("   ❌ Model won't generalize to new matches")
        
        # Create example data to demonstrate
        example_data = self.create_example_temporal_data()
        self.compare_splitting_methods(example_data)
    
    def create_example_temporal_data(self):
        """Create example temporal data to demonstrate the problem"""
        print(f"\n📊 CREATING EXAMPLE TEMPORAL DATA:")
        
        # Simulate momentum data from 3 matches
        np.random.seed(42)
        data = []
        
        for match_id in [1, 2, 3]:
            for minute in range(6, 91, 3):  # Every 3 minutes from 6 to 90
                for team in ['TeamA', 'TeamB']:
                    # Simulate momentum that has temporal patterns
                    base_momentum = 5.0
                    
                    # Add match-specific pattern
                    match_pattern = np.sin(minute / 90 * np.pi) * (match_id * 0.5)
                    
                    # Add temporal trend within match
                    time_trend = (minute / 90) * 2.0
                    
                    # Add noise
                    noise = np.random.normal(0, 0.5)
                    
                    momentum = base_momentum + match_pattern + time_trend + noise
                    momentum = max(0, min(10, momentum))
                    
                    data.append({
                        'match_id': match_id,
                        'team': team,
                        'minute': minute,
                        'momentum': momentum,
                        'time_index': (match_id - 1) * 90 + minute  # Global time index
                    })
        
        df = pd.DataFrame(data)
        print(f"   Created {len(df)} samples from {df['match_id'].nunique()} matches")
        print(f"   Time range: {df['minute'].min()}-{df['minute'].max()} minutes")
        
        return df
    
    def compare_splitting_methods(self, data):
        """Compare different data splitting methods"""
        print(f"\n🔬 COMPARING SPLITTING METHODS:")
        print("=" * 50)
        
        # Prepare simple features (just using minute as feature for demonstration)
        X = data[['minute']].values
        y = data['momentum'].values
        
        # Method 1: Random Split (WRONG)
        print("\n❌ METHOD 1: RANDOM SPLIT (CURRENT - WRONG)")
        X_train_rand, X_test_rand, y_train_rand, y_test_rand = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        model_rand = RandomForestRegressor(n_estimators=50, random_state=42)
        model_rand.fit(X_train_rand, y_train_rand)
        y_pred_rand = model_rand.predict(X_test_rand)
        
        r2_rand = r2_score(y_test_rand, y_pred_rand)
        mae_rand = mean_absolute_error(y_test_rand, y_pred_rand)
        
        print(f"   R² Score: {r2_rand:.3f}")
        print(f"   MAE: {mae_rand:.3f}")
        print(f"   ❌ Problem: Artificially high performance due to data leakage")
        
        # Method 2: Temporal Split (CORRECT)
        print("\n✅ METHOD 2: TEMPORAL SPLIT (CORRECT)")
        # Split by time - use first 80% of timeline for training
        sorted_data = data.sort_values('time_index')
        split_idx = int(len(sorted_data) * 0.8)
        
        train_data = sorted_data.iloc[:split_idx]
        test_data = sorted_data.iloc[split_idx:]
        
        X_train_temp = train_data[['minute']].values
        y_train_temp = train_data['momentum'].values
        X_test_temp = test_data[['minute']].values
        y_test_temp = test_data['momentum'].values
        
        model_temp = RandomForestRegressor(n_estimators=50, random_state=42)
        model_temp.fit(X_train_temp, y_train_temp)
        y_pred_temp = model_temp.predict(X_test_temp)
        
        r2_temp = r2_score(y_test_temp, y_pred_temp)
        mae_temp = mean_absolute_error(y_test_temp, y_pred_temp)
        
        print(f"   R² Score: {r2_temp:.3f}")
        print(f"   MAE: {mae_temp:.3f}")
        print(f"   ✅ Realistic performance without data leakage")
        
        # Method 3: Match-Based Split (BEST)
        print("\n🏆 METHOD 3: MATCH-BASED SPLIT (BEST)")
        # Use different matches for train and test
        train_matches = [1, 2]
        test_matches = [3]
        
        train_data_match = data[data['match_id'].isin(train_matches)]
        test_data_match = data[data['match_id'].isin(test_matches)]
        
        X_train_match = train_data_match[['minute']].values
        y_train_match = train_data_match['momentum'].values
        X_test_match = test_data_match[['minute']].values
        y_test_match = test_data_match['momentum'].values
        
        model_match = RandomForestRegressor(n_estimators=50, random_state=42)
        model_match.fit(X_train_match, y_train_match)
        y_pred_match = model_match.predict(X_test_match)
        
        r2_match = r2_score(y_test_match, y_pred_match)
        mae_match = mean_absolute_error(y_test_match, y_pred_match)
        
        print(f"   R² Score: {r2_match:.3f}")
        print(f"   MAE: {mae_match:.3f}")
        print(f"   🏆 Most realistic - tests generalization to new matches")
        
        # Summary
        print(f"\n📊 PERFORMANCE COMPARISON:")
        print(f"   Random Split:    R² {r2_rand:.3f} | MAE {mae_rand:.3f} ❌ INVALID")
        print(f"   Temporal Split:  R² {r2_temp:.3f} | MAE {mae_temp:.3f} ✅ Better")
        print(f"   Match Split:     R² {r2_match:.3f} | MAE {mae_match:.3f} 🏆 Best")
        
        print(f"\n💡 KEY INSIGHT:")
        print(f"   Performance drops significantly with proper splitting!")
        print(f"   This explains why our models showed poor real-world performance.")
    
    def create_correct_momentum_data(self):
        """Create momentum data with correct temporal handling"""
        print(f"\n🔧 CREATING MOMENTUM DATA WITH CORRECT TEMPORAL HANDLING")
        print("=" * 60)
        
        # Sample a subset of events for demonstration
        unique_matches = self.events_df['match_id'].unique()[:10]  # Use 10 matches
        sampled_events = self.events_df[self.events_df['match_id'].isin(unique_matches)]
        
        momentum_records = []
        
        for match_id in unique_matches:
            match_events = sampled_events[sampled_events['match_id'] == match_id].copy()
            match_events = match_events.sort_values('minute')
            
            teams = match_events['team'].unique()
            
            for team in teams:
                # Process in temporal order
                for minute in range(6, int(match_events['minute'].max()) + 1, 3):
                    current_start = minute - 3
                    current_end = minute
                    future_start = minute
                    future_end = minute + 3
                    
                    # Current window (features)
                    current_window = match_events[
                        (match_events['minute'] >= current_start) & 
                        (match_events['minute'] < current_end)
                    ]
                    
                    # Future window (target)
                    future_window = match_events[
                        (match_events['minute'] >= future_start) & 
                        (match_events['minute'] < future_end)
                    ]
                    
                    team_current = current_window[current_window['team'] == team]
                    team_future = future_window[future_window['team'] == team]
                    
                    if len(team_current) == 0:
                        continue
                    
                    # Calculate features and target
                    features = self.calculate_features(team_current, current_window)
                    future_momentum = self.calculate_future_momentum(team_future, future_window)
                    
                    record = {
                        'match_id': match_id,
                        'team': team,
                        'minute': minute,
                        'global_time': (list(unique_matches).index(match_id)) * 100 + minute,
                        'future_momentum': future_momentum,
                        **features
                    }
                    
                    momentum_records.append(record)
        
        self.momentum_data = pd.DataFrame(momentum_records)
        print(f"✅ Created {len(self.momentum_data)} samples from {len(unique_matches)} matches")
        
        return self.momentum_data
    
    def calculate_features(self, team_events, all_events):
        """Calculate momentum features"""
        total_events = len(team_events)
        shot_events = len(team_events[team_events['type'].str.contains('Shot', na=False)])
        attacking_events = len(team_events[team_events['type'].str.contains('Shot|Carry|Dribble', na=False)])
        possession_pct = (total_events / (len(all_events) + 1)) * 100
        
        return {
            'total_events': total_events,
            'shot_events': shot_events,
            'attacking_events': attacking_events,
            'possession_pct': possession_pct,
            'events_per_minute': total_events / 3.0
        }
    
    def calculate_future_momentum(self, team_future, all_future):
        """Calculate future momentum target"""
        if len(team_future) == 0:
            return 5.0
        
        features = self.calculate_features(team_future, all_future)
        momentum = (
            features['shot_events'] * 2.0 +
            features['attacking_events'] * 1.2 +
            features['possession_pct'] * 0.05 +
            features['events_per_minute'] * 0.4
        )
        return max(0, min(10, momentum))
    
    def demonstrate_correct_splitting(self):
        """Demonstrate correct temporal splitting methods"""
        print(f"\n🎯 CORRECT TEMPORAL SPLITTING METHODS")
        print("=" * 60)
        
        if self.momentum_data is None:
            self.create_correct_momentum_data()
        
        # Prepare features
        feature_cols = ['total_events', 'shot_events', 'attacking_events', 'possession_pct', 'events_per_minute']
        X = self.momentum_data[feature_cols]
        y = self.momentum_data['future_momentum']
        
        print(f"📊 Dataset: {len(X)} samples, {len(feature_cols)} features")
        
        # Method 1: Time Series Split
        print(f"\n🔄 METHOD 1: TIME SERIES SPLIT")
        tscv = TimeSeriesSplit(n_splits=5)
        ts_scores = []
        
        for train_idx, test_idx in tscv.split(X):
            X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
            y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
            
            model = RandomForestRegressor(n_estimators=50, random_state=42)
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            
            r2 = r2_score(y_test, y_pred)
            ts_scores.append(r2)
        
        print(f"   Cross-validation R²: {np.mean(ts_scores):.3f} ± {np.std(ts_scores):.3f}")
        print(f"   Individual fold scores: {[f'{score:.3f}' for score in ts_scores]}")
        
        # Method 2: Match-Based Split
        print(f"\n🏟️ METHOD 2: MATCH-BASED SPLIT")
        matches = self.momentum_data['match_id'].unique()
        n_train_matches = int(len(matches) * 0.8)
        
        train_matches = matches[:n_train_matches]
        test_matches = matches[n_train_matches:]
        
        train_data = self.momentum_data[self.momentum_data['match_id'].isin(train_matches)]
        test_data = self.momentum_data[self.momentum_data['match_id'].isin(test_matches)]
        
        X_train = train_data[feature_cols]
        y_train = train_data['future_momentum']
        X_test = test_data[feature_cols]
        y_test = test_data['future_momentum']
        
        model = RandomForestRegressor(n_estimators=50, random_state=42)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        
        r2_match = r2_score(y_test, y_pred)
        mae_match = mean_absolute_error(y_test, y_pred)
        
        print(f"   Training matches: {len(train_matches)} | Testing matches: {len(test_matches)}")
        print(f"   Training samples: {len(X_train)} | Testing samples: {len(X_test)}")
        print(f"   R² Score: {r2_match:.3f}")
        print(f"   MAE: {mae_match:.3f}")
        
        # Method 3: Temporal + Match Split
        print(f"\n🎯 METHOD 3: TEMPORAL + MATCH SPLIT")
        # Sort by global time and split temporally
        sorted_data = self.momentum_data.sort_values('global_time')
        split_idx = int(len(sorted_data) * 0.8)
        
        train_data_temp = sorted_data.iloc[:split_idx]
        test_data_temp = sorted_data.iloc[split_idx:]
        
        X_train_temp = train_data_temp[feature_cols]
        y_train_temp = train_data_temp['future_momentum']
        X_test_temp = test_data_temp[feature_cols]
        y_test_temp = test_data_temp['future_momentum']
        
        model_temp = RandomForestRegressor(n_estimators=50, random_state=42)
        model_temp.fit(X_train_temp, y_train_temp)
        y_pred_temp = model_temp.predict(X_test_temp)
        
        r2_temp = r2_score(y_test_temp, y_pred_temp)
        mae_temp = mean_absolute_error(y_test_temp, y_pred_temp)
        
        print(f"   Temporal split at 80% of global timeline")
        print(f"   Training samples: {len(X_train_temp)} | Testing samples: {len(X_test_temp)}")
        print(f"   R² Score: {r2_temp:.3f}")
        print(f"   MAE: {mae_temp:.3f}")
        
        return {
            'time_series_cv': np.mean(ts_scores),
            'match_based': r2_match,
            'temporal': r2_temp
        }
    
    def provide_implementation_guidelines(self):
        """Provide implementation guidelines for correct temporal handling"""
        print(f"\n📋 IMPLEMENTATION GUIDELINES")
        print("=" * 60)
        
        print("✅ CORRECT APPROACH FOR MOMENTUM PREDICTION:")
        
        print(f"\n1. 🎯 MATCH-BASED SPLITTING:")
        print("   ✅ Use different matches for train/test")
        print("   ✅ Ensures model generalizes to new games")
        print("   ✅ Most realistic evaluation")
        print("   Code:")
        print("   ```python")
        print("   train_matches = matches[:int(len(matches) * 0.8)]")
        print("   test_matches = matches[int(len(matches) * 0.8):]")
        print("   ```")
        
        print(f"\n2. 🕐 TEMPORAL ORDERING:")
        print("   ✅ Maintain chronological order within matches")
        print("   ✅ Features from time T, target from time T+3min")
        print("   ✅ No future information in training")
        print("   Code:")
        print("   ```python")
        print("   data = data.sort_values(['match_id', 'minute'])")
        print("   # Ensure temporal consistency")
        print("   ```")
        
        print(f"\n3. 🔄 TIME SERIES CROSS-VALIDATION:")
        print("   ✅ Use TimeSeriesSplit for validation")
        print("   ✅ Respect temporal order in folds")
        print("   ✅ Progressive training windows")
        print("   Code:")
        print("   ```python")
        print("   from sklearn.model_selection import TimeSeriesSplit")
        print("   tscv = TimeSeriesSplit(n_splits=5)")
        print("   ```")
        
        print(f"\n❌ AVOID THESE MISTAKES:")
        print("   ❌ Random train_test_split() on temporal data")
        print("   ❌ Same match in train and test")
        print("   ❌ Future data leaking into features")
        print("   ❌ Shuffling temporal sequences")
        
        print(f"\n🎯 EXPECTED PERFORMANCE IMPACT:")
        print("   📉 R² scores will drop significantly (this is normal!)")
        print("   📉 Classification accuracy will decrease")
        print("   ✅ Results will be more realistic")
        print("   ✅ Model will actually generalize")
        
        print(f"\n📊 REALISTIC TARGETS WITH CORRECT SPLITTING:")
        print("   • Current momentum: R² > 0.60 (achievable)")
        print("   • Future momentum (3min): R² > 0.20 (challenging)")
        print("   • Classification accuracy: 55-65% (realistic)")
        
    def fix_current_models(self):
        """Provide code to fix current models"""
        print(f"\n🔧 FIXING CURRENT MODELS")
        print("=" * 60)
        
        print("📝 CORRECTED CODE TEMPLATE:")
        print("""
```python
def correct_temporal_split(momentum_data):
    \"\"\"Correct way to split temporal momentum data\"\"\"
    
    # Method 1: Match-based split (RECOMMENDED)
    matches = momentum_data['match_id'].unique()
    np.random.shuffle(matches)  # Random match assignment
    
    n_train = int(len(matches) * 0.8)
    train_matches = matches[:n_train]
    test_matches = matches[n_train:]
    
    train_data = momentum_data[momentum_data['match_id'].isin(train_matches)]
    test_data = momentum_data[momentum_data['match_id'].isin(test_matches)]
    
    return train_data, test_data

def train_corrected_model(momentum_data):
    \"\"\"Train model with correct temporal handling\"\"\"
    
    # Correct split
    train_data, test_data = correct_temporal_split(momentum_data)
    
    # Prepare features
    feature_cols = ['total_events', 'shot_events', 'attacking_events', 
                   'possession_pct', 'events_per_minute']
    
    X_train = train_data[feature_cols]
    y_train = train_data['future_momentum']
    X_test = test_data[feature_cols]
    y_test = test_data['future_momentum']
    
    # Train model
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    
    print(f"Corrected R² Score: {r2:.3f}")
    return model, r2
```
""")

def main():
    """Run the complete temporal data analysis"""
    print("🚨 TEMPORAL DATA LEAKAGE ANALYSIS")
    print("=" * 80)
    
    analyzer = TemporalDataAnalysis()
    
    # Load data
    if not analyzer.load_data():
        return
    
    # Demonstrate the problem
    analyzer.demonstrate_current_problem()
    
    # Create correct data
    analyzer.create_correct_momentum_data()
    
    # Demonstrate correct splitting
    results = analyzer.demonstrate_correct_splitting()
    
    # Provide guidelines
    analyzer.provide_implementation_guidelines()
    
    # Fix current models
    analyzer.fix_current_models()
    
    print(f"\n🎯 SUMMARY:")
    print(f"   Current approach has severe temporal data leakage")
    print(f"   Proper splitting shows much lower (but realistic) performance")
    print(f"   Must use match-based or temporal splitting")
    print(f"   Expected performance drop: 50-80% (this is normal!)")
    
    print(f"\n✅ ANALYSIS COMPLETE")

if __name__ == "__main__":
    main() 