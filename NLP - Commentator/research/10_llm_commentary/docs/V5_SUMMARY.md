# GPT Commentator V5 - Summary

## Overview

V5 is the latest version of the GPT-based football commentary generator with:
1. **Score Fix** - Goal commentary shows correct score AFTER the goal
2. **Momentum Agent** - Intelligent agent for General commentary
3. **Dual Model Architecture** - GPT-4o for agent, GPT-4o-mini for commentary

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           V5 COMMENTARY GENERATION                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────┐     ┌──────────────────────────────────────────────────┐   │
│  │   EVENT     │     │              PROCESSING                           │   │
│  │   TYPE      │     │                                                   │   │
│  └──────┬──────┘     │  Goal ────────────► Score Fix (+1 to scorer)     │   │
│         │            │                                                   │   │
│         ├────────────┤  Shot/Card/etc ───► Standard processing          │   │
│         │            │                                                   │   │
│         │            │  General ─────────► Momentum Agent (GPT-4o)      │   │
│         │            │                          │                        │   │
│         │            │                          ▼                        │   │
│         │            │                    Explore patterns               │   │
│         │            │                    Find interesting               │   │
│         │            │                    Generate phrase                │   │
│         │            │                          │                        │   │
│         │            └──────────────────────────┼────────────────────────┘   │
│         │                                       │                            │
│         ▼                                       ▼                            │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                    GPT COMMENTARY (GPT-4o-mini)                       │   │
│  │                                                                       │   │
│  │  Receives:                                                            │   │
│  │  - Event data (player, team, outcome)                                 │   │
│  │  - Match context (score, minute, stage)                               │   │
│  │  - Momentum phrase (if General + interesting)                         │   │
│  │                                                                       │   │
│  │  Generates:                                                           │   │
│  │  - "[Event Type] Professional ESPN-style commentary"                  │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Key Fixes

### 1. Score Count Fix

**Problem:** Goal commentary showed score BEFORE the goal
```
Minute 10: Wirtz scores for Germany
Old V4: "Goal! Germany 0 - 0 Scotland"  ← WRONG
```

**Solution:** Detect Goal event and add 1 to scoring team
```python
if detected_type == 'Goal':
    if scoring_team == home_team:
        return (home_score + 1, away_score)
    else:
        return (home_score, away_score + 1)
```

**Result:**
```
Minute 10: Wirtz scores for Germany
V5: "Goal! Germany 1 - 0 Scotland"  ← CORRECT
```

---

## Momentum Data Explained

### Understanding the 3-Minute Windows

