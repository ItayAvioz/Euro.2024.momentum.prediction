#!/usr/bin/env python3
"""
Quick Direct Future Momentum Prediction Test
Compare predicting absolute future momentum vs momentum change
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error
import warnings
warnings.filterwarnings('ignore')

class QuickDirectMomentumTest:
    def __init__(self):
        self.events_df = None
        
    def load_data(self):
        """Load Euro 2024 data"""
        print("📊 Loading Euro 2024 Tournament Data...")
        try:
            self.events_df = pd.read_csv("../Data/events_complete.csv", low_memory=False)
            print(f"✅ Events loaded: {len(self.events_df):,}")
            
            # Extract event names
            self.events_df['event_name'] = self.events_df['type'].apply(self.extract_event_type)
            
            # Create match identifiers
            if 'match_id' not in self.events_df.columns:
                self.events_df['match_id'] = pd.factorize(
                    self.events_df['home_team'].astype(str) + '_vs_' + 
                    self.events_df['away_team'].astype(str)
                )[0]
            
            return True
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def extract_event_type(self, type_str):
        """Extract event name from type dictionary string"""
        if pd.isna(type_str) or type_str == '':
            return ''
        try:
            if "'name':" in str(type_str):
                start = str(type_str).find("'name': '") + 9
                end = str(type_str).find("'", start)
                return str(type_str)[start:end]
            else:
                return str(type_str)
        except:
            return str(type_str)
    
    def create_comparison_features(self, sample_matches=15):
        """Create features for both direct and change-based prediction"""
        print(f"\n🔧 CREATING FEATURES FOR COMPARISON TEST")
        print("Using key insights: activity trends, recent events, time windows")
        
        unique_matches = self.events_df['match_id'].unique()[:sample_matches]
        momentum_records = []
        
        for i, match_id in enumerate(unique_matches):
            print(f"Processing match {i+1}/{len(unique_matches)}")
            
            match_events = self.events_df[self.events_df['match_id'] == match_id]
            match_events = match_events.sort_values('minute')
            
            teams = match_events['team_name'].dropna().unique()
            if len(teams) < 2:
                continue
            
            match_duration = int(match_events['minute'].max())
            if match_duration < 45:
                continue
            
            for team in teams:
                opponent_team = [t for t in teams if t != team][0]
                
                # Process every 5 minutes for faster processing
                for minute in range(15, match_duration - 10, 5):
                    
                    # Extract core features
                    features = self.extract_core_features(
                        match_events, team, opponent_team, minute
                    )
                    
                    if features is None:
                        continue
                    
                    # Calculate current momentum
                    current_momentum = self.calculate_momentum(features)
                    
                    # Calculate future momentum
                    future_momentum = self.calculate_future_momentum(
                        match_events, team, minute + 5
                    )
                    
                    if future_momentum is None:
                        continue
                    
                    # Both targets for comparison
                    target_absolute = future_momentum  # ABSOLUTE future momentum
                    target_change = future_momentum - current_momentum  # CHANGE
                    
                    record = {
                        'match_id': match_id,
                        'team': team,
                        'minute': minute,
                        'current_momentum': current_momentum,
                        'future_momentum': future_momentum,
                        'target_absolute': target_absolute,
                        'target_change': target_change,
                        **features
                    }
                    
                    momentum_records.append(record)
        
        momentum_df = pd.DataFrame(momentum_records)
        print(f"✅ Created {len(momentum_df)} momentum samples")
        
        return momentum_df
    
    def extract_core_features(self, match_events, team, opponent_team, minute):
        """Extract core features from comprehensive model"""
        
        # Time windows
        last_10min = match_events[
            (match_events['minute'] >= minute-10) & 
            (match_events['minute'] < minute)
        ]
        last_5min = match_events[
            (match_events['minute'] >= minute-5) & 
            (match_events['minute'] < minute)
        ]
        last_2min = match_events[
            (match_events['minute'] >= minute-2) & 
            (match_events['minute'] < minute)
        ]
        
        # Team events
        team_all = match_events[match_events['team_name'] == team]
        team_current = team_all[team_all['minute'] < minute]
        team_10min = last_10min[last_10min['team_name'] == team]
        team_5min = last_5min[last_5min['team_name'] == team]
        team_2min = last_2min[last_2min['team_name'] == team]
        
        # Opponent events  
        opponent_current = match_events[
            (match_events['team_name'] == opponent_team) & 
            (match_events['minute'] < minute)
        ]
        
        if len(team_2min) == 0 and len(team_5min) == 0:
            return None
        
        # Core metrics
        team_goals_total = len(team_current[team_current['event_name'].str.contains('Goal', na=False, case=False)])
        team_shots_total = len(team_current[team_current['event_name'].str.contains('Shot', na=False, case=False)])
        opponent_goals_total = len(opponent_current[opponent_current['event_name'].str.contains('Goal', na=False, case=False)])
        
        # Activity levels (KEY INSIGHT from our analysis)
        team_events_total = len(team_current)
        team_events_10min = len(team_10min)
        team_events_5min = len(team_5min)
        team_events_2min = len(team_2min)
        
        # Activity trends (TOP FEATURE from comprehensive model)
        activity_rate_2min = team_events_2min / 2.0
        activity_rate_5min = team_events_5min / 5.0
        activity_trend = activity_rate_2min - activity_rate_5min
        
        # Recent activity
        team_goals_5min = len(team_5min[team_5min['event_name'].str.contains('Goal', na=False, case=False)])
        team_shots_5min = len(team_5min[team_5min['event_name'].str.contains('Shot', na=False, case=False)])
        team_shots_2min = len(team_2min[team_2min['event_name'].str.contains('Shot', na=False, case=False)])
        
        # Possession estimation
        total_events_5min = len(last_5min)
        possession_5min = (team_events_5min / max(total_events_5min, 1)) * 100
        
        # Advantages
        goal_advantage = team_goals_total - opponent_goals_total
        shot_advantage = team_shots_total - len(opponent_current[opponent_current['event_name'].str.contains('Shot', na=False, case=False)])
        
        # Time pressure
        time_pressure = 1.0 - (max(0, 90 - minute) / 90.0)
        
        # Core features (TOP 15 from comprehensive model)
        features = {
            'team_events_2min': team_events_2min,
            'activity_trend': activity_trend,
            'team_events_5min': team_events_5min,
            'team_events_10min': team_events_10min,
            'team_goals_total': team_goals_total,
            'team_shots_total': team_shots_total,
            'team_goals_5min': team_goals_5min,
            'team_shots_5min': team_shots_5min,
            'team_shots_2min': team_shots_2min,
            'possession_5min': possession_5min,
            'goal_advantage': goal_advantage,
            'shot_advantage': shot_advantage,
            'activity_rate_2min': activity_rate_2min,
            'activity_rate_5min': activity_rate_5min,
            'time_pressure': time_pressure,
            'current_minute': minute,
            'team_events_total': team_events_total
        }
        
        return features
    
    def calculate_momentum(self, features):
        """Calculate current momentum"""
        momentum = (
            features['team_events_2min'] * 0.4 +
            features['team_goals_5min'] * 3.0 +
            features['team_shots_5min'] * 0.8 +
            features['activity_trend'] * 1.5 +
            features['goal_advantage'] * 2.0 +
            features['possession_5min'] * 0.02 +
            features['time_pressure'] * 0.5
        )
        return max(0, min(10, momentum))
    
    def calculate_future_momentum(self, match_events, team, future_minute):
        """Calculate future momentum"""
        future_window = match_events[
            (match_events['minute'] >= future_minute) & 
            (match_events['minute'] < future_minute + 3)
        ]
        
        if len(future_window) == 0:
            return None
        
        team_future = future_window[future_window['team_name'] == team]
        
        future_events = len(team_future)
        future_goals = len(team_future[team_future['event_name'].str.contains('Goal', na=False, case=False)])
        future_shots = len(team_future[team_future['event_name'].str.contains('Shot', na=False, case=False)])
        
        future_momentum = min(10, max(0,
            future_events * 0.4 +
            future_goals * 3.0 +
            future_shots * 1.0
        ))
        
        return future_momentum
    
    def run_comparison_test(self, momentum_df):
        """Run comparison test between direct and change-based prediction"""
        print(f"\n🚀 RUNNING COMPARISON TEST")
        print("DIRECT (absolute) vs CHANGE-BASED prediction")
        
        # Prepare features
        feature_cols = [col for col in momentum_df.columns 
                       if col not in ['match_id', 'team', 'minute', 'current_momentum', 
                                     'future_momentum', 'target_absolute', 'target_change']]
        
        X = momentum_df[feature_cols].fillna(0)
        y_absolute = momentum_df['target_absolute']  # ABSOLUTE future momentum
        y_change = momentum_df['target_change']      # CHANGE in momentum
        
        print(f"📊 Dataset:")
        print(f"   Features: {len(feature_cols)}")
        print(f"   Samples: {len(X)}")
        print(f"   Current momentum: {momentum_df['current_momentum'].min():.2f} to {momentum_df['current_momentum'].max():.2f}")
        print(f"   Future momentum: {momentum_df['future_momentum'].min():.2f} to {momentum_df['future_momentum'].max():.2f}")
        print(f"   Absolute target: {y_absolute.min():.2f} to {y_absolute.max():.2f}")
        print(f"   Change target: {y_change.min():.2f} to {y_change.max():.2f}")
        
        # Match-based split
        matches = momentum_df['match_id'].unique()
        np.random.seed(42)
        np.random.shuffle(matches)
        
        n_train = int(len(matches) * 0.8)
        train_matches = matches[:n_train]
        test_matches = matches[n_train:]
        
        train_data = momentum_df[momentum_df['match_id'].isin(train_matches)]
        test_data = momentum_df[momentum_df['match_id'].isin(test_matches)]
        
        X_train = train_data[feature_cols].fillna(0)
        X_test = test_data[feature_cols].fillna(0)
        
        print(f"\n🎯 Match-based split:")
        print(f"   Train matches: {len(train_matches)}, Test matches: {len(test_matches)}")
        print(f"   Train samples: {len(X_train)}, Test samples: {len(X_test)}")
        
        # Test 1: Direct absolute prediction
        print(f"\n📈 TEST 1: DIRECT ABSOLUTE MOMENTUM PREDICTION")
        y_train_abs = train_data['target_absolute']
        y_test_abs = test_data['target_absolute']
        
        model_abs = RandomForestRegressor(n_estimators=100, random_state=42)
        model_abs.fit(X_train, y_train_abs)
        y_pred_abs = model_abs.predict(X_test)
        
        r2_abs = r2_score(y_test_abs, y_pred_abs)
        mae_abs = mean_absolute_error(y_test_abs, y_pred_abs)
        
        print(f"   R² Score: {r2_abs:.3f}")
        print(f"   MAE: {mae_abs:.3f}")
        
        # Test 2: Change-based prediction
        print(f"\n📈 TEST 2: CHANGE-BASED MOMENTUM PREDICTION")
        y_train_chg = train_data['target_change']
        y_test_chg = test_data['target_change']
        
        model_chg = RandomForestRegressor(n_estimators=100, random_state=42)
        model_chg.fit(X_train, y_train_chg)
        y_pred_chg = model_chg.predict(X_test)
        
        r2_chg = r2_score(y_test_chg, y_pred_chg)
        mae_chg = mean_absolute_error(y_test_chg, y_pred_chg)
        
        print(f"   R² Score: {r2_chg:.3f}")
        print(f"   MAE: {mae_chg:.3f}")
        
        # Test 3: Convert absolute predictions to change for comparison
        print(f"\n📈 TEST 3: DERIVED CHANGE FROM ABSOLUTE PREDICTIONS")
        current_test = test_data['current_momentum'].values
        derived_change = y_pred_abs - current_test
        actual_change = test_data['target_change'].values
        
        r2_derived = r2_score(actual_change, derived_change)
        mae_derived = mean_absolute_error(actual_change, derived_change)
        
        print(f"   R² Score: {r2_derived:.3f}")
        print(f"   MAE: {mae_derived:.3f}")
        
        # Feature importance comparison
        importance_abs = pd.DataFrame({
            'feature': feature_cols,
            'importance': model_abs.feature_importances_
        }).sort_values('importance', ascending=False)
        
        importance_chg = pd.DataFrame({
            'feature': feature_cols,
            'importance': model_chg.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print(f"\n🔝 TOP FEATURES - ABSOLUTE PREDICTION:")
        for _, row in importance_abs.head(5).iterrows():
            print(f"   {row['feature']:<25}: {row['importance']:.3f}")
        
        print(f"\n🔝 TOP FEATURES - CHANGE PREDICTION:")
        for _, row in importance_chg.head(5).iterrows():
            print(f"   {row['feature']:<25}: {row['importance']:.3f}")
        
        return {
            'absolute_r2': r2_abs,
            'absolute_mae': mae_abs,
            'change_r2': r2_chg,
            'change_mae': mae_chg,
            'derived_r2': r2_derived,
            'derived_mae': mae_derived
        }

def main():
    """Main function"""
    print("🎯 QUICK DIRECT MOMENTUM PREDICTION COMPARISON")
    print("=" * 80)
    print("Testing: ABSOLUTE future momentum vs CHANGE prediction")
    print("Using: Key insights from comprehensive analysis")
    print("=" * 80)
    
    test = QuickDirectMomentumTest()
    
    # Load data
    if not test.load_data():
        return
    
    # Create features
    momentum_df = test.create_comparison_features(sample_matches=15)
    
    if len(momentum_df) == 0:
        print("❌ No data created")
        return
    
    # Run comparison
    results = test.run_comparison_test(momentum_df)
    
    print(f"\n🎯 FINAL COMPARISON RESULTS:")
    print(f"=" * 80)
    print(f"📊 DIRECT ABSOLUTE MOMENTUM PREDICTION:")
    print(f"   R² Score: {results['absolute_r2']:.3f}")
    print(f"   MAE: {results['absolute_mae']:.3f}")
    
    print(f"\n🔄 CHANGE-BASED MOMENTUM PREDICTION:")
    print(f"   R² Score: {results['change_r2']:.3f}")
    print(f"   MAE: {results['change_mae']:.3f}")
    
    print(f"\n🔄 DERIVED CHANGE FROM ABSOLUTE MODEL:")
    print(f"   R² Score: {results['derived_r2']:.3f}")
    print(f"   MAE: {results['derived_mae']:.3f}")
    
    print(f"\n🎯 ARCHITECTURAL IMPACT ANALYSIS:")
    if results['change_r2'] > results['absolute_r2']:
        improvement = results['change_r2'] - results['absolute_r2']
        print(f"   ✅ CONFIRMED: Change-based prediction is superior")
        print(f"   ✅ R² improvement: {improvement:.3f} ({improvement*100:.1f}% better)")
        print(f"   ✅ Architecture choice was CRITICAL for success")
    else:
        print(f"   ⚠️  UNEXPECTED: Absolute prediction performed similarly")
        print(f"   🔍 Features may be more important than architecture")
    
    print(f"\n🏆 QUICK COMPARISON TEST COMPLETE!")

if __name__ == "__main__":
    main() 