# Hybrid Momentum Agent Architecture

## Overview (Updated December 2024)

The agent uses an **EXPLORATORY** approach with freedom to discover patterns.
The 3-layer system ensures efficiency while giving LLM freedom to judge.

---

## Agent Judgment Process (How It Decides)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    AGENT JUDGMENT FLOW                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  STEP 1: RECEIVE ALL DATA                                               │
│  ─────────────────────────                                               │
│  • Current momentum (both teams)                                        │
│  • History (last 10 minutes)                                            │
│  • Derived metrics (window dominance, sequences, crossovers)            │
│  • Predictions (minute 76+ only)                                        │
│  • Static research tables (thresholds, correlations)                    │
│                                                                         │
│  STEP 2: PATTERN SCANNING (LLM explores freely)                         │
│  ──────────────────────────────────────────────────                      │
│  Agent looks for ANY of:                                                │
│  ✓ Streaks (2, 3, 4+ consecutive positive/negative)                     │
│  ✓ Divergence (one team rising, other falling)                          │
│  ✓ Window dominance (one team controls 70%+ of minutes)                 │
│  ✓ Sequence margins matching research thresholds                        │
│  ✓ Prediction patterns (76+): trends, crossovers, dominance             │
│                                                                         │
│  STEP 3: CONFIDENCE CALCULATION                                         │
│  ──────────────────────────────                                          │
│                                                                         │
│  confidence = BASE (0.5)                                                │
│             + POSITIVE_FACTORS (patterns found)                         │
│             - NEGATIVE_FACTORS (no patterns / stable)                   │
│                                                                         │
│  Example A - Strong patterns found:                                     │
│    Base:            0.50                                                │
│    4+ streak:      +0.35                                                │
│    Divergence:     +0.30                                                │
│    Pred dominance: +0.30                                                │
│    ────────────────────────                                              │
│    Total:           1.45 → clamped to 1.0                               │
│                                                                         │
│  Example B - NO patterns found:                                         │
│    Base:            0.50                                                │
│    both_stable:    -0.30                                                │
│    no_pattern:     -0.25                                                │
│    ────────────────────────                                              │
│    Total:          -0.05 → clamped to 0.0                               │
│                                                                         │
│  Example C - Weak patterns:                                             │
│    Base:            0.50                                                │
│    2-min streak:   +0.15                                                │
│    small gap:      +0.10                                                │
│    ────────────────────────                                              │
│    Total:           0.75 → just above threshold                         │
│                                                                         │
│  STEP 4: THRESHOLD CHECK                                                │
│  ────────────────────────                                                │
│  • confidence >= 0.7 → INTERESTING (forward data)                       │
│  • confidence < 0.7  → NOT INTERESTING (skip)                           │
│                                                                         │
│  STEP 5: DATA SELECTION (if interesting)                                │
│  ──────────────────────────────────────────                              │
│  Select most important data points to forward:                          │
│  • Strongest pattern found                                              │
│  • Supporting values                                                    │
│  • Predictions (emphasized if minute 76+)                               │
│  • Brief reason                                                         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Confidence Scoring Detail

### Positive Factors (ADD to base 0.5)

| Factor | Points | When Applied |
|--------|--------|--------------|
| Streak 3+ minutes | +0.25 | Current streak >= 3 |
| Streak 4+ minutes | +0.35 | Current streak >= 4 |
| Divergence detected | +0.30 | One team +0.4, other -0.4 |
| Window dominance 70%+ | +0.20 | One team won 70%+ windows |
| Sequence margin 3+ | +0.35 | Matches 0% lose research! |
| Momentum margin 50%+ | +0.25 | Matches 64% win research! |
| Metrics disagree pattern | +0.35 | Winning→A, Chasing→B |
| Prediction streak 4+ | +0.30 | 4+ consecutive same sign |
| Clear prediction trend | +0.20 | Improving or declining |
| Prediction dominance 80%+ | +0.30 | One team wins 80%+ predictions |
| Prediction crossover | +0.25 | Leadership change predicted |

### Negative Factors (SUBTRACT from score)

