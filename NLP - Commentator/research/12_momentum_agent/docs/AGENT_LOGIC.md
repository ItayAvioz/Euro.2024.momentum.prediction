# Momentum Agent - Detailed Logic Documentation

## 🎯 Purpose

The Momentum Agent is designed to analyze momentum data and provide intelligent commentary suggestions for **General** play moments (when no specific event like Goal, Shot, or Card is detected).

---

## 🆕 VERSION 3.0 UPDATE (December 2024)

### Simplified Philosophy

The agent now operates with **direction, not strict rules**:
- Focus on KEY INDICATORS (comparisons between teams)
- Use GAME CONTEXT to determine importance
- Find HOT TIMES (max gap, max change, tension)
- LOG all decisions for future learning

### Key Indicators (What Agent Compares)

| Indicator | What It Means | Why It Matters |
|-----------|---------------|----------------|
| **Abs Momentum vs Pos Changes** | Team A has higher VALUE, Team B has more positive CHANGES | Team B is CATCHING UP! (66.7% WIN when metrics disagree) |
| **Abs Momentum vs Longest Seq** | Team A has higher VALUE, Team B has longer streak | Streak = sustained pressure building |
| **Highest Momentum Diff (VALUE)** | Current gap vs match history | MAX gap = "Hot Time" - peak control |
| **Highest Momentum Change Diff** | Current change vs match history | MAX change = Momentum SHIFT happening |
| **TENSION** | Score leader ≠ Momentum leader | Creates drama - losing team pushing back |

### Game Context Importance

| Context | Implication |
|---------|-------------|
| Close game (0-0, 1-1) | Every momentum shift matters |
| Blowout (3-0+) | Less relevant |
| Late game (75+ min) | More important - running out of time |
| Early game (< 15 min) | Only extreme patterns matter |
| Score ≠ Momentum leader | HIGH tension - always interesting |

### Hot Time Detection

Agent flags these as "hot times":
- Current gap is **LARGEST** in match so far
- Current change is **LARGEST** in match so far
- **Tension** exists (score leader vs momentum leader disagree)
- **Sudden spike** (change > 2x usual)

### Decision Logging

All decisions are logged to `logs/agent_decisions_YYYYMMDD.csv`:
- Match context (score, minute, teams)
- Decision (interesting, confidence, reason)
- Momentum metrics (gap, changes, streaks)
- Hot time indicators

This enables future analysis of:
- Which patterns led to actual events?
- Should thresholds be adjusted?
- What makes a "good" interesting moment?

---

## 📊 Input Data Structure

### **1. Momentum Data (Per Minute)**

```
minute: 35
period: 1
match_id: 3930158

home_team: "Germany"
away_team: "Scotland"

home_momentum: 5.42          # Current momentum (0-10 scale)
away_momentum: 4.98          # Current momentum (0-10 scale)

home_change: +0.38           # Change in LAST 3 minutes
away_change: -0.12           # Change in LAST 3 minutes

momentum_diff: +0.44         # home - away
```

### **2. Historical Data (Last 5 Minutes)**

```
history: [
    { minute: 30, home_momentum: 5.10, home_change: +0.22, away_change: -0.05 },
    { minute: 31, home_momentum: 5.18, home_change: +0.15, away_change: +0.08 },
    { minute: 32, home_momentum: 5.25, home_change: +0.28, away_change: -0.10 },
    { minute: 33, home_momentum: 5.32, home_change: +0.31, away_change: -0.08 },
    { minute: 34, home_momentum: 5.38, home_change: +0.35, away_change: -0.05 },
    { minute: 35, home_momentum: 5.42, home_change: +0.38, away_change: -0.12 }
]
```

### **3. Predictions (75+ only)**

```
predictions: {
    home_predicted_change: +0.55    # NEXT 3 minutes
    away_predicted_change: -0.22
    directional_accuracy: 0.78       # Model confidence
}
```

---

## 🔍 Analysis Logic

### **1. Dominance Analysis**

**Question:** Which team has higher momentum?

