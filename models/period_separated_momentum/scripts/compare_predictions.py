import pandas as pd
import numpy as np

# Load original predictions
orig_pred = pd.read_csv('models/modeling/scripts/outputs/predictions/arimax_predictions.csv')
print(f"Original predictions: {len(orig_pred)}")

# Load new predictions
new_pred = pd.read_csv('models/period_separated_momentum/outputs/arimax_predictions_by_period.csv')
print(f"New predictions: {len(new_pred)}")

print("\nOriginal prediction columns:")
print(orig_pred.columns.tolist())

print("\nNew prediction columns:")
print(new_pred.columns.tolist())

# Check original structure
print("\n" + "="*60)
print("ORIGINAL PREDICTION STRUCTURE")
print("="*60)
print(orig_pred.head(10))

# Check new structure
print("\n" + "="*60)
print("NEW PREDICTION STRUCTURE")
print("="*60)
print(new_pred.head(10))