```
MINUTE 72 EXAMPLE:

┌─────────────────────────────────────────────────────────────────────┐
│                                                                      │
│  MOMENTUM VALUE at minute 72:                                        │
│  ═══════════════════════════                                        │
│  Calculated from events in window [69, 70, 71]                      │
│  → This is the "current state" of momentum                          │
│                                                                      │
│  Timeline:                                                           │
│  ... 69 ─── 70 ─── 71 ─── [72] ─── 73 ─── 74 ─── 75 ...            │
│       └──────────────┘      │                                        │
│       Events in window      │                                        │
│       for minute 72         │                                        │
│                             │                                        │
│  Example:                   │                                        │
│  Germany momentum = 5.42    │                                        │
│  Scotland momentum = 4.89   │                                        │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                                                                      │
│  MOMENTUM CHANGE at minute 72:                                       │
│  ════════════════════════════                                       │
│  = momentum[72,73,74] - momentum[69,70,71]                          │
│  = y(t+3) - y(t)                                                    │
│                                                                      │
│  This tells us: "How did momentum change in the LAST 3 minutes?"    │
│                                                                      │
│  Timeline:                                                           │
│  ... 69 ─── 70 ─── 71 ─── [72] ─── 73 ─── 74 ─── 75 ...            │
│       └──────────────┘      │      └──────────────┘                  │
│       PREVIOUS window       │      CURRENT window                    │
│       (baseline)            │      (where we are now)                │
│                             │                                        │
│  Example:                   │                                        │
│  Germany change = +0.38     │  (momentum rose)                       │
│  Scotland change = -0.52    │  (momentum fell)                       │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                                                                      │
│  PREDICTION (ARIMAX) - Only from minute 75+:                         │
│  ════════════════════════════════════════════                       │
│  Predicts: What will the momentum change be in the NEXT 3 minutes?  │
│                                                                      │
│  At minute 75:                                                       │
│  → Predicts momentum change for [76, 77, 78]                        │
│                                                                      │
│  Timeline:                                                           │
│  ... 72 ─── 73 ─── 74 ─── [75] ─── 76 ─── 77 ─── 78 ─── 79 ...     │
│                             │      └──────────────────┘              │
│                             │      PREDICTED window                  │
│                             │                                        │
│                             │                                        │
│  Why only from 75?                                                   │
│  → Need enough training data (minutes 0-74) for ARIMAX model        │
│  → Second half ends ~90, predictions until ~87                       │
│                                                                      │
│  Example at minute 80:                                               │
│  Germany predicted = +0.65  (model expects surge)                   │
│  Scotland predicted = -0.22 (model expects decline)                 │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Data Available at Each Minute

| Minute | Momentum Value | Momentum Change | ARIMAX Prediction |
|--------|---------------|-----------------|-------------------|
| 0-2 | ❌ (need 3 min history) | ❌ | ❌ |
| 3-74 | ✅ Both teams | ✅ Both teams | ❌ |
| 75-87 | ✅ Both teams | ✅ Both teams | ✅ Both teams |
| 88-90 | ✅ Both teams | ✅ Both teams | ⚠️ May be limited |

---

## Momentum Agent

### What the Agent Receives

```python
agent.explore(
    match_id=3930158,
    minute=72,
    period=2,
    score_home=3,
    score_away=0,
    home_team="Germany",
    away_team="Scotland",
    recent_events=[
        {'minute': 71, 'team': 'Germany', 'event_type': 'Shot', 'detail': 'Saved'},
        {'minute': 70, 'team': 'Scotland', 'event_type': 'Foul', 'detail': ''},
        {'minute': 69, 'team': 'Germany', 'event_type': 'Corner', 'detail': ''},
    ]
)
```

### What the Agent Sees

```
MATCH CONTEXT:
- Germany 3 - 0 Scotland
- Minute 72 (Second Half)

RECENT EVENTS:
├── 71' - Germany: Shot (Saved)
├── 70' - Scotland: Foul
└── 69' - Germany: Corner

MOMENTUM DATA:
├── Germany: 5.42 (change: +0.38)   ← Rising
├── Scotland: 4.89 (change: -0.52)  ← Falling
└── Dominant: Germany

DERIVED INSIGHTS:
├── Germany trajectory: Rising
├── Scotland trajectory: Falling
├── Gap trend: Widening
├── Germany: 4-minute positive streak
└── DIVERGENCE detected!

