import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import warnings
warnings.filterwarnings('ignore')

class MomentumPredictor:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=30, random_state=42)
        self.feature_names = ['total_events', 'pass_count', 'shot_count', 'carry_count', 
                             'dribble_count', 'possession_pct', 'attacking_actions', 
                             'events_per_minute', 'recent_intensity']
        self.is_trained = False
    
    def train_quick(self):
        # Quick training with synthetic data
        np.random.seed(42)
        X = np.random.rand(100, 9) * [50, 30, 5, 20, 10, 100, 25, 20, 40]
        y = (X[:, 6] * 1.5 + X[:, 5] * 0.05 + X[:, 2] * 2.0 + X[:, 8] * 0.3 + X[:, 7] * 0.5)
        y = np.clip(y, 0, 10)
        
        self.model.fit(X, y)
        self.is_trained = True
    
    def predict_with_interpretation(self, features):
        if not self.is_trained:
            return 5.0, 'Model not trained'
        
        X = [features.get(f, 0) for f in self.feature_names]
        momentum = self.model.predict([X])[0]
        momentum = max(0, min(10, momentum))
        
        if momentum >= 8.5:
            interpretation = 'VERY HIGH MOMENTUM - Complete dominance'
        elif momentum >= 7.0:
            interpretation = 'HIGH MOMENTUM - Strong control'
        elif momentum >= 5.5:
            interpretation = 'BUILDING MOMENTUM - Gaining advantage'
        elif momentum >= 4.0:
            interpretation = 'NEUTRAL MOMENTUM - Balanced play'
        elif momentum >= 2.5:
            interpretation = 'LOW MOMENTUM - Under pressure'
        else:
            interpretation = 'VERY LOW MOMENTUM - Struggling'
        
        return momentum, interpretation

