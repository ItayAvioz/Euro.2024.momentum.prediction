# Missing Values Analysis Summary
## Euro 2024 Complete Dataset

### Dataset Overview
- **Total Features**: 59
- **Features with Missing Values**: 32 (54.2%)
- **Total Dataset Size**: 187,858 events

### Key Findings

#### 1. Event-Specific Features Pattern
Most missing values (21 features with 96.66-100% missing rates) represent **events that did not occur** at that specific moment, not true missing data:

- `player_off` (100.0% missing)
- `miscontrol` (99.98% missing)
- `bad_behaviour` (99.97% missing)
- `injury_stoppage` (99.97% missing)
- `block` (99.95% missing)
- `tactics` (99.85% missing)
- `50_50` (99.84% missing)
- `ball_recovery` (99.84% missing)
- `foul_committed` (99.77% missing)
- `substitution` (99.75% missing)
- `foul_won` (99.71% missing)
- `interception` (99.57% missing)
- `dribble` (99.32% missing)
- `out` (99.3% missing)
- `shot` (99.29% missing)
- `goalkeeper` (99.14% missing)
- `clearance` (99.01% missing)
- `off_camera` (98.91% missing)
- `duel` (98.37% missing)
- `counterpress` (97.6% missing)
- `ball_receipt` (96.66% missing)

#### 2. Binomial Features Pattern
All 5 binomial features have high missing rates where **missing = false**:
- `injury_stoppage` (99.97% missing)
- `out` (99.3% missing)
- `off_camera` (98.91% missing)
- `counterpress` (97.6% missing)
- `under_pressure` (82.66% missing)

#### 3. Special Cases
- **`related_events`** (3.57% missing): Missing values represent **0 related events**
- **`location`** (0.89% missing): Highly complete coordinate data
- **`player`/`position`** (0.46% missing): Only missing when no player involved

#### 4. Valuable Complete Features
Features with low missing rates suitable for momentum analysis:
- `player` and `position` (0.46% missing)
- `location` (0.89% missing)
- `related_events` (3.57% missing)
- `visible_area` (12.95% missing)
- `duration` (27.48% missing)

### Recommendations for Feature Engineering

#### High-Missing Event Features (21 features)
**Options**:
1. **Delete entirely** - removes 96.66-100% sparse features
2. **Create occurrence flags** - binary indicators if event happened
3. **Event type encoding** - use main event type instead of detailed features

#### Binomial Features
- **Encode missing values as False** for all binomial features
- Maintains logical consistency with event structure

#### Related Events
- **Encode missing as 0** - represents no related events

#### Coordinate Features
- **Extract spatial features** from `location`, `visible_area`
- High completeness makes them valuable for momentum analysis

### Impact on Momentum Prediction Model
1. **Reduces feature space** from 59 to ~38 core features
2. **Improves model efficiency** by removing sparse features
3. **Maintains event context** through occurrence flags if needed
4. **Preserves spatial and temporal information** for momentum analysis

### Files Generated
- `missing_values_analysis.csv` - Detailed missing values statistics
- `analyze_missing_values.py` - Analysis script with variable group classifications 