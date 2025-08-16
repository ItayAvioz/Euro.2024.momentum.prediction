# 📊 **BASIC FEATURES PREPROCESSING TABLE AND SUMMARY**

---

## 🎯 **OVERVIEW**

This document provides a comprehensive preprocessing specification for all basic features in the Euro 2024 dataset for **Iteration 1** of the momentum forecasting framework. All features listed are available directly from the dataset without any engineering.

---

## 📋 **BASIC FEATURES PREPROCESSING TABLE**

| **Feature Name** | **Data Type** | **Missing %** | **Preprocessing Needed?** | **Preprocessing Method** | **Rationale** |
|------------------|---------------|---------------|----------------------------|---------------------------|---------------|
| **SEQUENTIAL FEATURES** | | | | | |
| `index` | Integer | 0.00% | **No** | None | Sequential order (1-5190), already numeric |
| `related_events` | JSON Array | 3.57% | **Yes** | Count + Fill 0 | Count related events, missing = 0 connections |
| **TEMPORAL FEATURES** | | | | | |
| `period` | Integer | 0.00% | **No** | None | Already numeric (1-5), proper range |
| `minute` | Integer | 0.00% | **No** | None | Already numeric (0-127), proper range |
| `second` | Integer | 0.00% | **No** | None | Already numeric (0-59), proper range |
| `timestamp` | Timestamp | 0.00% | **Yes** | Convert to total_seconds | Convert HH:MM:SS.mmm to numeric seconds |
| `possession` | Integer | 0.00% | **Yes** | StandardScaler | Normalize possession sequences (1-220) |
| `duration` | Float | 27.48% | **Yes** | Fill with 0.0 | Missing duration = instantaneous event |
| **SPATIAL FEATURES** | | | | | |
| `location` | Coordinate | 0.89% | **Yes** | Extract x_coord, y_coord | Extract [x,y] from JSON array |
| `x_coord` | Float | 0.89% | **Yes** | Fill 60.0 + StandardScaler | Pitch center X + normalize (0-120) |
| `y_coord` | Float | 0.89% | **Yes** | Fill 40.0 + StandardScaler | Pitch center Y + normalize (0-80) |
| `distance_to_goal` | Float | 0.89% | **Yes** | Calculate + StandardScaler | sqrt((120-x)² + (40-y)²) + normalize |
| **EVENT TYPE FEATURES** | | | | | |
| `event_type` | String | 0.00% | **Yes** | Label Encoding | Convert 33 event categories to numeric |
| `play_pattern` | JSON Object | 0.00% | **Yes** | Extract + Label Encoding | Extract pattern name, encode 9 categories |
| **TEAM FEATURES** | | | | | |
| `team_name` | String | 0.00% | **Yes** | Label Encoding | Convert 24 teams to numeric |
| `team_id` | UUID/ID | 0.00% | **Yes** | Label Encoding | Convert team IDs to numeric |
| `team_x` | String | 0.00% | **Yes** | Label Encoding | Convert team_x (formerly home) to numeric |
| `team_y` | String | 0.00% | **Yes** | Label Encoding | Convert team_y (formerly away) to numeric |
| `possession_team` | JSON Object | 0.00% | **Yes** | Extract + Label Encoding | Extract possession team name, encode |
| **PLAYER FEATURES** | | | | | |
| `player_name` | String | 0.46% | **Yes** | Label Encoding + Fill 'Unknown' | Convert 496 players to numeric |
| `player_id` | UUID/ID | 0.46% | **Yes** | Label Encoding + Fill 0 | Convert player IDs to numeric |
| `position` | JSON Object | 0.46% | **Yes** | Extract + Label Encoding + Fill 'Unknown' | Extract position name, encode 24 positions |
| **MATCH CONTEXT FEATURES** | | | | | |
| `match_date` | String | 0.00% | **Yes** | Extract day_of_week + Label Encoding | Extract weekday for temporal patterns |
| `kick_off` | String | 0.00% | **Yes** | **Ordinal Categorical Encoding** | **16:00→0, 19:00→1, 22:00→2** |
| `stage` | String | 0.00% | **Yes** | Label Encoding | Convert 5 tournament stages to numeric |
| `match_week` | Integer | 0.00% | **No** | None | Already numeric (1-7), proper range |
| `match_id` | UUID/ID | 0.00% | **Yes** | Label Encoding | Convert match UUIDs to numeric |
| **TACTICAL FEATURES** | | | | | |
| `tactics` | JSON Object | 99.85% | **Yes** | Extract formation + Fill 'Unknown' | Extract formation number, missing = 'Unknown' |
| **DERIVED SPATIAL FEATURES** | | | | | |
| `field_position` | String | 0.89% | **Yes** | Categorize + Label Encoding | Defensive/Middle/Attacking third based on x_coord |
| `attacking_third` | Boolean | 0.89% | **Yes** | Binary encoding | x_coord >= 80 (attacking third) |
| `defensive_third` | Boolean | 0.89% | **Yes** | Binary encoding | x_coord <= 40 (defensive third) |
| `central_zone` | Boolean | 0.89% | **Yes** | Binary encoding | 26.7 <= y_coord <= 53.3 (central zone) |
| **PRESSURE/CONTEXT FEATURES** | | | | | |
| `under_pressure` | Boolean | 82.66% | **Yes** | Fill with False | Missing pressure = no pressure |
| `counterpress` | Boolean | 97.60% | **Yes** | Fill with False | Missing counterpress = no counterpress |
| `off_camera` | Boolean | 98.91% | **Yes** | Fill with False | Missing off_camera = on camera |
| **EVENT-SPECIFIC FEATURES** | | | | | |
| `pass_length` | Float | 71.31% | **Yes** | Extract + Fill 0 + StandardScaler | From pass.length, non-pass events = 0 |
| `pass_angle` | Float | 71.31% | **Yes** | Extract + Fill 0 | From pass.angle, non-pass events = 0 |
| `carry_distance` | Float | 76.50% | **Yes** | Calculate + Fill 0 + StandardScaler | From carry.end_location, non-carry = 0 |
| `shot_xg` | Float | 99.29% | **Yes** | Extract + Fill 0 + MinMaxScaler | From shot.statsbomb_xg, non-shot = 0 |