| Factor | Points | When Applied |
|--------|--------|--------------|
| Both teams stable | -0.30 | Both changes < 0.1 |
| No clear pattern | -0.25 | No patterns detected |
| Insufficient data | -0.20 | History < 3 minutes |

### Final Calculation

```
confidence = clamp(0.5 + positive_factors - negative_factors, 0.0, 1.0)

Examples:
  Strong:  0.5 + 0.95 - 0.00 = 1.45 → 1.0
  Weak:    0.5 + 0.15 - 0.00 = 0.65 → NOT interesting
  None:    0.5 + 0.00 - 0.55 = -0.05 → 0.0
  Border:  0.5 + 0.30 - 0.00 = 0.80 → interesting
```

---

## 3-Layer Decision System

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           INPUT                                          │
│  match_id=3930158, minute=40, score=3-0, momentum data                  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  ██████████████████████████████████████████████████████████████████████ │
│  █                                                                     █ │
│  █  LAYER 1: HARD RULES (Python Code)                                  █ │
│  █  Purpose: Pre-filtering for EFFICIENCY                              █ │
│  █                                                                     █ │
│  █  ┌─────────────────────────────────────────────────────────────┐   █ │
│  █  │  SKIP CONDITIONS (save API cost):                           │   █ │
│  █  │  • No momentum data available → SKIP (no API call)          │   █ │
│  █  │                                                              │   █ │
│  █  │  Otherwise: → PASS TO LLM AGENT                             │   █ │
│  █  │  (Let agent decide with full freedom)                       │   █ │
│  █  └─────────────────────────────────────────────────────────────┘   █ │
│  █                                                                     █ │
│  ██████████████████████████████████████████████████████████████████████ │
└─────────────────────────────────────────────────────────────────────────┘
          │                              │
          ▼                              ▼
     ┌─────────┐                  ┌───────────────┐
     │  SKIP   │                  │  PASS TO LLM  │
     │ (done)  │                  │    AGENT      │
     └─────────┘                  └───────┬───────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │
│  ░                                                                     ░ │
│  ░  LAYER 2: SOFT RULES (In Prompt - Research Context)                 ░ │
│  ░  Purpose: Provide research insights as VOCABULARY                   ░ │
│  ░                                                                     ░ │
│  ░  ┌─────────────────────────────────────────────────────────────┐   ░ │
│  ░  │  ## Static Research Tables (Agent Knowledge)                │   ░ │
│  ░  │                                                              │   ░ │
│  ░  │  Goal-Momentum Correlation:                                  │   ░ │
│  ░  │  • 76.8% goals scored with POSITIVE momentum change         │   ░ │
│  ░  │  • 62.6% goals conceded with NEGATIVE momentum change       │   ░ │
│  ░  │                                                              │   ░ │
│  ░  │  Winning Thresholds:                                         │   ░ │
│  ░  │  • 50%+ momentum margin → 64.3% win rate                    │   ░ │
│  ░  │  • 3+ sequence margin → 0% lose rate!                       │   ░ │
│  ░  │  • Metrics disagree → 66.7% win rate                        │   ░ │
│  ░  │                                                              │   ░ │
│  ░  │  Pattern Vocabulary:                                         │   ░ │
│  ░  │  • Streaks (2, 3, 4+ consecutive)                           │   ░ │
│  ░  │  • Divergence (one up, one down)                            │   ░ │
│  ░  │  • Window dominance (70%+ control)                          │   ░ │
│  ░  │  • Prediction patterns (trends, crossovers)                 │   ░ │
│  ░  └─────────────────────────────────────────────────────────────┘   ░ │
│  ░                                                                     ░ │
│  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │
│  ▓                                                                     ▓ │
│  ▓  LAYER 3: LLM AGENT (GPT-4o) - DATA SELECTOR                        ▓ │
│  ▓  Purpose: EXPLORE data, CALCULATE confidence, SELECT data           ▓ │
│  ▓                                                                     ▓ │
│  ▓  ┌─────────────────────────────────────────────────────────────┐   ▓ │
│  ▓  │  Agent receives:                                            │   ▓ │
│  ▓  │  • All momentum data (current + history)                    │   ▓ │
│  ▓  │  • Derived metrics (dominance, sequences, crossovers)       │   ▓ │
│  ▓  │  • Predictions + summary (minute 76+)                       │   ▓ │
│  ▓  │  • Research tables (static knowledge)                       │   ▓ │
│  ▓  │                                                              │   ▓ │
│  ▓  │  Agent EXPLORES freely and calculates confidence:           │   ▓ │
│  ▓  │  • Scans for patterns                                       │   ▓ │
│  ▓  │  • Compares to research thresholds                          │   ▓ │
│  ▓  │  • Calculates: 0.5 + positives - negatives                  │   ▓ │
│  ▓  │                                                              │   ▓ │
│  ▓  │  Agent outputs:                                              │   ▓ │
│  ▓  │  • INTERESTING: YES/NO (based on confidence >= 0.7)         │   ▓ │
│  ▓  │  • CONFIDENCE: 0.0-1.0                                      │   ▓ │
│  ▓  │  • FORWARD_DATA: Selected data points                       │   ▓ │
│  ▓  │  • REASON: Why this is interesting                          │   ▓ │
│  ▓  └─────────────────────────────────────────────────────────────┘   ▓ │
│  ▓                                                                     ▓ │
│  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           OUTPUT                                         │
│                                                                          │
│  If INTERESTING (confidence >= 0.7):                                     │
│    Forward selected data to commentary LLM                               │
│    Commentary integrates momentum naturally                              │
│                                                                          │
│  If NOT INTERESTING (confidence < 0.7):                                  │
│    No momentum data forwarded                                            │
│    Commentary generated without momentum context                         │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Layer Comparison

