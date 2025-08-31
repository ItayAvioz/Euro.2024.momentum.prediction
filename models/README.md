# 📁 **Models Directory - Organized Structure**

## 🎯 **Overview**
This directory contains the complete momentum analysis and modeling pipeline for the Euro 2024 tournament data. The structure has been reorganized for better maintainability and follows software engineering best practices.

---

## 📂 **Directory Structure**

```
models/
├── 📚 CORE DOCUMENTATION/
│   ├── Model_Structure_Organization.md          # Main modeling framework guide
│   ├── Final_Momentum_Function_Summary.md       # Core momentum calculation methodology
│   ├── 3_Minute_Momentum_Calculation_Methodology.md  # Algorithm specification
│   └── Comprehensive_Momentum_Forecasting_Plan.md    # Project planning document
│
├── 🧪 TESTING/
│   ├── test.md                                  # Comprehensive test results
│   ├── test_momentum_calculator.py              # Unit test scripts
│   └── comprehensive_window_test.py             # Integration test scripts
│
├── 🏭 PREPROCESSING PIPELINE/
│   ├── data/
│   │   ├── targets/                             # Momentum target datasets
│   │   │   ├── momentum_targets_streamlined.csv    # Main dataset for modeling
│   │   │   └── momentum_targets_enhanced.csv       # Enhanced dataset with features
│   │   └── outputs/                             # Analysis result datasets
│   │       ├── correlation_summary.csv             # Correlation analysis results
│   │       ├── game_superiority_score_analysis.csv # Team superiority metrics
│   │       └── game_superiority_summary.csv        # Summary of superiority analysis
│   │
│   ├── input_generation/                        # Data input pipeline
│   │   ├── scripts/                             # Input generation scripts
│   │   ├── configs/                             # Configuration files
│   │   └── tests/                               # Input pipeline tests
│   │
│   ├── output_generation/                       # Data output pipeline
│   │   ├── scripts/                             # Output generation and analysis scripts
│   │   ├── configs/                             # Configuration files
│   │   └── tests/                               # Output pipeline tests
│   │
│   └── [Documentation Files]                   # README, completion summaries, validation reports
│
├── 🤖 MODELING PIPELINE/
│   ├── scripts/
│   │   ├── models/                              # Core model implementations
│   │   │   ├── base_model.py                       # Abstract base class for all models
│   │   │   ├── arima_model.py                      # Pure ARIMA model implementation
│   │   │   └── arimax_model.py                     # ARIMAX model with exogenous variables
│   │   │
│   │   ├── predictors/                          # Main prediction pipelines
│   │   │   ├── momentum_arima_predictor.py         # ARIMA prediction pipeline
│   │   │   └── momentum_arimax_predictor.py        # ARIMAX prediction pipeline
│   │   │
│   │   ├── analysis/                            # Model evaluation and analysis
│   │   │   ├── analyze_arimax.py                   # ARIMAX performance summary
│   │   │   ├── arimax_differential_sign_analysis.py # Differential sign accuracy analysis
│   │   │   ├── arimax_momentum_change_analysis.py  # Momentum change analysis
│   │   │   ├── calculate_sign_accuracy.py          # Sign prediction accuracy
│   │   │   └── team_momentum_sign_analysis.py      # Team-level sign analysis
│   │   │
│   │   └── outputs/
│   │       ├── predictions/                     # Model prediction results
│   │       │   ├── arima_predictions.csv           # Pure ARIMA results
│   │       │   └── arimax_predictions.csv          # ARIMAX results
│   │       └── analysis/                        # Analysis result files
│   │           └── arimax_differential_sign_analysis.csv # Differential analysis results
│   │
│   ├── configs/                                 # Model configuration files
│   │   └── arima_config.yaml                       # ARIMA/ARIMAX model parameters
│   │
│   ├── tests/                                   # Model testing (structure ready)
│   │
│   └── [Documentation Files]                   # README, implementation summaries
│
├── 🎯 FINAL/                                   # Production-ready components
│   └── README.md                               # Final implementation documentation
│
└── 🔬 EXPERIMENTS/                             # Research and experimental work
    ├── iterations/                             # Iterative model development
    ├── results/                                # Experimental results
    └── README.md                               # Experiment documentation
```

---

## 🚀 **Quick Start Guide**

### **1. Data Processing**
```bash
# Navigate to preprocessing
cd preprocessing/input_generation/scripts
python enhanced_momentum_generator_v2.py

# Generate analysis outputs
cd ../output_generation/scripts
python analyze_momentum_change_output.py
```

### **2. Model Training & Prediction**
```bash
# Navigate to modeling
cd modeling/scripts/predictors

# Run pure ARIMA models
python momentum_arima_predictor.py

# Run ARIMAX models (with exogenous variables)
python momentum_arimax_predictor.py
```

### **3. Analysis & Evaluation**
```bash
# Navigate to analysis scripts
cd modeling/scripts/analysis

# Analyze overall ARIMAX performance
python analyze_arimax.py

# Detailed differential sign analysis
python arimax_differential_sign_analysis.py

# Team-level momentum sign analysis
python team_momentum_sign_analysis.py
```

---

## 📊 **Key Data Files**

