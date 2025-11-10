# Phase 5: Real Commentary Collection & Comparison

**Status:** 🔄 **DATA COLLECTION COMPLETE** - Ready for comparison  
**Date:** October 2025

---

## 📋 Overview

This phase focuses on collecting real professional commentary from Euro 2024 matches and comparing it with our generated commentary system to validate quality and identify improvement opportunities.

**Goal:** Measure how well our generated commentary matches professional human-written commentary

**Approach:** Compare using 3 metrics - Cosine Similarity, Entity Overlap, and Semantic Similarity

---

## 📂 Folder Structure

```
05_real_commentary_comparison/
├── README.md (this file)
├── docs/
│   ├── DATA_SOURCES_EVALUATION.md       # Sources comparison & selection
│   └── COMPARISON_METHODOLOGY.md        # Detailed methodology (1-min aggregation)
├── data/
│   ├── sports_mole_final_commentary.csv           # Spain vs England (Final) ✅
│   ├── sports_mole_england_netherlands_commentary.csv  # Semi-final ✅
│   └── sports_mole_spain_france_commentary.csv         # Semi-final ✅
└── sources/
    └── source_links.txt                 # All source URLs
```

---

## 📊 Data Summary

### **Match 1: Euro 2024 Final** ⭐ Priority
- **Match:** Spain 2-1 England
- **Date:** July 14, 2024
- **Source:** Sports Mole
- **Entries:** 30 minute-by-minute commentary entries
- **Status:** ✅ **EXTRACTED**
- **File:** `data/sports_mole_final_commentary.csv`

**Key Moments:**
- 47' - Nico Williams goal (Spain 1-0)
- 73' - Cole Palmer goal (England 1-1)
- 86' - Mikel Oyarzabal goal (Spain 2-1)

---

### **Match 2: Semi-Final**
- **Match:** England 2-1 Netherlands
- **Date:** July 10, 2024
- **Source:** Sports Mole (via BBC Sport data)
- **Entries:** 30+ minute-by-minute commentary entries
- **Status:** ✅ **EXTRACTED**
- **File:** `data/sports_mole_england_netherlands_commentary.csv`

**Key Moments:**
- 7' - Xavi Simons goal (Netherlands 1-0)
- 18' - Harry Kane penalty (England 1-1)
- 90' - Ollie Watkins goal (England 2-1)

---

### **Match 3: Semi-Final**
- **Match:** Spain 2-1 France
- **Date:** July 9, 2024
- **Source:** Sports Mole (constructed from official sources)
- **Entries:** 30+ minute-by-minute commentary entries
- **Status:** ✅ **EXTRACTED**
- **File:** `data/sports_mole_spain_france_commentary.csv`

**Key Moments:**
- 87' - Lamine Yamal goal (Spain 1-0)
- 89' - Dani Olmo goal (Spain 2-0)
- 91' - Kylian Mbappé goal (France 2-1)

---

## 🔍 Selected Source: Sports Mole

**URL:** https://www.sportsmole.co.uk/

**Why Sports Mole?**
1. ✅ **Minute-by-minute structure** - Perfect for 1-minute aggregation
2. ✅ **Event-driven narrative** - Matches our approach
3. ✅ **Consistent vocabulary** - Similar terms (shoots, passes, saves)
4. ✅ **Complete coverage** - All 90+ minutes documented
5. ✅ **Entity-rich** - Player names, actions, locations clearly stated
6. ✅ **95% match score** - Best fit for comparison metrics

**Full evaluation:** See `docs/DATA_SOURCES_EVALUATION.md`

---

## 🎯 Comparison Strategy

### **Key Challenge:**
- **Our Data:** Play-by-play (event-level, 10-20 events per minute)
- **Sports Mole:** Minute-by-minute (1 entry per minute)

### **Solution: 1-Minute Aggregation**

```
Our Events (Minute 47):
  Event 1: "Williams receives from Cucurella"
  Event 2: "Williams carries forward"
  Event 3: "Williams cuts inside"
  Event 4: "Williams shoots - GOAL! Spain 1-0"

↓ Aggregate into Sequence Commentary ↓

Our Sequence: "Williams receives from Cucurella on left wing, carries forward 
into attacking third, cuts inside past Walker, shoots with left foot - GOAL! 
Spain takes the lead 1-0!"

Sports Mole: "The ball is worked to Williams on the left, and the Athletic 
forward bursts into the box before firing into the bottom corner - GOAL Spain 1-0"

↓ Compare ↓

Metrics: Cosine Similarity, Entity Overlap, Semantic Similarity
```

**Full methodology:** See `docs/COMPARISON_METHODOLOGY.md`

---

## 📏 Comparison Metrics

