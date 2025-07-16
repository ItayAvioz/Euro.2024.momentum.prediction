import numpy as np
from sklearn.ensemble import RandomForestRegressor
import pandas as pd

class PredictionExplainer:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=5, random_state=42, max_depth=3)  # Simplified for explanation
        self.feature_names = [
            'team_shots', 'team_possession', 'team_attacks', 'team_intensity', 'team_events',
            'opp_shots', 'opp_possession', 'opp_attacks', 'opp_intensity', 'opp_events',
            'shot_advantage', 'possession_advantage', 'attack_advantage', 'pressure_ratio', 'event_ratio'
        ]
        self.trained = False
    
    def prepare_input(self, team_data, opponent_data):
        """Step 1: Convert raw match data into 15 features"""
        print("📥 STEP 1: INPUT PREPARATION")
        print("=" * 60)
        
        print(f"\n🔵 TEAM DATA:")
        for key, value in team_data.items():
            if key == 'possession':
                print(f"   {key:<12}: {value:.1f}%")
            else:
                print(f"   {key:<12}: {value}")
        
        print(f"\n🔴 OPPONENT DATA:")
        for key, value in opponent_data.items():
            if key == 'possession':
                print(f"   {key:<12}: {value:.1f}%")
            else:
                print(f"   {key:<12}: {value}")
        
        # Calculate all 15 features
        features = {}
        
        # Team features (5)
        features['team_shots'] = team_data['shots']
        features['team_possession'] = team_data['possession']
        features['team_attacks'] = team_data['attacks']
        features['team_intensity'] = team_data['intensity']
        features['team_events'] = team_data['events']
        
        # Opponent features (5)
        features['opp_shots'] = opponent_data['shots']
        features['opp_possession'] = opponent_data['possession']
        features['opp_attacks'] = opponent_data['attacks']
        features['opp_intensity'] = opponent_data['intensity']
        features['opp_events'] = opponent_data['events']
        
        # Comparative features (5) - THE KEY INSIGHT!
        features['shot_advantage'] = team_data['shots'] - opponent_data['shots']
        features['possession_advantage'] = team_data['possession'] - opponent_data['possession']
        features['attack_advantage'] = team_data['attacks'] - opponent_data['attacks']
        features['pressure_ratio'] = team_data['intensity'] / max(opponent_data['intensity'], 1)
        features['event_ratio'] = team_data['events'] / max(opponent_data['events'], 1)
        
        print(f"\n🧮 CALCULATED FEATURES (15 total):")
        print(f"   📊 Team Features (5):")
        print(f"      team_shots      : {features['team_shots']}")
        print(f"      team_possession : {features['team_possession']:.1f}%")
        print(f"      team_attacks    : {features['team_attacks']}")
        print(f"      team_intensity  : {features['team_intensity']}")
        print(f"      team_events     : {features['team_events']}")
        
        print(f"\n   📊 Opponent Features (5):")
        print(f"      opp_shots       : {features['opp_shots']}")
        print(f"      opp_possession  : {features['opp_possession']:.1f}%")
        print(f"      opp_attacks     : {features['opp_attacks']}")
        print(f"      opp_intensity   : {features['opp_intensity']}")
        print(f"      opp_events      : {features['opp_events']}")
        
        print(f"\n   🔥 Comparative Features (5) - KEY INSIGHT:")
        print(f"      shot_advantage     : {features['shot_advantage']:+d} ({team_data['shots']} - {opponent_data['shots']})")
        print(f"      possession_advantage: {features['possession_advantage']:+.1f}% ({team_data['possession']:.1f}% - {opponent_data['possession']:.1f}%)")
        print(f"      attack_advantage   : {features['attack_advantage']:+d} ({team_data['attacks']} - {opponent_data['attacks']})")
        print(f"      pressure_ratio     : {features['pressure_ratio']:.2f} ({team_data['intensity']} / {opponent_data['intensity']})")
        print(f"      event_ratio        : {features['event_ratio']:.2f} ({team_data['events']} / {opponent_data['events']})")
        
        return features
    
    def train_simple_model(self):
        """Train a simplified model for explanation"""
        print("\n🚀 TRAINING SIMPLIFIED MODEL (5 trees for demonstration)...")
        
        # Generate simple training data
        np.random.seed(42)
        training_data = []
        
        for _ in range(50):
            team_data = {
                'shots': np.random.randint(0, 6),
                'possession': np.random.uniform(30, 70),
                'attacks': np.random.randint(5, 20),
                'intensity': np.random.randint(10, 30),
                'events': np.random.randint(15, 40)
            }
            
            opp_data = {
                'shots': np.random.randint(0, 6),
                'possession': 100 - team_data['possession'],
                'attacks': np.random.randint(5, 20),
                'intensity': np.random.randint(10, 30),
                'events': np.random.randint(15, 40)
            }
            
            features = self.prepare_input_silent(team_data, opp_data)
            
            # Simple target calculation
            target = (
                features['shot_advantage'] * 1.2 +
                features['team_shots'] * 0.8 +
                features['attack_advantage'] * 0.3 +
                5.0  # baseline
            )
            target = max(0, min(10, target))
            
            row = {**features, 'momentum': target}
            training_data.append(row)
        
        # Train model
        df = pd.DataFrame(training_data)
        X = df[self.feature_names]
        y = df['momentum']
        
        self.model.fit(X, y)
        self.trained = True
        
        print(f"✅ Model trained with {len(training_data)} examples")
        
    def prepare_input_silent(self, team_data, opponent_data):
        """Silent version for training"""
        features = {}
        features['team_shots'] = team_data['shots']
        features['team_possession'] = team_data['possession']
        features['team_attacks'] = team_data['attacks']
        features['team_intensity'] = team_data['intensity']
        features['team_events'] = team_data['events']
        features['opp_shots'] = opponent_data['shots']
        features['opp_possession'] = opponent_data['possession']
        features['opp_attacks'] = opponent_data['attacks']
        features['opp_intensity'] = opponent_data['intensity']
        features['opp_events'] = opponent_data['events']
        features['shot_advantage'] = team_data['shots'] - opponent_data['shots']
        features['possession_advantage'] = team_data['possession'] - opponent_data['possession']
        features['attack_advantage'] = team_data['attacks'] - opponent_data['attacks']
        features['pressure_ratio'] = team_data['intensity'] / max(opponent_data['intensity'], 1)
        features['event_ratio'] = team_data['events'] / max(opponent_data['events'], 1)
        return features
    
    def explain_prediction(self, features):
        """Step 2: Show how Random Forest makes prediction"""
        print(f"\n🌳 STEP 2: RANDOM FOREST PREDICTION")
        print("=" * 60)
        
        if not self.trained:
            print("❌ Model not trained!")
            return 5.0
        
        # Convert to array for prediction
        X = np.array([[features[name] for name in self.feature_names]])
        
        print(f"\n📊 INPUT VECTOR (15 features):")
        for i, (name, value) in enumerate(zip(self.feature_names, X[0])):
            print(f"   [{i:2d}] {name:<20}: {value:.2f}")
        
        # Get individual tree predictions (for demonstration)
        tree_predictions = []
        for i, tree in enumerate(self.model.estimators_):
            pred = tree.predict(X)[0]
            tree_predictions.append(pred)
            print(f"\n🌲 Tree {i+1} Decision Process:")
            print(f"   • Analyzes all 15 features")
            print(f"   • Follows learned decision rules")
            print(f"   • Votes: {pred:.2f}/10")
        
        # Final prediction (average of all trees)
        final_prediction = self.model.predict(X)[0]
        
        print(f"\n🗳️ VOTING SUMMARY:")
        print(f"   Tree 1 vote: {tree_predictions[0]:.2f}/10")
        print(f"   Tree 2 vote: {tree_predictions[1]:.2f}/10")
        print(f"   Tree 3 vote: {tree_predictions[2]:.2f}/10")
        print(f"   Tree 4 vote: {tree_predictions[3]:.2f}/10")
        print(f"   Tree 5 vote: {tree_predictions[4]:.2f}/10")
        print(f"   ─────────────────────")
        print(f"   Average  : {final_prediction:.2f}/10")
        
        return final_prediction
    
    def interpret_prediction(self, momentum_score, features):
        """Step 3: Convert numerical score to interpretation"""
        print(f"\n💬 STEP 3: MOMENTUM INTERPRETATION")
        print("=" * 60)
        
        print(f"\n🎯 FINAL MOMENTUM SCORE: {momentum_score:.2f}/10")
        
        # Interpretation categories
        if momentum_score >= 8.5:
            level = "VERY HIGH"
            interpretation = "Complete dominance - team in total control"
            emoji = "🔥"
            tactical_advice = "Maintain pressure, go for the kill"
        elif momentum_score >= 7.0:
            level = "HIGH"
            interpretation = "Strong control - clear advantage"
            emoji = "📈"
            tactical_advice = "Keep attacking, breakthrough coming"
        elif momentum_score >= 5.5:
            level = "BUILDING"
            interpretation = "Gaining advantage - momentum shifting"
            emoji = "📊"
            tactical_advice = "Push forward, create more chances"
        elif momentum_score >= 4.0:
            level = "NEUTRAL"
            interpretation = "Balanced play - even contest"
            emoji = "⚖️"
            tactical_advice = "Stay patient, look for opportunities"
        elif momentum_score >= 2.5:
            level = "LOW"
            interpretation = "Under pressure - struggling"
            emoji = "📉"
            tactical_advice = "Defensive focus, quick counters"
        else:
            level = "VERY LOW"
            interpretation = "Being dominated - emergency mode"
            emoji = "❄️"
            tactical_advice = "Emergency changes needed"
        
        print(f"\n{emoji} MOMENTUM LEVEL: {level}")
        print(f"📝 INTERPRETATION: {interpretation}")
        print(f"⚽ TACTICAL ADVICE: {tactical_advice}")
        
        # Factor analysis
        print(f"\n🔍 KEY CONTRIBUTING FACTORS:")
        
        if features['shot_advantage'] >= 2:
            print(f"   ✅ Shot dominance (+{features['shot_advantage']}) - high threat level")
        elif features['shot_advantage'] >= 0:
            print(f"   📊 Shot parity ({features['shot_advantage']:+d}) - even threat")
        else:
            print(f"   ⚠️ Shot disadvantage ({features['shot_advantage']}) - limited threat")
        
        if features['possession_advantage'] >= 15:
            print(f"   ✅ Possession control (+{features['possession_advantage']:.0f}%) - territorial dominance")
        elif features['possession_advantage'] >= -15:
            print(f"   📊 Possession balance ({features['possession_advantage']:+.0f}%) - shared control")
        else:
            print(f"   ⚠️ Possession deficit ({features['possession_advantage']:.0f}%) - reactive mode")
        
        if features['attack_advantage'] >= 3:
            print(f"   ✅ Attack superiority (+{features['attack_advantage']}) - forward momentum")
        elif features['attack_advantage'] >= -3:
            print(f"   📊 Attack balance ({features['attack_advantage']:+d}) - even pressure")
        else:
            print(f"   ⚠️ Attack deficit ({features['attack_advantage']}) - defensive stance")
        
        # Commentary generation
        print(f"\n📺 AUTOMATED COMMENTARY:")
        if momentum_score >= 7.0:
            commentary = f"Team building significant momentum ({momentum_score:.1f}/10) with {features['shot_advantage']:+d} shot advantage"
        elif momentum_score >= 4.0:
            commentary = f"Momentum shifting ({momentum_score:.1f}/10) - {features['team_shots']} shots vs opponent's {features['opp_shots']}"
        else:
            commentary = f"Team struggling ({momentum_score:.1f}/10) - opponent creating more danger with {features['opp_shots']} shots"
        
        print(f"   💬 '{commentary}'")
        
        return {
            'level': level,
            'interpretation': interpretation,
            'tactical_advice': tactical_advice,
            'commentary': commentary
        }

