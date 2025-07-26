import numpy as np
from sklearn.ensemble import RandomForestRegressor
import pandas as pd

class EnhancedMomentumModel:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=50, random_state=42)
        # Enhanced features including opponent data and comparisons
        self.feature_names = [
            # Team features
            'team_shots', 'team_possession', 'team_attacks', 'team_intensity', 'team_events',
            # Opponent features
            'opp_shots', 'opp_possession', 'opp_attacks', 'opp_intensity', 'opp_events',
            # Comparative features (the key insight!)
            'shot_advantage', 'possession_advantage', 'attack_advantage', 'pressure_ratio', 'event_ratio'
        ]
        self.trained = False
    
    def calculate_comparative_features(self, team_data, opponent_data):
        """Calculate head-to-head comparative features"""
        features = {}
        
        # Team features
        features['team_shots'] = team_data['shots']
        features['team_possession'] = team_data['possession']
        features['team_attacks'] = team_data['attacks']
        features['team_intensity'] = team_data['intensity']
        features['team_events'] = team_data['events']
        
        # Opponent features
        features['opp_shots'] = opponent_data['shots']
        features['opp_possession'] = opponent_data['possession']
        features['opp_attacks'] = opponent_data['attacks']
        features['opp_intensity'] = opponent_data['intensity']
        features['opp_events'] = opponent_data['events']
        
        # Comparative features (KEY IMPROVEMENT!)
        features['shot_advantage'] = team_data['shots'] - opponent_data['shots']
        features['possession_advantage'] = team_data['possession'] - opponent_data['possession']
        features['attack_advantage'] = team_data['attacks'] - opponent_data['attacks']
        
        # Ratios (avoid division by zero)
        features['pressure_ratio'] = team_data['intensity'] / max(opponent_data['intensity'], 1)
        features['event_ratio'] = team_data['events'] / max(opponent_data['events'], 1)
        
        return features
    
    def create_realistic_momentum(self, features):
        """Create momentum considering opponent context"""
        # Base team performance
        team_score = (
            features['team_shots'] * 1.2 +
            features['team_attacks'] * 0.1 +
            features['team_possession'] * 0.02 +
            features['team_intensity'] * 0.05
        )
        
        # Opponent pressure (reduces momentum)
        opponent_pressure = (
            features['opp_shots'] * 0.8 +
            features['opp_attacks'] * 0.08 +
            features['opp_intensity'] * 0.04
        )
        
        # Comparative advantages (KEY FACTORS!)
        comparative_boost = (
            features['shot_advantage'] * 0.8 +  # Shot superiority is crucial
            features['possession_advantage'] * 0.01 +  # Possession control
            features['attack_advantage'] * 0.06 +  # Attacking dominance
            (features['pressure_ratio'] - 1) * 2.0  # Pressure dominance
        )
        
        # Final momentum calculation
        momentum = team_score - opponent_pressure * 0.3 + comparative_boost
        
        # Normalize to 0-10
        momentum = max(0, min(10, momentum))
        return momentum
    
    def train_model(self):
        """Train with realistic head-to-head scenarios"""
        print("🚀 Training Enhanced Momentum Model (with Opponent Data)...")
        
        np.random.seed(42)
        training_data = []
        
        # Create realistic match scenarios
        scenario_types = [
            # Dominant vs Passive
            {
                'name': 'Dominant vs Passive',
                'team_ranges': {'shots': (3, 7), 'possession': (60, 80), 'attacks': (15, 25), 'intensity': (20, 35), 'events': (35, 55)},
                'opp_ranges': {'shots': (0, 2), 'possession': (20, 40), 'attacks': (3, 8), 'intensity': (5, 15), 'events': (15, 25)}
            },
            # Balanced battle
            {
                'name': 'Balanced Battle',
                'team_ranges': {'shots': (1, 4), 'possession': (45, 55), 'attacks': (8, 15), 'intensity': (12, 22), 'events': (20, 35)},
                'opp_ranges': {'shots': (1, 4), 'possession': (45, 55), 'attacks': (8, 15), 'intensity': (12, 22), 'events': (20, 35)}
            },
            # Under pressure
            {
                'name': 'Under Pressure',
                'team_ranges': {'shots': (0, 2), 'possession': (25, 45), 'attacks': (3, 10), 'intensity': (8, 18), 'events': (15, 30)},
                'opp_ranges': {'shots': (2, 6), 'possession': (55, 75), 'attacks': (12, 22), 'intensity': (18, 30), 'events': (30, 50)}
            },
            # Counter-attacking
            {
                'name': 'Counter-attacking',
                'team_ranges': {'shots': (2, 5), 'possession': (35, 50), 'attacks': (6, 12), 'intensity': (15, 25), 'events': (18, 32)},
                'opp_ranges': {'shots': (1, 3), 'possession': (50, 65), 'attacks': (10, 18), 'intensity': (10, 20), 'events': (25, 40)}
            }
        ]
        
        # Generate training examples
        for scenario in scenario_types:
            for _ in range(30):  # 30 examples per scenario
                # Generate team data
                team_data = {}
                for key, (min_val, max_val) in scenario['team_ranges'].items():
                    if key == 'possession':
                        team_data[key] = np.random.uniform(min_val, max_val)
                    else:
                        team_data[key] = np.random.randint(min_val, max_val + 1)
                
                # Generate opponent data
                opp_data = {}
                for key, (min_val, max_val) in scenario['opp_ranges'].items():
                    if key == 'possession':
                        opp_data[key] = np.random.uniform(min_val, max_val)
                    else:
                        opp_data[key] = np.random.randint(min_val, max_val + 1)
                
                # Ensure possession adds to ~100%
                total_poss = team_data['possession'] + opp_data['possession']
                if total_poss > 0:
                    team_data['possession'] = (team_data['possession'] / total_poss) * 100
                    opp_data['possession'] = (opp_data['possession'] / total_poss) * 100
                
                # Calculate features
                features = self.calculate_comparative_features(team_data, opp_data)
                
                # Calculate target momentum
                momentum = self.create_realistic_momentum(features)
                
                # Add noise
                momentum = max(0, min(10, momentum + np.random.normal(0, 0.2)))
                
                # Add to training data
                row = {**features, 'momentum': momentum, 'scenario': scenario['name']}
                training_data.append(row)
        
        # Train model
        df = pd.DataFrame(training_data)
        X = df[self.feature_names]
        y = df['momentum']
        
        self.model.fit(X, y)
        self.trained = True
        
        # Performance metrics
        from sklearn.metrics import r2_score
        y_pred = self.model.predict(X)
        r2 = r2_score(y, y_pred)
        
        print(f"✅ Enhanced model trained with R² = {r2:.3f}")
        print(f"📊 Training examples: {len(df)}")
        print(f"📈 Momentum range: {y.min():.1f} - {y.max():.1f}")
        
        # Show scenario distribution
        scenario_counts = df['scenario'].value_counts()
        print(f"\n📋 Scenario Distribution:")
        for scenario, count in scenario_counts.items():
            avg_momentum = df[df['scenario'] == scenario]['momentum'].mean()
            print(f"   {scenario:<20}: {count:2d} examples (avg: {avg_momentum:.1f})")
    
    def predict(self, team_data, opponent_data):
        """Predict momentum given team and opponent data"""
        if not self.trained:
            return 5.0
        
        features = self.calculate_comparative_features(team_data, opponent_data)
        X = np.array([[features[name] for name in self.feature_names]])
        
        return self.model.predict(X)[0]

def main():
    print("🎯 ENHANCED MOMENTUM: INCLUDING OPPONENT DATA")
    print("=" * 70)
    
    print("\n💡 YOUR BRILLIANT INSIGHT:")
    print("   🔄 OLD: Only team stats → Momentum")
    print("   🔥 NEW: Team vs Opponent → Relative Momentum")
    print("   🎯 KEY: Same stats vs different opponents = different momentum!")

if __name__ == "__main__":
    main() 