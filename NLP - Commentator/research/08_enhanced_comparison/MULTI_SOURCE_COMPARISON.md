# Multi-Source Comparison Approach

## Overview

Instead of generating ONE comparison CSV per match, we generate **multiple CSVs per match** - one for EACH available real commentary source.

---

## Why Multiple Sources?

### Benefit 1: Compare Commentary Styles

Different sources have different commentary styles:

**FlashScore:**
- Concise, factual
- Event-focused
- Example: "Goal! Kolo Muani (France) makes the score 0:1"

**SportsMole:**
- More descriptive
- Play-by-play
- Example: "Kolo Muani's Euro 2024 is up and running! A composed finish after a lovely pass from Kevin de Bruyne"

**BBC:**
- Enthusiastic, narrative
- Context and atmosphere
- Example: "Oh, WOW! Talk about fast starts. Belgium could not wish for a better start"

**FOX/ESPN:**
- Professional broadcast style
- Action description
- Referee decisions

### Benefit 2: Validate Our Generated Commentary

By comparing to multiple sources, we can see:
- Which style does our commentary match best?
- Are we too technical or too enthusiastic?
- Do we capture key moments consistently across sources?

### Benefit 3: Comprehensive Analysis

For important matches (Final, Semi-Finals), we have 2-3 sources:
- Allows cross-validation
- Identifies what's universally captured (goals, cards) vs source-specific (atmosphere, analysis)

---

## File Naming Convention

### Format:
```
match_[MATCH_ID]_[SOURCE]_enhanced_comparison.csv
```

### Examples:

**Spain vs France SF (match 3942752):**
- `match_3942752_flashscore_enhanced_comparison.csv`
- `match_3942752_sports_mole_enhanced_comparison.csv`

**Spain vs England Final (match 3943043):**
- `match_3943043_flashscore_enhanced_comparison.csv`
- `match_3943043_sports_mole_enhanced_comparison.csv`
- `match_3943043_bbc_enhanced_comparison.csv`
- `match_3943043_fox_enhanced_comparison.csv`
- `match_3943043_espn_enhanced_comparison.csv`

**Group Stage Match (only FlashScore):**
- `match_3930158_flashscore_enhanced_comparison.csv`

---

## Expected Output

### Total Files by Source

| Source | Games | Files |
|--------|-------|-------|
| **FlashScore** | 51 | 51 |
| **SportsMole** | 6 | 6 |
| **BBC** | 4 | 4 |
| **FOX** | 4 | 4 |
| **ESPN** | 4 | 4 |
| **TOTAL** | 51 unique | **~65-70 CSVs** |

### Overlap

Some matches appear in multiple sources:
- Final (Spain vs England): 5 sources
- Semi-Finals (2 matches): 2 sources each
- Quarter-Finals/Round 16: 1-2 sources

---

## Processing Logic

### For Each Match:

1. **Load generated commentary** (once per match)
2. **Find ALL available real commentary sources**
3. **Process EACH source separately**:
   - Compare minute-by-minute
   - Calculate all 44 metrics
   - Save to source-specific CSV
4. **Report** number of sources processed

### Example Output:

```
================================================================================
PROCESSING MATCH 3942752
================================================================================

Teams: spain vs france
[OK] Loaded generated commentary: 1234 events
[OK] Found 2 real commentary source(s): FLASHSCORE, SPORTS_MOLE

------------------------------------------------------------
Processing source: FLASHSCORE
------------------------------------------------------------
[OK] Loaded real commentary: 89 entries
[COMPARING] Processing 89 real commentary rows...
[SUCCESS] SAVED: match_3942752_flashscore_enhanced_comparison.csv
   Total comparisons: 392
   Minutes covered: 89
   Average score: 0.234
[SUCCESS] FLASHSCORE completed

------------------------------------------------------------
Processing source: SPORTS_MOLE
------------------------------------------------------------
[OK] Loaded real commentary: 112 entries
[COMPARING] Processing 112 real commentary rows...
[SUCCESS] SAVED: match_3942752_sports_mole_enhanced_comparison.csv
   Total comparisons: 487
   Minutes covered: 98
   Average score: 0.198
[SUCCESS] SPORTS_MOLE completed

[SUCCESS] Match 3942752 - 2 source(s) processed
```

---

## Analysis Possibilities

### Compare Across Sources

For matches with multiple sources, analyze:

**1. Similarity Scores by Source:**
- Which source does our commentary match best?
- FlashScore more technical → Higher TF-IDF?
- BBC more narrative → Higher BERT embeddings?

**2. Sentiment by Source:**
- Does BBC have more positive sentiment (enthusiastic)?
- Is FlashScore more neutral (factual)?
- How does our sentiment compare?

**3. Coverage:**
- Do all sources cover the same minutes?
- Which events are universally mentioned?
- Source-specific commentary (crowd reactions, analysis)?

---

## Dashboard Integration (Phase 4)

The multi-source approach enables rich dashboard features:

### Filters:
- Select source(s) to analyze
- Compare "our commentary" across different sources
- Filter by match stage (group, knockout, final)

### Visualizations:
- Similarity scores by source (box plot)
- Sentiment distribution by source (violin plot)
- Coverage heatmap (which minutes have commentary per source)

### Source Comparison:
- Side-by-side comparison of same minute across sources
- Identify which generated sequence matches best with each source

---

## Summary

✅ **Multi-source approach provides:**
- Comprehensive validation
- Style comparison insights
- Rich data for analysis
- Multiple perspectives on same events

✅ **File structure is clear:**
- One CSV per match-source combination
- Easy to identify and load
- Preserves all comparison data

✅ **Processing is efficient:**
- Generated commentary loaded once per match
- Each source processed independently
- Progress tracked per source

**Status: ✅ Implemented and Running**

