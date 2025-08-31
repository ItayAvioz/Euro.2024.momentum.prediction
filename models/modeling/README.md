# ARIMA/ARIMAX Momentum Prediction Models

## 🎯 Overview
Advanced time series implementation for momentum prediction using both univariate and multivariate models:

### ARIMA Models (Univariate):
1. **Momentum → Momentum**: Predicts future momentum using past momentum values
2. **Momentum Change → Momentum Change**: Predicts future momentum changes using past changes

### ARIMAX Models (With Exogenous Variables):
3. **Momentum Change → Momentum Change (with Momentum)**: Predicts momentum changes using past changes AND current momentum as exogenous variable

## 📊 Model Architecture
- **ARIMA**: Pure ARIMA(p,d,q) - univariate time series
- **ARIMAX**: ARIMA(p,d,q) with exogenous variables - multivariate time series
- **Training Period**: Minutes 0-75
- **Testing Period**: Minutes 75-90 (no overtime)
- **Teams**: Both Team X and Team Y per game
- **Total Models**: 6 per game (3 model types × 2 teams)

## 🔄 Data Flow
1. Load momentum_targets_streamlined.csv
2. For each game:
   - Split chronologically: 0-75 (train) vs 75-90 (test)
   - Train ARIMA on momentum values
   - Train ARIMA on momentum_change values
   - Train ARIMAX on momentum_change with momentum as exogenous
   - Generate predictions for test period
   - Calculate evaluation metrics (MSE, Adjusted R², Directional Accuracy)
3. Save all results to CSV

## 🔗 ARIMAX Advantages
- **Leverages Relationships**: Uses momentum to predict momentum changes
- **Enhanced Accuracy**: Incorporates additional information
- **Real-world Relevance**: Current momentum influences future changes

## 📈 Output Format
**arimax_predictions.csv columns:**
- game_id, team, model_type, minutes_prediction, minute_start
- prediction_value, actual_value
- mse, adjusted_r2, directional_accuracy
- arima_order, n_train_observations, has_exog
