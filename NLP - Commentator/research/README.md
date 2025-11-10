# NLP Commentator - Research Directory

## 📋 Overview

This directory contains the complete research and development journey for the **NLP Football Commentator System** - a project that generates natural language commentary from Euro 2024 event data.

**Main Output:** `04_final_game_production/data/final_game_rich_commentary.csv`  
**Documentation:** `04_final_game_production/docs/FULL_FINAL_GAME_COMPLETE_GUIDE.md`

---

## 📂 Directory Structure

The research is organized chronologically into **5 phases**, showing the evolution from initial experiments to production-ready system and validation:

```
research/
├── 01_initial_experiments/         # Phase 1: Data exploration (3 games, 30 sequences)
├── 02_starting_game_commentary/    # Phase 2: Pre-match commentary (10 games)
├── 03_top_11_events_analysis/      # Phase 3: Event type templates (11 types)
├── 04_final_game_production/       # Phase 4: Full final game ⭐ PRODUCTION
└── 05_real_commentary_comparison/  # Phase 5: Real commentary comparison ⭐ NEW
```

---

## 🎯 Quick Start

**To use the production system:**

1. **Read the guide:**
   ```
   04_final_game_production/docs/FULL_FINAL_GAME_COMPLETE_GUIDE.md
   ```

2. **Run data extraction:**
   ```bash
   python 04_final_game_production/scripts/extract_final_game_detailed.py
   ```

3. **Generate commentary:**
   ```bash
   python 04_final_game_production/scripts/generate_rich_commentary.py
   ```

4. **Output file:**
   ```
   04_final_game_production/data/final_game_rich_commentary.csv
   ```

---

## 📚 Phase Details

### Phase 1: Initial Experiments (Proof of Concept)
**Goal:** Validate that event data can be used for commentary generation

**What was done:**
- Extracted 30 event sequences from 3 matches
- Focused on key events: shots, dribbles, carries, pressure
- Created initial data extraction pipeline

**Key Files:**
- `scripts/extract_commentator_data_simple.py` - Main extraction script
- `data/commentator_training_data.csv` - 144 events, 30 sequences
- `docs/DATASET_DESCRIPTION.md` - Data structure documentation

**Status:** ✅ Experimental (Proof of concept successful)

---

### Phase 2: Starting Game Commentary
**Goal:** Generate pre-match and kick-off commentary with team statistics

**What was done:**
- Extracted first 4 events from 10 games
- Added pre-match team statistics (wins, draws, goals, last result)
- Created starting game templates with neutral terminology

**Key Files:**
- `scripts/extract_starting_events_with_stats.py` - Extraction with team stats
- `data/starting_game_training_pairs.csv` - Pre-match commentary examples
- `docs/STARTING_GAME_COMMENTARY_GUIDE.md` - Template guide

**Status:** ✅ Experimental (Template approach validated)

---

### Phase 3: Top 11 Events Analysis
**Goal:** Develop commentary templates for the 11 most common event types

**What was done:**
- Analyzed top 11 event types by frequency
- Created detailed templates for each event type
- Generated training data with metadata and commentary

**Key Event Types:**
1. Pass (917 events)
2. Ball Receipt* (878)
3. Carry (759)
4. Pressure (327)
5. Shot (25)
6. Dribble, Duel, Clearance, Block, Goal Keeper, Interception

**Key Files:**
- `scripts/create_complete_training_data.py` - Consolidated training data
- `data/event_commentary_training_data.csv` - 144 events, 40 columns
- `docs/TOP_11_EVENTS_COMMENTARY_GUIDE.md` - Comprehensive guide
- `docs/QUICK_REFERENCE_TOP_11_EVENTS.md` - Quick reference table

**Status:** ✅ Experimental (Templates refined)

---

### Phase 4: Final Game Production ⭐
**Goal:** Production-quality commentary for the full Euro 2024 final (Spain vs England)

**What was done:**
- Full match extraction: **3,312 events** (0:00-94:00)
- **19 event type templates** with sophisticated logic
- **13 enrichment fields** (key passes, danger zones, pressure tracking)
- **Dynamic in-match statistics** (score tracking, player goals)
- **Sequence narrative flow** (no player name repetition)
- **Special period commentary** (game start, 2nd half, stoppage time)
- **Bug fixes:** All critical issues resolved

