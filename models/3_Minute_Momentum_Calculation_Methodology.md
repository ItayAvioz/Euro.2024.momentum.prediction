# 📊 **3-MINUTE MOMENTUM CALCULATION METHODOLOGY**

---

## 🎯 **OVERVIEW**

This document defines the **complete methodology** for calculating momentum in 3-minute windows and determining momentum change for our forecasting framework.

### **🔄 Core Objective:**
Predict **momentum change in the next 3 minutes** based on **last 3 minutes** using a hybrid weighted average approach.

---

## 📋 **PREDICTION TARGET DEFINITION**

### **🎯 Mathematical Formula:**
```
Momentum Change = y(t+3) - y(t)

Where:
- y(t) = Weighted average momentum of input window (t-3 to t)
- y(t+3) = Weighted average momentum of target window (t to t+3)
- t = Current time point (starting from t=3 minutes)
```

### **📊 Interpretation:**
- **Positive value**: Momentum **increases** in next 3 minutes
- **Negative value**: Momentum **decreases** in next 3 minutes  
- **Zero value**: Momentum remains **stable** in next 3 minutes

---

## 🔧 **HYBRID WEIGHTING METHODOLOGY**

### **🎯 Core Principle:**
**Every event matters substantially, with recent events getting graduated additional importance**

### **🧮 Weight Calculation Formula:**
```python
def calculate_hybrid_weight(event_position, total_events):
    """
    Calculate hybrid weight for each event in 3-minute window
    
    Args:
        event_position: Position of event in window (0 = oldest, n-1 = newest)
        total_events: Total number of events in window (~120 events)
    
    Returns:
        weight: Value between 0.7 (oldest) and 1.0 (newest)
    """
    # Recency ratio: 0.0 (oldest) to 1.0 (newest)
    recency_ratio = event_position / (total_events - 1)
    
    # Base weight: all events have substantial importance
    base_weight = 0.7
    
    # Recency bonus: graduated additional weight for recent events
    recency_bonus = 0.3 * recency_ratio
    
    # Total weight: ranges from 0.7 to 1.0
    total_weight = base_weight + recency_bonus
    
    return total_weight
```

### **📈 Weight Distribution Characteristics:**
- **Oldest events**: 70% importance (substantial base weight)
- **Middle events**: 70-85% importance (gradual increase)
- **Newest events**: 85-100% importance (maximum weight)
- **Recent advantage**: 43% more weight than oldest (1.0 vs 0.7)

---

## 📊 **3-MINUTE WINDOW MOMENTUM CALCULATION**

### **🔄 Step-by-Step Process:**

#### **Step 1: Event Collection**
```python
def collect_window_events(start_time, end_time):
    """
    Collect all events within 3-minute window
    Expected: ~120 events per 3-minute window (~40 events/minute)
    """
    window_events = events_in_time_range(start_time, end_time)
    return window_events
```

#### **Step 2: Weight Assignment**
```python
def assign_hybrid_weights(events_window):
    """
    Assign hybrid weights to all events in window
    """
    n = len(events_window)
    weights = []
    
    for i, event in enumerate(events_window):
        weight = calculate_hybrid_weight(i, n)
        weights.append(weight)
    
    return weights
```

#### **Step 3: Weighted Average Calculation**
```python
def calculate_weighted_momentum_3min(events_window):
    """
    Calculate weighted average momentum for 3-minute window
    """
    # Extract momentum values
    momentum_values = [event.momentum for event in events_window]
    
    # Calculate hybrid weights
    weights = assign_hybrid_weights(events_window)
    
    # Weighted average calculation
    numerator = sum(momentum * weight for momentum, weight in zip(momentum_values, weights))
    denominator = sum(weights)
    
    weighted_momentum = numerator / denominator
    
    return weighted_momentum
```

---

## 🎯 **PRACTICAL EXAMPLE**

### **📋 Sample 3-Minute Window (7 Representative Events):**

