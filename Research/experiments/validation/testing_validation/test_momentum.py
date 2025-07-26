import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import warnings
warnings.filterwarnings('ignore')

print('MOMENTUM PREDICTION MODEL TEST')
print('=' * 60)

# Load Euro 2024 data
try:
    events_df = pd.read_csv('euro_2024_sample_100_rows.csv')
    print(f'Loaded {len(events_df)} events for testing')
    print(f'Match: {events_df["home_team"].iloc[0]} vs {events_df["away_team"].iloc[0]}')
    teams = events_df['team_name'].dropna().unique()
    print(f'Teams: {list(teams)}')
    print()
except Exception as e:
    print(f'Error loading data: {e}')
    exit()

# Add timestamp and analyze data
events_df['timestamp'] = events_df['minute'] * 60 + events_df['second']
print('DATA ANALYSIS:')
print(f'Time range: {events_df["minute"].min()}-{events_df["minute"].max()} minutes')
print(f'Timestamp range: {events_df["timestamp"].min()}-{events_df["timestamp"].max()} seconds')
print(f'Event types: {dict(events_df["event_type"].value_counts().head())}')
print()

# Simple Momentum Predictor
class MomentumPredictor:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=30, random_state=42)
        self.feature_names = []
        self.is_trained = False
    
    def extract_features(self, events_df, current_time, team_name):
        # Extract features from last 3 minutes (or available data)
        start_time = max(0, current_time - 180)
        recent = events_df[
            (events_df['timestamp'] >= start_time) & 
            (events_df['timestamp'] <= current_time)
        ]
        team_events = recent[recent['team_name'] == team_name]
        
        features = {
            'total_events': len(team_events),
            'pass_count': len(team_events[team_events['event_type'] == 'Pass']),
            'shot_count': len(team_events[team_events['event_type'] == 'Shot']),
            'carry_count': len(team_events[team_events['event_type'] == 'Carry']),
            'dribble_count': len(team_events[team_events['event_type'] == 'Dribble']),
            'possession_pct': len(team_events) / len(recent) * 100 if len(recent) > 0 else 50,
            'attacking_actions': len(team_events[team_events['event_type'].isin(['Shot', 'Dribble', 'Carry'])]),
            'events_per_minute': len(team_events) / 3 if len(team_events) > 0 else 0,
            'recent_intensity': len(team_events[team_events['timestamp'] >= current_time - 60]) * 2
        }
        return features
    
    def train(self, events_df):
        print('TRAINING MOMENTUM PREDICTION MODEL')
        print('=' * 50)
        
        training_data = []
        teams = events_df['team_name'].dropna().unique()
        
        # Adjust sampling based on available data
        max_time = int(events_df['timestamp'].max())
        min_time = int(events_df['timestamp'].min())
        
        print(f'Available time range: {min_time}-{max_time} seconds')
        
        # Sample more frequently for limited data
        start_sampling = max(180, min_time + 60)  # Start after 3 minutes or 1 minute into data
        sampling_interval = 15 if max_time - start_sampling < 300 else 30  # Sample every 15-30 seconds
        
        for time_point in range(start_sampling, max_time, sampling_interval):
            for team in teams:
                features = self.extract_features(events_df, time_point, team)
                
                # Create momentum score (0-10)
                momentum = min(10, max(0,
                    features['attacking_actions'] * 1.5 +
                    features['possession_pct'] * 0.05 +
                    features['shot_count'] * 2.0 +
                    features['recent_intensity'] * 0.3 +
                    features['events_per_minute'] * 0.5
                ))
                
                features['momentum'] = momentum
                features['time_point'] = time_point
                features['team'] = team
                training_data.append(features)
        
        df = pd.DataFrame(training_data)
        
        if len(df) == 0:
            print('Creating synthetic training data for demonstration...')
            # Create synthetic data for demonstration
            for i in range(20):
                for team in teams:
                    features = {
                        'total_events': np.random.randint(5, 25),
                        'pass_count': np.random.randint(3, 15),
                        'shot_count': np.random.randint(0, 3),
                        'carry_count': np.random.randint(1, 8),
                        'dribble_count': np.random.randint(0, 4),
                        'possession_pct': np.random.uniform(30, 70),
                        'attacking_actions': np.random.randint(1, 10),
                        'events_per_minute': np.random.uniform(2, 12),
                        'recent_intensity': np.random.randint(0, 8)
                    }
                    momentum = min(10, max(0,
                        features['attacking_actions'] * 1.5 +
                        features['possession_pct'] * 0.05 +
                        features['shot_count'] * 2.0 +
                        features['recent_intensity'] * 0.3 +
                        features['events_per_minute'] * 0.5
                    ))
                    features['momentum'] = momentum
                    training_data.append(features)
            df = pd.DataFrame(training_data)
        
        print(f'Training samples created: {len(df)}')
        
        self.feature_names = [c for c in df.columns if c not in ['momentum', 'time_point', 'team']]
        X = df[self.feature_names]
        y = df['momentum']
        
        self.model.fit(X, y)
        self.is_trained = True
        
        y_pred = self.model.predict(X)
        mse = mean_squared_error(y, y_pred)
        mae = mean_absolute_error(y, y_pred)
        r2 = r2_score(y, y_pred)
        
        print('MODEL TRAINED SUCCESSFULLY!')
        print(f'   Training samples: {len(df)}')
        print(f'   Features used: {len(self.feature_names)}')
        print(f'   R2 Score: {r2:.3f}')
        print(f'   MSE: {mse:.3f}')
        print(f'   MAE: {mae:.3f}')
        print(f'   Avg Momentum: {y.mean():.2f} +/- {y.std():.2f}')
        
        return df
    
    def predict(self, events_df, time_point, team):
        if not self.is_trained:
            return 5.0, {}
        features = self.extract_features(events_df, time_point, team)
        X = [features.get(f, 0) for f in self.feature_names]
        momentum = self.model.predict([X])[0]
        return max(0, min(10, momentum)), features

