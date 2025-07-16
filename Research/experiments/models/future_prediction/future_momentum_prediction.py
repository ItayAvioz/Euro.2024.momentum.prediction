#!/usr/bin/env python3
"""
FUTURE Momentum Prediction Model
Predicts momentum for the NEXT 3 minutes based on current patterns
TRUE PREDICTION, not just summary!
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import warnings
warnings.filterwarnings('ignore')

class FutureMomentumPredictor:
    """
    TRUE PREDICTION MODEL:
    - Input: Current 3-minute summary 
    - Output: Predicted momentum for NEXT 3 minutes
    """
    
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=50, random_state=42, max_depth=12)
        self.feature_names = []
        self.is_trained = False
        self.training_stats = {}
    
    def extract_current_features(self, events_df, current_time_seconds, team_name):
        """
        Extract features from CURRENT 3-minute window
        These will be used to predict FUTURE momentum
        """
        # Current window: last 3 minutes
        start_time = max(0, current_time_seconds - 180)
        current_window = events_df[
            (events_df['timestamp'] >= start_time) & 
            (events_df['timestamp'] <= current_time_seconds)
        ]
        
        team_events = current_window[current_window['team_name'] == team_name]
        opponent_events = current_window[current_window['team_name'] != team_name]
        
        # PREDICTIVE FEATURES (patterns that might indicate future momentum)
        features = {
            # 1. Current activity patterns
            'current_shot_rate': len(team_events[team_events['event_type'] == 'Shot']) / 3,
            'current_attack_rate': len(team_events[team_events['event_type'].isin(['Shot', 'Dribble', 'Carry'])]) / 3,
            'current_possession_pct': len(team_events) / len(current_window) * 100 if len(current_window) > 0 else 50,
            'current_pass_accuracy': len(team_events[team_events['event_type'] == 'Pass']) / max(1, len(team_events)) * 100,
            
            # 2. Momentum trends (recent vs earlier in window)
            'recent_shots': len(team_events[(team_events['event_type'] == 'Shot') & 
                                          (team_events['timestamp'] >= current_time_seconds - 60)]),
            'recent_attacks': len(team_events[(team_events['event_type'].isin(['Shot', 'Dribble', 'Carry'])) & 
                                            (team_events['timestamp'] >= current_time_seconds - 60)]),
            'momentum_trend': len(team_events[team_events['timestamp'] >= current_time_seconds - 60]) - 
                            len(team_events[team_events['timestamp'] < current_time_seconds - 60]),
            
            # 3. Pressure indicators (predictive of future dominance)
            'applying_pressure': len(team_events[team_events['event_type'] == 'Pressure']),
            'under_pressure': len(opponent_events[opponent_events['event_type'] == 'Pressure']),
            'pressure_balance': len(team_events[team_events['event_type'] == 'Pressure']) - 
                              len(opponent_events[opponent_events['event_type'] == 'Pressure']),
            
            # 4. Team rhythm indicators
            'event_consistency': len(team_events) / 3,  # Events per minute
            'attacking_rhythm': len(team_events[team_events['event_type'].isin(['Shot', 'Dribble', 'Carry'])]),
            'build_up_play': len(team_events[team_events['event_type'].isin(['Pass', 'Carry'])]),
            
            # 5. Opposition state (affects future opportunities)
            'opponent_defensive_actions': len(opponent_events[opponent_events['event_type'].isin(['Pressure', 'Tackle'])]),
            'opponent_possession_loss': max(0, 50 - (len(opponent_events) / len(current_window) * 100)) if len(current_window) > 0 else 0,
        }
        
        return features
    
    def calculate_future_momentum(self, events_df, current_time_seconds, future_time_seconds, team_name):
        """
        Calculate ACTUAL momentum that happened in the future window
        This is used for training labels
        """
        # Future window: next 3 minutes after current time
        future_window = events_df[
            (events_df['timestamp'] >= current_time_seconds) & 
            (events_df['timestamp'] <= future_time_seconds)
        ]
        
        team_future_events = future_window[future_window['team_name'] == team_name]
        
        if len(future_window) == 0:
            return 0
        
        # Calculate momentum that ACTUALLY happened in future
        future_momentum = min(10, max(0,
            len(team_future_events[team_future_events['event_type'] == 'Shot']) * 2.5 +  # Goals threat
            len(team_future_events[team_future_events['event_type'].isin(['Dribble', 'Carry'])]) * 1.2 +  # Attacking
            (len(team_future_events) / len(future_window) * 100) * 0.04 +  # Possession
            len(team_future_events[team_future_events['event_type'] == 'Pressure']) * 0.8 +  # Pressure
            len(team_future_events) * 0.3  # General activity
        ))
        
        return future_momentum
    
    def create_training_data(self, events_df):
        """
        Create training dataset for FUTURE momentum prediction
        """
        print("🔮 Creating FUTURE momentum prediction training data...")
        
        # Add timestamp column
        events_df['timestamp'] = events_df['minute'] * 60 + events_df['second']
        
        training_data = []
        teams = events_df['team_name'].dropna().unique()
        
        # Sample time points (need enough data before and after)
        max_time = int(events_df['timestamp'].max())
        time_points = range(180, max_time - 180, 45)  # Every 45 seconds, ensuring 3 min buffer
        
        print(f"   📊 Sampling {len(time_points)} time points for {len(teams)} teams")
        
        for current_time in time_points:
            future_time = current_time + 180  # 3 minutes in the future
            
            if future_time > max_time:
                continue
                
            for team in teams:
                # Extract CURRENT features (input)
                current_features = self.extract_current_features(events_df, current_time, team)
                
                # Calculate FUTURE momentum (target/label)
                future_momentum = self.calculate_future_momentum(events_df, current_time, future_time, team)
                
                # Add to training data
                current_features['future_momentum'] = future_momentum
                current_features['team'] = team
                current_features['current_time'] = current_time
                current_features['future_time'] = future_time
                
                training_data.append(current_features)
        
        df = pd.DataFrame(training_data)
        print(f"   ✅ Created {len(df)} training samples")
        return df
    
    def train(self, events_df):
        """Train the FUTURE momentum prediction model"""
        print("🚀 TRAINING FUTURE MOMENTUM PREDICTION MODEL")
        print("=" * 60)
        
        # Create training data
        training_df = self.create_training_data(events_df)
        
        if len(training_df) == 0:
            print("❌ No training data available")
            return None
        
        # Prepare features and target
        feature_columns = [col for col in training_df.columns 
                          if col not in ['future_momentum', 'team', 'current_time', 'future_time']]
        self.feature_names = feature_columns
        
        X = training_df[feature_columns]
        y = training_df['future_momentum']
        
        # Train model
        self.model.fit(X, y)
        self.is_trained = True
        
        # Calculate performance metrics
        y_pred = self.model.predict(X)
        
        self.training_stats = {
            'mse': mean_squared_error(y, y_pred),
            'mae': mean_absolute_error(y, y_pred),
            'r2': r2_score(y, y_pred),
            'samples': len(training_df),
            'features': len(feature_columns),
            'mean_future_momentum': y.mean(),
            'std_future_momentum': y.std()
        }
        
        print("✅ FUTURE PREDICTION MODEL TRAINED SUCCESSFULLY!")
        print(f"   📊 Training samples: {self.training_stats['samples']}")
        print(f"   🔢 Features used: {self.training_stats['features']}")
        print(f"   📈 R² Score: {self.training_stats['r2']:.3f}")
        print(f"   📉 MSE: {self.training_stats['mse']:.3f}")
        print(f"   📊 MAE: {self.training_stats['mae']:.3f}")
        print(f"   🎯 Avg Future Momentum: {self.training_stats['mean_future_momentum']:.2f} ± {self.training_stats['std_future_momentum']:.2f}")
        
        return training_df
    
    def predict_future_momentum(self, events_df, current_time_seconds, team_name):
        """
        PREDICT momentum for the NEXT 3 minutes
        This is TRUE prediction, not summary!
        """
        if not self.is_trained:
            return {'predicted_momentum': 5.0, 'current_features': {}, 'confidence': 'untrained'}
        
        # Extract current features
        current_features = self.extract_current_features(events_df, current_time_seconds, team_name)
        
        # Prepare feature vector
        feature_vector = [current_features.get(fname, 0) for fname in self.feature_names]
        
        # PREDICT future momentum
        predicted_momentum = self.model.predict([feature_vector])[0]
        predicted_momentum = max(0, min(10, predicted_momentum))  # Clip to valid range
        
        # Interpret prediction
        if predicted_momentum >= 8:
            interpretation = "🚀 WILL DOMINATE - High momentum predicted next 3 minutes"
        elif predicted_momentum >= 6:
            interpretation = "📈 WILL BUILD UP - Increasing momentum predicted"
        elif predicted_momentum >= 4:
            interpretation = "⚖️ WILL BALANCE - Neutral momentum predicted"
        elif predicted_momentum >= 2:
            interpretation = "📉 WILL STRUGGLE - Low momentum predicted"
        else:
            interpretation = "❄️ WILL BE PASSIVE - Very low momentum predicted"
        
        return {
            'predicted_momentum': predicted_momentum,
            'interpretation': interpretation,
            'current_features': current_features,
            'confidence': 'high' if len(current_features) > 10 else 'medium',
            'prediction_window': f"Next 3 minutes ({(current_time_seconds+180)//60}:{(current_time_seconds+180)%60:02d})"
        }
    
    def get_feature_importance(self):
        """Get feature importance for future momentum prediction"""
        if not self.is_trained:
            return {}
        
        importance_dict = dict(zip(self.feature_names, self.model.feature_importances_))
        return dict(sorted(importance_dict.items(), key=lambda x: x[1], reverse=True))

def test_future_momentum_prediction():
    """Test the future momentum prediction model"""
    print("🔮 TESTING FUTURE MOMENTUM PREDICTION MODEL")
    print("=" * 60)
    
    # Create sample data
    print("📊 Creating sample match data...")
    np.random.seed(42)
    
    sample_data = []
    teams = ['Netherlands', 'England']
    
    # Create 90 minutes of sample events
    for minute in range(90):
        for second in range(0, 60, 15):  # Every 15 seconds
            timestamp = minute * 60 + second
            
            # Simulate events with some patterns
            if np.random.random() < 0.7:  # 70% chance of event
                team = np.random.choice(teams)
                event_type = np.random.choice(['Pass', 'Shot', 'Carry', 'Dribble', 'Pressure'], 
                                            p=[0.4, 0.1, 0.2, 0.1, 0.2])
                
                sample_data.append({
                    'minute': minute,
                    'second': second,
                    'timestamp': timestamp,
                    'event_type': event_type,
                    'team_name': team
                })
    
    events_df = pd.DataFrame(sample_data)
    print(f"   ✅ Created {len(events_df)} sample events")
    
    # Train model
    future_predictor = FutureMomentumPredictor()
    training_df = future_predictor.train(events_df)
    
    if training_df is None:
        print("❌ Training failed")
        return
    
    # Test predictions at different time points
    print("\n🎯 TESTING FUTURE PREDICTIONS")
    print("=" * 60)
    
    test_times = [
        (900, "15:00", "Early game"),
        (1800, "30:00", "Mid first half"),
        (2700, "45:00", "End first half"),
        (3600, "60:00", "Mid second half"),
        (4500, "75:00", "Late game")
    ]
    
    for time_seconds, time_display, phase in test_times:
        if time_seconds <= events_df['timestamp'].max() - 180:  # Need buffer for future
            print(f"\n🕐 TIME: {time_display} ({phase})")
            print("-" * 40)
            
            for team in teams:
                prediction = future_predictor.predict_future_momentum(events_df, time_seconds, team)
                
                print(f"🏟️ {team}:")
                print(f"   🔮 PREDICTED Momentum (next 3 min): {prediction['predicted_momentum']:.2f}/10")
                print(f"   💬 Interpretation: {prediction['interpretation']}")
                print(f"   📅 Prediction Window: {prediction['prediction_window']}")
                print(f"   🔍 Key Current Features:")
                features = prediction['current_features']
                print(f"      - Current shot rate: {features['current_shot_rate']:.1f}/min")
                print(f"      - Current attack rate: {features['current_attack_rate']:.1f}/min")
                print(f"      - Current possession: {features['current_possession_pct']:.1f}%")
                print(f"      - Momentum trend: {features['momentum_trend']:.1f}")
                print()
    
    # Show feature importance
    print("\n📈 MOST PREDICTIVE FEATURES FOR FUTURE MOMENTUM:")
    print("=" * 60)
    
    feature_importance = future_predictor.get_feature_importance()
    for i, (feature, importance) in enumerate(list(feature_importance.items())[:8]):
        print(f"{i+1:2d}. {feature:<25} : {importance:.3f}")
    
    # Model comparison
    print("\n🆚 MODEL COMPARISON:")
    print("=" * 60)
    
    print("📊 PREVIOUS MODEL (Summary):")
    print("   Input:  Last 3 minutes events")
    print("   Output: Current momentum score")
    print("   Question: 'How much momentum does team have RIGHT NOW?'")
    print("   Use case: Live commentary, current assessment")
    print()
    
    print("🔮 NEW MODEL (Future Prediction):")
    print("   Input:  Current 3 minutes events")
    print("   Output: Predicted momentum for NEXT 3 minutes")
    print("   Question: 'How much momentum will team have in next 3 minutes?'")
    print("   Use case: Tactical planning, betting odds, strategy")
    print()
    
    print("🎯 PRACTICAL APPLICATIONS:")
    print("   • Coach: 'Model predicts we'll dominate next 3 minutes - press forward!'")
    print("   • Commentator: 'Netherlands predicted to build momentum - watch for goals!'")
    print("   • Analysis: 'Current patterns suggest England will struggle soon'")
    print("   • Betting: 'Model gives 8.2/10 for next goal probability'")

if __name__ == "__main__":
    test_future_momentum_prediction() 