import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import warnings
warnings.filterwarnings('ignore')

class RealisticMomentumPredictor:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=30, random_state=42)
        self.feature_names = ['total_events', 'pass_count', 'shot_count', 'carry_count', 
                             'dribble_count', 'possession_pct', 'attacking_actions', 
                             'events_per_minute', 'recent_intensity']
        self.is_trained = False
    
    def train_realistic(self):
        """Train with realistic momentum scenarios"""
        np.random.seed(42)
        
        # Create realistic training data with known momentum patterns
        training_data = []
        
        # Low momentum scenarios (0-3)
        for _ in range(30):
            features = {
                'total_events': np.random.randint(5, 20),
                'pass_count': np.random.randint(3, 12),
                'shot_count': np.random.randint(0, 2),
                'carry_count': np.random.randint(1, 6),
                'dribble_count': np.random.randint(0, 3),
                'possession_pct': np.random.uniform(20, 45),
                'attacking_actions': np.random.randint(1, 8),
                'events_per_minute': np.random.uniform(2, 8),
                'recent_intensity': np.random.randint(2, 12)
            }
            momentum = np.random.uniform(1, 3.5)
            training_data.append({**features, 'momentum': momentum})
        
        # Medium momentum scenarios (3-7)
        for _ in range(40):
            features = {
                'total_events': np.random.randint(20, 40),
                'pass_count': np.random.randint(10, 25),
                'shot_count': np.random.randint(1, 4),
                'carry_count': np.random.randint(5, 12),
                'dribble_count': np.random.randint(2, 6),
                'possession_pct': np.random.uniform(40, 65),
                'attacking_actions': np.random.randint(6, 18),
                'events_per_minute': np.random.uniform(7, 15),
                'recent_intensity': np.random.randint(10, 25)
            }
            momentum = np.random.uniform(3.5, 7)
            training_data.append({**features, 'momentum': momentum})
        
        # High momentum scenarios (7-10)
        for _ in range(30):
            features = {
                'total_events': np.random.randint(35, 60),
                'pass_count': np.random.randint(20, 40),
                'shot_count': np.random.randint(3, 8),
                'carry_count': np.random.randint(10, 20),
                'dribble_count': np.random.randint(4, 12),
                'possession_pct': np.random.uniform(60, 85),
                'attacking_actions': np.random.randint(15, 35),
                'events_per_minute': np.random.uniform(12, 25),
                'recent_intensity': np.random.randint(20, 45)
            }
            momentum = np.random.uniform(7, 10)
            training_data.append({**features, 'momentum': momentum})
        
        # Convert to dataframe and train
        df = pd.DataFrame(training_data)
        X = df[self.feature_names]
        y = df['momentum']
        
        self.model.fit(X, y)
        self.is_trained = True
        
        # Show training performance
        y_pred = self.model.predict(X)
        from sklearn.metrics import r2_score
        r2 = r2_score(y, y_pred)
        print(f"Model trained with R² = {r2:.3f}")
        
        return df
    
    def predict_with_interpretation(self, features):
        if not self.is_trained:
            return 5.0, 'Model not trained'
        
        X = [features.get(f, 0) for f in self.feature_names]
        momentum = self.model.predict([X])[0]
        momentum = max(0, min(10, momentum))
        
        if momentum >= 8.5:
            interpretation = '🔥 VERY HIGH MOMENTUM - Complete dominance'
        elif momentum >= 7.0:
            interpretation = '🔥 HIGH MOMENTUM - Strong control'
        elif momentum >= 5.5:
            interpretation = '📈 BUILDING MOMENTUM - Gaining advantage'
        elif momentum >= 4.0:
            interpretation = '⚖️ NEUTRAL MOMENTUM - Balanced play'
        elif momentum >= 2.5:
            interpretation = '📉 LOW MOMENTUM - Under pressure'
        else:
            interpretation = '❄️ VERY LOW MOMENTUM - Struggling'
        
        return momentum, interpretation

