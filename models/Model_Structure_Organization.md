# Euro 2024 Momentum Modeling - Project Structure Organization
## Version 1.0 - February 2024

## 🎯 Overview

This document outlines the organization and structure for the momentum modeling phase of the Euro 2024 project. The structure is designed to ensure clean separation of concerns, reproducibility, and maintainable code.

## 📁 Directory Structure

```
models/
├── preprocessing/
│   ├── README.md                     # Phase overview and methodology
│   ├── input_generation/
│   │   ├── scripts/
│   │   │   ├── window_generator.py   # 3-min window creation
│   │   │   └── feature_builder.py    # Feature engineering
│   │   ├── tests/
│   │   │   └── test_window_gen.py
│   │   └── configs/
│   │       └── feature_config.yaml
│   └── output_generation/
│       ├── scripts/
│       │   ├── target_calculator.py  # Y variable calculation
│       │   └── label_generator.py    # Target labeling
│       ├── tests/
│       │   └── test_targets.py
│       └── configs/
│           └── target_config.yaml
│
├── data_splitting/
│   ├── README.md                     # Validation strategies doc
│   ├── scripts/
│   │   ├── shift_splitter.py        # Y shift(-1) approach
│   │   └── walk_forward.py          # Walk-forward validation
│   ├── tests/
│   │   ├── test_shift.py
│   │   └── test_walk_forward.py
│   └── configs/
│       └── split_config.yaml
│
├── modeling/
│   ├── README.md                     # Models documentation
│   ├── scripts/
│   │   ├── base_model.py            # Abstract base class
│   │   └── arima_model.py           # ARIMA implementation
│   ├── tests/
│   │   └── test_arima.py
│   ├── configs/
│   │   └── model_config.yaml
│   └── notebooks/
│       └── model_exploration.ipynb
│
├── evaluation/
│   ├── README.md                     # Metrics documentation
│   ├── scripts/
│   │   ├── metrics.py               # Core metrics
│   │   └── visualization.py         # Results plotting
│   ├── tests/
│   │   └── test_metrics.py
│   └── configs/
│       └── eval_config.yaml
│
└── utils/                            # Shared utilities
    ├── data_loader.py
    ├── config_parser.py
    └── logger.py
```

## 📋 Component Details

### 1️⃣ Preprocessing Phase

#### Input Generation
- **Purpose**: Create clean 3-minute windows with engineered features
- **Key Components**:
  - Window generation with proper overlap handling
  - Feature engineering based on momentum calculation
  - Data validation and quality checks
- **Output**: Structured DataFrame with features per window

#### Output Generation
- **Purpose**: Define and calculate target variables
- **Key Components**:
  - Momentum change calculation for next window
  - Target variable normalization
  - Label generation for directional prediction
- **Output**: Target values aligned with input windows

### 2️⃣ Data Splitting Phase

#### Y Shift(-1) Approach
- **Purpose**: Traditional time series split with shifted targets
- **Implementation**:
  - Proper handling of window boundaries
  - Prevention of data leakage
  - Train/validation/test split ratios

#### Walk-Forward Validation
- **Purpose**: Rolling window validation strategy
- **Implementation**:
  - Dynamic training window size
  - Step size configuration
  - Multiple validation periods

### 3️⃣ Modeling Phase

#### ARIMA Implementation
- **Purpose**: Initial baseline model
- **Key Components**:
  - Parameter optimization
  - Seasonal components handling
  - Model persistence
- **Integration**: Common interface for future models

### 4️⃣ Evaluation Phase

#### Metrics Implementation
- **Purpose**: Comprehensive model assessment
- **Key Metrics**:
  - Adjusted R² for fit quality
  - MSE for prediction accuracy
  - Directional Accuracy for trend prediction
- **Visualization**: Performance plots and comparisons

## 🔄 Workflow Integration

### Data Flow
1. Raw events → Preprocessing → Feature windows
2. Feature windows → Target generation → Complete datasets
3. Datasets → Data splitting → Training/validation sets
4. Training sets → Model training → Trained models
5. Validation sets → Evaluation → Performance metrics

### Configuration Management
- YAML-based configuration files
- Environment-specific settings
- Reproducible experiments

### Testing Strategy
- Unit tests for each component
- Integration tests for workflows
- Data validation tests
- Performance benchmarks

## 📊 Expected Outputs

### Per Phase
1. **Preprocessing**:
   - Clean feature matrices
   - Target variables
   - Data quality reports

2. **Data Splitting**:
   - Multiple train/test sets
   - Validation performance logs
   - Split statistics

3. **Modeling**:
   - Trained model artifacts
   - Parameter optimization results
   - Training logs

4. **Evaluation**:
   - Metric reports
   - Performance visualizations
   - Model comparisons

## 🔍 Quality Assurance

### Code Standards
- PEP 8 compliance
- Type hints
- Comprehensive docstrings

### Documentation
- README per component
- API documentation
- Usage examples

### Testing Requirements
- >80% code coverage
- Performance benchmarks
- Edge case handling

## 🚀 Next Steps

1. **Implementation Order**:
   - Set up directory structure
   - Create base classes and interfaces
   - Implement preprocessing pipeline
   - Develop ARIMA baseline
   - Add evaluation framework

2. **Future Extensions**:
   - Additional models (XGBoost, LSTM)
   - Feature importance analysis
   - Model ensemble framework
   - Online learning capabilities

## 📝 Notes

- Keep all momentum calculation logic in current location
- Maintain backward compatibility with existing scripts
- Document all assumptions and decisions
- Version control all configurations
- Log all experimental results

---

*This structure is designed to be modular and extensible, allowing for easy addition of new models and evaluation metrics while maintaining clean separation of concerns.*