| Layer | Location | Type | Purpose | Example |
|-------|----------|------|---------|---------|
| **1** | Python code | Hard rule | Skip if no data | `if no_momentum_data: SKIP` |
| **2** | Prompt | Static knowledge | Research tables | "3+ seq margin = 0% lose" |
| **3** | API call | LLM agent | Explore + confidence | "4-min streak found, conf=0.85" |

---

## Decision Flow Examples

### Example 1: HARD SKIP (No API call needed)

```
Input: minute=5, period=1

Layer 1 Check:
  Momentum data available? NO (minute < 6, not enough history)
  
Result: HARD SKIP
API Call: NO (saved cost!)
Output: interesting=False, confidence=0
```

### Example 2: AGENT FINDS STRONG PATTERN

```
Input: minute=78, home=4.82, away=5.45, home_change=-0.18, away_change=+0.32

Agent Receives:
  • Current momentum values
  • History (10 minutes)
  • Derived: away 70% window dominance, 5-min streak
  • Predictions: away dominates 8/10, improving trend

Agent Analysis:
  Base:              0.50
  5-min streak:     +0.35
  70% dominance:    +0.20
  Pred dominance:   +0.30
  Pred trend:       +0.20
  ─────────────────────────
  Total:             1.55 → clamped to 1.0

Output:
  INTERESTING: YES
  CONFIDENCE: 0.95
  FORWARD_DATA:
    - Away: 5.45 (change: +0.32)
    - 5-minute positive streak
    - PREDICTIONS: 8/10 favor away
  REASON: Sustained away momentum, predictions confirm trend
```

### Example 3: AGENT FINDS NO PATTERN (Low Confidence)

```
Input: minute=35, home=4.92, away=4.88, home_change=+0.05, away_change=+0.03

Agent Receives:
  • Both teams very close
  • Small changes
  • No streaks (alternating)
  • No predictions (minute < 76)

Agent Analysis:
  Base:              0.50
  both_stable:      -0.30
  no_clear_pattern: -0.25
  ─────────────────────────
  Total:            -0.05 → clamped to 0.0

Output:
  INTERESTING: NO
  CONFIDENCE: 0.0
  FORWARD_DATA: none
  REASON: Both teams balanced, no significant patterns
```

### Example 4: BORDERLINE (Just Above Threshold)

