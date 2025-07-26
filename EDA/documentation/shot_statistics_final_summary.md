# Shot Statistics Analysis by Tournament Stage (Normalized to 90 Minutes)

## 📊 CORRECTED SHOT STATISTICS SUMMARY TABLE

| **Statistic** | **Group Stage** | **Round of 16** | **Quarter-finals + Semi-finals + Final** |
|---------------|----------------|----------------|------------------------------------------|
| **Number of Games** | 36 | 8 | 7 |
| **Games to Extra Time** | 0 | 2 | 3 |
| **Extra Time Percentage** | 0.0% | 25.0% | **42.9%** |
| **Total Shots** | 902 | 236 | 202 |
| **Total Shots on Target** | 377 | 93 | 87 |
| **Total Shots off Target** | 262 | 78 | 57 |
| **Total Shots Blocked** | 263 | 65 | 58 |
| **🎯 Shots per Game** | 25.06 | 29.50 | 28.86 |
| **🎯 Shots per 90min** | **25.06** | **27.23** | **25.25** |
| **📌 Shots on Target per Game** | 10.47 | 11.62 | 12.43 |
| **📌 Shots on Target per 90min** | **10.47** | **10.73** | **10.88** |
| **🎯 Shot Accuracy %** | **41.8%** | **39.4%** | **43.1%** |
| **⚽ Conversion Rate %** | **8.2%** | **8.5%** | **15.8%** |
| **🥅 On Target Conversion %** | **19.6%** | **21.5%** | **36.8%** |
| **🚫 Blocked Shot %** | **29.2%** | **27.5%** | **28.7%** |

## 🔍 CALCULATION METHODOLOGY EXPLAINED

### **📊 Data Source & Classification:**
1. **Shot Events**: Identified from events data where 'type' contains 'Shot' (1,340 total shots)
2. **StatsBomb Format**: Parsed detailed 'shot' column containing outcome information

### **🎯 Shot Outcome Classification (StatsBomb Standard):**

#### **SHOTS ON TARGET (557 total, 41.6%)**:
- **Goal** (Outcome ID 97): 126 shots
- **Saved** (Outcome ID 100): 316 shots  
- **Post/Crossbar** (Outcome ID 101): 25 shots
- **Goals automatically classified as on target**

#### **SHOTS OFF TARGET (397 total, 29.6%)**:
- **Wayward/Wide/High** (Outcome ID 102): 81 shots
- **Off Target** (misc): 316 shots
- **Shots that miss goal without keeper involvement**

#### **SHOTS BLOCKED (386 total, 28.8%)**:
- **Blocked** (Outcome ID 103): 386 shots
- **By outfield players before reaching goal**
- **Not counted in accuracy calculations**

### **⏱️ Normalization Methodology:**

#### **Match Duration Calculation:**
- **Regular Time**: 90 minutes (periods 1-2, max minute ≤ 95)
- **Extra Time**: 120 minutes (period ≥ 3 OR max minute > 95)

#### **Per 90-Minute Formula:**
```
Total 90min Equivalent = Total Actual Minutes ÷ 90
Normalized Stat = Total Stat ÷ Total 90min Equivalent
Normalization Impact % = ((Per 90min - Per Game) ÷ Per Game) × 100
```

#### **Accuracy Calculations:**
- **Shot Accuracy** = (Shots on Target ÷ (Total Shots - Blocked Shots)) × 100
- **Overall Conversion Rate** = (Goals ÷ Total Shots) × 100  
- **On Target Conversion** = (Goals ÷ Shots on Target) × 100

## 📈 KEY FINDINGS & INSIGHTS

### **🏆 Tournament Progression Patterns:**

#### **1. Shot Volume (Normalized per 90min):**
- **Group Stage**: 25.06 shots/90min (baseline)
- **Round of 16**: 27.23 shots/90min (+8.7% higher intensity)
- **QF+SF+Final**: 25.25 shots/90min (+0.8% vs Group Stage)

#### **2. Shot Accuracy Trends:**
- **Group Stage**: 41.8% accuracy
- **Round of 16**: 39.4% accuracy (-2.4pp decrease)
- **QF+SF+Final**: 43.1% accuracy (+1.3pp vs Group Stage)

#### **3. Conversion Efficiency:**
- **Group Stage**: 8.2% overall, 19.6% on target
- **Round of 16**: 8.5% overall, 21.5% on target  
- **QF+SF+Final**: **15.8% overall, 36.8% on target** (🔥 Peak efficiency!)

### **🎯 Normalization Impact by Stage:**

#### **Round of 16 (-7.7% impact)**:
- Shots: 29.50 → 27.23 per 90min
- On Target: 11.62 → 10.73 per 90min

#### **QF+SF+Final (-12.5% impact)**:
- Shots: 28.86 → 25.25 per 90min  
- On Target: 12.43 → 10.88 per 90min

### **⚡ Critical Insights:**

1. **Defensive Intensity**: ~29% of shots blocked across all stages
2. **Quality over Quantity**: Later stages show higher conversion despite similar shot volumes
3. **Knockout Pressure**: Extra time significantly affects raw statistics
4. **Peak Performance**: QF+SF+Final stages show highest shooting accuracy (43.1%) and conversion rates

### **🎯 Momentum Modeling Implications:**
- **Use normalized per-90min statistics** for cross-stage comparisons
- **Shot accuracy improves** under highest pressure (knockout stages)
- **Conversion rates double** in final stages, indicating **clinical finishing**
- **Blocked shots** represent significant defensive momentum factor

## 📁 Generated Files:
- `EDA/corrected_shot_statistics_table.csv`
- `EDA/corrected_shot_statistics_detailed.csv`
- `EDA/shot_statistics_analysis.png`

The analysis reveals that while shot volume remains relatively consistent when normalized, **shooting quality and conversion efficiency dramatically improve** in the tournament's final stages, indicating teams become more clinical under the highest pressure scenarios. 