| **Event #** | **Time** | **Type** | **Momentum** | **Position** | **Recency Ratio** | **Weight** | **Contribution** |
|-------------|----------|----------|--------------|--------------|-------------------|------------|------------------|
| 1 | t-3 min | Pass | 5.0 | 0 | 0.000 | 0.70 | 3.50 |
| 20 | t-2.5 min | Pass | 5.5 | 19 | 0.158 | 0.747 | 4.11 |
| 40 | t-2 min | Shot | 7.0 | 39 | 0.325 | 0.798 | 5.58 |
| 60 | t-1.5 min | Pass | 6.5 | 59 | 0.492 | 0.848 | 5.51 |
| 80 | t-1 min | Pass | 6.0 | 79 | 0.658 | 0.897 | 5.38 |
| 100 | t-0.5 min | Shot | 8.0 | 99 | 0.825 | 0.948 | 7.58 |
| 120 | t (now) | Pass | 7.5 | 119 | 1.000 | 1.000 | 7.50 |

### **📊 Calculation:**
```python
# Weighted sum calculation
numerator = 3.50 + 4.11 + 5.58 + 5.51 + 5.38 + 7.58 + 7.50 = 39.16
denominator = 0.70 + 0.747 + 0.798 + 0.848 + 0.897 + 0.948 + 1.000 = 5.939

# Weighted average momentum
y(t) = 39.16 / 5.939 = 6.59
```

**Interpretation**: Current 3-minute window has weighted average momentum of **6.59**

---

## 🔄 **MOMENTUM CHANGE CALCULATION**

### **📊 Complete Process:**

#### **Step 1: Input Window Momentum (t-3 to t)**
```python
# Collect events from input window
input_events = collect_window_events(t-3, t)

# Calculate weighted momentum for input window  
y_t = calculate_weighted_momentum_3min(input_events)
```

#### **Step 2: Target Window Momentum (t to t+3)**
```python
# Collect events from target window (future data)
target_events = collect_window_events(t, t+3)

# Calculate weighted momentum for target window
y_t_plus_3 = calculate_weighted_momentum_3min(target_events)
```

#### **Step 3: Momentum Change Calculation**
```python
# Calculate momentum change (our prediction target)
momentum_change = y_t_plus_3 - y_t
```

### **🎯 Example Scenario:**

#### **Input Window (t-3 to t):**
```python
# 120 events with various momentum values
# Weighted calculation result: y(t) = 6.59
```

#### **Target Window (t to t+3):**
```python
# Next 120 events in future 3 minutes
# Example events: [Goal (10.0), Passes (7.0), Shot (8.5), ...]
# Weighted calculation result: y(t+3) = 7.42
```

#### **Momentum Change:**
```python
momentum_change = 7.42 - 6.59 = +0.83
```

**Interpretation**: "Momentum will **increase by 0.83 points** in the next 3 minutes"

---

## 📊 **DATA WINDOWING STRUCTURE**

### **🔄 Sliding Window Implementation:**
```python
def generate_momentum_change_dataset():
    """
    Generate complete dataset with 3-minute sliding windows
    """
    dataset = []
    
    # Start from t=3 (need 3 minutes of history)
    # Step by 3 minutes (non-overlapping windows)
    for t in range(3, max_game_time, 3):
        
        # Input window: last 3 minutes
        input_events = collect_window_events(t-3, t)
        input_momentum = calculate_weighted_momentum_3min(input_events)
        
        # Target window: next 3 minutes
        target_events = collect_window_events(t, t+3)
        target_momentum = calculate_weighted_momentum_3min(target_events)
        
        # Features extracted from input window only
        features = extract_features_from_window(input_events)
        
        # Prediction target
        momentum_change = target_momentum - input_momentum
        
        # Add to dataset
        dataset.append({
            'features': features,
            'target': momentum_change,
            'input_momentum': input_momentum,
            'target_momentum': target_momentum,
            'time_window': f"{t-3}-{t} → {t}-{t+3}"
        })
    
    return dataset
```

