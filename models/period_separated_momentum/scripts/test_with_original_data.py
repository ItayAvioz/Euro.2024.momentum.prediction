"""
Test: Run the same ARIMAX approach on ORIGINAL data to verify we get same results.
"""
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

from statsmodels.tsa.arima.model import ARIMA

# Load ORIGINAL data (not period-separated)
orig_data = pd.read_csv('models/preprocessing/data/targets/momentum_targets_streamlined.csv')
orig_data['minute'] = orig_data['minute_range'].apply(lambda x: int(x.split('-')[0]))

# Load original predictions for comparison
orig_pred = pd.read_csv('models/modeling/scripts/outputs/predictions/arimax_predictions.csv')
orig_arimax = orig_pred[orig_pred['model_type'] == 'momentum_to_change_arimax'].copy()

print("="*60)
print("TEST: Running ARIMAX on ORIGINAL data")
print("="*60)

# Parameters matching original
TRAIN_END = 75
TEST_START = 75
TEST_END = 90
ARIMA_ORDER = (1, 1, 1)

# Test on one match first
match_id = 3930158  # Germany vs Scotland
team = 'Germany'

match_data = orig_data[orig_data['match_id'] == match_id].copy()
match_data = match_data.sort_values('minute').reset_index(drop=True)

train_data = match_data[match_data['minute'] < TRAIN_END]
test_data = match_data[(match_data['minute'] >= TEST_START) & (match_data['minute'] < TEST_END)]

print(f"\nMatch: Germany vs Scotland")
print(f"Training records: {len(train_data)}")
print(f"Test records: {len(test_data)}")

# Get series
train_momentum = train_data['team_home_momentum'].values
train_change = train_data['team_home_momentum_change'].values
test_momentum = test_data['team_home_momentum'].values
test_change = test_data['team_home_momentum_change'].values

print(f"\nTraining change series (last 5): {train_change[-5:]}")
print(f"Test change series (first 5): {test_change[:5]}")

# Fit ARIMAX
try:
    model = ARIMA(train_change, order=ARIMA_ORDER, exog=train_momentum)
    fitted = model.fit()
    
    # Predict
    predictions = fitted.forecast(steps=len(test_change), exog=test_momentum)
    
    print(f"\nPredictions (first 5): {predictions[:5]}")
    print(f"Actual (first 5): {test_change[:5]}")
    
    # Compare with original predictions
    orig_match = orig_arimax[(orig_arimax['game_id'] == match_id) & (orig_arimax['team'] == team)]
    orig_match = orig_match.sort_values('minute_start')
    
    print(f"\nOriginal predictions (first 5): {orig_match['prediction_value'].values[:5]}")
    print(f"Original actual (first 5): {orig_match['actual_value'].values[:5]}")
    
    # Check if predictions match
    my_preds = predictions[:len(orig_match)]
    orig_preds = orig_match['prediction_value'].values
    
    diff = np.abs(my_preds - orig_preds)
    print(f"\nDifference with original predictions:")
    print(f"  Mean diff: {diff.mean():.6f}")
    print(f"  Max diff: {diff.max():.6f}")
    print(f"  Exact matches (<0.001): {(diff < 0.001).sum()}/{len(diff)}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

