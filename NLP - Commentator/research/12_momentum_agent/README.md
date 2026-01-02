# Phase 12: Momentum Agent for General Commentary

## 🎯 Overview

This module implements an **intelligent agent** that decides IF and WHAT momentum information to include in **General commentary** (when no key event like Goal, Shot, Card is detected).

The agent uses:
- **Actual momentum data** (minutes 0-74) from `momentum_by_period.csv`
- **ARIMAX predictions** (minutes 75+) from `arimax_predictions_by_period.csv`

---

## 📊 Agent Decision Framework

### **The Agent Analyzes 6 Key Aspects:**

```
┌─────────────────────────────────────────────────────────────────────┐
│                    MOMENTUM AGENT ANALYSIS                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  1️⃣ DOMINANCE                                                        │
│     Who has higher momentum?                                         │
│     ├── Balanced (diff < 0.5)                                       │
│     ├── Slight Advantage (0.5-1.5)                                  │
│     ├── Dominant (1.5-2.5)                                          │
│     └── Complete Control (> 2.5)                                    │
│                                                                      │
│  2️⃣ TREND                                                            │
│     Is the dominant team improving or declining?                     │
│     ├── Surging (+0.6 or more)                                      │
│     ├── Improving (+0.3 to +0.6)                                    │
│     ├── Stable (-0.3 to +0.3)                                       │
│     ├── Losing Grip (-0.3 to -0.6)                                  │
│     └── Fading Fast (< -0.6)                                        │
│                                                                      │
│  3️⃣ STREAK                                                           │
│     Consecutive positive/negative momentum changes?                  │
│     ├── 2 minutes: Building                                         │
│     ├── 3 minutes: Strong                                           │
│     └── 4+ minutes: Dominant                                        │
│                                                                      │
│  4️⃣ DIVERGENCE                                                       │
│     One team rising while other falling?                             │
│     └── Total swing > 0.8: SIGNIFICANT SHIFT                        │
│                                                                      │
│  5️⃣ MAX DIFFERENTIAL                                                 │
│     How does current compare to biggest gap in match?                │
│     ├── At Peak: Biggest gap so far                                 │
│     ├── Near Peak: Within 80% of max                                │
│     └── Below Peak: Gap has been bigger                             │
│                                                                      │
│  6️⃣ PREDICTION (75+ only)                                            │
│     What does ARIMAX model predict for next 3 minutes?               │
│     ├── Surge expected (+0.6 or more)                               │
│     ├── Maintain pressure (+0.3 to +0.6)                            │
│     ├── Hold momentum (0 to +0.3)                                   │
│     └── May decline (< 0)                                           │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📂 Folder Structure

```
12_momentum_agent/
├── README.md                          ← This file
├── scripts/
│   ├── momentum_data_loader.py        ← Load momentum & prediction data
│   ├── momentum_agent.py              ← Main agent logic
│   └── test_agent.py                  ← Test script
├── data/
│   └── (output files)
└── docs/
    └── AGENT_LOGIC.md                 ← Detailed logic documentation
```

---

## 🔧 Data Sources

### **1. Actual Momentum Data**
**File:** `models/period_separated_momentum/outputs/momentum_by_period.csv`

| Column | Description |
|--------|-------------|
| `match_id` | Match identifier |
| `period` | Game period (1, 2, 3, 4) |
| `minute` | Game minute |
| `team_home` / `team_away` | Team names |
| `team_home_momentum` | Home team momentum (0-10 scale) |
| `team_away_momentum` | Away team momentum (0-10 scale) |
| `team_home_momentum_change` | Home team change in LAST 3 min |
| `team_away_momentum_change` | Away team change in LAST 3 min |

### **2. ARIMAX Predictions (75+ only)**
**File:** `models/period_separated_momentum/outputs/arimax_predictions_by_period.csv`

| Column | Description |
|--------|-------------|
| `match_id` | Match identifier |
| `minute_start` | Minute (75-90) |
| `team` | Team name |
| `is_home` | True/False |
| `prediction_value` | Predicted change for NEXT 3 min |
| `directional_accuracy` | Model confidence (0-1) |

---

## 🚀 Usage

### **Basic Usage**

```python
from momentum_agent import MomentumAgent

# Initialize agent
agent = MomentumAgent()

# Analyze for General commentary
result = agent.analyze_for_general(
    match_id=3930158,    # Germany vs Scotland
    minute=35,
    period=1
)

# Get the phrase suggestion
if result['include_momentum']:
    print(result['phrase_suggestion'])
    # Output: "Germany dominating proceedings with momentum at 5.4"
