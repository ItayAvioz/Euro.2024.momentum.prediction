# Preprocessing Phase - Euro 2024 Momentum Modeling

## Overview

This phase handles all data preprocessing for momentum modeling, including window generation, feature engineering, and target variable creation. The preprocessing is divided into two main components:

1. **Input Generation**: Creating clean 3-minute windows with engineered features
2. **Output Generation**: Defining and calculating target variables

## Purpose

Transform raw Euro 2024 event data into structured datasets suitable for momentum prediction modeling, ensuring proper temporal alignment and feature engineering.

## Key Components

### Input Generation
- **Window Generation**: Create overlapping 3-minute windows (0-3, 1-4, 2-5, etc.)
- **Momentum Calculation**: Calculate team momentum for each window
- **Feature Engineering**: Extract relevant features from event data
- **Data Validation**: Ensure data quality and consistency

### Output Generation  
- **Target Calculation**: Compute momentum change for next window y(t+3) - y(t)
- **Label Generation**: Create categorical labels for directional prediction
- **Temporal Alignment**: Ensure proper alignment between features and targets

## Data Flow

```
Raw Events → Window Generation → Momentum Calculation → Feature Matrix
                    ↓
Target Calculation → Target Alignment → Complete Dataset
```

## Implementation Status

### Phase 1: Input Generation ✅
- [x] Window generator for all 3-minute windows
- [x] Momentum calculation pipeline  
- [x] CSV output with match_id, minutes, team_x_momentum, team_y_momentum

### Phase 2: Output Generation (Planned)
- [ ] Target variable calculation
- [ ] Feature engineering expansion
- [ ] Data validation framework

## Usage

Navigate to the appropriate subfolder and refer to the specific README for detailed usage instructions.

## Dependencies

- pandas
- numpy
- Existing momentum calculation functions

## Output Format

Primary output: CSV with columns:
- `match_id`: Unique match identifier
- `minute_window`: Start minute of 3-minute window (e.g., 0 for 0-3 window)
- `team_home_momentum`: Home team momentum for the window
- `team_away_momentum`: Away team momentum for the window

## Configuration

Configuration files are stored in respective `configs/` subdirectories and use YAML format for easy modification and version control.
