import numpy as np
from sklearn.ensemble import RandomForestRegressor
import pandas as pd

class MomentumModelDemo:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=30, random_state=42)
        self.feature_names = ['total_events', 'shot_count', 'possession_pct', 'attacking_actions', 'recent_intensity']
        self.trained = False
    
    def target_formula(self, features):
        """Original formula used to CREATE training targets"""
        return (
            features['shot_count'] * 2.0 +
            features['attacking_actions'] * 1.5 +
            features['possession_pct'] * 0.05 +
            features['recent_intensity'] * 0.3 +
            (features['total_events'] / 3) * 0.5  # events per minute
        )
    
    def train_model(self):
        """Train the Random Forest model with realistic data"""
        print("🚀 Training Random Forest Model...")
        
        # Create training data using the formula + noise
        np.random.seed(42)
        training_data = []
        
        # Generate 100 realistic scenarios
        for _ in range(100):
            # Random features
            features = {
                'total_events': np.random.randint(5, 60),
                'shot_count': np.random.randint(0, 8),
                'possession_pct': np.random.uniform(20, 85),
                'attacking_actions': np.random.randint(1, 35),
                'recent_intensity': np.random.randint(2, 45)
            }
            
            # Calculate target using formula
            target = self.target_formula(features)
            
            # Add realistic noise
            target = max(0, min(10, target + np.random.normal(0, 0.5)))
            
            # Add to training data
            training_data.append({
                **features,
                'momentum': target
            })
        
        # Train model
        df = pd.DataFrame(training_data)
        X = df[self.feature_names]
        y = df['momentum']
        
        self.model.fit(X, y)
        self.trained = True
        
        from sklearn.metrics import r2_score
        y_pred = self.model.predict(X)
        r2 = r2_score(y, y_pred)
        print(f"✅ Model trained with R² = {r2:.3f}")
        print(f"📊 Training data: {len(df)} scenarios")
        
    def predict(self, features):
        """Model prediction (what the model actually does)"""
        if not self.trained:
            return 5.0
        
        X = np.array([[
            features['total_events'],
            features['shot_count'], 
            features['possession_pct'],
            features['attacking_actions'],
            features['recent_intensity']
        ]])
        
        return self.model.predict(X)[0]