---

## 🔧 **PREPROCESSING METHODOLOGY**

### **📊 1. Missing Value Strategies**

#### **Sequential Features:**
```python
# Index: No preprocessing needed - already numeric
df['index'] = df['index']  # Keep as-is (1 to 5190)

# Related events: Count number of related events
def process_related_events(related_events_json):
    """Count number of related events"""
    if pd.isna(related_events_json):
        return 0
    try:
        events_list = json.loads(related_events_json) if isinstance(related_events_json, str) else related_events_json
        return len(events_list) if events_list else 0
    except:
        return 0

df['related_events_count'] = df['related_events'].apply(process_related_events)
```

#### **Temporal Features:**
```python
# Duration: Missing = instantaneous event
df['duration'] = df['duration'].fillna(0.0)

# Timestamp: Convert to total seconds from match start
def convert_timestamp_to_seconds(timestamp_str):
    time_parts = timestamp_str.split(':')
    hours = int(time_parts[0])
    minutes = int(time_parts[1])
    seconds = float(time_parts[2])
    return hours * 3600 + minutes * 60 + seconds

df['total_seconds'] = df['timestamp'].apply(convert_timestamp_to_seconds)
```

#### **Spatial Features:**
```python
# Extract coordinates from location JSON
def extract_coordinates(location):
    if pd.isna(location):
        return 60.0, 40.0  # Pitch center
    try:
        coords = json.loads(location) if isinstance(location, str) else location
        return coords[0], coords[1]
    except:
        return 60.0, 40.0

df[['x_coord', 'y_coord']] = df['location'].apply(lambda x: pd.Series(extract_coordinates(x)))

# Validate coordinate boundaries
df['x_coord'] = np.clip(df['x_coord'], 0, 120)
df['y_coord'] = np.clip(df['y_coord'], 0, 80)

# Calculate distance to goal (right goal at [120, 40])
df['distance_to_goal'] = np.sqrt((120 - df['x_coord'])**2 + (40 - df['y_coord'])**2)
```

#### **Categorical Features:**
```python
# Extract event type from JSON
def extract_event_type(type_json):
    if pd.isna(type_json):
        return 'Unknown'
    try:
        type_dict = json.loads(type_json) if isinstance(type_json, str) else type_json
        return type_dict.get('name', 'Unknown')
    except:
        return 'Unknown'

df['event_type_name'] = df['type'].apply(extract_event_type)

# Label encoding for all categorical features
from sklearn.preprocessing import LabelEncoder

le_event = LabelEncoder()
df['event_type_encoded'] = le_event.fit_transform(df['event_type_name'])

le_team = LabelEncoder()
df['team_encoded'] = le_team.fit_transform(df['team_name'])

le_position = LabelEncoder()
df['position_encoded'] = le_position.fit_transform(df['position_name'].fillna('Unknown'))
```

