#!/usr/bin/env python3
"""
Future Momentum Prediction Demo
TRUE prediction model - predicts next 3 minutes based on current patterns
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import warnings
warnings.filterwarnings('ignore')

class FutureMomentumPredictor:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=30, random_state=42)
        self.is_trained = False
        
    def extract_current_features(self, events_df, current_time, team_name):
        # Get last 3 minutes as input
        start_time = max(0, current_time - 180)
        current_window = events_df[(events_df['timestamp'] >= start_time) & 
                                  (events_df['timestamp'] <= current_time)]
        
        team_events = current_window[current_window['team_name'] == team_name]
        
        features = {
            'current_shot_rate': len(team_events[team_events['event_type'] == 'Shot']) / 3,
            'current_attack_rate': len(team_events[team_events['event_type'].isin(['Shot', 'Dribble', 'Carry'])]) / 3,
            'current_possession_pct': len(team_events) / len(current_window) * 100 if len(current_window) > 0 else 50,
            'momentum_trend': len(team_events[team_events['timestamp'] >= current_time - 60]) - len(team_events[team_events['timestamp'] < current_time - 60]),
            'applying_pressure': len(team_events[team_events['event_type'] == 'Pressure'])
        }
        return features
    
    def calculate_future_momentum(self, events_df, current_time, future_time, team_name):
        # Calculate ACTUAL momentum that happened in the FUTURE window
        future_window = events_df[(events_df['timestamp'] >= current_time) & 
                                 (events_df['timestamp'] <= future_time)]
        
        team_future_events = future_window[future_window['team_name'] == team_name]
        
        if len(future_window) == 0:
            return 0
        
        # Calculate momentum that ACTUALLY happened in next 3 minutes
        future_momentum = min(10, max(0,
            len(team_future_events[team_future_events['event_type'] == 'Shot']) * 2.5 +
            len(team_future_events[team_future_events['event_type'].isin(['Dribble', 'Carry'])]) * 1.2 +
            (len(team_future_events) / len(future_window) * 100) * 0.04 +
            len(team_future_events) * 0.3
        ))
        
        return future_momentum
    
    def create_training_data(self, events_df):
        events_df['timestamp'] = events_df['minute'] * 60 + events_df['second']
        
        training_data = []
        teams = events_df['team_name'].dropna().unique()
        
        max_time = int(events_df['timestamp'].max())
        time_points = range(180, max_time - 180, 60)  # Every minute
        
        for current_time in time_points:
            future_time = current_time + 180  # 3 minutes in future
            
            for team in teams:
                # Current features (input)
                current_features = self.extract_current_features(events_df, current_time, team)
                
                # Future momentum (target)
                future_momentum = self.calculate_future_momentum(events_df, current_time, future_time, team)
                
                current_features['future_momentum'] = future_momentum
                current_features['team'] = team
                training_data.append(current_features)
        
        return pd.DataFrame(training_data)
    
    def train(self, events_df):
        training_df = self.create_training_data(events_df)
        
        feature_columns = [col for col in training_df.columns 
                          if col not in ['future_momentum', 'team']]
        
        X = training_df[feature_columns]
        y = training_df['future_momentum']
        
        self.model.fit(X, y)
        self.is_trained = True
        
        return training_df
    
    def predict_future_momentum(self, events_df, current_time, team_name):
        if not self.is_trained:
            return 5.0
        
        features = self.extract_current_features(events_df, current_time, team_name)
        X = [[features['current_shot_rate'], features['current_attack_rate'], 
              features['current_possession_pct'], features['momentum_trend'], 
              features['applying_pressure']]]
        
        predicted_momentum = self.model.predict(X)[0]
        return max(0, min(10, predicted_momentum))

def main():
    # Create sample data
    np.random.seed(42)
    sample_data = []
    teams = ['Netherlands', 'England']

    for minute in range(90):
        for second in range(0, 60, 20):
            timestamp = minute * 60 + second
            
            if np.random.random() < 0.6:
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

    print('🔮 FUTURE MOMENTUM PREDICTION MODEL')
    print('=' * 50)

    # Train model
    future_predictor = FutureMomentumPredictor()
    training_df = future_predictor.train(events_df)

    print(f'✅ Model trained with {len(training_df)} samples')

    # Test predictions
    test_times = [
        (900, '15:00'),
        (1800, '30:00'),
        (2700, '45:00'),
        (3600, '60:00')
    ]

    print('\n🎯 FUTURE PREDICTIONS:')
    print('=' * 50)

    for time_seconds, time_display in test_times:
        if time_seconds <= events_df['timestamp'].max() - 180:
            print(f'\n🕐 AT {time_display}:')
            
            for team in teams:
                predicted = future_predictor.predict_future_momentum(events_df, time_seconds, team)
                
                print(f'  {team}:')
                print(f'    🔮 PREDICTED momentum (next 3 min): {predicted:.2f}/10')
                
                # Show what current features were used
                features = future_predictor.extract_current_features(events_df, time_seconds, team)
                shot_rate = features['current_shot_rate']
                attack_rate = features['current_attack_rate']
                possession = features['current_possession_pct']
                print(f'    📊 Current shot rate: {shot_rate:.1f}/min')
                print(f'    📊 Current attack rate: {attack_rate:.1f}/min')
                print(f'    📊 Current possession: {possession:.1f}%')

    print('\n🆚 MODEL COMPARISON:')
    print('=' * 50)
    print('📊 OLD MODEL (Summary):')
    print('   Input:  Last 3 minutes events')
    print('   Output: Current momentum score')
    print('   Question: "How much momentum does team have RIGHT NOW?"')
    print()
    print('🔮 NEW MODEL (Future Prediction):')
    print('   Input:  Current 3 minutes events')
    print('   Output: Predicted momentum for NEXT 3 minutes')
    print('   Question: "How much momentum will team have in next 3 minutes?"')
    print()
    print('🎯 APPLICATIONS:')
    print('   • Coach: "Model predicts we will dominate next 3 minutes - attack!"')
    print('   • Commentator: "Netherlands predicted to build momentum - watch for goals!"')
    print('   • Analysis: "Current patterns suggest England will struggle soon"')
    
    # Show detailed example
    print('\n🔬 DETAILED EXAMPLE:')
    print('=' * 50)
    
    example_time = 1800  # 30:00
    example_team = 'Netherlands'
    
    print(f'📥 INPUT (Current State at {example_time//60}:{example_time%60:02d}):')
    features = future_predictor.extract_current_features(events_df, example_time, example_team)
    print(f'   - Shot rate in last 3 min: {features["current_shot_rate"]:.1f}/min')
    print(f'   - Attack rate in last 3 min: {features["current_attack_rate"]:.1f}/min')
    print(f'   - Possession in last 3 min: {features["current_possession_pct"]:.1f}%')
    print(f'   - Momentum trend: {features["momentum_trend"]:.1f}')
    print(f'   - Applying pressure: {features["applying_pressure"]:.1f}')
    
    predicted = future_predictor.predict_future_momentum(events_df, example_time, example_team)
    future_end_time = example_time + 180
    
    print(f'\n📤 OUTPUT (Prediction for {future_end_time//60}:{future_end_time%60:02d}):')
    print(f'   - Predicted momentum: {predicted:.2f}/10')
    
    if predicted >= 7:
        interpretation = 'HIGH - Will dominate next 3 minutes'
    elif predicted >= 5:
        interpretation = 'MEDIUM - Will have balanced momentum'
    else:
        interpretation = 'LOW - Will struggle next 3 minutes'
    
    print(f'   - Interpretation: {interpretation}')
    
    print('\n⚡ KEY DIFFERENCE:')
    print('   ❌ OLD: "Netherlands has 7.2/10 momentum right now"')
    print('   ✅ NEW: "Netherlands will have 6.8/10 momentum in next 3 minutes"')

if __name__ == "__main__":
    main() 