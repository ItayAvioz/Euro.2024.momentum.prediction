import pandas as pd
import numpy as np

# Load predictions
orig = pd.read_csv('models/modeling/scripts/outputs/predictions/arimax_predictions.csv')
orig_arimax = orig[orig['model_type'] == 'momentum_to_change_arimax'].copy()

new = pd.read_csv('models/period_separated_momentum/outputs/arimax_predictions_by_period.csv')

print("="*60)
print("MODEL PERFORMANCE COMPARISON")
print("="*60)

# Original metrics
print("\n📊 ORIGINAL MODEL:")
print(f"  Total predictions: {len(orig_arimax)}")
print(f"  MSE: {orig_arimax['mse'].mean():.4f}")
print(f"  Directional Accuracy: {orig_arimax['directional_accuracy'].mean()*100:.2f}%")

# Calculate sign accuracy for original
orig_arimax['sign_correct'] = (np.sign(orig_arimax['prediction_value']) == np.sign(orig_arimax['actual_value']))
orig_sign_acc = orig_arimax['sign_correct'].mean()
print(f"  Sign Accuracy: {orig_sign_acc*100:.2f}%")

print("\n📊 NEW MODEL (period-separated):")
print(f"  Total predictions: {len(new)}")
print(f"  MSE: {new['mse'].mean():.4f}")
print(f"  Directional Accuracy: {new['directional_accuracy'].mean()*100:.2f}%")

# Calculate sign accuracy for new
new['sign_correct'] = (np.sign(new['prediction_value']) == np.sign(new['actual_value']))
new_sign_acc = new['sign_correct'].mean()
print(f"  Sign Accuracy: {new_sign_acc*100:.2f}%")

print("\n" + "="*60)
print("COMPARISON")
print("="*60)
mse_diff = new['mse'].mean() - orig_arimax['mse'].mean()
dir_diff = (new['directional_accuracy'].mean() - orig_arimax['directional_accuracy'].mean()) * 100
sign_diff = (new_sign_acc - orig_sign_acc) * 100

print(f"  MSE difference: {mse_diff:+.4f} ({'worse' if mse_diff > 0 else 'better'})")
print(f"  Directional Acc diff: {dir_diff:+.2f}%")
print(f"  Sign Acc diff: {sign_diff:+.2f}%")