PREDICTION (if minute >= 75):
├── Germany predicted: +0.65
└── Scotland predicted: -0.22
```

### What the Agent Returns

```python
{
    'interesting': True,
    'pattern': 'Divergence with streak',
    'insight': 'Germany on 4-minute positive run while Scotland fading',
    'phrase': 'Germany building sustained pressure, Scotland struggling',
    'confidence': 'HIGH'
}
```

---

## Agent Decision Logic (NEW - Updated December 2024)

### How Does the Agent Decide if Momentum Data is Relevant?

The agent uses a **data-driven decision process**:

```
┌───────────────────────────────────────────────────────────────────┐
│                     AGENT DECISION FLOW                          │
├───────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Step 1: RECEIVE DATA                                            │
│  ─────────────────────                                            │
│  - Current momentum values (both teams)                           │
│  - Momentum changes (both teams)                                  │
│  - History (last 10 minutes)                                      │
│  - Derived metrics (NEW):                                         │
│    • Window dominance counts                                      │
│    • Sequence metrics (positive/negative counts)                  │
│    • Historical crossovers                                        │
│  - Predictions (minute 76+ only):                                 │
│    • Full prediction window (76 to ~90)                          │
│    • Prediction summary (NEW):                                    │
│      - Positive/negative prediction counts                        │
│      - Trends (improving/declining/stable)                        │
│      - Prediction crossovers                                      │
│      - Dominance ratio                                            │
│  - Static research tables (thresholds, correlations)              │
│                                                                   │
│  Step 2: PATTERN DETECTION                                        │
│  ──────────────────────────                                        │
│  Agent FREELY explores data looking for:                          │
│  - Streaks: 2, 3, 4+ consecutive positive/negative changes       │
│  - Divergence: One team rising, other falling                     │
│  - Window dominance: One team winning most windows                │
│  - Sequence margins: Compare to research thresholds               │
│  - Prediction patterns (minute 76+): Sustained trends             │
│  - Crossovers: Leadership changes (historical + predicted)        │
│                                                                   │
│  Step 3: THRESHOLD COMPARISON                                     │
│  ─────────────────────────────                                     │
│  Compare current state to RESEARCH INSIGHTS:                      │
│  - 50%+ momentum margin → 64.3% win correlation                   │
│  - 3+ sequence margin → 0% lose rate                              │
│  - 76.8% goals with positive momentum change                      │
│  - Metrics disagree pattern → 66.7% win                           │
│                                                                   │
│  Step 4: CONFIDENCE CALCULATION                                   │
│  ──────────────────────────────                                    │
│  Based on pattern strength and research correlation:              │
│  - 0.8-1.0: Strong research match (3+ seq margin, divergence)     │
│  - 0.6-0.8: Clear pattern (prediction trend, 2+ seq)              │
│  - 0.4-0.6: Minor pattern (short streak, small gap)               │
│  - 0.0-0.4: No interesting pattern                                │
│                                                                   │
│  Step 5: DATA SELECTION                                           │
│  ──────────────────────                                            │
│  If INTERESTING (confidence >= 0.7):                              │
│  - Select specific data points to forward                         │
│  - Include reason why data is interesting                         │
│  - Emphasize predictions when available                           │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

### Data the Agent Receives

#### Historical Data (until current minute)

| Metric | Description | Use |
|--------|-------------|-----|
| `window_dominance` | Home: X wins, Away: Y wins, Ties: Z | Who controls the match? |
| `sequence_metrics.home.total_positive_sequences` | Count of 2+ positive streaks | Research threshold comparison |
| `sequence_metrics.seq_count_margin` | Difference in sequence counts | 3+ margin = 0% lose! |
| `sequence_metrics.momentum_margin_pct` | % difference in total momentum | 50%+ = 64.3% win |
| `historical_crossovers` | Minutes where leadership switched | Momentum shifts |
| `home_streak.current_streak` | Current consecutive changes | Ongoing pattern |
| `home_trajectory` / `away_trajectory` | Rising/falling/stable | Direction |

#### Prediction Data (minute 76+ ONLY)

| Metric | Description | Use |
|--------|-------------|-----|
| `prediction_summary.home_positive_predictions` | Count of positive predictions | Future outlook |
| `prediction_summary.home_negative_predictions` | Count of negative predictions | Warning sign |
| `prediction_summary.home_trend` | improving/declining/stable | Direction of predictions |
| `prediction_summary.prediction_crossovers` | Predicted leadership changes | Future shifts |
| `prediction_summary.predicted_overall_dominant` | Who dominates predictions | Overall outlook |
| `prediction_summary.dominance_ratio` | e.g., "12/15" | Confidence in prediction |

### Confidence Calculation

The agent calculates confidence based on:

```python
# Pattern strength scoring (internal agent logic)

CONFIDENCE_FACTORS = {
    # Historical patterns
    'streak_3+': +0.25,
    'streak_4+': +0.35,
    'divergence_detected': +0.30,
    'window_dominance_70%+': +0.20,
    'sequence_margin_3+': +0.35,  # Research: 0% lose!
    'momentum_margin_50%+': +0.25,  # Research: 64.3% win
    
    # Prediction patterns (minute 76+)
    'prediction_streak_4+': +0.30,
    'prediction_trend_clear': +0.20,
    'prediction_crossover_detected': +0.25,
    'prediction_dominance_80%+': +0.30,
    
    # Research threshold matches
    'metrics_disagree_pattern': +0.35,  # Research: 66.7% win!
    'goal_vulnerability_pattern': +0.20,  # Team losing momentum
    
    # Negative factors
    'both_stable': -0.30,
    'no_clear_pattern': -0.25,
    'insufficient_data': -0.20,
}

# Final confidence = base (0.5) + sum of applicable factors
# Clamped to [0.0, 1.0]
```