**Key Features:**
- ✅ 62 columns of enriched data
- ✅ 376 sequences with natural narrative flow
- ✅ Mixed commentary style (neutral/excited)
- ✅ Player & team milestone tracking
- ✅ Tournament & in-match statistics
- ✅ Complete bug report & solutions

**Key Files:**
- `scripts/extract_final_game_detailed.py` - Data extraction (58 columns)
- `scripts/generate_rich_commentary.py` - Commentary generation (19 templates)
- `scripts/verify_all_fixes.py` - Verification script
- `data/final_game_rich_commentary.csv` - **⭐ MAIN OUTPUT** (3,312 events, 62 cols)
- `docs/FULL_FINAL_GAME_COMPLETE_GUIDE.md` - **⭐ START HERE** (Complete guide + bug report)
- `docs/FINAL_GAME_PROJECT_SUMMARY.md` - Project summary
- `docs/COMMENTARY_EXAMPLES_SHOWCASE.md` - Real examples

**Status:** ✅ **PRODUCTION READY**

---

### Phase 5: Real Commentary Comparison ⭐ NEW
**Goal:** Validate generated commentary quality by comparing with professional human commentary

**What is being done:**
- **Data Collection (Complete):** Extracted real commentary from Sports Mole
- **3 Matches:** Final + 2 Semi-finals (~90 minute-by-minute entries)
- **Comparison Method:** 1-minute aggregation strategy
- **3 Metrics:** Cosine Similarity, Entity Overlap, Semantic Similarity

**Why Sports Mole:**
✅ Minute-by-minute structure (perfect for 1-min aggregation)  
✅ Event-driven narrative (matches our approach)  
✅ Consistent vocabulary (similar terms: shoots, passes, saves)  
✅ Entity-rich descriptions (players, actions, locations)  
✅ 95% match score (best fit for comparison)

**Key Files:**
- `docs/DATA_SOURCES_EVALUATION.md` - Why Sports Mole (7 sources compared)
- `docs/COMPARISON_METHODOLOGY.md` - How to compare (1-min aggregation strategy)
- `data/sports_mole_final_commentary.csv` - Spain vs England (30 entries)
- `data/sports_mole_england_netherlands_commentary.csv` - Semi-final (30+ entries)
- `data/sports_mole_spain_france_commentary.csv` - Semi-final (30+ entries)

**Comparison Strategy:**
```
Our Data (47'):     [Event 1] → [Event 2] → [Event 3] → [Event 4]
                    ↓
Sequence:           "Williams receives, carries, shoots - GOAL! Spain 1-0"
                    ↓ Compare ↓
Sports Mole (47'):  "Williams bursts into box, fires into corner - GOAL Spain 1-0"
                    ↓
Metrics:            Cosine=0.55, Entity=0.90, Semantic=0.85 (Excellent)
```

**Expected Results:**
- Goals (n=9): Cosine 0.55-0.65, Entity 0.85-0.95, Semantic 0.80-0.90
- Shots (n=70): Cosine 0.40-0.50, Entity 0.70-0.80, Semantic 0.65-0.75
- Overall Quality Score: 0.65-0.80 (Good to Excellent)

**Next Steps:**
1. 🔄 Aggregate our data by minute
2. 🔄 Calculate all 3 metrics for key moments
3. 🔄 Analyze results and identify improvements
4. 🔄 Update templates based on real examples

**Status:** 🔄 **DATA COLLECTION COMPLETE** - Ready for comparison

---

## 📊 Dataset Evolution

| Phase | Events | Columns | Matches | Sequences | Status |
|-------|--------|---------|---------|-----------|--------|
| Phase 1 | 144 | 30 | 3 | 30 | Experimental |
| Phase 2 | 40 | 20+ | 10 | 10 | Experimental |
| Phase 3 | 144 | 40 | 3 | 30 | Experimental |
| **Phase 4** | **3,312** | **62** | **1** | **376** | **✅ Production** |
| **Phase 5** | **~90** | **7** | **3** | **N/A** | **🔄 Data Collection** |