```python
diff = home_momentum - away_momentum

if abs(diff) < 0.5:
    # BALANCED - No clear dominant team
    return "Even", "balanced"

elif abs(diff) < 1.5:
    # SLIGHT ADVANTAGE - One team slightly ahead
    dominant = "Home" if diff > 0 else "Away"
    return dominant, "slight_advantage"

elif abs(diff) < 2.5:
    # DOMINANT - One team clearly in control
    dominant = "Home" if diff > 0 else "Away"
    return dominant, "dominant"

else:
    # COMPLETE CONTROL - One team overwhelmingly dominant
    dominant = "Home" if diff > 0 else "Away"
    return dominant, "complete_control"
```

**Example:**
```
Germany 5.42, Scotland 4.98
diff = +0.44

Result: Slight advantage, no clear dominance (diff < 0.5)
```

---

### **2. Trend Analysis**

**Question:** Is the dominant team improving or declining?

```python
# Get dominant team's change
if dominant_team == home_team:
    dom_change = home_change
    opp_change = away_change
else:
    dom_change = away_change
    opp_change = home_change

# Classify trend
if dom_change > 0.6:
    if opp_change < -0.3:
        return "EXTENDING CONTROL"  # Rising fast, opponent falling
    else:
        return "SURGING"            # Rising fast

elif dom_change > 0.3:
    return "IMPROVING"              # Rising steadily

elif dom_change > -0.3:
    return "STABLE"                 # Maintaining level

elif dom_change > -0.6:
    if opp_change > 0.3:
        return "MOMENTUM SHIFTING"  # Falling, opponent rising
    else:
        return "LOSING GRIP"        # Falling

else:
    return "FADING FAST"            # Falling rapidly
```

**Example:**
```
Germany change: +0.38 (rising)
Scotland change: -0.12 (slight decline)

Result: IMPROVING (dom_change > 0.3)
```

---

### **3. Streak Detection**

**Question:** Are there consecutive positive or negative changes?

```python
def detect_streak(history, team_change_key):
    positive_streak = 0
    negative_streak = 0
    current_pos = 0
    current_neg = 0
    
    for entry in history:
        change = entry[team_change_key]
        
        if change > 0.1:      # Positive threshold
            current_pos += 1
            current_neg = 0
            positive_streak = max(positive_streak, current_pos)
        
        elif change < -0.1:   # Negative threshold
            current_neg += 1
            current_pos = 0
            negative_streak = max(negative_streak, current_neg)
        
        else:
            current_pos = 0
            current_neg = 0
    
    return positive_streak, negative_streak
```

**Streak Classification:**

| Length | Classification | Description |
|--------|---------------|-------------|
| 2 | Building | Short positive/negative run |
| 3 | Strong | Sustained momentum |
| 4+ | Dominant | Extended control |

**Example:**
```
Germany changes over 5 minutes: [+0.22, +0.15, +0.28, +0.31, +0.35, +0.38]
All positive!

Result: 6-minute positive streak → "Germany on a 6-minute positive run"
```

---

### **4. Divergence Detection**

**Question:** Is one team rising while the other is falling?

```python
DIVERGENCE_THRESHOLD = 0.4

if home_change > DIVERGENCE_THRESHOLD and away_change < -DIVERGENCE_THRESHOLD:
    # Home rising, Away falling
    return {
        "has_divergence": True,
        "rising_team": home_team,
        "falling_team": away_team,
        "total_swing": home_change - away_change  # Total gap created
    }

elif away_change > DIVERGENCE_THRESHOLD and home_change < -DIVERGENCE_THRESHOLD:
    # Away rising, Home falling
    return {
        "has_divergence": True,
        "rising_team": away_team,
        "falling_team": home_team,
        "total_swing": away_change - home_change
    }

else:
    return {"has_divergence": False}
```

**Example:**
```
Germany change: +0.65
Scotland change: -0.48

Both exceed threshold (0.4)!
Total swing: 0.65 - (-0.48) = 1.13

Result: "Germany surging (+0.65) while Scotland fades (-0.48)"
```

---

### **5. Max Differential Analysis**

**Question:** Is the current gap the biggest in the match?

```python
# Get max differential in match so far
max_diff = 1.67  # Example: biggest gap was 1.67 at minute 8
current_diff = 0.44

ratio = current_diff / max_diff  # 0.26

if ratio >= 0.95:
    comparison = "AT PEAK"      # Current is the biggest gap
elif ratio >= 0.8:
    comparison = "NEAR PEAK"    # Close to biggest
elif ratio >= 0.5:
    comparison = "MODERATE"     # Mid-range
else:
    comparison = "BELOW PEAK"   # Gap has been bigger
```

