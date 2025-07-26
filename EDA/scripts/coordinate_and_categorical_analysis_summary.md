# Updated Coordinate Examples and Categorical Feature Analysis Summary

## 📊 Analysis Overview
**Dataset:** euro_2024_complete_dataset.csv (187,858 rows × 59 columns)  
**Analysis Date:** {{ current_date }}  
**Features Analyzed:** 13 real coordinate examples + 9 categorical features (4 ordinal + 5 binomial)

## 🗺️ Coordinate Examples - Real Data Updates

### ✅ Location Coordinates (Real Examples)
- **Range:** X: 21.1-100.9m (field width 0-120m), Y: 11.0-57.8m (field height 0-80m)
- **Real Examples:**
  - `[46.2, 34.3]` → Center field area (midfield play)
  - `[100.9, 11.0]` → Attacking third, near goal line
  - `[21.1, 34.0]` → Defensive third, left side
- **Momentum Relevance:** Position indicates attack/defense zones, proximity to goal affects momentum

### ✅ Carry Data (Real Examples with Calculations)  
- **Forward Carries (Positive Momentum):**
  - `99.8, 11.2` with 16.8m distance, 24.3° direction → Strong attacking momentum
  - `102.1, 5.6` with 2.5m distance, -4.6° direction → Goal area approach
- **Defensive Carries:**
  - `87.8, 35.5` with 1.0m distance, 90° direction → Sideways defensive play
- **Momentum Impact:** Forward carries = positive momentum, distance = magnitude

### ✅ Visible Area (360° Tracking)
- **Real Examples:** 10-12 boundary points per polygon
- **Coverage:** Full 360° player field vision tracking
- **Momentum Relevance:** Larger areas = better field control, centroids = pressure zones

## 📈 Categorical Feature Analysis (9 Features)

### 🔢 Ordinal Features (4 Features)

| Feature | Total Values | Unique Values | Missing % | Most Frequent | Distribution Pattern |
|---------|-------------|---------------|-----------|---------------|---------------------|
| **period** | 187,858 | 5 | 0% | Period 1 (93,628) | Normal game flow: 1st half > 2nd half > extra time |
| **match_week** | 187,858 | 7 | 0% | Week 1 (43,290) | Tournament progression: group stage heavy |
| **minute** | 187,858 | 128 | 0% | Minute 45 (4,228) | Peak at half-time (45min), uniform distribution |
| **second** | 187,858 | 60 | 0% | Second 0 (3,582) | Even distribution across 60-second intervals |

### ⚖️ Binomial Features (5 Features)

| Feature | Total Values | Missing % | True Count | True % | Analysis |
|---------|-------------|-----------|------------|--------|----------|
| **under_pressure** | 187,858 | 82.7% | 32,578 | 17.3% | High-pressure situations rare but significant |
| **off_camera** | 187,858 | 98.9% | 2,041 | 1.1% | Most events captured on camera |
| **counterpress** | 187,858 | 97.6% | 4,514 | 2.4% | Defensive counter-pressing tactics |
| **out** | 187,858 | 99.3% | 1,318 | 0.7% | Ball out of play events (rare) |
| **injury_stoppage** | 187,858 | 99.97% | 50 | 0.03% | Very rare injury stoppage events |

## 🎯 Key Insights for Momentum Analysis

### Coordinate Features
1. **Location vectors** provide precise field positioning for momentum zones
2. **Carry calculations** reveal directional momentum (forward = positive, backward = defensive)
3. **Visible area polygons** indicate field control and pressure zones

### Temporal Patterns (Ordinal)
1. **Period distribution:** 1st half (50%) vs 2nd half (47%) vs extra time (3%)
2. **Match progression:** Tournament front-loaded (weeks 1-3 = 69%)
3. **Time granularity:** Minute-level (128 values) and second-level (60 values) precision

### Event Quality (Binomial)
1. **Pressure situations:** 17% of events under pressure (momentum indicator)
2. **Camera coverage:** 99% events captured (high data quality)
3. **Tactical events:** Counterpress (2.4%) indicates defensive momentum shifts

## 📁 Generated Files

### 📊 Visualization Files (9 plots)
- **Ordinal Charts:** `period_ordinal_chart.png`, `match_week_ordinal_chart.png`, `minute_ordinal_chart.png`, `second_ordinal_chart.png`
- **Binomial Charts:** `under_pressure_binomial_chart.png`, `off_camera_binomial_chart.png`, `counterpress_binomial_chart.png`, `out_binomial_chart.png`, `injury_stoppage_binomial_chart.png`

### 📈 Data Files  
- **Updated:** `coordinate_extraction_examples.csv` (13 real examples)
- **New:** `categorical_feature_statistics.csv` (9 feature statistics)

## ✅ Validation Results

### Real Data Verification
- ✅ **Location coordinates** confirmed as real pitch positions (21-101m x-axis, 11-58m y-axis)
- ✅ **Carry distances** calculated from real movements (0.1-16.8m range)
- ✅ **Carry directions** computed from real trajectories (-4.6° to 90°)
- ✅ **Visible areas** extracted from actual 360° tracking data (10-12 boundary points)

### Momentum Relevance
- ✅ **Forward carries** identified as positive momentum indicators
- ✅ **Pressure events** (17%) marked as momentum shift points
- ✅ **Time intervals** provide precise momentum timing context
- ✅ **Field zones** mapped for attacking/defensive momentum analysis

---
**Status:** ✅ All coordinate examples updated with real data + 9 categorical features analyzed with individual plots and comprehensive statistics 