#### **Team Features (Updated):**
```python
# Team names: No home/away advantage in neutral tournament
le_team_x = LabelEncoder()
df['team_x_encoded'] = le_team_x.fit_transform(df['team_x'])  # Formerly home_team

le_team_y = LabelEncoder()
df['team_y_encoded'] = le_team_y.fit_transform(df['team_y'])  # Formerly away_team

# Add team context feature
df['is_team_x'] = (df['team_name'] == df['team_x']).astype(int)
```

#### **Match Context Features (Updated):**
```python
# Kick-off time: Ordinal categorical encoding
def encode_kickoff_ordinal(kickoff_time):
    """Convert kick-off to ordinal categories"""
    kickoff_mapping = {
        '16:00:00.000': 0,  # Early evening
        '19:00:00.000': 1,  # Prime time  
        '22:00:00.000': 2   # Late evening
    }
    return kickoff_mapping.get(kickoff_time, 1)  # Default to prime time

df['kick_off_ordinal'] = df['kick_off'].apply(encode_kickoff_ordinal)
```

#### **Tactical Features (New):**
```python
# Tactics: Extract formation from tactics JSON
def extract_formation(tactics_json):
    """Extract formation number from tactics"""
    if pd.isna(tactics_json):
        return 'Unknown'
    try:
        tactics_dict = json.loads(tactics_json) if isinstance(tactics_json, str) else tactics_json
        formation = tactics_dict.get('formation', 'Unknown')
        return str(formation) if formation else 'Unknown'
    except:
        return 'Unknown'

df['formation'] = df['tactics'].apply(extract_formation)
df['formation_encoded'] = LabelEncoder().fit_transform(df['formation'])
```

#### **Boolean Features:**
```python
# Boolean features: Missing = False (no pressure/counterpress/off-camera)
boolean_features = ['under_pressure', 'counterpress', 'off_camera']
for feature in boolean_features:
    df[feature] = df[feature].fillna(False).astype(int)
```

### **📊 2. Feature Scaling**

#### **Features Requiring StandardScaler:**
```python
from sklearn.preprocessing import StandardScaler

# Continuous features with varying ranges
scaling_features = [
    'x_coord', 'y_coord', 'distance_to_goal',
    'total_seconds', 'possession', 
    'pass_length', 'carry_distance'
]

scaler = StandardScaler()
df[scaling_features] = scaler.fit_transform(df[scaling_features])
```

#### **Features Requiring MinMaxScaler:**
```python
from sklearn.preprocessing import MinMaxScaler

# Bounded features (0-1 range)
minmax_features = ['shot_xg']

minmax_scaler = MinMaxScaler()
df[minmax_features] = minmax_scaler.fit_transform(df[minmax_features])
```

### **📊 3. Derived Feature Creation**

#### **Field Position Categories:**
```python
def categorize_field_position(x_coord):
    if x_coord <= 40:
        return 'Defensive'
    elif x_coord <= 80:
        return 'Middle'
    else:
        return 'Attacking'

df['field_position'] = df['x_coord'].apply(categorize_field_position)

# Binary indicators
df['attacking_third'] = (df['x_coord'] >= 80).astype(int)
df['defensive_third'] = (df['x_coord'] <= 40).astype(int)
df['central_zone'] = ((df['y_coord'] >= 26.7) & (df['y_coord'] <= 53.3)).astype(int)
```

#### **Event-Specific Features:**
```python
# Pass features
def extract_pass_length(pass_json):
    if pd.isna(pass_json):
        return 0.0
    try:
        pass_dict = json.loads(pass_json) if isinstance(pass_json, str) else pass_json
        return pass_dict.get('length', 0.0)
    except:
        return 0.0

df['pass_length'] = df['pass'].apply(extract_pass_length)
df['pass_angle'] = df['pass'].apply(lambda x: extract_pass_angle(x))

# Shot features  
df['shot_xg'] = df['shot'].apply(lambda x: extract_shot_xg(x))

# Carry features
df['carry_distance'] = df['carry'].apply(lambda x: calculate_carry_distance(x))
```