```

### **Full Result Structure**

```python
result = {
    'include_momentum': True,
    'minute': 35,
    'period': 1,
    
    # Dominance
    'dominant_team': 'Germany',
    'dominant_momentum': 5.42,
    'dominance_type': 'slight_advantage',
    'dominance_strength': 'moderate',
    
    # Trend
    'trend_description': 'improving',
    'trend_direction': 'rising',
    
    # Streak
    'has_streak': True,
    'streak_team': 'Germany',
    'streak_length': 3,
    'streak_direction': 'positive',
    'streak_description': 'Germany on a 3-minute positive run',
    
    # Divergence
    'has_divergence': False,
    'divergence_description': None,
    
    # Max Differential
    'max_diff_info': {
        'max_diff': 1.67,
        'max_minute': 8,
        'comparison': 'near_peak'
    },
    
    # Prediction (only if minute >= 75)
    'has_prediction': False,
    'prediction_note': None,
    
    # Output
    'phrase_suggestion': 'Germany on a 3-minute positive run',
    'detailed_summary': '...(full analysis text)...',
    
    # Raw data
    'raw_data': {
        'home_momentum': 5.42,
        'away_momentum': 4.98,
        'home_change': 0.38,
        'away_change': -0.12,
        'diff': 0.44
    }
}
```

---

## 📊 Agent Decision Examples

### **Example 1: Dominant Team Extending Control**

```
Minute 38': Germany 5.9, Scotland 4.1
- Dominance: Germany (strong, diff = 1.8)
- Trend: Germany +0.7, Scotland -0.3 → EXTENDING CONTROL
- Divergence: YES (Germany rising, Scotland falling)

Phrase: "Germany firmly in control and pulling further ahead"
```

### **Example 2: Momentum Shifting**

```
Minute 55': Spain 5.2, England 5.8
- Dominance: England (slight, diff = 0.6)
- Trend: Spain -0.5, England +0.8 → SHIFTING
- Streak: England 3 consecutive positive

Phrase: "Tide turning! England building momentum against Spain"
```

### **Example 3: Late Game with Prediction**

```
Minute 82': France 6.5, Portugal 4.8
- Dominance: France (strong, diff = 1.7)
- Trend: France +0.2 (stable)
- Prediction: France +0.6, Portugal -0.3