### Example Agent Decision

**Minute 78, England vs Switzerland:**

```
INPUT DATA:
- Current: England 4.82 (+0.12), Switzerland 5.21 (+0.38)
- Window dominance: England 4, Switzerland 6
- England sequences: 2 positive, 1 negative, longest: 3
- Switzerland sequences: 4 positive, 0 negative, longest: 4
- Sequence margin: 2 (Switzerland favor)
- Predictions (78-87):
  - England: 3 positive, 7 negative, trend: declining
  - Switzerland: 8 positive, 2 negative, trend: improving
  - Crossover at: minute 82

AGENT ANALYSIS:
- Switzerland 4-minute positive streak ✓ (+0.35)
- Clear divergence detected ✓ (+0.30)
- Predictions favor Switzerland 8/10 ✓ (+0.30)
- Predicted crossover at 82 ✓ (+0.25)
- Matches research: sustained momentum = goal threat (+0.20)

CONFIDENCE: 0.5 + 1.40 = 1.0 (capped)

OUTPUT:
INTERESTING: YES
CONFIDENCE: 0.92
FORWARD_DATA:
- Switzerland: 5.21 (change: +0.38)
- 4-minute positive streak (longest in match)
- PREDICTIONS: 8/10 favor Switzerland
- Expected crossover at minute 82
REASON: Model predicts Switzerland momentum dominance for remaining 12 minutes
```

---

## Model Configuration

| Component | Model | Purpose | Cost |
|-----------|-------|---------|------|
| **Commentary** | gpt-4o-mini | Generate short ESPN text | Low |
| **Momentum Agent** | gpt-4o | Pattern discovery, reasoning | Medium |

---

## File Structure

```
10_llm_commentary/
├── scripts/
│   ├── gpt_commentator_v5.py      ← NEW: Main V5 commentator
│   ├── gpt_commentator_v4.py      ← Previous version (penalties)
│   ├── gpt_commentator_v3.py      ← Previous version (multi-events)
│   └── config.py                   ← Configuration
├── docs/
│   ├── V5_SUMMARY.md              ← This file
│   └── PROMPTS.md                  ← Prompt documentation
└── data/
    └── llm_commentary/             ← Output files

12_momentum_agent/
├── scripts/
│   ├── exploratory_momentum_agent.py  ← Agent with freedom
│   ├── momentum_data_loader.py        ← Load momentum CSV files
│   └── config.py                       ← Agent thresholds
├── docs/
│   ├── AGENT_LOGIC.md                 ← Detailed logic
│   └── HYBRID_AGENT_ARCHITECTURE.md   ← 3-layer design
└── README.md                          ← Agent documentation
```

---

## Usage Example

```python
from gpt_commentator_v5 import GPTCommentatorV5

# Initialize with momentum agent
commentator = GPTCommentatorV5(
    api_key="sk-...",
    model="gpt-4o-mini",      # Commentary model
    agent_model="gpt-4o",     # Momentum agent model
    enable_momentum=True
)

# Generate commentary
result = commentator.generate_minute_commentary(
    minute=72,
    events_data=[],
    match_context={
        'match_id': 3930158,
        'home_team': 'Germany',
        'away_team': 'Scotland',
        'home_score': 3,
        'away_score': 0,
        'period': 2,
        'stage': 'Group Stage',
        'detected_type': 'General',  # Momentum agent triggered
    },
    recent_events=[
        {'minute': 71, 'team': 'Germany', 'event_type': 'Shot'},
        {'minute': 70, 'team': 'Scotland', 'event_type': 'Foul'},
    ]
)

print(result)
# "[General] Germany building sustained pressure, Scotland on the back foot"
```

---

## Version History

| Version | Date | Key Features |
|---------|------|--------------|
| V1 | 2024-12 | Basic GPT commentary |
| V2 | 2024-12 | Few-shot examples, ESPN style |
| V3 | 2024-12 | Multi-events, domination detection |
| V4 | 2024-12 | Penalty handling, shootouts |
| **V5** | **2024-12** | **Score fix, Momentum agent** |

---

## Author

Euro 2024 Momentum Project  
December 2024

