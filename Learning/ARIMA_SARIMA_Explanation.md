# Understanding ARIMA and SARIMA Models

## What are ARIMA Models? 📊

ARIMA (AutoRegressive Integrated Moving Average) is a statistical model for analyzing and forecasting time series data. It combines three components:

1. **AR (AutoRegressive)**: Uses the relationship between an observation and a number of lagged observations
2. **I (Integrated)**: Differencing to make the time series stationary
3. **MA (Moving Average)**: Uses the dependency between an observation and residual errors from a moving average model

### ARIMA Components Explained

ARIMA(p,d,q) where:
- p = order of AR term (lags of dependent variable)
- d = number of differencing required to make time series stationary
- q = order of MA term (lags of forecast errors)

## Simple ARIMA Example

```python
import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA

# Sample data: Goals scored per match
goals_data = pd.Series([2, 1, 3, 2, 4, 1, 2, 3, 2, 1])

# Fit ARIMA model
model = ARIMA(goals_data, order=(1, 0, 1))  # ARIMA(1,0,1)
results = model.fit()

# Make predictions
forecast = results.forecast(steps=3)
print("Next 3 matches goal predictions:", forecast)
```

## What is SARIMA? 🔄

SARIMA (Seasonal ARIMA) extends ARIMA to capture seasonal patterns. It's particularly useful for our Euro 2024 momentum predictions because football matches often show seasonal patterns (like home/away alternation, or patterns within a match).

SARIMA adds seasonal components:
- Seasonal AR (P)
- Seasonal differencing (D)
- Seasonal MA (Q)
- Seasonal period (s)

### SARIMA Example for Match Momentum

```python
from statsmodels.tsa.statespace.sarimax import SARIMAX

# Sample momentum data (10-minute intervals in a match)
momentum_data = pd.Series([
    5.2, 5.8, 6.1, 5.9, 5.7, 6.3,  # First half
    5.1, 5.5, 6.2, 6.4, 6.0, 5.8,  # Second half
])

# SARIMA model with seasonal period of 6 (half-time pattern)
model = SARIMAX(
    momentum_data,
    order=(1, 0, 1),           # Non-seasonal components (p,d,q)
    seasonal_order=(1, 0, 1, 6)  # Seasonal components (P,D,Q,s)
)
results = model.fit()

# Predict next 3 intervals
forecast = results.forecast(steps=3)
```

## When to Use Each Model? 🤔

### Use ARIMA when:
- Data shows no seasonal patterns
- You need to model short-term dependencies
- Working with regular time intervals

### Use SARIMA when:
- Clear seasonal patterns exist
- Data shows repeating cycles
- Dealing with match-specific patterns (e.g., first half vs second half)

## Application in Euro 2024 Momentum Project

For our project, SARIMA might be more appropriate because:
1. Football matches have natural periods (45-minute halves)
2. Teams often show consistent patterns in momentum across matches
3. We can capture both in-game and between-game seasonal effects

### Example Implementation for Our Project

```python
def train_momentum_sarima(momentum_data, match_length=90):
    """
    Train SARIMA model for match momentum prediction
    
    Args:
        momentum_data: DataFrame with momentum scores
        match_length: Length of match in minutes
    """
    model = SARIMAX(
        momentum_data,
        order=(2, 1, 2),             # Non-seasonal components
        seasonal_order=(1, 0, 1, 45)  # Seasonal with half-time period
    )
    
    results = model.fit()
    return results

def predict_future_momentum(model, steps=15):
    """
    Predict momentum for next 15 minutes
    """
    forecast = model.forecast(steps=steps)
    return forecast
```

## Best Practices 🎯

1. **Data Preparation**:
   - Always check for stationarity
   - Plot ACF and PACF to determine orders
   - Handle missing values appropriately

2. **Model Selection**:
   - Start with simple models (lower orders)
   - Use AIC/BIC for model comparison
   - Consider multiple seasonal patterns

3. **Validation**:
   - Use walk-forward validation
   - Check residuals for randomness
   - Compare with simpler baselines

## Common Pitfalls to Avoid ⚠️

1. Overfitting with too many parameters
2. Ignoring data stationarity requirements
3. Not validating seasonal patterns
4. Using too long seasonal periods
5. Not considering external factors

Remember: The best model is often the simplest one that adequately captures the patterns in your data! 