Phrase: "France in control. Model predicts momentum surge (+0.6)"
```

---

## 🎯 Thresholds (Configurable)

| Threshold | Default | Description |
|-----------|---------|-------------|
| `DOMINANCE_THRESHOLD` | 0.5 | Minimum diff for slight advantage |
| `STRONG_DOMINANCE` | 1.5 | Diff for strong dominance |
| `VERY_STRONG_DOMINANCE` | 2.5 | Diff for complete control |
| `SIGNIFICANT_CHANGE` | 0.3 | Change to be considered significant |
| `STRONG_CHANGE` | 0.6 | Change for strong trend |
| `MIN_STREAK` | 2 | Minimum consecutive mins for streak |
| `STRONG_STREAK` | 3 | Strong streak length |
| `DOMINANT_STREAK` | 4 | Dominant streak length |
| `DIVERGENCE_THRESHOLD` | 0.4 | Change threshold for divergence |

---

## 🔄 Agent Flow Diagram

```
┌────────────────────────────────────────────────────────────────────┐
│                    GENERAL COMMENTARY AT MINUTE M                   │
└────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────────────────┐
│  STEP 1: Load Momentum Data                                         │
│  ┌────────────────────────────────────────────────────────────────┐│
│  │ From: momentum_by_period.csv                                   ││
│  │ Get: home_momentum, away_momentum, changes, history            ││
│  └────────────────────────────────────────────────────────────────┘│
└────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────────────────┐
│  STEP 2: Analyze Dominance                                          │
│  ┌────────────────────────────────────────────────────────────────┐│
│  │ diff = home_momentum - away_momentum                           ││
│  │ if |diff| > 2.5 → Complete Control                             ││
│  │ if |diff| > 1.5 → Dominant                                     ││
│  │ if |diff| > 0.5 → Slight Advantage                             ││
│  │ else → Balanced                                                ││
│  └────────────────────────────────────────────────────────────────┘│
└────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────────────────┐
│  STEP 3: Analyze Trend                                              │
│  ┌────────────────────────────────────────────────────────────────┐│
│  │ Check dominant team's momentum_change:                         ││
│  │ - change > +0.6 → "Surging"                                    ││
│  │ - change > +0.3 → "Improving"                                  ││
│  │ - change < -0.3 → "Losing grip"                                ││
│  │ - change < -0.6 → "Fading fast"                                ││
│  │ Also compare to opponent's change for context                  ││
│  └────────────────────────────────────────────────────────────────┘│
└────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────────────────┐
│  STEP 4: Detect Streaks                                             │
│  ┌────────────────────────────────────────────────────────────────┐│
│  │ Look at last 5 minutes of history                              ││
│  │ Count consecutive positive/negative changes for each team      ││
│  │ - 2 minutes → "Building"                                       ││
│  │ - 3 minutes → "Strong streak"                                  ││
│  │ - 4+ minutes → "Dominant streak"                               ││
│  └────────────────────────────────────────────────────────────────┘│
└────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────────────────┐
│  STEP 5: Detect Divergence                                          │
│  ┌────────────────────────────────────────────────────────────────┐│
│  │ Check if one team rising while other falling:                  ││
│  │ - home_change > +0.4 AND away_change < -0.4 → DIVERGENCE       ││
│  │ - This indicates a significant momentum shift                  ││
│  └────────────────────────────────────────────────────────────────┘│
└────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────────────────┐
│  STEP 6: Check Predictions (If minute >= 75)                        │
│  ┌────────────────────────────────────────────────────────────────┐│
│  │ From: arimax_predictions_by_period.csv                         ││
│  │ Get: predicted_change for both teams                           ││
│  │ Interpret: Who's expected to improve in next 3 min?            ││
│  └────────────────────────────────────────────────────────────────┘│
└────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────────────────┐
│  STEP 7: Generate Phrase                                            │
│  ┌────────────────────────────────────────────────────────────────┐│
│  │ Priority order:                                                ││
│  │ 1. Divergence (most dramatic)                                  ││
│  │ 2. Strong streak (3+ minutes)                                  ││
│  │ 3. Dominance + Trend combination                               ││
│  │ 4. Prediction note (if available)                              ││
│  └────────────────────────────────────────────────────────────────┘│
└────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────────────────┐
│  OUTPUT: Agent Decision                                             │
│  {                                                                  │
│    dominant_team, dominance_type,                                   │
│    trend_description, streak_info,                                  │
│    divergence_info, max_diff_info,                                  │
│    prediction_note, phrase_suggestion,                              │
│    detailed_summary                                                 │
│  }                                                                  │
└────────────────────────────────────────────────────────────────────┘
```

---

## 🧪 Testing

```bash
cd "NLP - Commentator/research/12_momentum_agent/scripts"
python test_agent.py
```

Expected output:
```
MOMENTUM AGENT TEST SUITE
==================================================================
✅ Basic functionality test PASSED
✅ Streak detection test PASSED
✅ Divergence detection test PASSED
✅ Prediction integration test PASSED
✅ Detailed summary test PASSED
✅ Multiple matches test PASSED
==================================================================
TEST RESULTS: 6 passed, 0 failed
```

---

## 📈 Integration with GPT Commentator

To integrate with the existing LLM commentary system:

```python
# In gpt_commentator integration
from momentum_agent import MomentumAgent

class MomentumCommentator:
    def __init__(self):
        self.momentum_agent = MomentumAgent()
    
    def generate_general_commentary(self, match_id, minute, period, match_context):
        # Get momentum analysis
        momentum = self.momentum_agent.analyze_for_general(
            match_id, minute, period
        )
        
        # Add to context for GPT
        if momentum['include_momentum']:
            match_context['momentum_phrase'] = momentum['phrase_suggestion']
            match_context['momentum_details'] = momentum['raw_data']
            
            if momentum.get('has_prediction'):
                match_context['momentum_prediction'] = momentum['prediction_note']
        
        # Generate commentary with momentum context
        return self.generate_with_context(match_context)
```

---

## 📝 Sample Detailed Summary Output

```
============================================================
MOMENTUM AGENT ANALYSIS - Minute 35'
============================================================

📊 CURRENT MOMENTUM:
   Germany: 5.42 (change: +0.38)
   Scotland: 4.98 (change: -0.12)
   Differential: +0.44

🏆 DOMINANCE:
   Status: Slight Advantage
   Dominant team: Germany
   Strength: moderate

📈 TREND:
   Description: Improving
   Direction: rising

🔥 STREAK ANALYSIS:
   Detected: YES
   Team: Germany
   Length: 3 consecutive minutes
   Type: positive momentum
   Strength: strong

↔️ DIVERGENCE:
   Detected: No (both teams moving similarly)

📏 MAX DIFFERENTIAL:
   Max in match: 1.67 at minute 8
   Max team: Germany
   Current vs max: near_peak

🔮 PREDICTION (ARIMAX):
   Not available (only for minute 75+)

============================================================
```

---

## 🔗 Related Phases

- **Phase 7**: All games commentary (rule-based)
- **Phase 10**: LLM commentary (GPT-based)
- **Phase 11**: LLM vs Real comparison

---

**Status:** ✅ Implemented  
**Date:** December 2024  
**Author:** Euro 2024 Momentum Project