---

### **6. Prediction Analysis (75+ only)**

**Question:** What does the ARIMAX model predict?

```python
home_predicted = +0.55
away_predicted = -0.22

if home_predicted > away_predicted + 0.3:
    expected_dominant = home_team
elif away_predicted > home_predicted + 0.3:
    expected_dominant = away_team
else:
    expected_dominant = "Neither/Both"

# Generate prediction note
if home_predicted > 0.6:
    note = f"Model predicts {home_team} momentum surge (+{home_predicted:.1f})"
elif home_predicted > 0.3:
    note = f"Model suggests {home_team} will maintain pressure"
else:
    note = "No clear momentum shift predicted"
```

---

## 📝 Phrase Generation Priority

The agent generates a phrase based on priority:

### **Priority 1: Divergence (Most Dramatic)**
```
If divergence detected:
    return "{rising_team} surging (+{rising_change}) while {falling_team} fades ({falling_change})"
```

### **Priority 2: Strong Streak (3+ minutes)**
```
If streak length >= 3:
    return "{team} on a {length}-minute {direction} run"
```

### **Priority 3: Dominance + Trend Combination**

| Dominance | Trend | Phrase |
|-----------|-------|--------|
| Complete Control | Widening | "{team} completely dominating, momentum at {value} and rising" |
| Dominant | Extending Control | "{team} firmly in control and pulling further ahead" |
| Dominant | Shifting | "Tide turning! {opponent} building momentum against {team}" |
| Dominant | Losing Grip | "{team} still ahead but {opponent} sensing an opportunity" |
| Slight Advantage | Surging | "{team} gaining the upper hand, momentum rising" |
| Slight Advantage | Fading | "{team} with slim advantage but momentum fading fast" |
| Balanced | - | "Evenly matched with neither side able to dominate" |

### **Priority 4: Add Prediction (if available)**
```
If minute >= 75 and has_prediction:
    phrase += f". {prediction_note}"
```

---

## 📊 Complete Decision Example

**Input:**
```
Match: Germany vs Scotland
Minute: 38, Period: 1
Home momentum: 5.93, Away momentum: 4.25
Home change: +0.72, Away change: -0.41
History: 5 consecutive positive changes for Germany
```

**Analysis:**
```
1. DOMINANCE:
   diff = 5.93 - 4.25 = 1.68
   → DOMINANT (1.5 < diff < 2.5)

2. TREND:
   Germany change: +0.72 (> 0.6)
   Scotland change: -0.41 (< -0.3)
   → EXTENDING CONTROL

3. STREAK:
   Germany: 5 consecutive positive
   → DOMINANT STREAK

4. DIVERGENCE:
   Home: +0.72 > 0.4 ✓
   Away: -0.41 < -0.4 ✓
   → DIVERGENCE DETECTED!

5. MAX DIFF:
   Current: 1.68
   Max so far: 1.67 at minute 8
   → AT PEAK (new maximum!)
```

**Output:**
```
{
    dominant_team: "Germany",
    dominance_type: "dominant",
    
    has_streak: True,
    streak_description: "Germany on a 5-minute positive run",
    
    has_divergence: True,
    divergence_description: "Germany surging (+0.72) while Scotland fades (-0.41)",
    
    max_diff_info: {
        comparison: "at_peak",
        note: "Biggest momentum gap in the match so far (1.68)"
    },
    
    phrase_suggestion: "Germany surging (+0.72) while Scotland fades (-0.41)"
}
```

---

## 🔧 Configuration

All thresholds are configurable in `momentum_agent.py`:

```python
class MomentumAgent:
    # Dominance thresholds
    DOMINANCE_THRESHOLD = 0.5       # Slight advantage
    STRONG_DOMINANCE = 1.5          # Dominant
    VERY_STRONG_DOMINANCE = 2.5     # Complete control
    
    # Change thresholds
    SIGNIFICANT_CHANGE = 0.3        # Notable change
    STRONG_CHANGE = 0.6             # Strong change
    
    # Streak thresholds
    MIN_STREAK = 2                  # Minimum streak
    STRONG_STREAK = 3               # Strong streak
    DOMINANT_STREAK = 4             # Dominant streak
    
    # Divergence threshold
    DIVERGENCE_THRESHOLD = 0.4      # For divergence detection
```

