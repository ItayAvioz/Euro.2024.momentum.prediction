# ⚽ Euro 2024 Momentum & AI Commentary

## 🎯 Project Overview

A Data Science & AI project with three core objectives:

1. **Predict Momentum Change** → ARIMAX model forecasts which team will gain/lose momentum in next 3 minutes
2. **Generate Commentary** → GPT-4o-mini creates ESPN-style match commentary
3. **Integrate Momentum via Agent** → GPT-4o agent decides when momentum insights are interesting enough to include

### What is Momentum?

Momentum = **Who controls the game right now?**

Built from **every event** (passes, shots, tackles, fouls) weighted by:
- **What happened** → Event type & outcome (success/failure)
- **Where** → Field location (attacking third = higher impact)
- **When** → Game time (late game = more critical)
- **Context** → Score state, pressure situation

**Key idea:** One team's positive = other team's negative (zero-sum)

---

## 🏆 Key Achievements

| Component | Result |
|-----------|--------|
| **ARIMAX Prediction** | 77.87% directional accuracy |
| **Differential Sign** | 66.00% (which team gains advantage) |
| **Sign Agreement** | 63.88% positive/negative prediction |
| **Commentary** | GPT-4 with ESPN-style comparison |
| **Dashboards** | 4 interactive Streamlit applications |

---

## 📊 Dataset (Euro 2024)

**Source:** StatsBomb Open Data

| Metric | Value | Detail |
|--------|-------|--------|
| **Matches** | 51 | Group (36) + Knockout (15) |
| **Events** | 187,858 | 3,683/game • 40.9/min |
| **Goals** | 117 | 2.29/match (2 in extra time) |
| **Yellow Cards** | 227 | 4.45/match |
| **Red Cards** | 5 | 0.10/match |
| **Corners** | 512 | 10.04/match |
| **Extra Time** | 5 matches | 2 goals scored |
| **Penalty Shootouts** | 3 | 60% of ET matches |
| **Own Goals** | 10 | 8.5% of all goals |
| **Penalties** | 12 awarded | 9 scored, 3 missed |

### Data Files
| File | Description |
|------|-------------|
| `euro_2024_complete_dataset.csv` | 187,858 events merged |
| `events_complete.csv` | All match events with 59 columns |
| `matches_complete.csv` | 51 matches metadata |
| `data_360_complete.csv` | 360° spatial tracking (163,521 events) |

📁 **Location:** `Data/`

---

## 📊 EDA - Key Findings

### Why 3-Minute Windows? (Autocorrelation Analysis)

| Lag | Autocorrelation | Interpretation |
|-----|-----------------|----------------|
| 1-min | 0.852 | Too high (noise) |
| **3-min** | **0.493** | **Optimal balance** |
| 5-min | 0.300 | Signal too weak |
| 15-min | 0.232 | Too much decay |

**Evidence:** 4,927 minute-level observations across 51 matches

### Why Predict Minutes 76-90? (Goal Distribution)

| Time Period | Goals | % of Total |
|-------------|-------|------------|
| 1-15 min | 18 | 15.7% |
| 16-30 min | 21 | 18.3% |
| 31-45+ min | 12 | 10.4% |
| 46-60 min | 18 | 15.7% |
| 61-75 min | 19 | 16.5% |
| **76-90+ min** | **27** | **23.5%** ⚡ |

**86-90+ minutes alone:** 15 goals (13.0%) - Dramatic finishes!

### Why Momentum Matters? (Result Analysis)

| Pattern | Matches | Finding |
|---------|---------|---------|
| Draws at Halftime | 27 (52.9%) | High uncertainty |
| Draws at 90 min | 19 (37.3%) | 8 resolved by late goals |
| Result Changes HT→FT | 21 (41.2%) | Momentum shifts matter |
| Late Winners (75-90+) | 10 (19.6%) | Critical window |
| Momentum ≠ Result | 8 (15.7%) | Combined metrics needed |

**Quarter-finals insight:** 100% close games (0-1 goal), 75% went to extra time

📁 **Location:** `EDA/` (70+ documented insights)

---

## ⚙️ Momentum Feature

### Calculation Logic

```
Momentum = Σ(base_weight × team_perspective × context) per 3-min window
```

**Three key aspects:**

1. **Base Weight** → 25 event types scored 0-10 by impact
   - High: Shot, Goal, Dribble, Interception (6-9.5)
   - Medium: Pass, Carry, Duel, Pressure (4-7)
   - Low: Clearance, Ball Receipt (2.5-4.5)

