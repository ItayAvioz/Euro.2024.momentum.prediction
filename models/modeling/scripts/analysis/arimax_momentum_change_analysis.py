"""
Focused Analysis: ARIMAX Momentum→Momentum Change Model
Summary statistics and distribution analysis for predictions vs actuals
"""

import pandas as pd
import numpy as np

# Load the ARIMAX predictions
df = pd.read_csv('../outputs/predictions/arimax_predictions.csv')

# Filter for ARIMAX momentum-to-change model only
arimax_data = df[df['model_type'] == 'momentum_to_change_arimax'].copy()

print("🎯 ARIMAX MOMENTUM→CHANGE MODEL - DETAILED ANALYSIS")
print("=" * 70)
print(f"Total predictions analyzed: {len(arimax_data):,}")
print(f"Games covered: {arimax_data['game_id'].nunique()}")
print(f"Teams analyzed: {arimax_data['team'].nunique()}")

# Extract prediction and actual values
predictions = arimax_data['prediction_value'].values
actuals = arimax_data['actual_value'].values

print(f"\n📊 SUMMARY STATISTICS COMPARISON")
print("=" * 50)

def get_summary_stats(values, name):
    """Calculate comprehensive summary statistics"""
    stats = {
        'count': len(values),
        'mean': np.mean(values),
        'median': np.median(values),
        'std': np.std(values),
        'min': np.min(values),
        'max': np.max(values),
        'q25': np.percentile(values, 25),
        'q75': np.percentile(values, 75),
        'iqr': np.percentile(values, 75) - np.percentile(values, 25),
        'range': np.max(values) - np.min(values),
        'skewness': pd.Series(values).skew(),
        'kurtosis': pd.Series(values).kurtosis()
    }
    return stats

# Calculate statistics for both
pred_stats = get_summary_stats(predictions, "Predictions")
actual_stats = get_summary_stats(actuals, "Actuals")

# Display side by side
print(f"{'Statistic':<15} {'Predictions':<15} {'Actuals':<15} {'Difference':<15}")
print("-" * 65)

for key in ['count', 'mean', 'median', 'std', 'min', 'max', 'q25', 'q75', 'iqr', 'range']:
    pred_val = pred_stats[key]
    actual_val = actual_stats[key]
    diff = pred_val - actual_val if key != 'count' else 0
    
    if key == 'count':
        print(f"{key:<15} {pred_val:<15.0f} {actual_val:<15.0f} {'-':<15}")
    else:
        print(f"{key:<15} {pred_val:<15.4f} {actual_val:<15.4f} {diff:<15.4f}")

print(f"\nSkewness:       {pred_stats['skewness']:<15.4f} {actual_stats['skewness']:<15.4f}")
print(f"Kurtosis:       {pred_stats['kurtosis']:<15.4f} {actual_stats['kurtosis']:<15.4f}")

print(f"\n🔍 SIGN DISTRIBUTION ANALYSIS")
print("=" * 40)

# Calculate signs
pred_signs = np.sign(predictions)
actual_signs = np.sign(actuals)

# Count distributions
pred_positive = (pred_signs > 0).sum()
pred_negative = (pred_signs < 0).sum()
pred_zero = (pred_signs == 0).sum()

actual_positive = (actual_signs > 0).sum()
actual_negative = (actual_signs < 0).sum()
actual_zero = (actual_signs == 0).sum()

total = len(predictions)

print(f"{'Sign':<12} {'Predictions':<15} {'%':<8} {'Actuals':<15} {'%':<8}")
print("-" * 60)
print(f"{'Positive':<12} {pred_positive:<15} {pred_positive/total*100:<8.2f} {actual_positive:<15} {actual_positive/total*100:<8.2f}")
print(f"{'Negative':<12} {pred_negative:<15} {pred_negative/total*100:<8.2f} {actual_negative:<15} {actual_negative/total*100:<8.2f}")
print(f"{'Zero':<12} {pred_zero:<15} {pred_zero/total*100:<8.2f} {actual_zero:<15} {actual_zero/total*100:<8.2f}")

print(f"\n📈 PREDICTION vs ACTUAL SIGN COMBINATIONS")
print("=" * 50)

# Calculate 2x2 contingency table
pos_pred_pos_actual = ((pred_signs > 0) & (actual_signs > 0)).sum()
pos_pred_neg_actual = ((pred_signs > 0) & (actual_signs < 0)).sum()
neg_pred_pos_actual = ((pred_signs < 0) & (actual_signs > 0)).sum()
neg_pred_neg_actual = ((pred_signs < 0) & (actual_signs < 0)).sum()