# Train the model
momentum_model = MomentumPredictor()
training_data = momentum_model.train(events_df)

print()
print('=' * 60)
print('FEATURE IMPORTANCE ANALYSIS')
print('=' * 60)

importance = dict(zip(momentum_model.feature_names, momentum_model.model.feature_importances_))
sorted_importance = sorted(importance.items(), key=lambda x: x[1], reverse=True)

print('TOP FEATURES FOR MOMENTUM PREDICTION:')
for i, (feature, score) in enumerate(sorted_importance, 1):
    print(f'   {i:2d}. {feature:<20} : {score:.3f}')

print()
print('=' * 60)
print('MOMENTUM PREDICTION EXAMPLES')
print('=' * 60)

# Test at available time points
available_times = sorted(events_df['timestamp'].unique())
test_indices = [0, len(available_times)//3, len(available_times)*2//3, -1]

for idx in test_indices:
    if idx < len(available_times):
        time_seconds = available_times[idx]
        time_display = f'{int(time_seconds//60)}:{int(time_seconds%60):02d}'
        
        print(f'\nTIME: {time_display}')
        print('-' * 30)
        
        for team in teams:
            momentum, features = momentum_model.predict(events_df, time_seconds, team)
            
            if momentum >= 7:
                interpretation = 'HIGH MOMENTUM'
            elif momentum >= 4:
                interpretation = 'MEDIUM MOMENTUM'
            else:
                interpretation = 'LOW MOMENTUM'
            
            print(f'{team}:')
            print(f'   Score: {momentum:.2f}/10 - {interpretation}')
            print(f'   Events: {features["total_events"]} | Possession: {features["possession_pct"]:.1f}%')
            print(f'   Attacking: {features["attacking_actions"]} | Shots: {features["shot_count"]}')
            print()

print('=' * 60)
print('DETAILED INPUT/OUTPUT EXAMPLE')
print('=' * 60)

# Use a real time point from our data
example_time = available_times[len(available_times)//2]
example_team = teams[0]
momentum, features = momentum_model.predict(events_df, example_time, example_team)

print(f'INPUT:')
print(f'   Time: {int(example_time//60)}:{int(example_time%60):02d}')
print(f'   Team: {example_team}')
print(f'   Window: Last 3 minutes (or available data)')

print(f'\nEXTRACTED FEATURES:')
for feature_name, value in features.items():
    print(f'   {feature_name:<20} : {value:>8.2f}')

print(f'\nOUTPUT:')
print(f'   Momentum Score: {momentum:.2f}/10')
if momentum >= 7:
    interp = 'HIGH - Team dominating play'
elif momentum >= 4:
    interp = 'MEDIUM - Balanced momentum'
else:
    interp = 'LOW - Team under pressure'
print(f'   Interpretation: {interp}')

print()
print('=' * 60)
print('TECHNIQUES AND METHODS')
print('=' * 60)

print('FEATURE ENGINEERING:')
print('   1. Sliding Window: 3-minute lookback for temporal relevance')
print('   2. Event Aggregation: Count events by type (Pass, Shot, Carry)')
print('   3. Possession Metrics: Team vs total events ratio')
print('   4. Attacking Intent: Weight aggressive actions higher')
print('   5. Recent Activity: Last minute events weighted 2x')

print('\nMACHINE LEARNING:')
print('   1. Algorithm: Random Forest Regressor')
print('   2. Features: 9 engineered features from raw events')
print('   3. Target: Composite momentum score (0-10)')
print('   4. Training: Samples throughout match timeline')

print('\nEVALUATION METRICS:')
print('   1. R2 Score: Measures variance explained by model')
print('   2. MSE/MAE: Prediction accuracy metrics')
print('   3. Feature Importance: Shows most predictive features')
print('   4. Real-time Testing: Predictions at different game phases')

print('\nMODEL ARCHITECTURE:')
print('   - Input: Event data from last 3 minutes')
print('   - Processing: Feature extraction and engineering')
print('   - Model: Random Forest with 30 estimators')
print('   - Output: Momentum score (0-10) with interpretation')

print('\nUSE CASES:')
print('   1. Live match commentary: "Team gaining momentum!"')
print('   2. Tactical analysis: Identify momentum shifts')
print('   3. Performance evaluation: Track team dynamics')
print('   4. Prediction models: Input for outcome prediction')

print('\nMODEL TESTING COMPLETE!')
print('Successfully demonstrated momentum prediction using sliding window approach') 