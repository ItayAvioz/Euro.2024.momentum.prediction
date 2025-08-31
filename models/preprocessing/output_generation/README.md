# Output Generation - Target Variable Creation

## 🎯 **Purpose**

This module creates the **target variable (y)** for momentum prediction by calculating **momentum change** over 3-minute windows.

## 📊 **Target Variable Definition**

### **Momentum Change Formula:**
```
y(t) = Momentum(t+3) - Momentum(t)
```

Where:
- **t** = Current 3-minute window  
- **t+3** = Next 3-minute window (3 minutes later)
- **Momentum Change** = How much momentum shifts in the next 3 minutes

### **Example:**
- **Window 20-22**: Spain momentum = 5.7, France momentum = 4.2
- **Window 23-25**: Spain momentum = 6.1, France momentum = 3.8
- **Target for 20-22**: Spain = +0.4, France = -0.4

## 📂 **Folder Structure**

```
output_generation/
├── README.md                           📝 This documentation
├── scripts/                           📁 Target generation scripts
│   ├── target_generator.py           🎯 Main target variable calculator
│   └── output_validator.py           ✅ Data validation script
├── configs/                           📁 Configuration files
│   └── target_config.yaml           ⚙️ Target generation parameters
├── tests/                             📁 Testing scripts
│   └── test_target_generation.py     🧪 Unit tests
└── momentum_targets_enhanced.csv      📊 Final output dataset
```

## 🔄 **Data Flow**

### **Input:**
- `../input_generation/momentum_windows_enhanced_v2.csv`
- Contains momentum values for all 3-minute windows

### **Processing:**
1. **Load Input Data** - All momentum windows
2. **Calculate Shifts** - Find t+3 windows for each t window  
3. **Compute Changes** - y = momentum(t+3) - momentum(t)
4. **Handle Edge Cases** - End-of-match windows without t+3
5. **Quality Validation** - Ensure data integrity

### **Output:**
- `momentum_targets_enhanced.csv` - Same structure as input + target columns

## 📋 **Output Schema**

The output CSV will contain all input columns PLUS:

```
New Target Columns:
├── team_home_momentum_change           🎯 Home team y-target
├── team_away_momentum_change           🎯 Away team y-target  
├── has_future_window                   ✅ Boolean: Can calculate target?
├── future_window_minutes               📅 t+3 window minutes
└── target_calculation_notes            📝 Any processing notes
```

## ⚙️ **Configuration Parameters**

- **Lag Minutes**: 3 (standard 3-minute prediction horizon)
- **Edge Case Handling**: Drop windows without future data
- **Validation Checks**: Completeness, continuity, outliers

## 🎯 **Key Features**

- **✅ Temporal Integrity** - Respects time-series nature of data
- **✅ Match Boundaries** - Handles end-of-match edge cases  
- **✅ Data Validation** - Comprehensive quality checks
- **✅ Consistent Format** - Same structure as input for seamless modeling
- **✅ Complete Analytics** - Preserves all input statistics

## 🚀 **Usage**

```bash
# Generate target variables
python scripts/target_generator.py

# Validate output
python scripts/output_validator.py

# Run tests
python tests/test_target_generation.py
```

---

**Next Phase:** Data Splitting (train/test with temporal validation)