```
Input: minute=60, home streak=3, small divergence

Agent Analysis:
  Base:              0.50
  3-min streak:     +0.25
  ─────────────────────────
  Total:             0.75 → just above 0.7 threshold

Output:
  INTERESTING: YES (barely)
  CONFIDENCE: 0.75
  FORWARD_DATA:
    - Home: 3-minute positive streak
  REASON: Building momentum pattern
```

---

## Why This Architecture?

### Hard Rules (Layer 1)
- **Fast**: No network latency
- **Free**: No API cost
- **Minimal**: Only skip when truly no data

### Static Knowledge (Layer 2)
- **Research-backed**: Thresholds from Euro 2024 analysis
- **Consistent**: Same knowledge for all decisions
- **Transparent**: Agent knows what patterns matter

### LLM Agent (Layer 3)
- **Exploratory**: Freedom to discover patterns
- **Confidence-based**: Quantified certainty
- **Selective**: Only forwards interesting data

---

## Configuration

```python
# LAYER 1: Hard Rules (in Python)
SKIP_IF_NO_DATA = True  # Only skip if literally no momentum data

# LAYER 2: Static Knowledge (in prompt)
# Research tables embedded in EXPLORATION_PROMPT

# LAYER 3: LLM Agent Settings
MODEL = "gpt-4o"              # Smart model for pattern detection
TEMPERATURE = 0.3             # Lower for consistency
MAX_TOKENS = 200              # Allow detailed response
CONFIDENCE_THRESHOLD = 0.7    # Minimum to forward data

# Confidence Scoring
BASE_CONFIDENCE = 0.5
POSITIVE_FACTORS = {
    'streak_3': 0.25,
    'streak_4': 0.35,
    'divergence': 0.30,
    'window_dominance_70': 0.20,
    'seq_margin_3': 0.35,
    'momentum_margin_50': 0.25,
    'metrics_disagree': 0.35,
    'pred_streak_4': 0.30,
    'pred_trend_clear': 0.20,
    'pred_dominance_80': 0.30,
    'pred_crossover': 0.25,
}
NEGATIVE_FACTORS = {
    'both_stable': -0.30,
    'no_pattern': -0.25,
    'insufficient_data': -0.20,
}
```

---

## Data Leakage Prevention

```
┌───────────────────────────────────────────────────────────────┐
│                    NO DATA LEAKAGE                            │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│  Agent ONLY sees:                                             │
│                                                               │
│  ✓ HISTORY: Actual momentum up to current minute              │
│  ✓ STATIC: Research tables (from past tournament analysis)    │
│  ✓ PREDICTIONS: Model output (NOT future actuals!)            │
│                                                               │
│  Agent NEVER sees:                                            │
│                                                               │
│  ✗ Future actual momentum values                              │
│  ✗ Future events                                              │
│  ✗ Match outcome                                              │
│                                                               │
│  Predictions are MODEL OUTPUT, not real future data!          │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

---

## Cost Analysis

| Scenario | API Calls | Est. Cost per Match |
|----------|-----------|---------------------|
| Agent (GPT-4o) | ~30-50 calls | ~$0.15-0.25 |
| Commentary (GPT-4o-mini) | ~90 calls | ~$0.05 |
| **Total** | **~120-140 calls** | **~$0.20-0.30** |

Note: Only ~30% of agent calls result in data being forwarded (confidence >= 0.7)

---

## Complete Flow Summary

```
1. Event detected as "General"
2. Layer 1: Check if momentum data exists
   - No data → SKIP (no API call)
   - Data exists → Pass to agent
3. Layer 2: Agent receives static research knowledge
4. Layer 3: Agent explores data
   - Scans for patterns
   - Calculates confidence (0.5 + positives - negatives)
   - If confidence >= 0.7 → Selects data to forward
   - If confidence < 0.7 → Returns "not interesting"
5. If interesting: Commentary LLM receives selected data
6. Commentary LLM integrates momentum naturally
```

---

**File:** `exploratory_momentum_agent.py`  
**Version:** 2.0  
**Date:** December 2024