---

## 📊 **PREPROCESSING SUMMARY**

### **🎯 Processing Requirements:**

| **Category** | **Count** | **Details** |
|--------------|-----------|-------------|
| **Total Basic Features** | **35** | +3 from originally missing features |
| **Features Requiring Encoding** | **17** | +2 from new features |
| **Features Requiring Scaling** | **8** | StandardScaler (7) + MinMaxScaler (1) |
| **Features with Missing Values** | **14** | +2 from new features |
| **Derived Features** | **8** | +1 from related_events_count |
| **Boolean Features** | **6** | Binary indicators (0/1) |

### **📋 Processing Pipeline Order:**

1. **Data Loading & JSON Parsing** (5 min)
2. **Feature Extraction** (coordinates, event types, team info) (10 min)
3. **Missing Value Imputation** (temporal, spatial, categorical) (5 min)
4. **Derived Feature Creation** (distance, field position, event-specific) (5 min)
5. **Categorical Encoding** (Label Encoding for 15 features) (3 min)
6. **Feature Scaling** (StandardScaler + MinMaxScaler) (2 min)
7. **Validation & Quality Check** (boundaries, data types, ranges) (5 min)

**Total Processing Time**: ~35 minutes for full Euro 2024 dataset (187,858 events)

### **✅ Expected Output Characteristics:**

| **Aspect** | **Specification** |
|------------|-------------------|
| **Feature Count** | 35 basic features ready for selection |
| **Missing Values** | 0% (all imputed appropriately) |
| **Data Types** | All numeric (int/float) for ML algorithms |
| **Memory Usage** | Optimized dtypes for 187K+ events |
| **Feature Ranges** | Normalized/standardized where appropriate |
| **Categorical Encoding** | All strings converted to numeric labels |

### **🔍 Quality Validation Checks:**

```python
# Post-processing validation
def validate_preprocessing(df):
    # Check for missing values
    missing_counts = df.isnull().sum()
    assert missing_counts.sum() == 0, f"Missing values found: {missing_counts[missing_counts > 0]}"
    
    # Check coordinate boundaries
    assert df['x_coord'].between(-3, 3).all(), "X coordinates not properly scaled"
    assert df['y_coord'].between(-3, 3).all(), "Y coordinates not properly scaled"
    
    # Check categorical encodings
    assert df['event_type_encoded'].dtype in [int, float], "Event types not encoded"
    assert df['team_encoded'].dtype in [int, float], "Teams not encoded"
    
    # Check boolean features
    boolean_features = ['attacking_third', 'defensive_third', 'central_zone', 
                       'under_pressure', 'counterpress', 'off_camera']
    for feature in boolean_features:
        assert df[feature].isin([0, 1]).all(), f"{feature} not properly binarized"
    
    print("✅ All preprocessing validation checks passed!")
```

---

## 🚀 **READY FOR ITERATION 1**

### **📊 Final Feature Set (35 Basic Features):**

#### **Sequential & Temporal (8 features):**
- `index`, `related_events_count`, `period`, `minute`, `second`, `total_seconds`, `possession`, `duration`

#### **Spatial (10 features):**
- `x_coord`, `y_coord`, `distance_to_goal`, `field_position`, `attacking_third`, `defensive_third`, `central_zone`

#### **Event & Context (11 features):**
- `event_type_encoded`, `play_pattern_encoded`, `team_encoded`, `possession_team_encoded`, `stage_encoded`, `match_week`, `match_id_encoded`, `formation_encoded`

#### **Team Context (8 features):**
- `team_x_encoded`, `team_y_encoded`, `is_team_x`, `kick_off_ordinal`, `day_of_week`

#### **Player & Pressure (8 features):**
- `player_encoded`, `position_encoded`, `under_pressure`, `counterpress`, `pass_length`, `pass_angle`, `carry_distance`, `shot_xg`

### **🎯 Next Steps:**
1. **Implement preprocessing pipeline** using these specifications
2. **Apply to 3-minute windowing** for momentum calculation
3. **Run 9-method feature selection** with ≥7 voting threshold
4. **Train 7 models** on selected features
5. **Generate Iteration 1 summary** with performance comparison

---

*📊 **Document Status**: Complete preprocessing specification*  
*🎯 **Purpose**: Foundation for Iteration 1 implementation*  
*📅 **Date**: January 31, 2025*