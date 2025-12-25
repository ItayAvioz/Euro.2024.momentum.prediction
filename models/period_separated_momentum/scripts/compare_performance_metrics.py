import pandas as pd
import numpy as np

# Load predictions
orig = pd.read_csv('models/modeling/scripts/outputs/predictions/arimax_predictions.csv')
orig = orig[orig['model_type'] == 'momentum_to_change_arimax'].copy()

new = pd.read_csv('models/period_separated_momentum/outputs/arimax_predictions_by_period.csv')

print("="*60)
print("PERFORMANCE COMPARISON: ORIGINAL vs NEW")
print("="*60)

# Calculate metrics for ORIGINAL
orig_mse = np.mean((orig['prediction_value'] - orig['actual_value'])**2)
orig_sign_match = (np.sign(orig['prediction_value']) == np.sign(orig['actual_value'])).mean()

# Calculate metrics for NEW
new_mse = np.mean((new['prediction_value'] - new['actual_value'])**2)
new_sign_match = (np.sign(new['prediction_value']) == np.sign(new['actual_value'])).mean()

print(f"\n{'Metric':<25} {'Original':<15} {'New':<15} {'Better?':<10}")
print("-"*65)
print(f"{'MSE':<25} {orig_mse:<15.4f} {new_mse:<15.4f} {'NEW ✅' if new_mse < orig_mse else 'ORIG ✅'}")
print(f"{'Sign Accuracy':<25} {100*orig_sign_match:<14.1f}% {100*new_sign_match:<14.1f}% {'NEW ✅' if new_sign_match > orig_sign_match else 'ORIG ✅'}")

# RMSE
orig_rmse = np.sqrt(orig_mse)
new_rmse = np.sqrt(new_mse)
print(f"{'RMSE':<25} {orig_rmse:<15.4f} {new_rmse:<15.4f} {'NEW ✅' if new_rmse < orig_rmse else 'ORIG ✅'}")

# MAE
orig_mae = np.mean(np.abs(orig['prediction_value'] - orig['actual_value']))
new_mae = np.mean(np.abs(new['prediction_value'] - new['actual_value']))
print(f"{'MAE':<25} {orig_mae:<15.4f} {new_mae:<15.4f} {'NEW ✅' if new_mae < orig_mae else 'ORIG ✅'}")

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"\nOriginal: MSE={orig_mse:.4f}, Sign={100*orig_sign_match:.1f}%")
print(f"New:      MSE={new_mse:.4f}, Sign={100*new_sign_match:.1f}%")

