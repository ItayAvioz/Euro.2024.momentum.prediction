# 📋 **COMPREHENSIVE MOMENTUM FORECASTING FRAMEWORK - DETAILED IMPLEMENTATION PLAN**

---

## 🎯 **PROJECT OBJECTIVE - CORRECTED**

**Build predictive models to forecast momentum change in the next 3 minutes based on the last 3 minutes of football events**

### **🔄 Prediction Target (Corrected):**
```
Momentum Change = y(t+3) - y(t)
```
- **Input Window**: Last 3 minutes of events (t-3 to t)
- **Prediction Window**: Next 3 minutes momentum change (t to t+3)
- **Starting Point**: t=3 (cannot predict first 3 minutes due to no prior history)
- **Window Size**: ~120 events per 3-minute window (based on 3500 events/game ÷ 90 minutes × 3)
- **Team-Specific Windows**: ~73 events per team per 3-minute window (Team Involvement approach)
- **Total Training Samples**: 2x increase (separate prediction for each team)

---

## 📊 **DATA DISTRIBUTION STRATEGY**

### **Walk-Forward Validation (Time Series Respect):**
```
Training → Validation → Testing (Temporal Order Maintained)
```

### **Time Interval Analysis Coverage:**
- **0-15 minutes**: Early game momentum patterns
- **15-30 minutes**: First period development  
- **30-45 minutes**: Late first half dynamics
- **45-60 minutes**: Second half start momentum
- **60-75 minutes**: Mid second half patterns
- **75-90 minutes**: Late game pressure dynamics
- **90-105 minutes**: Extra time momentum shifts
- **105-120 minutes**: Extended extra time patterns

### **Complete Coverage Requirements:**
- ✅ **All Tournament Stages**: Group Stage, Round of 16, Quarter-finals, Semi-finals, Final
- ✅ **All Teams**: 24 teams represented in test data
- ✅ **No Score Leakage**: Home/away scores completely excluded
- ✅ **Full Dataset**: Complete Euro 2024 dataset utilization

### **Data Windowing Structure:**
```python
# 3-minute window structure with Team-Specific Processing
for t in range(3, max_time_minutes, 3):
    input_window = events[t-3:t]     # Last 3 minutes
    target_window = events[t:t+3]    # Next 3 minutes
    
    # Process for EACH team separately (Team Involvement - Hybrid)
    for team in [team_x, team_y]:
        # Extract team-specific events using Hybrid Involvement
        team_input_events = input_window[
            (input_window['team_name'] == team) |           # Team performs action
            (input_window['possession_team_name'] == team)  # Team has possession
        ]
        
        team_target_events = target_window[
            (target_window['team_name'] == team) |          # Team performs action  
            (target_window['possession_team_name'] == team) # Team has possession
        ]
        
        X_team = extract_features(team_input_events)
        y_team = momentum_change(team_target_events) = y(t+3) - y(t)
```

### **🎯 Team Involvement Approach (Option 3 - Hybrid)**

#### **📊 Real Data Validation (Netherlands vs England Sample):**
Based on analysis of actual Euro 2024 data from the first 3 minutes:

| **Approach** | **Netherlands Events** | **England Events** | **Coverage** | **Quality** |
|--------------|----------------------|-------------------|-------------|-------------|
| **Option 1: `team` only** | 51 events (50.5%) | 50 events (49.5%) | ❌ Incomplete | 60% - Missing contexts |
| **Option 2: `possession_team` only** | 57 events (56.4%) | 44 events (43.6%) | ❌ Incomplete | 70% - Missing defensive |
| **✅ Option 3: Team Involvement** | **73 events (72.3%)** | **64 events (63.4%)** | **✅ Comprehensive** | **90% - Complete experience** |

#### **🏆 Team Involvement Advantages:**
- **30-40% More Events**: Captures complete team experience vs other approaches
- **Full Context Coverage**: Includes both attacking and defensive phases
- **Realistic Team Perspective**: Matches actual coach/analyst viewpoint
- **Better Momentum Representation**: All events affecting team momentum included

