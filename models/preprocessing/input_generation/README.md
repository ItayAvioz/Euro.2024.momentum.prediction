# Input Generation - 3-Minute Window Momentum Calculation

## Overview

This module generates 3-minute momentum windows for all Euro 2024 matches, calculating team momentum for overlapping time periods with 1-minute lag intervals.

## Purpose

Create a comprehensive dataset of team momentum values for every possible 3-minute window across all matches, enabling time-series momentum prediction modeling.

## Window Strategy

- **Window Size**: 3 minutes
- **Lag Interval**: 1 minute  
- **Pattern**: 0-3, 1-4, 2-5, 3-6, ..., until end of match
- **Teams**: Both home and away team momentum calculated per window

## Key Scripts

### `momentum_3min_calculator.py`
Core momentum calculation engine (relocated from models root):
- Event-level momentum calculation
- Context multipliers (location, time, score, pressure)
- Team-specific momentum aggregation

### `window_generator.py` 
Window generation and batch processing:
- Match data loading and validation
- 3-minute window extraction with 1-minute lag
- Batch processing across all matches
- CSV output generation

### `momentum_pipeline.py`
End-to-end pipeline orchestration:
- Data loading and preprocessing
- Window generation coordination  
- Momentum calculation execution
- Results aggregation and export

## Configuration

### `feature_config.yaml`
```yaml
window_settings:
  duration_minutes: 3
  lag_minutes: 1
  min_events_threshold: 5

momentum_settings:
  eliminated_events: ["Bad Behaviour", "Injury Stoppage", ...]
  context_multipliers:
    location: true
    time: true  
    score: true
    pressure: true

output_settings:
  format: "csv"
  filename_pattern: "momentum_windows_{timestamp}.csv"
```

## Output Format

CSV file with columns:
- `match_id`: Unique match identifier
- `minute_window`: Start minute of window (0, 1, 2, 3, ...)
- `team_home_momentum`: Home team momentum (0.0-10.0+ scale)
- `team_away_momentum`: Away team momentum (0.0-10.0+ scale)
- `total_events`: Total events in window
- `home_events`: Home team events count
- `away_events`: Away team events count

## Testing

### `test_window_generation.py`
- Window boundary validation
- Momentum calculation accuracy
- Edge case handling (overtime, short matches)
- Performance benchmarks

## Usage Example

```python
from scripts.momentum_pipeline import MomentumPipeline

# Initialize pipeline
pipeline = MomentumPipeline(config_path="configs/feature_config.yaml")

# Generate all windows
results = pipeline.generate_all_momentum_windows()

# Export to CSV
pipeline.export_results("momentum_windows_complete.csv")
```

## Quality Assurance

- **Data Validation**: Match boundaries, event counts, team assignments
- **Momentum Validation**: Score ranges, calculation consistency
- **Performance Monitoring**: Processing time, memory usage
- **Edge Case Handling**: Overtime periods, abandoned matches

## Integration

This module provides input features for the downstream modeling pipeline. Output CSV serves as the primary feature matrix for momentum prediction models.