### **📋 Timeline Example:**
```
Game Timeline: 0 ——— 3 ——— 6 ——— 9 ——— 12 ——— 15 ——— ... ——— 90 minutes

Window 1: [0-3] → [3-6]   (predict change from minute 3-6 based on 0-3)
Window 2: [3-6] → [6-9]   (predict change from minute 6-9 based on 3-6)  
Window 3: [6-9] → [9-12]  (predict change from minute 9-12 based on 6-9)
...
Window N: [87-90] → [90-93] (if game goes to extra time)
```

---

## ✅ **METHODOLOGY ADVANTAGES**

### **🎯 Hybrid Weighting Benefits:**
1. **Full Context Preservation**: All 120 events in window contribute meaningfully (≥70% weight)
2. **Appropriate Recency Bias**: Recent events get 43% more importance without dominating
3. **Smooth Progression**: Linear weight increase prevents sudden jumps
4. **Football Logic**: Matches how momentum actually builds over 3 minutes
5. **Robust Calculation**: Works regardless of exact event count variations

### **📊 Momentum Change Benefits:**
1. **Clear Interpretation**: Direct momentum increase/decrease prediction
2. **Balanced Scale**: Typical values range from -3 to +3 (manageable for ML models)
3. **Time Series Appropriate**: Proper temporal separation of input/target
4. **No Data Leakage**: Complete separation between features and target calculation

### **🔄 Implementation Benefits:**
1. **Computationally Efficient**: Simple weighted average calculation
2. **Scalable**: Works with any number of events (80-150 per window)
3. **Tunable**: Base weight and recency range can be optimized
4. **Interpretable**: Clear mathematical foundation for all calculations

---

## 🔧 **IMPLEMENTATION PARAMETERS**

### **📊 Key Parameters:**
```python
# Weighting parameters
BASE_WEIGHT = 0.7          # Minimum importance for oldest events
RECENCY_RANGE = 0.3        # Additional weight range (0.0 to 0.3)
WINDOW_SIZE = 3            # Minutes per window
STEP_SIZE = 3              # Minutes between windows (non-overlapping)

# Expected data characteristics  
EVENTS_PER_MINUTE = 40     # Approximate event density
EVENTS_PER_WINDOW = 120    # Expected events in 3-minute window

# Momentum scale
MOMENTUM_MIN = 0           # Minimum momentum value
MOMENTUM_MAX = 10          # Maximum momentum value
```

### **🎯 Quality Validation:**
```python
# Validate weighted momentum calculations
assert 0 <= weighted_momentum <= 10, "Momentum must be within valid range"
assert -10 <= momentum_change <= 10, "Change must be within realistic bounds"
assert len(weights) == len(events), "One weight per event required"
assert all(0.7 <= w <= 1.0 for w in weights), "Weights must be in hybrid range"
```

---

## 🎯 **NEXT STEPS**

### **📋 Implementation Checklist:**
1. ✅ **Methodology defined**: Hybrid weighting approach confirmed
2. ⏳ **Code implementation**: Develop windowing and calculation functions
3. ⏳ **Data preprocessing**: Apply methodology to Euro 2024 dataset
4. ⏳ **Feature extraction**: Extract features from input windows only
5. ⏳ **Model training**: Train 7 models on momentum change prediction
6. ⏳ **Validation**: Evaluate with Adjusted R² and time series validation

### **🔄 Ready for Iteration 1:**
- **Feature Selection**: 9-method voting with ≥7 threshold
- **Basic Features**: Temporal, spatial, event-based from input windows
- **7 Models**: SARIMA, Linear, Poisson, XGBoost, SVM, Prophet, RNN
- **Evaluation**: Adjusted R², MSE, MAE with proper time series validation

---

*📊 **Document Status**: Complete methodology definition*  
*🎯 **Next Phase**: Iteration 1 implementation*  
*📅 **Date**: January 31, 2025*