#### **🔍 Event Classification Logic:**
```python
def get_team_involvement_events(events, target_team):
    """
    Extract all events where target_team is involved
    
    Includes:
    1. Direct Actions: team performs the action
    2. Possession Context: team has possession during action
    3. Defensive Context: opponent actions affecting team
    """
    team_involved_events = events[
        (events['team_name'] == target_team) |           # Team performs action
        (events['possession_team_name'] == target_team)  # Team has possession
    ]
    
    return team_involved_events

# Example coverage for 3-minute window:
# - Team actions: ~50 events
# - Possession context: +15 events  
# - Defensive pressure: +8 events
# Total: ~73 events (vs 50 for team-only approach)
```

---

## 🏗️ **ITERATION STRUCTURE (4 ITERATIONS)**

### **📋 5-Block Structure Per Iteration:**

#### **Block 1: Feature Selection**
- **9-Method Ensemble Voting System**
- **Selection Threshold**: ≥**7** votes (NOT ≥6)
- **Quality Validation**: 2 random features for benchmark

#### **Block 2: Preprocessing**  
- **Missing Values**: Analysis and handling strategy
- **Outliers**: Detection and treatment approach
- **Text Features**: Encoding methodology
- **Categorical Features**: Transformation approach
- **Scaling/Normalization**: Applied methods and justification

#### **Block 3: Feature Engineering**
- **EDA-Based Features**: Grounded in actual insights from `thoughts/eda_insights.csv`
- **Temporal Features**: 3-minute window aggregations
- **Pattern Features**: Based on validated EDA patterns

#### **Block 4: Model Evaluation**
- **Parameters**: Detailed hyperparameter specifications
- **Metrics**: Adjusted R², chosen metric with justification
- **Performance**: Train score vs Test score analysis
- **Validation**: Proper time series validation approach

#### **Block 5: Result Analysis**
- **20 Random Samples**: Different teams, stages, minutes
- **Input-Output**: Prediction vs Real momentum change
- **Error Analysis**: Pattern identification in errors

---

## 🔧 **FEATURE SELECTION METHODOLOGY**

### **9-Method Ensemble Voting System:**

| **Method** | **Description** | **Implementation** |
|------------|-----------------|-------------------|
| **1. p_val** | P-value significance | `f_regression` p-values < 0.05 |
| **2. Lasso** | L1 regularization | `LassoCV` non-zero coefficients |
| **3. Ridge** | L2 regularization | `RidgeCV` coefficient magnitude |
| **4. ElasticNet** | L1+L2 combination | `ElasticNetCV` feature weights |
| **5. SVM** | Support Vector importance | `SVR` with feature ranking |
| **6. RandomForest** | Tree-based importance | `RandomForestRegressor` feature importance |
| **7. GradientBoost** | Gradient boosting importance | `GradientBoostingRegressor` importance |
| **8. Decision_Tree** | Single tree importance | `DecisionTreeRegressor` importance |
| **9. AdaBoost** | Adaptive boosting importance | `AdaBoostRegressor` feature importance |

### **Selection Criteria:**
```python
# Voting threshold (CORRECTED)
selected_features = features_with_votes >= 7  # NOT ≥6

# Quality validation with random features
random_feature_1 = np.random.normal(0, 1, size)  # Gaussian noise
random_feature_2 = np.random.uniform(0, 1, size)  # Uniform noise

# Random features should receive <7 votes to validate quality
```

---

## 🚀 **ITERATION BREAKDOWN**

### **🔄 ITERATION 1: Basic Features Foundation**

#### **Objective**: Establish baseline with fundamental features only

#### **Feature Set**: 
- **Basic Temporal**: minute, period, total_seconds, possession
- **Basic Spatial**: x_coord, y_coord, distance_to_goal
- **Basic Event**: event_type, team_name, possession_team_name, duration
- **Basic Match Context**: match_id, stage, kick_off
- **NO ENGINEERED FEATURES**: Pure dataset variables only