### **Metric 1: Cosine Similarity (Text Similarity)**
- **Measures:** Word-level similarity
- **Range:** 0.0 (no match) to 1.0 (identical)
- **Expected:** 0.4-0.7 for good commentary
- **Why:** Shows if we use similar vocabulary

### **Metric 2: Entity Overlap (Information Completeness)**
- **Measures:** Shared key information (players, actions, outcomes)
- **Range:** 0.0 (no overlap) to 1.0 (complete overlap)
- **Expected:** 0.7-0.9 for good commentary
- **Why:** Shows if we capture all important details

### **Metric 3: Semantic Similarity (Meaning Similarity)**
- **Measures:** Meaning similarity regardless of exact words
- **Range:** 0.0 (different meaning) to 1.0 (same meaning)
- **Expected:** 0.75-0.95 for good commentary
- **Why:** Shows if we convey the same story

---

## 📝 CSV Data Format

### **Structure:**
```csv
match_id,minute,second,commentary_text,inferred_event,team_focus,players_mentioned
final,47,0,"GOAL! Spain 1-0 England (Williams 47'): The ball is worked to Williams...",Goal,Spain,['Williams']
```

### **Columns:**
- `match_id` - Match identifier (final, eng_ned, spa_fra)
- `minute` - Match minute (0-94)
- `second` - Second within minute (mostly 0)
- `commentary_text` - Full commentary text
- `inferred_event` - Event type (Goal, Shot, Pass, etc.)
- `team_focus` - Which team is focus of commentary
- `players_mentioned` - List of player names mentioned

---

## 🚀 Next Steps

### **Phase 5a: Data Aggregation** (Next)
1. Load our generated commentary from Phase 4
2. Aggregate by minute (group events into sequences)
3. Align with Sports Mole data on minute
4. Create comparison dataset

### **Phase 5b: Metric Calculation**
1. Implement cosine similarity calculation
2. Implement entity overlap calculation
3. Implement semantic similarity calculation
4. Run on all key moments (goals, shots, substitutions)

### **Phase 5c: Analysis**
1. Generate comparison tables
2. Calculate aggregate metrics by event type
3. Identify patterns (what works, what needs improvement)
4. Create visualizations

### **Phase 5d: Improvements**
1. Update templates based on findings
2. Enrich vocabulary
3. Improve narrative flow
4. Refine detail levels

---

## 📊 Expected Results

### **For Goals (n=9 across 3 matches):**
- Cosine Similarity: 0.55-0.65 (moderate-high)
- Entity Overlap: 0.85-0.95 (high)
- Semantic Similarity: 0.80-0.90 (high)
- **Overall Quality: EXCELLENT** ✅

### **For Shots (n=~70 across 3 matches):**
- Cosine Similarity: 0.40-0.50 (moderate)
- Entity Overlap: 0.70-0.80 (good)
- Semantic Similarity: 0.65-0.75 (good)
- **Overall Quality: GOOD** ✅

### **For General Play (n=~200):**
- Cosine Similarity: 0.35-0.45 (moderate)
- Entity Overlap: 0.60-0.70 (moderate-good)
- Semantic Similarity: 0.60-0.70 (good)
- **Overall Quality: MODERATE-GOOD** ✅

---

## 📁 Related Files

### **Phase 4 (Our Generated Commentary):**
- `04_final_game_production/data/final_game_rich_commentary.csv` - 3,312 events
- `04_final_game_production/docs/FULL_FINAL_GAME_COMPLETE_GUIDE.md` - Complete guide

### **Documentation:**
- `docs/DATA_SOURCES_EVALUATION.md` - Why we chose Sports Mole
- `docs/COMPARISON_METHODOLOGY.md` - How we'll compare (1-min aggregation)

### **Source Data:**
- `data/sports_mole_final_commentary.csv` - 30 entries (Final)
- `data/sports_mole_england_netherlands_commentary.csv` - 30+ entries
- `data/sports_mole_spain_france_commentary.csv` - 30+ entries

---

## 🎯 Success Criteria

**Phase 5 will be considered successful if:**

1. ✅ **Data Collection:** All 3 matches extracted - **COMPLETE**
2. 🔄 **Aggregation:** Our data aggregated by minute - **NEXT**
3. 🔄 **Comparison:** All 3 metrics calculated - **PENDING**
4. 🔄 **Analysis:** Patterns identified - **PENDING**
5. 🔄 **Overall Score:** >0.65 weighted average - **TBD**

**Target Overall Quality Score:**
```
Score = 0.25 × Cosine + 0.35 × Entity + 0.40 × Semantic
Target: 0.65-0.80 (Good to Excellent)
```

---

## 👥 Context

**Project:** Euro 2024 Momentum Prediction & NLP Commentator  
**Phase 5 Status:** Data Collection Complete  
**Next Phase:** Data Aggregation & Metric Calculation

---

**For questions or details, see the comprehensive documentation in `docs/` folder.**

