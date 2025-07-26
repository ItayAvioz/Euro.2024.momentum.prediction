#!/usr/bin/env python3
"""
Momentum Classification Analysis: Continuous vs Categorical Impact
Comparing regression vs classification approaches for momentum prediction
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import matplotlib.pyplot as plt
import seaborn as sns

class MomentumClassificationAnalysis:
    """Compare continuous vs categorical momentum prediction approaches"""
    
    def __init__(self):
        self.continuous_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.categorical_model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.data = None
        self.features = None
        self.continuous_target = None
        self.categorical_target = None
    
    def generate_training_data(self, n_samples=5000):
        """Generate realistic momentum training data"""
        print("🔄 GENERATING TRAINING DATA...")
        print("=" * 50)
        
        np.random.seed(42)
        
        # Generate realistic feature combinations
        data = []
        
        for _ in range(n_samples):
            # Generate correlated features that reflect realistic soccer scenarios
            
            # Base activity level (affects all other features)
            base_activity = np.random.uniform(0.1, 1.0)
            
            # Features with realistic ranges and correlations
            features = {
                'events_3min': int(np.random.normal(25, 8) * base_activity),
                'shots_3min': int(np.random.poisson(2.5 * base_activity)),
                'attacking_actions': int(np.random.normal(15, 5) * base_activity),
                'possession_pct': np.random.normal(50, 15) + (base_activity - 0.5) * 20,
                'events_per_minute': np.random.normal(8, 2) * base_activity,
                'recent_intensity': np.random.normal(12, 4) * base_activity,
                'passes_3min': int(np.random.normal(35, 10) * base_activity),
                'dribbles_3min': int(np.random.poisson(3 * base_activity)),
                'carries_3min': int(np.random.poisson(8 * base_activity)),
                'pressure_applied': int(np.random.poisson(4 * base_activity)),
            }
            
            # Ensure realistic ranges
            features['events_3min'] = max(1, min(80, features['events_3min']))
            features['shots_3min'] = max(0, min(10, features['shots_3min']))
            features['attacking_actions'] = max(0, min(40, features['attacking_actions']))
            features['possession_pct'] = max(15, min(85, features['possession_pct']))
            features['events_per_minute'] = max(1, min(25, features['events_per_minute']))
            features['recent_intensity'] = max(1, min(35, features['recent_intensity']))
            
            # Calculate continuous momentum target using the established formula
            momentum_score = (
                features['shots_3min'] * 2.0 +
                features['attacking_actions'] * 1.5 +
                features['possession_pct'] * 0.05 +
                features['recent_intensity'] * 0.3 +
                features['events_per_minute'] * 0.5
            )
            
            # Normalize to 0-10 scale with some noise
            momentum_score = max(0, min(10, momentum_score * 0.08 + np.random.normal(0, 0.3)))
            
            # Create categorical target
            if momentum_score >= 7.0:
                momentum_category = 'High'
            elif momentum_score >= 4.0:
                momentum_category = 'Medium'
            else:
                momentum_category = 'Low'
            
            # Add targets to features
            features['momentum_continuous'] = momentum_score
            features['momentum_categorical'] = momentum_category
            
            data.append(features)
        
        self.data = pd.DataFrame(data)
        
        # Separate features and targets
        feature_cols = [col for col in self.data.columns if not col.startswith('momentum_')]
        self.features = self.data[feature_cols]
        self.continuous_target = self.data['momentum_continuous']
        self.categorical_target = self.data['momentum_categorical']
        
        print(f"✅ Generated {len(self.data)} training samples")
        print(f"📊 Features: {len(feature_cols)}")
        print(f"📈 Continuous target range: {self.continuous_target.min():.2f} - {self.continuous_target.max():.2f}")
        print(f"📂 Categorical distribution:")
        print(self.categorical_target.value_counts())
        
        return self.data
    
    def train_both_models(self):
        """Train both continuous and categorical models"""
        print("\n🚀 TRAINING BOTH MODELS...")
        print("=" * 50)
        
        # Split data
        X_train, X_test, y_cont_train, y_cont_test, y_cat_train, y_cat_test = train_test_split(
            self.features, self.continuous_target, self.categorical_target, 
            test_size=0.2, random_state=42
        )
        
        # Train continuous model
        print("🔄 Training continuous (regression) model...")
        self.continuous_model.fit(X_train, y_cont_train)
        
        # Train categorical model
        print("🔄 Training categorical (classification) model...")
        self.categorical_model.fit(X_train, y_cat_train)
        
        # Store test data for evaluation
        self.X_test = X_test
        self.y_cont_test = y_cont_test
        self.y_cat_test = y_cat_test
        
        print("✅ Both models trained successfully")
        
        return X_train, X_test, y_cont_train, y_cont_test, y_cat_train, y_cat_test
    
    def evaluate_continuous_model(self):
        """Evaluate continuous momentum prediction model"""
        print("\n📊 CONTINUOUS MODEL EVALUATION")
        print("=" * 50)
        
        # Make predictions
        y_pred_cont = self.continuous_model.predict(self.X_test)
        
        # Calculate metrics
        r2 = r2_score(self.y_cont_test, y_pred_cont)
        mae = mean_absolute_error(self.y_cont_test, y_pred_cont)
        rmse = np.sqrt(mean_squared_error(self.y_cont_test, y_pred_cont))
        
        print(f"🎯 R² Score: {r2:.4f} ({r2*100:.1f}% variance explained)")
        print(f"📏 Mean Absolute Error: {mae:.3f} momentum points")
        print(f"📐 Root Mean Square Error: {rmse:.3f} momentum points")
        
        # Convert continuous predictions to categories for comparison
        y_pred_cont_as_cat = []
        for score in y_pred_cont:
            if score >= 7.0:
                y_pred_cont_as_cat.append('High')
            elif score >= 4.0:
                y_pred_cont_as_cat.append('Medium')
            else:
                y_pred_cont_as_cat.append('Low')
        
        # Calculate "categorical accuracy" from continuous predictions
        categorical_accuracy = accuracy_score(self.y_cat_test, y_pred_cont_as_cat)
        print(f"🎯 Categorical Accuracy (from continuous): {categorical_accuracy:.3f} ({categorical_accuracy*100:.1f}%)")
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': self.features.columns,
            'importance': self.continuous_model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print(f"\n🔍 TOP 5 FEATURES (Continuous Model):")
        for i, (_, row) in enumerate(feature_importance.head().iterrows()):
            print(f"   {i+1}. {row['feature']}: {row['importance']:.3f}")
        
        return {
            'r2': r2,
            'mae': mae,
            'rmse': rmse,
            'categorical_accuracy': categorical_accuracy,
            'feature_importance': feature_importance
        }
    
    def evaluate_categorical_model(self):
        """Evaluate categorical momentum prediction model"""
        print("\n📊 CATEGORICAL MODEL EVALUATION")
        print("=" * 50)
        
        # Make predictions
        y_pred_cat = self.categorical_model.predict(self.X_test)
        
        # Calculate metrics
        accuracy = accuracy_score(self.y_cat_test, y_pred_cat)
        
        print(f"🎯 Classification Accuracy: {accuracy:.3f} ({accuracy*100:.1f}%)")
        
        # Detailed classification report
        print(f"\n📋 DETAILED CLASSIFICATION REPORT:")
        report = classification_report(self.y_cat_test, y_pred_cat, output_dict=True)
        
        for category in ['Low', 'Medium', 'High']:
            if category in report:
                metrics = report[category]
                print(f"\n   {category.upper()} MOMENTUM:")
                print(f"      Precision: {metrics['precision']:.3f} ({metrics['precision']*100:.1f}%)")
                print(f"      Recall: {metrics['recall']:.3f} ({metrics['recall']*100:.1f}%)")
                print(f"      F1-Score: {metrics['f1-score']:.3f}")
        
        # Overall metrics
        print(f"\n   OVERALL METRICS:")
        print(f"      Macro Avg F1: {report['macro avg']['f1-score']:.3f}")
        print(f"      Weighted Avg F1: {report['weighted avg']['f1-score']:.3f}")
        
        # Confusion matrix
        cm = confusion_matrix(self.y_cat_test, y_pred_cat)
        print(f"\n📊 CONFUSION MATRIX:")
        print("     Predicted:")
        print("       Low  Med  High")
        categories = ['Low', 'Medium', 'High']
        for i, true_cat in enumerate(categories):
            if i < len(cm):
                row = cm[i]
                print(f"  {true_cat[:3]}: {row[0]:3d}  {row[1]:3d}  {row[2]:3d}")
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': self.features.columns,
            'importance': self.categorical_model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print(f"\n🔍 TOP 5 FEATURES (Categorical Model):")
        for i, (_, row) in enumerate(feature_importance.head().iterrows()):
            print(f"   {i+1}. {row['feature']}: {row['importance']:.3f}")
        
        return {
            'accuracy': accuracy,
            'classification_report': report,
            'confusion_matrix': cm,
            'feature_importance': feature_importance
        }
    
    def compare_approaches(self):
        """Compare continuous vs categorical approaches"""
        print("\n⚖️ CONTINUOUS vs CATEGORICAL COMPARISON")
        print("=" * 60)
        
        # Evaluate both models
        cont_results = self.evaluate_continuous_model()
        cat_results = self.evaluate_categorical_model()
        
        print(f"\n📊 PERFORMANCE COMPARISON:")
        print(f"┌─────────────────────────────┬──────────────┬──────────────┐")
        print(f"│ Metric                      │ Continuous   │ Categorical  │")
        print(f"├─────────────────────────────┼──────────────┼──────────────┤")
        print(f"│ Primary Metric              │ R² = {cont_results['r2']:.3f}   │ Acc = {cat_results['accuracy']:.3f}  │")
        print(f"│ Variance Explained          │ {cont_results['r2']*100:.1f}%        │ N/A          │")
        print(f"│ Categorical Accuracy        │ {cont_results['categorical_accuracy']:.3f}        │ {cat_results['accuracy']:.3f}        │")
        print(f"│ Mean Absolute Error         │ {cont_results['mae']:.3f}        │ N/A          │")
        print(f"│ Precision (Macro Avg)       │ N/A          │ {cat_results['classification_report']['macro avg']['precision']:.3f}        │")
        print(f"│ Recall (Macro Avg)          │ N/A          │ {cat_results['classification_report']['macro avg']['recall']:.3f}        │")
        print(f"│ F1-Score (Macro Avg)        │ N/A          │ {cat_results['classification_report']['macro avg']['f1-score']:.3f}        │")
        print(f"└─────────────────────────────┴──────────────┴──────────────┘")
        
        print(f"\n💡 KEY INSIGHTS:")
        
        # Compare categorical accuracy
        cont_cat_acc = cont_results['categorical_accuracy']
        cat_acc = cat_results['accuracy']
        
        if cont_cat_acc > cat_acc:
            diff = cont_cat_acc - cat_acc
            print(f"   ✅ Continuous model achieves BETTER categorical accuracy (+{diff:.3f})")
            print(f"      This suggests continuous prediction contains more information")
        elif cat_acc > cont_cat_acc:
            diff = cat_acc - cont_cat_acc
            print(f"   ✅ Categorical model achieves BETTER accuracy (+{diff:.3f})")
            print(f"      This suggests direct classification is more effective")
        else:
            print(f"   ⚖️ Both approaches achieve similar categorical accuracy")
        
        # Information loss analysis
        print(f"\n🔍 INFORMATION ANALYSIS:")
        print(f"   📊 Continuous model provides:")
        print(f"      • Exact momentum scores (0-10 scale)")
        print(f"      • Confidence intervals and uncertainty")
        print(f"      • Gradual momentum changes")
        print(f"      • Fine-grained comparisons")
        
        print(f"\n   📂 Categorical model provides:")
        print(f"      • Simple interpretable labels")
        print(f"      • Clear decision boundaries")
        print(f"      • Robust to small variations")
        print(f"      • Easier for non-technical users")
        
        # Practical implications
        print(f"\n⚽ PRACTICAL IMPLICATIONS:")
        
        print(f"\n   🎯 USE CONTINUOUS when:")
        print(f"      • Need precise momentum tracking")
        print(f"      • Comparing similar momentum levels")
        print(f"      • Building advanced analytics")
        print(f"      • Integrating with other numerical models")
        
        print(f"\n   🎯 USE CATEGORICAL when:")
        print(f"      • Simplifying for broadcasts")
        print(f"      • Quick tactical decisions")
        print(f"      • Fan-facing applications")
        print(f"      • Alert systems (high/low momentum)")
        
        return cont_results, cat_results
    
    def demonstrate_real_examples(self):
        """Show real examples of both prediction types"""
        print("\n🎮 REAL PREDICTION EXAMPLES")
        print("=" * 60)
        
        # Generate a few example scenarios
        examples = [
            {
                'name': 'High Attacking Phase',
                'features': {
                    'events_3min': 45, 'shots_3min': 4, 'attacking_actions': 20,
                    'possession_pct': 65, 'events_per_minute': 15, 'recent_intensity': 22,
                    'passes_3min': 25, 'dribbles_3min': 5, 'carries_3min': 8, 'pressure_applied': 6
                }
            },
            {
                'name': 'Balanced Midfield Battle',
                'features': {
                    'events_3min': 28, 'shots_3min': 1, 'attacking_actions': 8,
                    'possession_pct': 48, 'events_per_minute': 9, 'recent_intensity': 12,
                    'passes_3min': 20, 'dribbles_3min': 2, 'carries_3min': 4, 'pressure_applied': 3
                }
            },
            {
                'name': 'Under Pressure Defense',
                'features': {
                    'events_3min': 15, 'shots_3min': 0, 'attacking_actions': 3,
                    'possession_pct': 28, 'events_per_minute': 5, 'recent_intensity': 6,
                    'passes_3min': 8, 'dribbles_3min': 1, 'carries_3min': 2, 'pressure_applied': 1
                }
            }
        ]
        
        for i, example in enumerate(examples, 1):
            print(f"\n📊 EXAMPLE {i}: {example['name']}")
            print(f"   {'─' * 50}")
            
            # Create feature vector
            feature_vector = pd.DataFrame([example['features']])
            
            # Get both predictions
            cont_pred = self.continuous_model.predict(feature_vector)[0]
            cat_pred = self.categorical_model.predict(feature_vector)[0]
            
            # Convert continuous to category for comparison
            if cont_pred >= 7.0:
                cont_as_cat = 'High'
            elif cont_pred >= 4.0:
                cont_as_cat = 'Medium'
            else:
                cont_as_cat = 'Low'
            
            print(f"   📥 INPUT FEATURES:")
            print(f"      • {example['features']['shots_3min']} shots, {example['features']['attacking_actions']} attacks")
            print(f"      • {example['features']['possession_pct']:.0f}% possession, {example['features']['events_per_minute']} events/min")
            print(f"      • {example['features']['recent_intensity']} recent intensity")
            
            print(f"\n   📤 PREDICTIONS:")
            print(f"      🎯 Continuous: {cont_pred:.2f}/10 → {cont_as_cat}")
            print(f"      📂 Categorical: {cat_pred}")
            
            # Agreement check
            if cont_as_cat == cat_pred:
                print(f"      ✅ AGREEMENT: Both predict {cat_pred} momentum")
            else:
                print(f"      ❌ DISAGREEMENT: Continuous→{cont_as_cat}, Categorical→{cat_pred}")
            
            # Interpretation
            if cont_pred >= 7.0:
                interpretation = "🔥 High momentum - team threatening"
            elif cont_pred >= 4.0:
                interpretation = "⚖️ Medium momentum - competitive phase"
            else:
                interpretation = "📉 Low momentum - defensive phase"
            
            print(f"      💬 INTERPRETATION: {interpretation}")

def main():
    """Run the complete analysis"""
    print("⚽ MOMENTUM PREDICTION: CONTINUOUS vs CATEGORICAL ANALYSIS")
    print("=" * 80)
    
    # Initialize analyzer
    analyzer = MomentumClassificationAnalysis()
    
    # Generate training data
    analyzer.generate_training_data(n_samples=5000)
    
    # Train both models
    analyzer.train_both_models()
    
    # Compare approaches
    analyzer.compare_approaches()
    
    # Show real examples
    analyzer.demonstrate_real_examples()
    
    print(f"\n✅ ANALYSIS COMPLETE!")
    print(f"🎯 KEY TAKEAWAY: Both approaches have merit - choice depends on use case")

if __name__ == "__main__":
    main() 