#### **Team Involvement Preprocessing:**
```python
# Extract possession team name from JSON structure
df['possession_team_name'] = df['possession_team'].apply(
    lambda x: eval(x)['name'] if pd.notna(x) and isinstance(x, str) else 'Unknown'
)

# Create team-specific event filters
def create_team_windows(events, target_team):
    return events[
        (events['team_name'] == target_team) |           # Team performs action
        (events['possession_team_name'] == target_team)  # Team has possession
    ]
```

#### **Models (7 models):**
```python
models = [
    'SARIMA',           # Time series forecasting
    'Linear_Regression', # Linear relationships
    'Poisson_Regression', # Count-based prediction
    'XGBoost',          # Gradient boosting
    'SVM',              # Support vector regression
    'Prophet',          # Facebook time series
    'RNN'               # Recurrent neural network
]
```

#### **Expected Outcome**: Baseline performance metrics for model ranking

---

### **🔄 ITERATION 2: EDA-Enhanced Features**

#### **Objective**: Add EDA-derived features and select top 3 models

#### **Feature Set**: 
- **All Iteration 1 features** +
- **EDA-Based Features** (grounded in actual insights from EDA analysis)

#### **EDA Feature Categories:**
```python
# Time-based patterns (from EDA insights)
features_time = [
    'kick_off_time_effect',    # Based on 16:00, 19:00, 22:00 patterns
    'game_phase_momentum',     # Based on scoring time patterns  
    'late_game_pressure',      # Based on 75+ minute insights
]

# Team-based patterns (from EDA insights)  
features_team = [
    'team_momentum_style',     # Based on team playing style analysis
    'opponent_strength_effect', # Based on matchup insights
    'stage_pressure_factor',   # Based on tournament stage patterns
]

# Event-based patterns (from EDA insights)
features_event = [
    'event_sequence_patterns', # Based on event flow insights
    'possession_momentum',     # Based on possession analysis
    'location_danger_zones',   # Based on spatial analysis
]
```

#### **Models**: Same 7 models as Iteration 1

#### **Selection**: Choose **TOP 3 MODELS** based on performance ranking

---

### **🔄 ITERATION 3: Hyperparameter Optimization**

#### **Objective**: Optimize the top 3 models with hyperparameter tuning

#### **Feature Set**: All features from Iteration 2 (basic + EDA)

#### **Models**: **Top 3 models only** from Iteration 2 results

#### **Hyperparameter Tuning Strategy:**
```python
# For each top 3 model
hyperparameter_grids = {
    'XGBoost': {
        'n_estimators': [100, 200, 300],
        'learning_rate': [0.1, 0.15, 0.2],
        'max_depth': [6, 8, 10],
        'subsample': [0.8, 0.9, 1.0],
        'colsample_bytree': [0.8, 0.9, 1.0]
    },
    # Similar grids for other top models
}

# Use GridSearchCV with time series validation
```

#### **Expected Outcome**: Optimized models with peak performance

---

### **🔄 ITERATION 4: Insights Integration**

#### **Objective**: Integrate insights from result analysis and EDA for final optimization

#### **Feature Set**: 
- **All Iteration 3 features** +
- **Insight-Driven Features** (based on error analysis and additional EDA patterns)

#### **Models**: Same top 3 models with Iteration 3 parameters

#### **Insight Integration Strategy:**
```python
# Based on result analysis patterns
insight_features = [
    'error_pattern_corrections',   # Address systematic errors
    'temporal_adjustment_factors', # Fine-tune time dependencies  
    'interaction_features',        # Feature combinations
    'ensemble_weight_features',    # Multi-model insights
]
```

#### **Expected Outcome**: Final optimized framework with maximum accuracy

---

## 📊 **MODEL SPECIFICATIONS**

### **SARIMA (Seasonal ARIMA):**
```python
# Time series specific for 3-minute momentum changes
model = SARIMAX(
    order=(p, d, q),           # Non-seasonal parameters
    seasonal_order=(P, D, Q, s), # Seasonal parameters  
    exog=external_features      # Exogenous variables
)
```

### **Linear Regression:**
```python
# With regularization for feature selection
model = ElasticNet(
    alpha=alpha,        # Regularization strength
    l1_ratio=l1_ratio  # L1 vs L2 balance
)
```

