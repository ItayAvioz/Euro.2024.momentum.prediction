import pandas as pd

orig = pd.read_csv('models/modeling/scripts/outputs/predictions/arimax_predictions.csv')
arimax = orig[orig['model_type'] == 'momentum_to_change_arimax']

print('Original ARIMAX settings:')
print(f'  has_exog values: {arimax["has_exog"].unique()}')
print(f'  n_train values: {arimax["n_train_observations"].unique()}')
print(f'\n  ARIMA orders used:')
print(arimax['arima_order'].value_counts().head(10))

new = pd.read_csv('models/period_separated_momentum/outputs/arimax_predictions_by_period.csv')
print('\nNew ARIMAX settings:')
print(f'  has_exog values: {new["has_exog"].unique()}')
print(f'  n_train range: {new["n_train"].min()} - {new["n_train"].max()}')
print(f'\n  ARIMA orders used:')
print(new['arima_order'].value_counts().head(10))

