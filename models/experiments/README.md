# 📊 models/experiments - Experimental Model Assets

## 🎯 Overview

This folder contains **experimental model assets**, **prototype models**, and **development artifacts** created during the research and development phase of the Euro 2024 momentum prediction system. These assets document the model development journey and experimental approaches.

## 📋 Experimental Assets

### 🤖 **Prototype Models**
- **`baseline_model.pkl`** *(Initial baseline model)*
  - **Algorithm**: Simple Linear Regression
  - **Performance**: R² = 0.312 (baseline)
  - **Purpose**: Initial benchmark
  - **Status**: 🔬 Experimental

- **`feature_limited_model.pkl`** *(Limited feature model)*
  - **Algorithm**: Random Forest (basic features)
  - **Performance**: R² = 0.487
  - **Purpose**: Feature importance testing
  - **Status**: 🔬 Experimental

- **`hybrid_prototype.pkl`** *(Early hybrid model)*
  - **Algorithm**: Classification + Regression
  - **Performance**: R² = 0.643
  - **Purpose**: Hybrid approach testing
  - **Status**: 🔬 Experimental

### 🔧 **Development Artifacts**
- **`feature_experiments/`** *(Feature engineering experiments)*
  - **`feature_v1.pkl`** - Initial feature set
  - **`feature_v2.pkl`** - Enhanced features
  - **`feature_v3.pkl`** - Optimized features
  - **Status**: 🔬 Experimental

- **`hyperparameter_tuning/`** *(Hyperparameter experiments)*
  - **`grid_search_results.json`** - Grid search results
  - **`random_search_results.json`** - Random search results
  - **`bayesian_optimization.json`** - Bayesian optimization
  - **Status**: 🔬 Experimental

### 📊 **Performance Tracking**
- **`model_comparison.json`** *(Model comparison results)*
  - **Content**: Performance metrics for all experiments
  - **Purpose**: Track model evolution
  - **Status**: 🔬 Experimental

- **`experiment_log.csv`** *(Experiment tracking)*
  - **Content**: Detailed experiment log
  - **Purpose**: Track all experiments and results
  - **Status**: 🔬 Experimental

- **`validation_experiments.json`** *(Validation experiments)*
  - **Content**: Different validation strategies tested
  - **Purpose**: Validation approach development
  - **Status**: 🔬 Experimental

### 🎯 **Specialized Experiments**
- **`temporal_validation/`** *(Temporal validation experiments)*
  - **`naive_split.pkl`** - Naive train/test split
  - **`random_split.pkl`** - Random split approach
  - **`temporal_split.pkl`** - Temporal split approach
  - **Status**: 🔬 Experimental

- **`feature_selection/`** *(Feature selection experiments)*
  - **`all_features.pkl`** - Model with all features
  - **`selected_features.pkl`** - Feature selection applied
  - **`importance_based.pkl`** - Importance-based selection
  - **Status**: 🔬 Experimental

## 🚀 Key Experiments

### 1. **Baseline Model Development**
**Purpose**: Establish performance baseline
**Models Tested**:
- Linear Regression: R² = 0.312
- Simple Random Forest: R² = 0.423
- Gradient Boosting: R² = 0.356

**Result**: Random Forest showed promise

### 2. **Feature Engineering Evolution**
**Purpose**: Optimize feature set
**Experiments**:
- All Features (127): R² = 0.534 (overfitted)
- Selected Features (89): R² = 0.672
- Optimal Features (56): R² = 0.756

**Result**: Feature selection crucial for performance

### 3. **Validation Strategy Development**
**Purpose**: Prevent data leakage
**Approaches Tested**:
- Naive Split: CV = 0.823 ± 0.045 (overfitted)
- Random Split: CV = 0.734 ± 0.067 (leakage)
- Temporal Split: CV = 0.684 ± 0.029 (realistic)

**Result**: Temporal validation essential

### 4. **Hyperparameter Optimization**
**Purpose**: Optimize model parameters
**Methods**:
- Grid Search: Systematic but slow
- Random Search: Faster, good coverage
- Bayesian Optimization: Most efficient

**Result**: Bayesian optimization adopted

## 📊 Experimental Results

### **Model Performance Evolution**
```json
{
  "baseline_linear": {
    "r2_score": 0.312,
    "cv_score": 0.289,
    "features": 12
  },
  "basic_rf": {
    "r2_score": 0.487,
    "cv_score": 0.456,
    "features": 34
  },
  "enhanced_rf": {
    "r2_score": 0.643,
    "cv_score": 0.612,
    "features": 67
  },
  "optimized_rf": {
    "r2_score": 0.756,
    "cv_score": 0.684,
    "features": 56
  }
}
```