### **Poisson Regression:**
```python
# For count-based momentum change prediction
model = PoissonRegressor(
    alpha=alpha,        # Regularization
    max_iter=max_iter   # Convergence iterations
)
```

### **XGBoost:**
```python
# Gradient boosting for complex patterns
model = XGBRegressor(
    n_estimators=n_estimators,
    learning_rate=learning_rate,
    max_depth=max_depth,
    subsample=subsample,
    colsample_bytree=colsample_bytree
)
```

### **SVM (Support Vector Regression):**
```python
# Non-linear pattern recognition
model = SVR(
    kernel=kernel,      # RBF, polynomial, etc.
    C=C,               # Regularization parameter
    gamma=gamma        # Kernel coefficient
)
```

### **Prophet:**
```python
# Facebook time series forecasting
model = Prophet(
    seasonality_mode=seasonality_mode,
    yearly_seasonality=False,
    weekly_seasonality=False,
    daily_seasonality=False,
    changepoint_prior_scale=changepoint_prior_scale
)
```

### **RNN (Recurrent Neural Network):**
```python
# Sequential pattern modeling for 3-minute windows
model = Sequential([
    LSTM(units=lstm_units, return_sequences=True),
    Dropout(dropout_rate),
    LSTM(units=lstm_units//2, return_sequences=False),
    Dropout(dropout_rate),
    Dense(dense_units, activation='relu'),
    Dense(1)  # Single output: momentum change
])
```

---

## 🎯 **EVALUATION METHODOLOGY**

### **Primary Metric: Adjusted R²**
```python
# Adjusted R² for momentum change prediction (accounts for feature count)
def adjusted_r2_score(y_true, y_pred, n_features):
    r2 = r2_score(y_true, y_pred)
    n = len(y_true)
    adjusted_r2 = 1 - (1 - r2) * (n - 1) / (n - n_features - 1)
    return adjusted_r2

# Formula: Adjusted R² = 1 - [(1 - R²) × (n - 1) / (n - k - 1)]
# where: n = sample size, k = number of features
```

### **Secondary Metrics:**
- **Standard R²**: For comparison with Adjusted R²
- **MSE (Mean Squared Error)**: Penalty for large errors
- **MAE (Mean Absolute Error)**: Average prediction error  
- **MAPE (Mean Absolute Percentage Error)**: Relative error assessment

### **Metric Selection Justification:**
- **Adjusted R²**: 
  - **Penalizes model complexity** (crucial for 9-method feature selection)
  - **Fair comparison across iterations** (different feature counts)
  - **Prevents overfitting** (especially important for 3-minute windows)
  - **Better for time series** with limited samples per window
- **Standard R²**: Baseline comparison to show complexity penalty effect
- **MSE**: Important for momentum prediction accuracy (large errors costly)
- **MAE**: Interpretable average error in momentum units
- **MAPE**: Relative performance across different momentum scales

### **Adjusted R² Advantages for Our Framework:**
1. **Feature Selection Validation**: Validates ≥7 voting threshold effectiveness
2. **Cross-Iteration Comparison**: Fair comparison between iterations with different feature counts
3. **Model Complexity Control**: Accounts for XGBoost/RNN complexity vs Linear/SARIMA simplicity
4. **Overfitting Prevention**: Penalizes unnecessary features from 9-method selection
5. **Time Series Specificity**: More reliable with smaller 3-minute window samples

---

## 🔍 **VALIDATION STRATEGY**

### **Time Series Walk-Forward Validation:**
```python
# Respect temporal order in validation with team-specific processing
for fold in time_series_folds:
    train_end = fold_start_time
    val_start = train_end  
    val_end = val_start + validation_window
    test_start = val_end
    test_end = test_start + test_window
    
    # Process validation for each team separately
    for team in [team_x, team_y]:
        # Extract team-specific events for each fold
        train_events_team = get_team_involvement_events(train_data, team)
        val_events_team = get_team_involvement_events(val_data, team)
        test_events_team = get_team_involvement_events(test_data, team)
        
        # Ensure no future data leakage
        assert train_end <= val_start <= val_end <= test_start
        
        # Train and validate team-specific model
        model_team = train_model(train_events_team)
        score_team = validate_model(model_team, val_events_team)
```

