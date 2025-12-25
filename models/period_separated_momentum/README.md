# Period-Separated Momentum Analysis

## Overview

This module generates momentum data and ARIMAX predictions with **proper period separation** to avoid mixing first half stoppage time (period 1) with second half data (period 2).

## The Problem

In football/soccer, the game has two periods:
- **Period 1 (First Half):** Minutes 0-45 + stoppage time (e.g., 45+3')
- **Period 2 (Second Half):** Minutes 45-90 + stoppage time (e.g., 90+5')

The issue: Minutes 45-48 can occur in BOTH periods:
- Minute 46 in Period 1 = First half stoppage time (45+1')
- Minute 46 in Period 2 = Second half, minute 1

The original momentum calculation **mixed events from both periods** at overlapping minutes, causing data contamination.

## The Solution

This module calculates momentum **separately for each period**:
1. Filter events by period BEFORE calculating momentum
2. Add `period` column to all outputs
3. Keep first half and second half data separate

## Files

### Scripts

| File | Description |
|------|-------------|
| `period_momentum_generator.py` | Generates momentum data with period separation |
| `period_arimax_predictor.py` | Runs ARIMAX model on period-separated data |
| `validate_data_consistency.py` | Validates new data against original |

### Outputs

| File | Description |
|------|-------------|
| `momentum_by_period.csv` | Momentum data with period column |
| `arimax_predictions_by_period.csv` | ARIMAX predictions with period column |
| `validation_report.csv` | Data consistency validation report |

## Data Format

### momentum_by_period.csv

```
match_id | period | minute_range | minute | team_home | team_away | team_home_momentum | team_away_momentum | team_home_momentum_change | team_away_momentum_change
3930158  | 1      | 0-2          | 0      | Germany   | Scotland  | 4.802              | 4.166              | 0.0                       | 0.0
3930158  | 1      | 45-47        | 45     | Germany   | Scotland  | 5.5                | 4.2                | 0.3                       | -0.1
3930158  | 2      | 45-47        | 45     | Germany   | Scotland  | 5.0                | 4.5                | 0.0                       | 0.0
```

### arimax_predictions_by_period.csv

```
match_id | period | team | minute_range | prediction_value | actual_value | mse | directional_accuracy
3930158  | 1      | Germany | 34-36     | -0.375           | -0.229       | 0.37 | 0.63
```

## Results Summary

### Momentum Data
- **Total records:** 4,819
- **Period 1 records:** 2,327
- **Period 2 records:** 2,492
- **Overlapping minutes (45-48):** Now properly separated by period

### ARIMAX Predictions
- **Total predictions:** 2,492
- **Period 1:** MSE=0.37, Directional Accuracy=62.95%
- **Period 2:** MSE=0.44, Directional Accuracy=61.56%
- **Overall Sign Accuracy:** 62.24%

## Usage

```python
# Generate momentum data
python scripts/period_momentum_generator.py

# Validate against original
python scripts/validate_data_consistency.py

# Generate ARIMAX predictions
python scripts/period_arimax_predictor.py
```

## Dashboard Integration

To use this data in the dashboard, update `Dashboard/pages/arimax_momentum.py` to:
1. Load `momentum_by_period.csv` instead of `momentum_targets_streamlined.csv`
2. Filter by period for first/second half graphs
3. Use `arimax_predictions_by_period.csv` for predictions

---

*Generated: December 2024*