---

## 🆕 NEW: Enhanced Data (December 2024 Update)

### **NEW Input Data Structure**

The agent now receives significantly more data:

#### **A. Window Dominance**
```python
window_dominance = {
    'home_windows_won': 6,           # Minutes where home_mom > away_mom
    'away_windows_won': 3,           # Minutes where away_mom > home_mom
    'tied_windows': 1,               # Very close (diff < 0.1)
    'home_dominance_pct': 60.0,      # Percentage
    'away_dominance_pct': 30.0
}
```

#### **B. Sequence Metrics (Research Thresholds)**
```python
sequence_metrics = {
    'home': {
        'total_positive_sequences': 3,   # Count of 2+ consecutive positive
        'total_negative_sequences': 1,
        'longest_positive': 4,           # Max streak length
        'longest_negative': 2
    },
    'away': {...},
    
    # Margins (for research threshold comparison)
    'seq_count_margin': 2,               # Difference in sequence counts
    'seq_leader': 'home',
    'longest_margin': 2,
    'longest_leader': 'home',
    'momentum_margin_pct': 15.5,         # % difference in total momentum
    'momentum_leader': 'home'
}
```

#### **C. Historical Crossovers**
```python
historical_crossovers = [45, 62, 71]  # Minutes where leadership changed
```

#### **D. Prediction Summary (minute 76+ only)**
```python
prediction_summary = {
    # Counts
    'home_positive_predictions': 3,
    'home_negative_predictions': 9,
    'home_neutral_predictions': 0,
    'away_positive_predictions': 8,
    'away_negative_predictions': 4,
    'away_neutral_predictions': 0,
    
    # Averages
    'home_avg_predicted': -0.18,
    'away_avg_predicted': +0.12,
    
    # Extremes
    'home_max_predicted': +0.15,
    'home_min_predicted': -0.45,
    'away_max_predicted': +0.35,
    'away_min_predicted': -0.08,
    
    # Trends
    'home_trend': 'declining',          # improving/declining/stable
    'away_trend': 'improving',
    
    # Crossovers
    'prediction_crossovers': [82, 86],  # When predicted leadership changes
    
    # Overall
    'home_dominant_predictions': 3,
    'away_dominant_predictions': 9,
    'predicted_overall_dominant': 'away',
    'dominance_ratio': '9/12',
    'total_predictions': 12
}
```

---

### **Research Thresholds (Static Knowledge)**

The agent has access to research findings:

#### **Goal-Momentum Correlation**
```
How calculated:
- Goal at minute X → Check Change = Momentum(X) - Momentum(X-3)
- Example: Goal at 78 → Past window (73,74,75), Future window (76,77,78)
- If change POSITIVE → team gaining momentum INTO goal

Results:
- 76.8% goals scored with POSITIVE momentum change
- 62.6% goals conceded with NEGATIVE momentum change
```

#### **Winning vs Chasing Metrics**
```
Winning Metrics (higher = better):
- Absolute Momentum: 46% WIN, 20% LOSE
- Number of Sequences: 35% WIN, 28% LOSE

Chasing Metrics (higher = WORSE - team is chasing!):
- Positive Changes: 28% WIN, 38% LOSE
- Longest Sequence: 23% WIN, 43% LOSE
```

#### **Critical Thresholds**
```
| Condition | WIN | LOSE |
|-----------|-----|------|
| 50%+ momentum margin | 64.3% | 14.3% |
| 3+ sequence margin | 66.7% | 11.1% |
| 4+ sequence margin | 83.3% | 0.0% |
| 10%+ mom + 3+ seq | 83.3% | 0.0% |
| Metrics disagree | 66.7% | 16.7% |
```

---

### **Decision Process Flow**