def main():
    print('🎯 REALISTIC MOMENTUM PREDICTION EXAMPLES')
    print('=' * 80)

    # Initialize and train model
    momentum_model = RealisticMomentumPredictor()
    momentum_model.train_realistic()

    print('\n📊 DETAILED INPUT/OUTPUT EXAMPLES')
    print('=' * 80)

    # Realistic example scenarios with expected different momentum levels
    examples = [
        {
            'scenario': 'HIGH ATTACKING MOMENTUM',
            'description': 'Team dominating final third with multiple shots',
            'features': {
                'total_events': 45, 'pass_count': 18, 'shot_count': 5, 'carry_count': 12,
                'dribble_count': 8, 'possession_pct': 75.0, 'attacking_actions': 25,
                'events_per_minute': 15.0, 'recent_intensity': 30
            },
            'context': {'time': '67:23', 'team': 'Manchester City', 'situation': 'Sustained pressure in opponent box'}
        },
        {
            'scenario': 'DEFENSIVE MOMENTUM (LOW)',
            'description': 'Team struggling to keep possession',
            'features': {
                'total_events': 12, 'pass_count': 6, 'shot_count': 0, 'carry_count': 2,
                'dribble_count': 1, 'possession_pct': 28.0, 'attacking_actions': 3,
                'events_per_minute': 4.0, 'recent_intensity': 6
            },
            'context': {'time': '23:45', 'team': 'Liverpool', 'situation': 'Deep defensive shape, limited attacks'}
        },
        {
            'scenario': 'BALANCED MIDFIELD BATTLE',
            'description': 'Even contest with moderate possession',
            'features': {
                'total_events': 28, 'pass_count': 15, 'shot_count': 2, 'carry_count': 8,
                'dribble_count': 3, 'possession_pct': 52.0, 'attacking_actions': 13,
                'events_per_minute': 9.3, 'recent_intensity': 16
            },
            'context': {'time': '41:12', 'team': 'Barcelona', 'situation': 'Midfield possession battle'}
        },
        {
            'scenario': 'LATE GAME DESPERATION (HIGH)',
            'description': 'Team pushing for equalizer with high intensity',
            'features': {
                'total_events': 52, 'pass_count': 22, 'shot_count': 6, 'carry_count': 15,
                'dribble_count': 9, 'possession_pct': 68.0, 'attacking_actions': 30,
                'events_per_minute': 17.3, 'recent_intensity': 35
            },
            'context': {'time': '87:56', 'team': 'Real Madrid', 'situation': 'Trailing 1-0, all-out attack'}
        },
        {
            'scenario': 'EARLY GAME CAUTION (LOW)',
            'description': 'Teams feeling each other out cautiously',
            'features': {
                'total_events': 8, 'pass_count': 5, 'shot_count': 0, 'carry_count': 2,
                'dribble_count': 0, 'possession_pct': 45.0, 'attacking_actions': 2,
                'events_per_minute': 2.7, 'recent_intensity': 4
            },
            'context': {'time': '08:15', 'team': 'Bayern Munich', 'situation': 'Cautious start, no risks taken'}
        },
        {
            'scenario': 'DOMINANT POSSESSION (MEDIUM-HIGH)',
            'description': 'High possession but limited penetration',
            'features': {
                'total_events': 38, 'pass_count': 28, 'shot_count': 1, 'carry_count': 6,
                'dribble_count': 2, 'possession_pct': 78.0, 'attacking_actions': 9,
                'events_per_minute': 12.7, 'recent_intensity': 18
            },
            'context': {'time': '34:28', 'team': 'Spain', 'situation': 'Tiki-taka without final ball'}
        }
    ]

    # Process each example
    for i, example in enumerate(examples, 1):
        print(f'\n🎮 EXAMPLE {i}: {example["scenario"]}')
        print('=' * 60)
        
        # Context
        print(f'📋 CONTEXT:')
        print(f'   🕐 Time: {example["context"]["time"]}')
        print(f'   🏟️ Team: {example["context"]["team"]}')
        print(f'   📝 Situation: {example["context"]["situation"]}')
        print(f'   💭 Description: {example["description"]}')
        
        # Input features
        print(f'\n📥 INPUT FEATURES:')
        features = example['features']
        for feature, value in features.items():
            if 'pct' in feature:
                print(f'   {feature:<20} : {value:>8.1f}%')
            else:
                print(f'   {feature:<20} : {value:>8.1f}')
        
        # Prediction
        momentum, interpretation = momentum_model.predict_with_interpretation(features)
        
        # Output
        print(f'\n📤 OUTPUT:')
        print(f'   🎯 Momentum Score: {momentum:.2f}/10')
        print(f'   💬 Interpretation: {interpretation}')
        
        # Feature analysis breakdown
        print(f'\n🔍 FEATURE ANALYSIS:')
        high_impact_features = []
        if features['attacking_actions'] > 20:
            high_impact_features.append(f"High attacking actions ({features['attacking_actions']})")
        if features['shot_count'] > 3:
            high_impact_features.append(f"Multiple shots ({features['shot_count']})")
        if features['possession_pct'] > 65:
            high_impact_features.append(f"Dominant possession ({features['possession_pct']:.1f}%)")
        elif features['possession_pct'] < 35:
            high_impact_features.append(f"Low possession ({features['possession_pct']:.1f}%)")
        if features['events_per_minute'] > 15:
            high_impact_features.append(f"High intensity ({features['events_per_minute']:.1f} events/min)")
        elif features['events_per_minute'] < 5:
            high_impact_features.append(f"Low intensity ({features['events_per_minute']:.1f} events/min)")
        
        for feature in high_impact_features:
            print(f'   ▶️ {feature}')
        
        # Tactical recommendation
        print(f'\n⚽ TACTICAL RECOMMENDATION:')
        if momentum >= 8:
            print(f'   🔥 Maintain aggressive approach - team is dominating')
        elif momentum >= 6:
            print(f'   📈 Continue current tactics - momentum building')
        elif momentum >= 4:
            print(f'   ⚖️ Fine-tune approach - small adjustments needed')
        else:
            print(f'   🔄 Major tactical change required - current approach not working')

    print('\n' + '=' * 80)
    print('⚔️ MOMENTUM COMPARISON SCENARIOS')
    print('=' * 80)

    # Comparison examples with different momentum levels
    comparisons = [
        {
            'title': 'ATTACKING vs DEFENSIVE STYLES',
            'team_a': {
                'name': 'Team A (High Attacking)',
                'features': {
                    'total_events': 45, 'pass_count': 20, 'shot_count': 6, 'carry_count': 14,
                    'dribble_count': 8, 'possession_pct': 62.0, 'attacking_actions': 28,
                    'events_per_minute': 15.0, 'recent_intensity': 32
                }
            },
            'team_b': {
                'name': 'Team B (Low Defensive)',
                'features': {
                    'total_events': 18, 'pass_count': 10, 'shot_count': 0, 'carry_count': 4,
                    'dribble_count': 1, 'possession_pct': 38.0, 'attacking_actions': 5,
                    'events_per_minute': 6.0, 'recent_intensity': 8
                }
            }
        },
        {
            'title': 'POSSESSION vs COUNTER-ATTACK',
            'team_a': {
                'name': 'Team A (Medium Possession)',
                'features': {
                    'total_events': 35, 'pass_count': 25, 'shot_count': 2, 'carry_count': 6,
                    'dribble_count': 2, 'possession_pct': 72.0, 'attacking_actions': 10,
                    'events_per_minute': 11.7, 'recent_intensity': 16
                }
            },
            'team_b': {
                'name': 'Team B (Medium Counter)',
                'features': {
                    'total_events': 22, 'pass_count': 12, 'shot_count': 3, 'carry_count': 5,
                    'dribble_count': 2, 'possession_pct': 28.0, 'attacking_actions': 10,
                    'events_per_minute': 7.3, 'recent_intensity': 18
                }
            }
        }
    ]

    for i, comp in enumerate(comparisons, 1):
        print(f'\n⚔️ COMPARISON {i}: {comp["title"]}')
        print('-' * 60)
        
        momentum_a, interp_a = momentum_model.predict_with_interpretation(comp['team_a']['features'])
        momentum_b, interp_b = momentum_model.predict_with_interpretation(comp['team_b']['features'])
        
        print(f'\n🔵 {comp["team_a"]["name"]}:')
        print(f'   📊 Momentum: {momentum_a:.2f}/10')
        print(f'   💬 Status: {interp_a}')
        features_a = comp['team_a']['features']
        print(f'   📈 Stats: {features_a["possession_pct"]:.1f}% poss | {features_a["shot_count"]} shots | {features_a["attacking_actions"]} attacks')
        
        print(f'\n🔴 {comp["team_b"]["name"]}:')
        print(f'   📊 Momentum: {momentum_b:.2f}/10')
        print(f'   💬 Status: {interp_b}')
        features_b = comp['team_b']['features']
        print(f'   📈 Stats: {features_b["possession_pct"]:.1f}% poss | {features_b["shot_count"]} shots | {features_b["attacking_actions"]} attacks')
        
        print(f'\n🎯 MOMENTUM GAP: {abs(momentum_a - momentum_b):.2f} points')
        if momentum_a > momentum_b + 0.5:
            print(f'   📈 {comp["team_a"]["name"].split("(")[0].strip()} has significant advantage')
        elif momentum_b > momentum_a + 0.5:
            print(f'   📈 {comp["team_b"]["name"].split("(")[0].strip()} has significant advantage')
        else:
            print(f'   ⚖️ Very close momentum battle')

    print('\n' + '=' * 80)
    print('🎭 EDGE CASE SCENARIOS')
    print('=' * 80)

    edge_cases = [
        {
            'case': 'ULTRA LOW ACTIVITY',
            'features': {
                'total_events': 3, 'pass_count': 2, 'shot_count': 0, 'carry_count': 1,
                'dribble_count': 0, 'possession_pct': 25.0, 'attacking_actions': 1,
                'events_per_minute': 1.0, 'recent_intensity': 2
            }
        },
        {
            'case': 'EXTREME HIGH INTENSITY',
            'features': {
                'total_events': 65, 'pass_count': 35, 'shot_count': 8, 'carry_count': 18,
                'dribble_count': 12, 'possession_pct': 80.0, 'attacking_actions': 38,
                'events_per_minute': 21.7, 'recent_intensity': 45
            }
        },
        {
            'case': 'SHOTS WITHOUT POSSESSION',
            'features': {
                'total_events': 20, 'pass_count': 8, 'shot_count': 7, 'carry_count': 4,
                'dribble_count': 1, 'possession_pct': 25.0, 'attacking_actions': 12,
                'events_per_minute': 6.7, 'recent_intensity': 16
            }
        }
    ]

    for i, case in enumerate(edge_cases, 1):
        print(f'\n🎭 EDGE CASE {i}: {case["case"]}')
        print('-' * 40)
        
        momentum, interpretation = momentum_model.predict_with_interpretation(case['features'])
        
        features = case['features']
        print(f'📥 INPUT: {features["total_events"]} events | {features["possession_pct"]:.1f}% possession | {features["shot_count"]} shots')
        print(f'📤 OUTPUT: {momentum:.2f}/10 - {interpretation}')
        
        # Edge case analysis
        if case['case'] == 'ULTRA LOW ACTIVITY':
            print(f'   💡 Analysis: Very passive phase, likely early game or defensive period')
        elif case['case'] == 'EXTREME HIGH INTENSITY':
            print(f'   💡 Analysis: Frantic attacking phase, possibly late in game')
        else:
            print(f'   💡 Analysis: Counter-attacking style with clinical finishing')

    print(f'\n' + '=' * 80)
    print('📋 COMPREHENSIVE SUMMARY')
    print('=' * 80)
    print('✅ Demonstrated realistic momentum variations:')
    print('   🔥 High Momentum (8-10): Dominant attacking phases')
    print('   📈 Medium Momentum (4-8): Balanced competitive phases')  
    print('   📉 Low Momentum (0-4): Defensive/struggling phases')
    print('')
    print('📊 Total Examples Provided:')
    print('   • 6 detailed scenario examples')
    print('   • 2 head-to-head team comparisons')
    print('   • 3 edge case demonstrations')
    print('   • Complete input/output analysis for each')
    print('')
    print('🎯 Each example includes:')
    print('   ✓ Match context and timing')
    print('   ✓ Complete feature breakdown')
    print('   ✓ Momentum score with interpretation')
    print('   ✓ Feature impact analysis')
    print('   ✓ Tactical recommendations')

if __name__ == "__main__":
    main() 