print(f"{'Combination':<25} {'Count':<10} {'%':<10} {'Description'}")
print("-" * 60)
print(f"{'Positive → Positive':<25} {pos_pred_pos_actual:<10} {pos_pred_pos_actual/total*100:<10.2f} ✅ Correct")
print(f"{'Negative → Negative':<25} {neg_pred_neg_actual:<10} {neg_pred_neg_actual/total*100:<10.2f} ✅ Correct")
print(f"{'Positive → Negative':<25} {pos_pred_neg_actual:<10} {pos_pred_neg_actual/total*100:<10.2f} ❌ Wrong")
print(f"{'Negative → Positive':<25} {neg_pred_pos_actual:<10} {neg_pred_pos_actual/total*100:<10.2f} ❌ Wrong")

# Calculate accuracies
correct_total = pos_pred_pos_actual + neg_pred_neg_actual
sign_accuracy = correct_total / total

print(f"\n🎯 SIGN ACCURACY METRICS")
print("=" * 30)
print(f"Overall Sign Accuracy: {sign_accuracy:.4f} ({sign_accuracy*100:.2f}%)")
print(f"Correct predictions: {correct_total:,} out of {total:,}")

# Conditional accuracies
if actual_positive > 0:
    pos_precision = pos_pred_pos_actual / (pos_pred_pos_actual + pos_pred_neg_actual) if (pos_pred_pos_actual + pos_pred_neg_actual) > 0 else 0
    pos_recall = pos_pred_pos_actual / actual_positive
    print(f"\nWhen PREDICTING positive:")
    print(f"  Precision: {pos_precision:.4f} ({pos_precision*100:.2f}%)")
    print(f"  Recall: {pos_recall:.4f} ({pos_recall*100:.2f}%)")

if actual_negative > 0:
    neg_precision = neg_pred_neg_actual / (neg_pred_neg_actual + neg_pred_pos_actual) if (neg_pred_neg_actual + neg_pred_pos_actual) > 0 else 0
    neg_recall = neg_pred_neg_actual / actual_negative
    print(f"\nWhen PREDICTING negative:")
    print(f"  Precision: {neg_precision:.4f} ({neg_precision*100:.2f}%)")
    print(f"  Recall: {neg_recall:.4f} ({neg_recall*100:.2f}%)")

print(f"\n📊 VALUE RANGE ANALYSIS")
print("=" * 30)

# Analyze ranges
print(f"Prediction range: [{np.min(predictions):.4f}, {np.max(predictions):.4f}]")
print(f"Actual range:     [{np.min(actuals):.4f}, {np.max(actuals):.4f}]")

# Percentile analysis
percentiles = [1, 5, 10, 25, 50, 75, 90, 95, 99]
print(f"\nPercentile Analysis:")
print(f"{'Percentile':<12} {'Predictions':<15} {'Actuals':<15}")
print("-" * 42)
for p in percentiles:
    pred_p = np.percentile(predictions, p)
    actual_p = np.percentile(actuals, p)
    print(f"{p}th{'':<9} {pred_p:<15.4f} {actual_p:<15.4f}")

# Error analysis
errors = predictions - actuals
print(f"\n🎯 PREDICTION ERROR ANALYSIS")
print("=" * 35)
print(f"Mean Error (Bias):    {np.mean(errors):.4f}")
print(f"Mean Absolute Error:  {np.mean(np.abs(errors)):.4f}")
print(f"Root Mean Sq Error:   {np.sqrt(np.mean(errors**2)):.4f}")
print(f"Error Std Dev:        {np.std(errors):.4f}")
print(f"Error Range:          [{np.min(errors):.4f}, {np.max(errors):.4f}]")

# Correlation analysis
correlation = np.corrcoef(predictions, actuals)[0, 1]
print(f"\n📈 CORRELATION ANALYSIS")
print("=" * 25)
print(f"Pearson Correlation: {correlation:.4f}")
print(f"R-squared:           {correlation**2:.4f}")

print(f"\n✅ ANALYSIS COMPLETE!")
print(f"ARIMAX Momentum→Change model shows {sign_accuracy*100:.2f}% sign accuracy")
print(f"with {correlation:.3f} correlation between predictions and actuals.")