```
┌───────────────────────────────────────────────────────────────┐
│                    AGENT DECISION FLOW                        │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│  1. DATA COLLECTION                                          │
│     ├─ Current momentum + changes                            │
│     ├─ History (last 10 minutes)                             │
│     ├─ Window dominance                                      │
│     ├─ Sequence metrics                                      │
│     ├─ Historical crossovers                                 │
│     └─ Predictions (76+ only) + summary                      │
│                                                               │
│  2. PATTERN DETECTION (Exploratory)                          │
│     ├─ Streaks (2, 3, 4+ consecutive)                        │
│     ├─ Divergence (one up, one down)                         │
│     ├─ Window dominance (70%+)                               │
│     ├─ Sequence margins vs research thresholds               │
│     ├─ Prediction trends (min 76+)                           │
│     └─ Crossovers (historical + predicted)                   │
│                                                               │
│  3. RESEARCH COMPARISON                                       │
│     ├─ Does sequence margin match 0% lose threshold?         │
│     ├─ Does momentum margin match 64% win threshold?         │
│     ├─ Does pattern match goal correlation?                  │
│     └─ Are metrics disagreeing (66.7% win signal)?           │
│                                                               │
│  4. CONFIDENCE CALCULATION                                    │
│     Base: 0.5                                                 │
│     + Pattern factors (0.15 to 0.35 each)                    │
│     + Research matches (0.20 to 0.35 each)                   │
│     - Negative factors (-0.20 to -0.30)                      │
│     → Final: 0.0 to 1.0                                       │
│                                                               │
│  5. OUTPUT DECISION                                           │
│     ├─ If confidence >= 0.7: INTERESTING = YES               │
│     ├─ Select most important data points                     │
│     ├─ Include reason                                        │
│     └─ Emphasize predictions if minute 76+                   │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

---

### **Confidence Scoring**

| Factor | Points | Condition |
|--------|--------|-----------|
| **Positive Factors** | | |
| 3+ minute streak | +0.25 | Current streak >= 3 |
| 4+ minute streak | +0.35 | Current streak >= 4 |
| Divergence detected | +0.30 | One team +0.4, other -0.4 |
| 70%+ window dominance | +0.20 | One team won 70%+ of windows |
| 3+ sequence margin | +0.35 | Research: 0% lose! |
| 50%+ momentum margin | +0.25 | Research: 64.3% win |
| Metrics disagree | +0.35 | Research: 66.7% win |
| 4+ prediction streak | +0.30 | 4+ consecutive positive/negative |
| Clear prediction trend | +0.20 | Improving/declining |
| 80%+ prediction dominance | +0.30 | One team dominates predictions |
| Prediction crossover | +0.25 | Leadership change predicted |
| **Negative Factors** | | |
| Both teams stable | -0.30 | No significant changes |
| No clear pattern | -0.25 | Metrics balanced |
| Insufficient data | -0.20 | History too short |

**Final Confidence = clamp(base + factors, 0.0, 1.0)**

---

### **Example with New Data**

**Input at Minute 80:**
```
current_momentum:
  home: 4.82, away: 5.45
  home_change: -0.18, away_change: +0.32

window_dominance:
  home_windows_won: 3, away_windows_won: 7
  home_dominance_pct: 30%, away_dominance_pct: 70%

sequence_metrics:
  home: 2 positive seq, longest: 2
  away: 4 positive seq, longest: 5
  seq_count_margin: 2 (away)
  momentum_margin_pct: 12%

historical_crossovers: [68]

prediction_summary:
  home_positive: 2, home_negative: 5
  away_positive: 6, away_negative: 1
  home_trend: declining
  away_trend: improving
  prediction_crossovers: []
  predicted_overall_dominant: away
  dominance_ratio: 6/7
```

**Analysis:**
```
Pattern Detection:
  ✓ Away 70% window dominance: +0.20
  ✓ Away 5-minute streak (longest_positive): +0.35
  ✓ Away sequence margin 2+: +0.25
  ✓ Prediction dominance 86% (6/7): +0.30
  ✓ Clear prediction trend (away improving): +0.20

Research Match:
  ✓ Sequence margin 2+ matches research pattern

Confidence: 0.5 + 0.20 + 0.35 + 0.25 + 0.30 + 0.20 = 1.0 (capped)
```

**Output:**
```
INTERESTING: YES
CONFIDENCE: 0.95

FORWARD_DATA:
- Away: 5.45 (change: +0.32)
- 5-minute positive streak (longest in match)
- 70% window dominance (7/10 minutes)
- PREDICTIONS: Away dominates 6/7, trend: improving

REASON: Away building sustained momentum, model predicts continued dominance
```

---

**Document Version:** 2.0  
**Last Updated:** December 2024