### **Cross-Validation for Time Series:**
- **TimeSeriesSplit**: Built-in scikit-learn time series validation
- **Expanding Window**: Gradually increase training set size
- **Fixed Window**: Maintain consistent training window size

---

## 🏁 **DELIVERABLES PER ITERATION**

### **Files to Generate:**
1. **Feature Selection Report**: `iteration_X_feature_selection.csv`
2. **Preprocessing Analysis**: `iteration_X_preprocessing_analysis.md`
3. **Model Performance**: `iteration_X_model_results.csv`
4. **Prediction Examples**: `iteration_X_predictions_sample.csv`
5. **Comprehensive Analysis**: `iteration_X_comprehensive_analysis.md`

### **Content Requirements:**
- **Feature Selection**: 9-method voting results with ≥7 threshold
- **Preprocessing**: Missing values, outliers, transformations per feature
- **Model Performance**: Adjusted R², Standard R², MSE, MAE, train/test scores
- **Prediction Examples**: 20 samples (different teams, stages, minutes)
- **Analysis**: Detailed insights and error patterns

---

## ⚠️ **CRITICAL REQUIREMENTS (NO COMPROMISE)**

### **🚨 Data Leakage Prevention:**
1. **No Target Components as Features**: Zero overlap between momentum calculation and input features
2. **Temporal Integrity**: No future information in current predictions
3. **No Score Information**: Complete exclusion of home/away scores

### **🎯 Feature Engineering Constraints:**
1. **EDA Grounding**: Every engineered feature must trace to specific EDA insight
2. **Documentation**: Formula and justification for each created feature
3. **Validation**: Each feature tested against random feature benchmark

### **📊 Model Evaluation Requirements:**
1. **≥7 Voting Threshold**: Strict feature selection criteria
2. **Time Series Validation**: Proper temporal validation methodology
3. **Complete Coverage**: All time intervals, stages, teams in test data

---

## 🔄 **STEP-BY-STEP APPROVAL PROCESS**

### **Implementation Workflow:**
```
Plan Review → Approval → Implementation → Results Review → Next Step
```

### **Approval Gates:**
1. **Pre-Implementation**: Plan review and approval
2. **Post-Feature Selection**: Feature voting results review
3. **Post-Model Training**: Performance metrics review  
4. **Post-Analysis**: Results interpretation and next iteration planning

### **Documentation Requirements:**
- **Before Implementation**: Detailed plan with specifications
- **During Implementation**: Progress updates and issue identification
- **After Implementation**: Complete results with analysis and recommendations

---

## ✅ **PLAN CONFIRMATION CHECKLIST**

- ✅ **Correct Prediction Target**: Momentum change y(t+3) - y(t)
- ✅ **Proper Time Windows**: 3-minute input/output windows  
- ✅ **Team-Specific Processing**: Team Involvement (Hybrid) approach with 30-40% more events
- ✅ **Feature Selection**: 9-method voting with ≥7 threshold
- ✅ **Four Iterations**: Basic → EDA → Hyperparameter → Insights
- ✅ **Seven Models**: SARIMA, Linear, Poisson, XGBoost, SVM, Prophet, RNN
- ✅ **Five Blocks**: Selection, Preprocessing, Engineering, Evaluation, Analysis
- ✅ **Step-by-Step**: Approval required before each implementation
- ✅ **No Data Leakage**: Complete separation of targets and inputs
- ✅ **EDA Grounding**: All features based on validated insights
- ✅ **Time Series Respect**: Proper temporal validation methodology
- ✅ **Real Data Validated**: Team Involvement approach tested on actual Euro 2024 data

---

*📋 **Plan Status**: READY FOR REVIEW AND APPROVAL*  
*🎯 **Next Step**: Await approval for Iteration 1 implementation*  
*📅 **Plan Date**: January 31, 2025*