### **Feature Importance Discovery**
```json
{
  "initial_features": {
    "count": 127,
    "top_feature": "team_events_2min",
    "importance": 0.156
  },
  "selected_features": {
    "count": 89,
    "top_feature": "activity_trend",
    "importance": 0.298
  },
  "optimized_features": {
    "count": 56,
    "top_feature": "activity_trend",
    "importance": 0.422
  }
}
```

### **Validation Experiments**
```json
{
  "validation_strategies": {
    "naive_split": {
      "cv_score": 0.823,
      "cv_std": 0.045,
      "issue": "Data leakage"
    },
    "random_split": {
      "cv_score": 0.734,
      "cv_std": 0.067,
      "issue": "Temporal leakage"
    },
    "temporal_split": {
      "cv_score": 0.684,
      "cv_std": 0.029,
      "issue": "None"
    }
  }
}
```

## 🔍 Experiment Insights

### **What Worked**
1. **Random Forest**: Consistently outperformed other algorithms
2. **Feature Selection**: Critical for preventing overfitting
3. **Temporal Validation**: Essential for realistic performance
4. **Bayesian Optimization**: Most efficient hyperparameter tuning
5. **Incremental Development**: Small improvements compound

### **What Didn't Work**
1. **Linear Models**: Too simple for complex patterns
2. **Deep Learning**: Overkill for this dataset size
3. **All Features**: Led to overfitting
4. **Naive Validation**: Overestimated performance
5. **Complex Ensembles**: Diminishing returns

## 🚀 Usage Examples

### **Load Experimental Model**
```python
import pickle
import json

# Load experiment results
with open('models/experiments/model_comparison.json', 'r') as f:
    comparison = json.load(f)

# Load specific experimental model
with open('models/experiments/baseline_model.pkl', 'rb') as f:
    baseline = pickle.load(f)
```

### **Reproduce Experiments**
```python
# Load experiment configuration
with open('models/experiments/hyperparameter_tuning/grid_search_results.json', 'r') as f:
    grid_results = json.load(f)

# Reproduce best parameters
best_params = grid_results['best_params']
print(f"Best parameters: {best_params}")
```

### **Compare Model Performance**
```python
import pandas as pd

# Load experiment log
exp_log = pd.read_csv('models/experiments/experiment_log.csv')

# Compare performance
performance_summary = exp_log.groupby('model_type')['r2_score'].describe()
print(performance_summary)
```

## 📈 Performance Tracking

### **Experiment Logging**
```python
# Example experiment log entry
{
  "experiment_id": "exp_045",
  "timestamp": "2024-01-15T10:30:00Z",
  "model_type": "RandomForest",
  "features": 67,
  "parameters": {
    "n_estimators": 100,
    "max_depth": 10
  },
  "performance": {
    "r2_score": 0.643,
    "cv_score": 0.612,
    "cv_std": 0.034
  }
}
```

### **Model Comparison Matrix**
```python
# Performance comparison across experiments
comparison_matrix = {
  "baseline": {"r2": 0.312, "cv": 0.289},
  "feature_eng": {"r2": 0.487, "cv": 0.456},
  "hybrid": {"r2": 0.643, "cv": 0.612},
  "optimized": {"r2": 0.756, "cv": 0.684}
}
```

## 🔬 Research Value

### **Historical Context**
- **Evolution Path**: Clear progression from baseline to optimized
- **Decision Points**: Key decisions and their rationale
- **Failed Experiments**: What didn't work and why
- **Lessons Learned**: Insights for future development

### **Reproducibility**
- **Fixed Seeds**: All experiments use consistent random seeds
- **Parameter Tracking**: Complete parameter documentation
- **Environment**: Documented development environment
- **Data Versioning**: Consistent dataset versions

## 🚨 Important Notes

1. **Experimental Nature**: These are research artifacts, not production
2. **Version Control**: Track all experimental changes
3. **Documentation**: Each experiment thoroughly documented
4. **Reproducibility**: Fixed seeds and documented parameters
5. **Learning Value**: Shows model development methodology

## 🔄 Evolution Path

```
🔬 EXPERIMENTS (This Folder)
    ↓
Hypothesis → Experiment → Validate → Iterate
    ↓
Best Approach Identified
    ↓
📊 PRODUCTION MODELS (models/final/)
```

## 📞 Support

- **Historical Context**: Git history shows evolution
- **Experiment Questions**: See experiment documentation
- **Reproduction**: Use fixed seeds and parameters
- **Learning**: Extract patterns for future projects

---

**🔬 Experimental Archive**: Documents the model development journey 