### **Input Data**
- `preprocessing/data/targets/momentum_targets_streamlined.csv` - **Main dataset** for all modeling
- `preprocessing/data/targets/momentum_targets_enhanced.csv` - Enhanced dataset with additional features

### **Model Results**
- `modeling/scripts/outputs/predictions/arima_predictions.csv` - Pure ARIMA model predictions
- `modeling/scripts/outputs/predictions/arimax_predictions.csv` - ARIMAX model predictions (includes all 3 models)

### **Analysis Results**
- `preprocessing/data/outputs/correlation_summary.csv` - Correlation between momentum metrics and game outcomes
- `preprocessing/data/outputs/game_superiority_score_analysis.csv` - Team superiority analysis
- `modeling/scripts/outputs/analysis/arimax_differential_sign_analysis.csv` - Differential sign prediction analysis

---

## 🔧 **Configuration**

### **Model Parameters**
- `modeling/configs/arima_config.yaml` - ARIMA/ARIMAX model configuration
- `preprocessing/input_generation/configs/feature_config.yaml` - Feature engineering configuration
- `preprocessing/output_generation/configs/target_config.yaml` - Target generation configuration

---

## 🧪 **Testing**

### **Available Tests**
- `tests/test_momentum_calculator.py` - Unit tests for momentum calculation
- `tests/comprehensive_window_test.py` - Integration tests for window processing
- `tests/test.md` - Comprehensive test results documentation

### **Component-Specific Tests**
- `preprocessing/input_generation/tests/` - Input pipeline tests
- `preprocessing/output_generation/tests/` - Output pipeline tests
- `modeling/tests/` - Model testing (structure ready)

---

## 📈 **Models Implemented**

### **1. Pure ARIMA Models**
- **momentum → momentum**: Predicts future momentum values based on historical momentum
- **momentum_change → momentum_change**: Predicts future momentum changes based on historical changes

### **2. ARIMAX Models**
- **momentum → momentum_change**: Uses momentum as exogenous variable to predict momentum changes
- Leverages cross-correlation between momentum and momentum changes for better predictions

### **3. Evaluation Metrics**
- **MSE (Mean Squared Error)**: Prediction accuracy
- **Adjusted R²**: Model fit quality
- **Directional Accuracy**: Trend prediction accuracy (improvement vs decline)
- **Sign Accuracy**: Positive/negative prediction accuracy

---

## 📝 **Documentation**

### **Core Methodology**
- `Model_Structure_Organization.md` - Overall modeling framework
- `Final_Momentum_Function_Summary.md` - Detailed momentum calculation methodology
- `3_Minute_Momentum_Calculation_Methodology.md` - Algorithm specification

### **Implementation Summaries**
- `modeling/ARIMAX_IMPLEMENTATION_SUMMARY.md` - ARIMAX implementation details
- `modeling/ARIMAX_DIFFERENTIAL_ANALYSIS_SUMMARY.md` - Differential analysis results
- `preprocessing/PREPROCESSING_COMPLETION_SUMMARY.md` - Preprocessing pipeline summary

---

## 🎯 **Key Findings**

### **Model Performance Summary**
- **ARIMAX** generally outperforms pure ARIMA due to exogenous variable incorporation
- **Differential Sign Accuracy**: 71.11% (improvement of 42.5% over random)
- **Team-level Sign Predictions**: Varying accuracy across different momentum metrics

### **Momentum Insights**
- **Median Momentum**: 8.44
- **Median Momentum Change**: 0.00
- **Team Momentum Patterns**: 60.5% of time windows show opposite momentum change directions between teams
- **Correlation with Game Outcomes**: Weak but statistically significant correlations between momentum superiority and final scores

---

## 🔄 **Workflow**

### **Typical Analysis Workflow**
1. **Data Preparation**: Use `preprocessing/` pipeline to generate momentum targets
2. **Model Training**: Run `modeling/scripts/predictors/` to generate predictions
3. **Analysis**: Use `modeling/scripts/analysis/` to evaluate results
4. **Iteration**: Modify configs and repeat for different parameters

### **Adding New Models**
1. Extend `modeling/scripts/models/base_model.py` 
2. Implement new model in `modeling/scripts/models/`
3. Create predictor pipeline in `modeling/scripts/predictors/`
4. Add analysis scripts in `modeling/scripts/analysis/`

---

## ⚠️ **Important Notes**

### **Path Dependencies**
- All import paths have been updated to reflect the new structure
- Scripts expect to be run from their respective directories
- Config files use relative paths that work with the new structure

### **Data Integrity**
- Main dataset: `momentum_targets_streamlined.csv` contains 3-minute window momentum calculations
- All correlation analysis uses real match scores from `../../../Data/euro_2024_complete_dataset.csv`
- Prediction timeframes: Train on minutes 0-75, predict minutes 75-90 (no overtime)

---

## 📞 **Support**

### **Directory-Specific READMEs**
- `preprocessing/README.md` - Preprocessing pipeline details
- `modeling/README.md` - Modeling pipeline details  
- `experiments/README.md` - Experimental work documentation
- `final/README.md` - Production-ready components

### **Configuration Help**
- Check `configs/` directories for parameter explanations
- Review documentation files for methodology details
- Examine test files for usage examples

---

*Last Updated: August 31, 2025*  
*Structure Version: 2.0 (Reorganized)*  
*Status: ✅ Production Ready*