2. **Team Perspective** → Relative to target team
   - Own success = positive
   - Opponent success = negative (inverse)
   - Opponent failure = positive (our gain)

3. **Context Multipliers** → Location × Time × Score × Pressure
   - Attacking third, late game, trailing = amplified
   - Dampening applied if combined > 1.0

### Hybrid Recency Weighting

```
Weight = Base × (0.7 + 0.3 × recency_factor)
```
| Time in Window | Multiplier |
|----------------|------------|
| t-3 min (oldest) | ×0.70 |
| t-2 min | ×0.80 |
| t-1 min | ×0.90 |
| t-0 min (newest) | ×1.00 |

### Period Separation

| Period | Minutes | Events |
|--------|---------|--------|
| Period 1 | 0-45+stoppage | 93,628 |
| Period 2 | 45-90+stoppage | 88,447 |

**Why?** Prevents data contamination at half-time (minutes 45-48 overlap)

📁 **Location:** `models/period_separated_momentum/`

---

## 🎯 ARIMAX Model

### Performance Metrics

| Metric | Value | vs Random |
|--------|-------|-----------|
| **Directional** | 77.87% | +27.87% |
| **Differential** | 66.00% | +16.00% |
| **Sign Agreement** | 63.88% | +13.88% |

### Model Configuration
```
Prediction: Momentum Change = y(t+3) - y(t)
Training: Minutes 0-74
Testing: Minutes 75-90
Order: ARIMA(1,1,1)
Exogenous: Current momentum value
```

📁 **Location:** `models/period_separated_momentum/outputs/`

---

## 📈 Result Analysis: Winning vs Chasing Metrics

### Metric Classification

| Metric | Type | Meaning |
|--------|------|---------|
| **Absolute Momentum** | ✅ Winning | Controls the game, dictates play |
| **Number of Sequences** | ✅ Winning | Multiple attack phases, sustained pressure |
| **Positive Changes** | ❌ Chasing | Trying to recover, reactive play |
| **Longest Sequence** | ❌ Chasing | Desperate sustained push, often trailing |

### The Insight: Different Teams Analysis

When **Team A leads Winning metrics** AND **Team B leads Chasing metrics**:
- Team A = Dominant, in control
- Team B = Desperately trying to catch up
- **Result: Team A wins!**

### Best Combination: Abs Momentum (Winning) vs Positive Changes (Chasing)

| Abs Mom % | Pos Chg % | Games | WIN | LOSE |
|-----------|-----------|-------|-----|------|
| 0%+ | 0%+ | 18 | 61.1% | 16.7% |
| **0%+** | **5%+** | **4** | **100%** | **0%** |
| 10%+ | 0%+ | 16 | 68.8% | 6.2% |
| 15%+ | 0%+ | 16 | 68.8% | 6.2% |
| 20%+ | 0%+ | 12 | 75.0% | 8.3% |

🔥 **At 5%+ Pos Chg margin: 100% WIN rate!**

### Abs Momentum (Winning) vs Longest Sequence (Chasing)

| Abs Mom % | Longest | Games | WIN | LOSE |
|-----------|---------|-------|-----|------|
| 0%+ | 0+ | 23 | 52.2% | 13.0% |
| 0%+ | 3+ | 11 | 54.5% | 18.2% |
| 15%+ | 0+ | 16 | 62.5% | **0%** |
| 15%+ | 3+ | 6 | 83.3% | **0%** |
| **20%+** | **3+** | **5** | **100%** | **0%** |

### Late Game Impact (75-90+)

| Pattern | Matches | % of Total |
|---------|---------|------------|
| Late Winners | 10 | 19.6% |
| Late Equalizers | 9 | 17.6% |
| **Total Late Decisive** | **19** | **37.3%** |
| Dramatic Games (multiple changes) | 4 | 7.8% |

### Key Findings
- **15%+ Mom + 3+ Seq margin** = 0% lose rate
- **5%+ Pos Change margin** = 100% win rate
- **Winning + Chasing split** = clearest prediction signal

---

## 💬 Commentary System (NLP + LLM + Agent)

### Pipeline Overview

```
Events → NLP Analysis → GPT-4o-mini (Commentary) → GPT-4o Agent (Momentum) → Final Output
```

### Phase 1: Learn & Analyze (NLP)