def main():
    print("🎯 MODEL PREDICTIONS vs FORMULA: WHAT THE MODEL ACTUALLY DOES")
    print("=" * 80)
    
    print("\n💡 KEY UNDERSTANDING:")
    print("   • FORMULA: Used to create training targets (teaching data)")
    print("   • MODEL: Learns patterns from training data (Random Forest)")
    print("   • PREDICTION: Model makes decisions, NOT formula")
    
    # Initialize and train model
    demo = MomentumModelDemo()
    demo.train_model()
    
    print("\n📊 REAL EXAMPLES: INPUT → MODEL PREDICTION")
    print("=" * 80)
    
    # Real Euro 2024 inspired examples
    examples = [
        {
            'scenario': 'Netherlands vs England - Early Pressure',
            'context': 'Netherlands 15:23 - Building attack',
            'features': {
                'total_events': 22,
                'shot_count': 1,
                'possession_pct': 58.0,
                'attacking_actions': 8,
                'recent_intensity': 12
            }
        },
        {
            'scenario': 'Spain vs Germany - Dominant Phase',
            'context': 'Spain 67:45 - Sustained pressure',
            'features': {
                'total_events': 41,
                'shot_count': 4,
                'possession_pct': 73.0,
                'attacking_actions': 19,
                'recent_intensity': 26
            }
        },
        {
            'scenario': 'England vs Switzerland - Defensive Shape',
            'context': 'England 89:12 - Protecting lead',
            'features': {
                'total_events': 9,
                'shot_count': 0,
                'possession_pct': 31.0,
                'attacking_actions': 2,
                'recent_intensity': 5
            }
        },
        {
            'scenario': 'France vs Portugal - Counter Attack',
            'context': 'France 54:38 - Quick transition',
            'features': {
                'total_events': 16,
                'shot_count': 2,
                'possession_pct': 42.0,
                'attacking_actions': 6,
                'recent_intensity': 14
            }
        },
        {
            'scenario': 'Italy vs Croatia - Late Desperation',
            'context': 'Italy 87:56 - Must score',
            'features': {
                'total_events': 48,
                'shot_count': 6,
                'possession_pct': 69.0,
                'attacking_actions': 24,
                'recent_intensity': 32
            }
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n🎮 EXAMPLE {i}: {example['scenario']}")
        print("-" * 60)
        print(f"📋 Context: {example['context']}")
        
        features = example['features']
        
        # Show input
        print(f"\n📥 INPUT FEATURES:")
        for key, value in features.items():
            if 'pct' in key:
                print(f"   {key:<18}: {value}%")
            else:
                print(f"   {key:<18}: {value}")
        
        # Calculate what formula would give
        formula_result = demo.target_formula(features)
        
        # Get actual model prediction
        model_prediction = demo.predict(features)
        
        print(f"\n🧮 FORMULA CALCULATION:")
        print(f"   shots×2.0: {features['shot_count']} × 2.0 = {features['shot_count'] * 2.0:.1f}")
        print(f"   attacking×1.5: {features['attacking_actions']} × 1.5 = {features['attacking_actions'] * 1.5:.1f}")
        print(f"   possession×0.05: {features['possession_pct']} × 0.05 = {features['possession_pct'] * 0.05:.1f}")
        print(f"   intensity×0.3: {features['recent_intensity']} × 0.3 = {features['recent_intensity'] * 0.3:.1f}")
        print(f"   events/min×0.5: {features['total_events']/3:.1f} × 0.5 = {(features['total_events']/3) * 0.5:.1f}")
        print(f"   ───────────────────")
        print(f"   FORMULA TOTAL: {formula_result:.2f}")
        
        print(f"\n🤖 ACTUAL MODEL PREDICTION:")
        print(f"   Random Forest Result: {model_prediction:.2f}/10")
        
        # Interpretation
        if model_prediction >= 8.5:
            interpretation = "VERY HIGH MOMENTUM - Complete dominance"
        elif model_prediction >= 7.0:
            interpretation = "HIGH MOMENTUM - Strong control"
        elif model_prediction >= 5.5:
            interpretation = "BUILDING MOMENTUM - Gaining advantage"
        elif model_prediction >= 4.0:
            interpretation = "NEUTRAL MOMENTUM - Balanced play"
        elif model_prediction >= 2.5:
            interpretation = "LOW MOMENTUM - Under pressure"
        else:
            interpretation = "VERY LOW MOMENTUM - Struggling"
        
        print(f"   Interpretation: {interpretation}")
        
        # Show difference
        difference = abs(model_prediction - formula_result)
        print(f"\n📈 COMPARISON:")
        print(f"   Formula: {formula_result:.2f}")
        print(f"   Model:   {model_prediction:.2f}")
        print(f"   Difference: {difference:.2f}")
        
        if difference > 1.0:
            print(f"   💡 Model learned to adjust from training patterns")
        else:
            print(f"   💡 Model prediction close to formula baseline")
    
    print(f"\n" + "=" * 80)
    print("🧠 WHAT THE MODEL ACTUALLY DOES")
    print("=" * 80)
    
    print("\n🎯 TRAINING PHASE:")
    print("   1. Formula creates target values for 100+ scenarios")
    print("   2. Random Forest learns patterns from this training data")
    print("   3. Model captures complex relationships between features")
    print("   4. Model can make predictions DIFFERENT from formula")
    
    print("\n🤖 PREDICTION PHASE:")
    print("   1. Input: 5 feature values")
    print("   2. Random Forest uses 30 decision trees")
    print("   3. Each tree 'votes' on momentum score")
    print("   4. Final prediction = average of all tree votes")
    print("   5. Result: Momentum score 0-10 + interpretation")
    
    print("\n💡 KEY DIFFERENCES:")
    print("   📐 FORMULA: Fixed mathematical calculation")
    print("      → Always same result for same input")
    print("      → Used only for creating training targets")
    
    print("\n   🌳 MODEL: Learned decision-making")
    print("      → Can adapt based on training patterns")
    print("      → Captures complex feature interactions")
    print("      → May predict differently than formula")
    
    print("\n🎮 WHY USE MACHINE LEARNING?")
    print("   ✅ Handles complex feature interactions")
    print("   ✅ Learns from realistic soccer scenarios")
    print("   ✅ Can capture non-linear relationships")
    print("   ✅ Robust to different input patterns")
    print("   ✅ Generalizes to new situations")
    
    print("\n📊 FEATURE IMPORTANCE (What model learned):")
    if demo.trained:
        feature_importance = demo.model.feature_importances_
        features_with_importance = list(zip(demo.feature_names, feature_importance))
        features_with_importance.sort(key=lambda x: x[1], reverse=True)
        
        for feature, importance in features_with_importance:
            print(f"   {feature:<18}: {importance*100:.1f}%")
    
    print(f"\n✅ SUMMARY:")
    print(f"   • Formula: Created training targets")
    print(f"   • Model: Learned patterns from targets")
    print(f"   • Predictions: Model decides, not formula")
    print(f"   • Result: Intelligent momentum assessment")

if __name__ == "__main__":
    main() 