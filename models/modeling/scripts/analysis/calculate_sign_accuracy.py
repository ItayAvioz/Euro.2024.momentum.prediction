"""
Calculate Sign Accuracy for ARIMAX Model
Compares if predicted sign (positive/negative) matches actual sign (positive/negative)
"""

import pandas as pd
import numpy as np

# Load the ARIMAX predictions
df = pd.read_csv('../outputs/predictions/arimax_predictions.csv')

# Filter for ARIMAX momentum-to-change model only
arimax_data = df[df['model_type'] == 'momentum_to_change_arimax'].copy()

print("🔍 SIGN ACCURACY ANALYSIS - ARIMAX MOMENTUM→CHANGE MODEL")
print("=" * 70)
print(f"Total ARIMAX predictions: {len(arimax_data):,}")

# Calculate sign accuracy
def calculate_sign_accuracy(predictions, actuals):
    """
    Calculate sign accuracy: 1 if same sign, 0 if different sign
    """
    pred_signs = np.sign(predictions)  # +1 for positive, -1 for negative, 0 for zero
    actual_signs = np.sign(actuals)    # +1 for positive, -1 for negative, 0 for zero
    
    # Same sign = 1, different sign = 0
    correct_signs = (pred_signs == actual_signs).astype(int)
    
    return correct_signs, pred_signs, actual_signs

# Extract prediction and actual values
predictions = arimax_data['prediction_value'].values
actuals = arimax_data['actual_value'].values

# Calculate sign accuracy
correct_signs, pred_signs, actual_signs = calculate_sign_accuracy(predictions, actuals)

# Overall statistics
total_predictions = len(predictions)
correct_count = correct_signs.sum()
sign_accuracy = correct_count / total_predictions

print(f"\n📊 OVERALL SIGN ACCURACY:")
print(f"Correct signs: {correct_count:,} out of {total_predictions:,}")
print(f"Sign Accuracy: {sign_accuracy:.4f} ({sign_accuracy*100:.2f}%)")

# Detailed breakdown
print(f"\n🔍 DETAILED BREAKDOWN:")

# Count by sign combinations
positive_pred_positive_actual = ((pred_signs > 0) & (actual_signs > 0)).sum()
negative_pred_negative_actual = ((pred_signs < 0) & (actual_signs < 0)).sum()
positive_pred_negative_actual = ((pred_signs > 0) & (actual_signs < 0)).sum()
negative_pred_positive_actual = ((pred_signs < 0) & (actual_signs > 0)).sum()
zero_cases = ((pred_signs == 0) | (actual_signs == 0)).sum()

print(f"✅ Positive pred, Positive actual: {positive_pred_positive_actual:,}")
print(f"✅ Negative pred, Negative actual: {negative_pred_negative_actual:,}")
print(f"❌ Positive pred, Negative actual: {positive_pred_negative_actual:,}")
print(f"❌ Negative pred, Positive actual: {negative_pred_positive_actual:,}")
print(f"⚪ Zero cases (pred=0 or actual=0): {zero_cases:,}")

# Accuracy by sign type
total_positive_actual = (actual_signs > 0).sum()
total_negative_actual = (actual_signs < 0).sum()

if total_positive_actual > 0:
    positive_accuracy = positive_pred_positive_actual / total_positive_actual
    print(f"\n📈 When actual is POSITIVE: {positive_accuracy:.4f} ({positive_accuracy*100:.2f}%) accuracy")

if total_negative_actual > 0:
    negative_accuracy = negative_pred_negative_actual / total_negative_actual
    print(f"📉 When actual is NEGATIVE: {negative_accuracy:.4f} ({negative_accuracy*100:.2f}%) accuracy")

# Sample examples
print(f"\n📋 SAMPLE EXAMPLES:")
print("Prediction | Actual | Pred Sign | Actual Sign | Correct?")
print("-" * 55)

sample_indices = np.random.choice(len(predictions), min(15, len(predictions)), replace=False)
for i in sample_indices:
    pred_val = predictions[i]
    actual_val = actuals[i]
    pred_sign = "+" if pred_signs[i] > 0 else "-" if pred_signs[i] < 0 else "0"
    actual_sign = "+" if actual_signs[i] > 0 else "-" if actual_signs[i] < 0 else "0"
    is_correct = "✅" if correct_signs[i] == 1 else "❌"
    
    print(f"{pred_val:9.3f} | {actual_val:7.3f} | {pred_sign:9s} | {actual_sign:11s} | {is_correct}")

# Compare with random chance
random_accuracy = 0.5  # 50% chance for random guessing
improvement = (sign_accuracy - random_accuracy) / random_accuracy * 100

print(f"\n🎯 PERFORMANCE COMPARISON:")
print(f"ARIMAX Sign Accuracy: {sign_accuracy*100:.2f}%")
print(f"Random Chance: {random_accuracy*100:.2f}%")
print(f"Improvement over random: {improvement:.2f}%")

# Distribution analysis
print(f"\n📊 SIGN DISTRIBUTION:")
pred_positive_pct = (pred_signs > 0).mean() * 100
pred_negative_pct = (pred_signs < 0).mean() * 100
actual_positive_pct = (actual_signs > 0).mean() * 100
actual_negative_pct = (actual_signs < 0).mean() * 100

print(f"Predictions: {pred_positive_pct:.1f}% positive, {pred_negative_pct:.1f}% negative")
print(f"Actuals:     {actual_positive_pct:.1f}% positive, {actual_negative_pct:.1f}% negative")

print(f"\n✅ ANALYSIS COMPLETE!")
print(f"Sign accuracy for all {total_predictions:,} ARIMAX predictions: {sign_accuracy*100:.2f}%")