| Analysis | Method | Findings |
|----------|--------|----------|
| **Event Patterns** | Statistical analysis | 70+ insights documented |
| **Commentary Structure** | Template extraction | Event-type specific formats |
| **Sentiment Patterns** | RoBERTa sentiment | Goal events most positive |
| **Entity Recognition** | NER extraction | Player/team mention patterns |

### Phase 2: Compare Real Commentary (69 files)

| Source | Files | Comparison Metrics |
|--------|-------|-------------------|
| FlashScore | 51 | TF-IDF similarity |
| Sports Mole | 6 | BERT embeddings (semantic) |
| ESPN | 4 | Entity matching |
| BBC | 4 | Sentiment alignment |
| FOX | 4 | Word overlap ratio |

**Comparison Results:**
- TF-IDF: Lexical similarity to real commentary
- BERT: Semantic meaning alignment
- Entities: Player/team/event recognition accuracy
- Sentiment: Emotional tone matching

### Phase 3: Choose Style → ESPN (Sports Mole)

Selected for: Professional tone, balanced detail, momentum-aware language

### Phase 4: Generate Commentary (GPT-4o-mini)

| Version | Features |
|---------|----------|
| V3 | Basic event commentary |
| V4 | Context-aware (score, time) |
| V5 | Full integration (momentum + agent) |
| V6 | Variety + Event chains + Momentum clarity + Fine-tuned parameters + Hallucination fix + Agent threshold 0.70 |

### Phase 5: Momentum Agent Integration (GPT-4o)

The agent decides **when and what** momentum data to include:

| Component | Description |
|-----------|-------------|
| **Model** | GPT-4o (reasoning) |
| **Input** | Momentum, change, predictions, game context |
| **Threshold** | ≥0.75 confidence to include |
| **Output** | Selected momentum insights |

**Agent Focus Areas:**
1. **Tension** → Score leader ≠ Momentum leader
2. **Predictions** → ARIMAX forecasts (min 76-90)
3. **Patterns** → 4+ min streaks, max gaps, crossovers
4. **Research** → 0% LOSE threshold matches

**Result:** ~28% of commentary includes momentum (selective, not spam)

📁 **Location:** `NLP - Commentator/research/`

---

## 📊 Dashboards (4 Applications)

| Dashboard | Port | Key Features |
|-----------|------|--------------|
| **Tournament Overview** | 8505 | Stats, stages, goals, time patterns |
| **ARIMAX Momentum** | 8503 | Accuracy, differential, paired analysis |
| **Commentary Analysis** | 8501 | Events, templates, patterns |
| **LLM vs Real** | 8502 | Side-by-side comparison |

---

## 📁 Project Structure

```
Euro-2024-Momentum-Project/
├── 📊 Data/                          # StatsBomb Euro 2024 Dataset
│   └── euro_2024_complete_dataset.csv
├── 📈 EDA/                           # Exploratory Data Analysis (70+ insights)
├── ⚙️ models/                        # Momentum & ARIMAX Models
│   └── period_separated_momentum/    # Period-Separated Analysis
│       ├── dashboard/                # ARIMAX Dashboard
│       └── outputs/                  # Predictions & Analysis
├── 💬 NLP - Commentator/             # AI Commentary System
│   └── research/                     # 12 Research Phases
│       ├── 05_real_commentary/       # ESPN-style comparison
│       ├── 08_enhanced_comparison/   # 69 CSVs, 5 sources
│       ├── 10_llm_commentary/        # GPT-4 generation (V3-V5)
│       ├── 11_llm_real_comparison/   # LLM vs Real dashboard
│       └── 12_momentum_agent/        # GPT-4o agent
└── 📊 Dashboard/                     # Tournament Overview
```

---

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run Tournament Dashboard (port 8505)
cd Dashboard
streamlit run main.py --server.port 8505

# Run ARIMAX Dashboard (port 8503)
cd models/period_separated_momentum/dashboard
streamlit run main.py --server.port 8503

# Generate Commentary
cd "NLP - Commentator/research/10_llm_commentary/scripts"
python batch_generate_v5.py --match-id 3943043
```

---

## 🙏 Acknowledgments

- **StatsBomb** - Euro 2024 open dataset
- **OpenAI** - GPT-4 API
- **ESPN/BBC/FlashScore** - Commentary reference

---

*Euro 2024 Analytics | StatsBomb Data | December 2024*
