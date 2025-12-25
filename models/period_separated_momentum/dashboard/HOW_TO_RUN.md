# Euro 2024 ARIMAX Dashboard - Period-Separated Version

## Overview

This dashboard presents the ARIMAX momentum prediction model using **period-separated momentum data**.

The key difference from the original dashboard:
- First half (Period 1) and second half (Period 2) momentum are calculated **separately**
- No mixing of events at overlapping minutes (45-48, 90-93)
- Cleaner visualization for stoppage time
- Slightly different model performance due to cleaner data

## Data Source

The dashboard uses these files from `models/period_separated_momentum/outputs/`:
- `momentum_by_period.csv` - Period-separated momentum calculations
- `arimax_predictions_by_period.csv` - ARIMAX predictions using period-separated data

## Quick Start

### Option 1: Run from project root
```bash
cd "C:\Users\yonatanam\Desktop\Euro 2024 - momentum - DS-AI project"
streamlit run models/period_separated_momentum/dashboard/main.py
```

### Option 2: Run from dashboard folder
```bash
cd "C:\Users\yonatanam\Desktop\Euro 2024 - momentum - DS-AI project\models\period_separated_momentum\dashboard"
streamlit run main.py
```

### Option 3: Use the batch file
```bash
run_dashboard.bat
```

## Requirements

Install dependencies:
```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install streamlit pandas numpy plotly
```

## Dashboard Structure

```
dashboard/
├── main.py                 # Entry point
├── pages/
│   ├── __init__.py
│   └── arimax_momentum.py  # Main ARIMAX analysis page
├── utils/
│   ├── __init__.py
│   ├── config.py           # Configuration and paths
│   └── data_loader.py      # Data loading utilities
├── requirements.txt
├── HOW_TO_RUN.md          # This file
└── run_dashboard.bat       # Windows batch runner
```

## Dashboard Tabs

1. **📊 Model Overview** - Performance metrics, model explanation, autocorrelation
2. **🎯 Sign Accuracy Analysis** - Sign agreement, contingency tables
3. **👥 Paired Team Analysis** - Both teams in same window
4. **📈 Metric Definitions** - Explanation of all metrics
5. **🔬 Real Data Analysis** - Momentum vs match outcomes
6. **📉 Game Comparison** - Interactive game-by-game graphs

## Comparison with Original Dashboard

| Metric | Original | Period-Separated |
|--------|----------|------------------|
| Data Source | Mixed periods | Separated periods |
| MSE | 0.5702 | 0.4437 (better) |
| Sign Accuracy | 67.3% | 63.0% (lower) |
| Stoppage Time | Mixed events | Clean separation |

## Troubleshooting

### Data not found error
Make sure you've run the momentum generator first:
```bash
python models/period_separated_momentum/scripts/period_momentum_generator.py
python models/period_separated_momentum/scripts/period_arimax_predictor.py
```

### Port already in use
```bash
streamlit run main.py --server.port 8502
```

### Clear cache
```bash
streamlit cache clear
```