---

## 🎯 Event Type Coverage

### Phase 1-3 (Experimental):
- 11 basic event types

### Phase 4 (Production):
**19 event types with full templates:**
1. Pass (917 events)
2. Ball Receipt* (878)
3. Carry (759)
4. Pressure (327)
5. Ball Recovery (71)
6. Duel (70)
7. Clearance (43)
8. Block (43)
9. Goal Keeper (30)
10. Shot (25)
11. Substitution (7) ⭐ NEW
12. Foul Committed (19) ⭐ NEW
13. Interception
14. Dribble
15. Injury Stoppage (6) ⭐ NEW
16. Dispossessed (23) ⭐ NEW
17. Miscontrol (12) ⭐ NEW
18. Dribbled Past (10) ⭐ NEW
19. 50/50 (4) ⭐ NEW

**Coverage:** 100% of match events

---

## 🐛 Bug Fixes (Phase 4)

All critical bugs were identified and fixed:

| Bug | Issue | Status |
|-----|-------|--------|
| #1 | Sequence narrative flow (player name repetition) | ✅ Fixed |
| #2 | Missing templates (14 event types) | ✅ Fixed |
| #3 | Player match goals counting error | ✅ Fixed |
| #4 | Semi-final results incorrect | ✅ Fixed |
| #5 | Data enrichment verification | ✅ Verified |

**Full details:** `04_final_game_production/docs/FULL_FINAL_GAME_COMPLETE_GUIDE.md` (Part 9)

---

## 📖 Documentation Guide

### For New Users:
1. Start with: `04_final_game_production/docs/FULL_FINAL_GAME_COMPLETE_GUIDE.md`
2. See examples: `04_final_game_production/docs/COMMENTARY_EXAMPLES_SHOWCASE.md`

### For Developers:
1. Project summary: `04_final_game_production/docs/FINAL_GAME_PROJECT_SUMMARY.md`
2. Templates: `04_final_game_production/docs/FINAL_GAME_COMMENTARY_TEMPLATE_GUIDE.md`
3. Quick reference: `03_top_11_events_analysis/docs/QUICK_REFERENCE_TOP_11_EVENTS.md`

### For Historical Context:
- Phase 1: `01_initial_experiments/docs/DATASET_DESCRIPTION.md`
- Phase 2: `02_starting_game_commentary/docs/STARTING_GAME_COMMENTARY_GUIDE.md`
- Phase 3: `03_top_11_events_analysis/docs/TOP_11_EVENTS_COMMENTARY_GUIDE.md`

---

## 🚀 Next Steps

The production system (Phase 4) is **ready for:**

1. **NLP Model Training**
   - Use `final_game_rich_commentary.csv` as training data
   - 3,312 event-commentary pairs
   - 376 sequence-commentary pairs

2. **System Extension**
   - Apply to other matches (semi-finals, quarter-finals)
   - Expand to full tournament (51 matches)
   - Add more languages

3. **Model Development**
   - Train sequence-to-sequence model
   - Fine-tune pre-trained LLM
   - Implement real-time commentary generation

---

## 📊 Key Metrics

### Production System (Phase 4):
- **Events:** 3,312 (100% of final match)
- **Columns:** 62 (58 enriched + 4 commentary)
- **Sequences:** 376 with narrative flow
- **Event Types:** 19 with full templates
- **Coverage:** 0:00 - 94:00 (full match + stoppage)
- **Quality:** Production-ready ✅

### Data Enrichment:
- Tournament statistics (before final)
- In-match statistics (dynamic tracking)
- Event context (previous/next events)
- Field zones (9 zones)
- Key moments (key passes, danger zones, high pressure)
- Player milestones (goals, tournament performance)

---

## 👥 Contributors

**Project:** Euro 2024 Momentum Prediction & NLP Commentator  
**Phase 4 Status:** Production Ready (October 6, 2025)

---

## 📝 License

See main project LICENSE file.

---

**For questions or issues, refer to the comprehensive guide in Phase 4 documentation.**