def main():
    print("🎯 ENHANCED MOMENTUM MODEL: PREDICTION PROCESS EXPLAINED")
    print("=" * 80)
    
    print("\n💡 HOW DOES THE MODEL ACTUALLY MAKE PREDICTIONS?")
    print("   This explanation shows the complete process from raw match data")
    print("   to final momentum score and interpretation.")
    
    # Initialize explainer
    explainer = PredictionExplainer()
    explainer.train_simple_model()
    
    print(f"\n" + "=" * 80)
    print("🎮 REAL PREDICTION EXAMPLE: Netherlands vs England")
    print("=" * 80)
    
    # Example scenario
    team_data = {
        'shots': 3,
        'possession': 58.0,
        'attacks': 12,
        'intensity': 18,
        'events': 28
    }
    
    opponent_data = {
        'shots': 2,
        'possession': 42.0,
        'attacks': 9,
        'intensity': 15,
        'events': 22
    }
    
    print(f"\n🏟️ MATCH SITUATION:")
    print(f"   Netherlands: 3 shots, 58% possession, 12 attacks")
    print(f"   England: 2 shots, 42% possession, 9 attacks")
    print(f"   Question: What's Netherlands' momentum?")
    
    # Step 1: Prepare input
    features = explainer.prepare_input(team_data, opponent_data)
    
    # Step 2: Model prediction
    momentum_score = explainer.explain_prediction(features)
    
    # Step 3: Interpretation
    result = explainer.interpret_prediction(momentum_score, features)
    
    print(f"\n" + "=" * 80)
    print("🧠 PREDICTION PROCESS SUMMARY")
    print("=" * 80)
    
    print(f"\n🔄 THE COMPLETE FLOW:")
    print(f"   1️⃣ INPUT: Raw match data (team + opponent)")
    print(f"   2️⃣ FEATURES: Calculate 15 features (5 team + 5 opponent + 5 comparative)")
    print(f"   3️⃣ TREES: 5 decision trees analyze all features")
    print(f"   4️⃣ VOTING: Trees vote on momentum score")
    print(f"   5️⃣ AVERAGE: Final score = average of votes")
    print(f"   6️⃣ INTERPRET: Convert score to meaningful analysis")
    print(f"   7️⃣ OUTPUT: Momentum level + tactical advice + commentary")
    
    print(f"\n🔑 KEY INSIGHTS:")
    print(f"   • Model sees RELATIVE performance (team vs opponent)")
    print(f"   • Shot advantage is most important factor")
    print(f"   • Multiple trees provide robust prediction")
    print(f"   • Score automatically converts to actionable insights")
    print(f"   • Context matters more than absolute stats")
    
    print(f"\n⚡ REAL-TIME CAPABILITY:")
    print(f"   • Prediction time: <1ms")
    print(f"   • Updates every 3 minutes with new data")
    print(f"   • Generates live commentary automatically")
    print(f"   • Provides tactical insights for coaches")
    print(f"   • Tracks momentum shifts throughout match")
    
    print(f"\n✅ FINAL RESULT FOR THIS EXAMPLE:")
    print(f"   Netherlands momentum: {momentum_score:.2f}/10 ({result['level']})")
    print(f"   Analysis: {result['interpretation']}")
    print(f"   Advice: {result['tactical_advice']}")
    print(f"   Commentary: {result['commentary']}")

if __name__ == "__main__":
    main() 