def main():
    print('COMPREHENSIVE MOMENTUM PREDICTION EXAMPLES')
    print('=' * 80)

    # Initialize and train model
    momentum_model = MomentumPredictor()
    momentum_model.train_quick()

    print('\nDETAILED INPUT/OUTPUT EXAMPLES')
    print('=' * 80)

    # Example scenarios
    examples = [
        {
            'scenario': 'HIGH ATTACKING MOMENTUM',
            'features': {
                'total_events': 45, 'pass_count': 18, 'shot_count': 4, 'carry_count': 12,
                'dribble_count': 6, 'possession_pct': 75.0, 'attacking_actions': 22,
                'events_per_minute': 15.0, 'recent_intensity': 28
            },
            'context': {'time': '67:23', 'team': 'Manchester City', 'situation': 'Sustained pressure in opponent box'}
        },
        {
            'scenario': 'DEFENSIVE MOMENTUM',
            'features': {
                'total_events': 18, 'pass_count': 8, 'shot_count': 0, 'carry_count': 3,
                'dribble_count': 1, 'possession_pct': 35.0, 'attacking_actions': 4,
                'events_per_minute': 6.0, 'recent_intensity': 8
            },
            'context': {'time': '23:45', 'team': 'Liverpool', 'situation': 'Compact defensive shape'}
        },
        {
            'scenario': 'BALANCED MIDFIELD BATTLE',
            'features': {
                'total_events': 28, 'pass_count': 15, 'shot_count': 1, 'carry_count': 8,
                'dribble_count': 3, 'possession_pct': 52.0, 'attacking_actions': 12,
                'events_per_minute': 9.3, 'recent_intensity': 16
            },
            'context': {'time': '41:12', 'team': 'Barcelona', 'situation': 'Midfield possession battle'}
        },
        {
            'scenario': 'LATE GAME DESPERATION',
            'features': {
                'total_events': 52, 'pass_count': 22, 'shot_count': 6, 'carry_count': 15,
                'dribble_count': 8, 'possession_pct': 68.0, 'attacking_actions': 29,
                'events_per_minute': 17.3, 'recent_intensity': 34
            },
            'context': {'time': '87:56', 'team': 'Real Madrid', 'situation': 'Trailing 1-0, all-out attack'}
        },
        {
            'scenario': 'EARLY GAME CAUTION',
            'features': {
                'total_events': 12, 'pass_count': 7, 'shot_count': 0, 'carry_count': 2,
                'dribble_count': 1, 'possession_pct': 48.0, 'attacking_actions': 3,
                'events_per_minute': 4.0, 'recent_intensity': 6
            },
            'context': {'time': '08:15', 'team': 'Bayern Munich', 'situation': 'Cautious start'}
        },
        {
            'scenario': 'DOMINANT POSSESSION',
            'features': {
                'total_events': 38, 'pass_count': 28, 'shot_count': 2, 'carry_count': 6,
                'dribble_count': 2, 'possession_pct': 82.0, 'attacking_actions': 10,
                'events_per_minute': 12.7, 'recent_intensity': 20
            },
            'context': {'time': '34:28', 'team': 'Spain', 'situation': 'Tiki-taka possession dominance'}
        }
    ]

    # Process each example
    for i, example in enumerate(examples, 1):
        print(f'\nEXAMPLE {i}: {example["scenario"]}')
        print('=' * 60)
        
        # Context
        print(f'CONTEXT:')
        print(f'   Time: {example["context"]["time"]}')
        print(f'   Team: {example["context"]["team"]}')
        print(f'   Situation: {example["context"]["situation"]}')
        
        # Input features
        print(f'\nINPUT FEATURES:')
        features = example['features']
        for feature, value in features.items():
            if 'pct' in feature:
                print(f'   {feature:<20} : {value:>8.1f}%')
            else:
                print(f'   {feature:<20} : {value:>8.1f}')
        
        # Prediction
        momentum, interpretation = momentum_model.predict_with_interpretation(features)
        
        # Output
        print(f'\nOUTPUT:')
        print(f'   Momentum Score: {momentum:.2f}/10')
        print(f'   Interpretation: {interpretation}')
        
        # Feature contributions
        print(f'\nKEY CONTRIBUTIONS:')
        print(f'   Attacking Actions: +{features["attacking_actions"] * 1.5:.1f}')
        print(f'   Possession %: +{features["possession_pct"] * 0.05:.1f}')
        print(f'   Shot Count: +{features["shot_count"] * 2.0:.1f}')
        print(f'   Recent Intensity: +{features["recent_intensity"] * 0.3:.1f}')
        
        # Tactical insights
        print(f'\nTACTICAL INSIGHT:')
        if momentum >= 8:
            print(f'   Team has clear advantage - maintain pressure')
        elif momentum >= 6:
            print(f'   Building momentum - capitalize on opportunities')
        elif momentum >= 4:
            print(f'   Balanced phase - small margins matter')
        else:
            print(f'   Consider tactical changes to gain momentum')

    print('\n' + '=' * 80)
    print('HEAD-TO-HEAD MOMENTUM COMPARISON')
    print('=' * 80)

    # Comparison examples
    comparisons = [
        {
            'title': 'ATTACKING VS DEFENSIVE TEAMS',
            'team_a': {
                'name': 'Team A (Attacking)',
                'features': {
                    'total_events': 42, 'pass_count': 18, 'shot_count': 5, 'carry_count': 14,
                    'dribble_count': 7, 'possession_pct': 58.0, 'attacking_actions': 26,
                    'events_per_minute': 14.0, 'recent_intensity': 30
                }
            },
            'team_b': {
                'name': 'Team B (Defensive)',
                'features': {
                    'total_events': 30, 'pass_count': 12, 'shot_count': 1, 'carry_count': 6,
                    'dribble_count': 2, 'possession_pct': 42.0, 'attacking_actions': 9,
                    'events_per_minute': 10.0, 'recent_intensity': 12
                }
            }
        },
        {
            'title': 'POSSESSION VS COUNTER-ATTACK',
            'team_a': {
                'name': 'Team A (Possession)',
                'features': {
                    'total_events': 48, 'pass_count': 35, 'shot_count': 2, 'carry_count': 8,
                    'dribble_count': 3, 'possession_pct': 75.0, 'attacking_actions': 13,
                    'events_per_minute': 16.0, 'recent_intensity': 20
                }
            },
            'team_b': {
                'name': 'Team B (Counter)',
                'features': {
                    'total_events': 16, 'pass_count': 8, 'shot_count': 3, 'carry_count': 4,
                    'dribble_count': 1, 'possession_pct': 25.0, 'attacking_actions': 8,
                    'events_per_minute': 5.3, 'recent_intensity': 14
                }
            }
        }
    ]

    for i, comp in enumerate(comparisons, 1):
        print(f'\nCOMPARISON {i}: {comp["title"]}')
        print('-' * 60)
        
        momentum_a, interp_a = momentum_model.predict_with_interpretation(comp['team_a']['features'])
        momentum_b, interp_b = momentum_model.predict_with_interpretation(comp['team_b']['features'])
        
        print(f'\n{comp["team_a"]["name"]}:')
        print(f'   Momentum: {momentum_a:.2f}/10 - {interp_a}')
        features_a = comp['team_a']['features']
        print(f'   Key Stats: {features_a["possession_pct"]:.1f}% possession | {features_a["shot_count"]} shots | {features_a["attacking_actions"]} attacking actions')
        
        print(f'\n{comp["team_b"]["name"]}:')
        print(f'   Momentum: {momentum_b:.2f}/10 - {interp_b}')
        features_b = comp['team_b']['features']
        print(f'   Key Stats: {features_b["possession_pct"]:.1f}% possession | {features_b["shot_count"]} shots | {features_b["attacking_actions"]} attacking actions')
        
        print(f'\nMOMENTUM DIFFERENCE: {abs(momentum_a - momentum_b):.2f} points')
        if momentum_a > momentum_b:
            print(f'   {comp["team_a"]["name"].split("(")[0]} has momentum advantage (+{momentum_a - momentum_b:.2f})')
        else:
            print(f'   {comp["team_b"]["name"].split("(")[0]} has momentum advantage (+{momentum_b - momentum_a:.2f})')

    print('\n' + '=' * 80)
    print('EDGE CASE EXAMPLES')
    print('=' * 80)

    edge_cases = [
        {
            'case': 'VERY LOW ACTIVITY',
            'features': {
                'total_events': 3, 'pass_count': 2, 'shot_count': 0, 'carry_count': 1,
                'dribble_count': 0, 'possession_pct': 30.0, 'attacking_actions': 1,
                'events_per_minute': 1.0, 'recent_intensity': 2
            }
        },
        {
            'case': 'EXTREMELY HIGH ACTIVITY',
            'features': {
                'total_events': 75, 'pass_count': 40, 'shot_count': 8, 'carry_count': 20,
                'dribble_count': 12, 'possession_pct': 85.0, 'attacking_actions': 40,
                'events_per_minute': 25.0, 'recent_intensity': 50
            }
        },
        {
            'case': 'HIGH SHOTS LOW POSSESSION',
            'features': {
                'total_events': 15, 'pass_count': 5, 'shot_count': 7, 'carry_count': 3,
                'dribble_count': 0, 'possession_pct': 25.0, 'attacking_actions': 10,
                'events_per_minute': 5.0, 'recent_intensity': 14
            }
        }
    ]

    for i, case in enumerate(edge_cases, 1):
        print(f'\nEDGE CASE {i}: {case["case"]}')
        print('-' * 40)
        
        momentum, interpretation = momentum_model.predict_with_interpretation(case['features'])
        
        print(f'INPUT: {case["case"].lower().replace("_", " ")}')
        features = case['features']
        print(f'   Events: {features["total_events"]} | Possession: {features["possession_pct"]:.1f}% | Shots: {features["shot_count"]}')
        
        print(f'OUTPUT:')
        print(f'   Momentum: {momentum:.2f}/10 - {interpretation}')

    print('\nSUMMARY OF ALL EXAMPLES')
    print('=' * 40)
    print('Demonstrated 11 different momentum scenarios:')
    print('   - 6 detailed individual examples')
    print('   - 2 head-to-head comparisons')  
    print('   - 3 edge case examples')
    print('\nAll examples show complete input/output with:')
    print('   - Context and timing')
    print('   - Feature breakdown')
    print('   - Momentum score and interpretation')
    print('   - Feature contributions')
    print('   - Tactical insights')

if __name__ == "__main__":
    main() 